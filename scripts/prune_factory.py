"""Drop factory clip-art traits and rest-copied hold rear-arms."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "config" / "traits.json"
RARITY = ROOT / "config" / "rarity.json"
STACK = ROOT / "config" / "layer_stack.json"
LAYERS = ROOT / "layers"

DROP_IDS = {
    ("held_item", "thermos"),
    ("facial", "sunglasses"),
    ("pattern", "stars"),
    ("ground_accessory", "tiny-campfire"),
    ("rear_environment", "distant-pines"),
    ("atmosphere", "steady-snow"),
    ("structural", "basic-baffles"),
    ("structural", "hood-drawstring"),
    ("structural", "a-frame-poles"),
    ("structural", "guy-lines"),
    ("structural", "cabin-poles"),
    ("eyebrows", "neutral"),
    ("eyebrows", "raised"),
    ("eyebrows", "concerned"),
    ("eyebrows", "mischievous"),
    ("eyebrows", "determined"),
}

CLASS_RESTRICT = {
    ("held_item", "coffee"): ["sleeping-bag"],
    ("held_item", "map"): ["small-tent"],
    ("held_item", "lantern"): ["large-tent"],
    ("pattern", "patchwork"): ["sleeping-bag"],
    ("pattern", "two-tone-panel"): ["small-tent"],
    ("eyes", "sleepy"): ["sleeping-bag", "small-tent"],
    ("footwear", "basic-shoes"): ["sleeping-bag"],
    ("facial", "blush"): ["sleeping-bag"],
}

FILES_OVERRIDE = {
    ("arm_pose", "hold-item"): ["front_arm"],
    ("arm_pose", "hold-two-hand"): ["front_arm"],
    ("held_item", "lantern"): ["front_held", "light_effect"],
}

SPECIAL_FIX = {
    "the-volunteer": {"held_item": "map", "arm_pose": "hold-two-hand", "eyebrows": "none", "structural": "none"},
    "the-outreach-worker": {"held_item": "lantern", "arm_pose": "hold-item", "eyebrows": "none", "pattern": "none", "structural": "none"},
    "the-survivor": {"held_item": "coffee", "arm_pose": "hold-item", "eyebrows": "none", "structural": "none"},
    "the-navigator": {"held_item": "map", "arm_pose": "hold-two-hand", "eyebrows": "none", "structural": "none", "mouth": "smile"},
    "the-night-watch": {"held_item": "lantern", "arm_pose": "hold-item", "eyebrows": "none", "structural": "none"},
    "the-campfire-keeper": {"held_item": "coffee", "arm_pose": "hold-item", "eyebrows": "none", "ground_accessory": "none", "structural": "none"},
    "the-warm-heart": {"held_item": "coffee", "arm_pose": "hold-item", "eyebrows": "none", "structural": "none"},
    "the-first-snow": {"held_item": "none", "arm_pose": "rest", "eyebrows": "none", "structural": "none"},
    "the-early-riser": {"held_item": "map", "arm_pose": "hold-two-hand", "eyebrows": "none", "structural": "none"},
    "the-trailblazer": {"held_item": "lantern", "arm_pose": "hold-item", "eyebrows": "none", "structural": "none"},
    "the-hope-dealer": {"held_item": "map", "arm_pose": "hold-two-hand", "eyebrows": "none", "structural": "none"},
    "the-second-chance": {"held_item": "coffee", "arm_pose": "hold-item", "eyebrows": "none", "structural": "none"},
    "the-not-by-chance": {"eyebrows": "none", "structural": "none", "held_item": "lantern", "arm_pose": "hold-item"},
}

DELETE_ALWAYS = [
    "sleeping-bag/arms-rear/hold-item.png",
    "sleeping-bag/arms-rear/hold-two-hand.png",
    "small-tent/arms-rear/hold-item.png",
    "small-tent/arms-rear/hold-two-hand.png",
    "large-tent/arms-rear/hold-item.png",
    "large-tent/arms-rear/hold-two-hand.png",
]


def main() -> None:
    data = json.loads(TRAITS.read_text(encoding="utf-8"))
    kept = []
    has_brow_none = False
    has_struct_none = False
    for t in data["traits"]:
        key = (t["slot"], t["id"])
        if key in DROP_IDS:
            continue
        if key in CLASS_RESTRICT:
            t["classes"] = CLASS_RESTRICT[key]
        if key in FILES_OVERRIDE:
            t["files"] = FILES_OVERRIDE[key]
        if t["slot"] == "eyebrows" and t["id"] == "none":
            has_brow_none = True
        if t["slot"] == "structural" and t["id"] == "none":
            has_struct_none = True
        kept.append(t)
    if not has_brow_none:
        kept.append({
            "id": "none", "slot": "eyebrows", "name": "None", "phase": 3,
            "band": "common", "weight": 1000,
            "classes": ["sleeping-bag", "small-tent", "large-tent"],
        })
    if not has_struct_none:
        kept.append({
            "id": "none", "slot": "structural", "name": "None", "phase": 3,
            "band": "common", "weight": 820,
            "classes": ["sleeping-bag", "small-tent", "large-tent"],
        })
    for slot in data.get("slots", []):
        if slot["id"] in {"eyebrows", "structural"}:
            slot["optional"] = True
    data["traits"] = kept
    TRAITS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    rarity = json.loads(RARITY.read_text(encoding="utf-8"))
    for ch in rarity["specials"]["characters"]:
        fix = SPECIAL_FIX.get(ch["id"])
        if not fix:
            continue
        ch["traits"].update(fix)
    RARITY.write_text(json.dumps(rarity, indent=2) + "\n", encoding="utf-8")

    stack = json.loads(STACK.read_text(encoding="utf-8"))
    stack["split_assets"]["arm_pose"]["hold-item"] = ["front_arm"]
    stack["split_assets"]["arm_pose"]["hold-two-hand"] = ["front_arm"]
    stack["split_assets"]["held_item"] = {
        "coffee": [],
        "lantern": ["front_held", "light_effect"],
        "map": [],
    }
    snow = stack["split_assets"].get("atmosphere", {})
    snow.pop("steady-snow", None)
    snow.pop("heavy-snow", None)
    STACK.write_text(json.dumps(stack, indent=2) + "\n", encoding="utf-8")

    deleted = 0
    for rel in DELETE_ALWAYS:
        p = LAYERS / rel
        if p.exists():
            p.unlink()
            deleted += 1
            print("deleted copy", rel)

    from warm_company.library import required_paths
    needed = {p.resolve() for p in required_paths()}
    for p in LAYERS.rglob("*.png"):
        if p.resolve() not in needed:
            p.unlink()
            deleted += 1
            print("deleted extra", p.relative_to(ROOT).as_posix())
    print("traits", len(kept), "deleted", deleted)


if __name__ == "__main__":
    main()
