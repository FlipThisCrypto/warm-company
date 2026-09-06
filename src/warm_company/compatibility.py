from __future__ import annotations

from typing import Any

from . import config


def _slot_value(traits: dict[str, str], slot: str) -> str:
    return traits.get(slot, "none")


def _if_matches(condition: dict[str, Any], traits: dict[str, str]) -> bool:
    slot = condition["slot"]
    value = _slot_value(traits, slot)
    if "equals" in condition:
        return value == condition["equals"]
    if "not_in" in condition:
        return value not in set(condition["not_in"])
    if "in" in condition:
        return value in set(condition["in"])
    return False


def apply_forces(traits: dict[str, str]) -> dict[str, str]:
    updated = dict(traits)
    for rule in config.compatibility()["rules"]:
        if "forces" not in rule:
            continue
        if _if_matches(rule["if"], updated):
            forced = rule["forces"]
            updated[forced["slot"]] = forced["id"]
    return updated


def violations(class_id: str, traits: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for rule in config.compatibility()["rules"]:
        if not _if_matches(rule["if"], traits):
            continue
        if "classes_only" in rule and class_id not in rule["classes_only"]:
            problems.append(f"{rule['id']}: class {class_id} cannot use this trait")
        if "excludes" in rule:
            slot = rule["excludes"]["slot"]
            banned = set(rule["excludes"]["ids"])
            if _slot_value(traits, slot) in banned:
                problems.append(f"{rule['id']}: {slot}={traits.get(slot)} excluded")
        if "requires" in rule:
            slot = rule["requires"]["slot"]
            allowed = set(rule["requires"]["ids"])
            if _slot_value(traits, slot) not in allowed:
                problems.append(f"{rule['id']}: {slot} must be one of {sorted(allowed)}")
        if "forces" in rule:
            slot = rule["forces"]["slot"]
            if _slot_value(traits, slot) != rule["forces"]["id"]:
                problems.append(f"{rule['id']}: {slot} must be {rule['forces']['id']}")
    # Class membership of the chosen trait itself.
    for slot, trait_id in traits.items():
        row = config.trait_by_id(slot, trait_id)
        if row is None:
            if slot == "special":
                continue
            problems.append(f"unknown trait {slot}/{trait_id}")
            continue
        classes = row.get("classes") or []
        if "shared" not in classes and class_id not in classes:
            problems.append(f"{slot}/{trait_id} is not legal on {class_id}")
    return problems


def _rule_trait_refs(rule: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    cond = rule.get("if") or {}
    slot = cond.get("slot")
    if slot and "equals" in cond:
        refs.append((slot, cond["equals"]))
    if slot:
        for trait_id in cond.get("in") or []:
            refs.append((slot, trait_id))
        for trait_id in cond.get("not_in") or []:
            refs.append((slot, trait_id))
    if "forces" in rule:
        refs.append((rule["forces"]["slot"], rule["forces"]["id"]))
    for key in ("excludes", "requires"):
        if key in rule:
            for trait_id in rule[key].get("ids") or []:
                refs.append((rule[key]["slot"], trait_id))
    return refs


def orphan_rule_problems() -> list[str]:
    problems: list[str] = []
    for rule in config.compatibility()["rules"]:
        for slot, trait_id in _rule_trait_refs(rule):
            if trait_id == "none":
                continue
            if config.trait_by_id(slot, trait_id) is None:
                problems.append(f"{rule.get('id')} references unknown {slot}/{trait_id}")
    return problems


def forces_stable(traits: dict[str, str]) -> bool:
    once = apply_forces(traits)
    twice = apply_forces(once)
    return once == twice


def is_legal(class_id: str, traits: dict[str, str]) -> bool:
    from .resolve import resolve_plan

    if violations(class_id, traits):
        return False
    return resolve_plan(class_id, traits)["ok"]
