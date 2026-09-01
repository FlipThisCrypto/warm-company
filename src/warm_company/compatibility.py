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


def is_legal(class_id: str, traits: dict[str, str]) -> bool:
    return not violations(class_id, traits)
