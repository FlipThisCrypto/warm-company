"""Resolve a token to a physical-resource plan before compositing."""

from __future__ import annotations

from typing import Any

from . import config

EMPTY_GRIP = {"hold-item", "hold-two-hand"}


def expand(names: list[str] | tuple[str, ...] | None) -> list[str]:
    aliases = config.resources().get("aliases") or {}
    out: list[str] = []
    for name in names or []:
        out.extend(aliases.get(name, [name]))
    return out


def spec_for(slot: str, trait_id: str) -> dict[str, Any]:
    if not trait_id or trait_id == "none":
        return {}
    defaults = config.resources().get("defaults") or {}
    found = defaults.get(f"{slot}/{trait_id}") or {}
    row = config.trait_by_id(slot, trait_id) or {}
    extra = row.get("resources") or {}
    merged = dict(found)
    for key, value in extra.items():
        merged[key] = value
    return merged


def matching_composites(traits: dict[str, str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for composite in config.resources().get("composites") or []:
        when = composite.get("when") or {}
        if all(traits.get(slot, "none") == value for slot, value in when.items()):
            hits.append(composite)
    return hits


def _add_owner(occupancy: dict[str, str], resource: str, owner: str, violations: list[str]) -> None:
    prior = occupancy.get(resource)
    if prior and prior != owner:
        violations.append(f"resource {resource} owned by {prior} and {owner}")
        return
    occupancy[resource] = owner


def resolve_plan(class_id: str, traits: dict[str, str]) -> dict[str, Any]:
    """Return occupancy, suppression, counts, and violations for a token."""
    violations: list[str] = []
    occupancy: dict[str, str] = {}
    suppress: set[str] = set()
    composites = matching_composites(traits)
    hands = 0
    legs = 0
    feet = 0

    pose = traits.get("arm_pose") or "rest"
    held = traits.get("held_item") or "none"
    if held == "none" and pose in EMPTY_GRIP:
        violations.append("empty grip pose")
    if held != "none" and pose in {"rest", "wave", "akimbo"}:
        violations.append("held item without grip pose")

    for composite in composites:
        owner = f"composite:{composite['id']}"
        for resource in expand(composite.get("occupies") or []):
            _add_owner(occupancy, resource, owner, violations)
        for slot in composite.get("suppresses_slots") or []:
            suppress.add(slot)
        hands = max(hands, int(composite.get("hands") or 0))
        legs = max(legs, int(composite.get("legs") or 0))
        feet = max(feet, int(composite.get("feet") or 0))

    slot_order = [
        "arm_pose",
        "held_item",
        "legs",
        "footwear",
        "headwear",
        "facial",
        "eyes",
        "mouth",
        "body_accessory",
        "rear_accessory",
        "ground_accessory",
        "rear_environment",
        "atmosphere",
        "structural",
        "pattern",
        "body",
    ]
    for slot in slot_order:
        trait_id = traits.get(slot) or "none"
        if trait_id == "none":
            continue
        spec = spec_for(slot, trait_id)
        owner = f"{slot}/{trait_id}"
        occupies = expand(spec.get("occupies") or [])
        contains = set(expand(spec.get("contains") or []))
        mode = spec.get("mode")
        if composites and slot in {"arm_pose", "held_item", "legs", "footwear", "body"}:
            continue
        for resource in occupies:
            if resource in occupancy:
                if mode == "duplicate":
                    suppress.add(slot)
                    continue
                if mode == "overlay":
                    continue
                if occupancy[resource].startswith("composite:"):
                    suppress.add(slot)
                    continue
                _add_owner(occupancy, resource, owner, violations)
            else:
                _add_owner(occupancy, resource, owner, violations)
        if "left_hand" in occupies or "right_hand" in occupies or "left_hand" in contains or "right_hand" in contains:
            used = {r for r in ("left_hand", "right_hand") if r in occupancy or r in contains or r in occupies}
            hands = max(hands, len(used))
        if "left_leg" in occupies or "right_leg" in occupies:
            used = {r for r in ("left_leg", "right_leg") if r in occupancy}
            legs = max(legs, len(used))
        if "left_foot" in occupies or "right_foot" in occupies:
            used = {r for r in ("left_foot", "right_foot") if r in occupancy}
            feet = max(feet, len(used))

    if not composites:
        if "left_hand" in occupancy or "right_hand" in occupancy:
            hands = len({r for r in ("left_hand", "right_hand") if r in occupancy})
        if "left_leg" in occupancy or "right_leg" in occupancy:
            legs = len({r for r in ("left_leg", "right_leg") if r in occupancy})
        if "left_foot" in occupancy or "right_foot" in occupancy:
            feet = len({r for r in ("left_foot", "right_foot") if r in occupancy})

    limits = config.resources().get("limits") or {}
    if hands > int(limits.get("hands", 2)):
        violations.append(f"hands {hands} > {limits.get('hands', 2)}")
    if legs > int(limits.get("legs", 2)):
        violations.append(f"legs {legs} > {limits.get('legs', 2)}")
    if feet > int(limits.get("feet", 2)):
        violations.append(f"feet {feet} > {limits.get('feet', 2)}")

    if held == "map" and hands < 2 and not composites:
        violations.append("two-hand prop does not consume both hands")
    if held in {"coffee", "lantern"} and hands < 1 and not composites:
        violations.append("one-hand prop does not consume a hand")

    from .compatibility import violations as compat_violations

    violations.extend(compat_violations(class_id, traits))

    return {
        "class_id": class_id,
        "traits": dict(traits),
        "composites": [row["id"] for row in composites],
        "occupancy": occupancy,
        "suppress": sorted(suppress),
        "hands": hands,
        "legs": legs,
        "feet": feet,
        "violations": violations,
        "ok": not violations,
    }


def resource_ok(class_id: str, traits: dict[str, str]) -> bool:
    return resolve_plan(class_id, traits)["ok"]


def definition_problems() -> list[str]:
    """Unknown composite targets, duplicate composite ids, circular when-keys."""
    problems: list[str] = []
    seen: set[str] = set()
    for composite in config.resources().get("composites") or []:
        cid = composite.get("id") or ""
        if cid in seen:
            problems.append(f"duplicate composite {cid}")
        seen.add(cid)
        when = composite.get("when") or {}
        if not when:
            problems.append(f"composite {cid} has empty when")
        for slot, value in when.items():
            if config.trait_by_id(slot, value) is None:
                problems.append(f"composite {cid} unknown {slot}/{value}")
        for other in config.resources().get("composites") or []:
            if other is composite:
                continue
            if other.get("when") == when:
                problems.append(f"composite {cid} duplicates when of {other.get('id')}")
    defaults = config.resources().get("defaults") or {}
    for key in defaults:
        slot, _, trait_id = key.partition("/")
        if config.trait_by_id(slot, trait_id) is None:
            problems.append(f"default {key} has no trait")
    return sorted(set(problems))
