"""Drop factory clip-art traits; keep illustrated assets; retarget specials."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "config" / "traits.json"
RARITY = ROOT / "config" / "rarity.json"
LAYERS = ROOT / "layers"

KEEP = {
    "background": None,  # keep all
    "rear_environment": {"distant-pines", "campfire-glow", "none"},
    "rear_accessory": {"none"},
    "arm_pose": {"rest", "hold-item", "hold-two-hand", "wave"},
    "held_item": {"none", "coffee", "lantern", "thermos", "map"},
    "body": None,
    "pattern": {"none", "plaid", "patchwork", "two-tone-panel", "stars"},
    "structural": {"basic-baffles", "a-frame-poles", "cabin-poles", "extra-panels", "hood-drawstring", "guy-lines"},
    "legs": {"short-legs"},
    "footwear": {"basic-shoes", "work-boots", "snow-boots"},
    "face": {"standard-face"},
    "eyes": {"normal", "happy", "sleepy", "determined", "sunglasses-compatible"},
    "eyebrows": {"neutral", "raised", "concerned", "determined", "mischievous"},
    "mouth": {"smile", "grin", "determined"},
    "facial": {"none", "blush"},
    "body_accessory": {"none"},
    "headwear": {"none", "beanie", "knit-cap", "baseball-cap", "bucket-hat", "trapper-hat", "santa-hat", "earflap-beanie", "crown", "halo"},
    "ground_accessory": {"none", "tiny-campfire"},
    "atmosphere": {"none", "light-snow", "steady-snow"},
    "special": None,
}

# Restrict some hats to classes that have illustrated files
HAT_CLASSES = {
    "beanie": ["sleeping-bag", "small-tent", "large-tent"],
    "knit-cap": ["sleeping-bag", "small-tent"],
    "baseball-cap": ["sleeping-bag", "large-tent"],
    "bucket-hat": ["small-tent"],
    "trapper-hat": ["large-tent"],
    "santa-hat": ["sleeping-bag"],
    "earflap-beanie": ["sleeping-bag"],
    "crown": ["large-tent"],
    "halo": ["large-tent"],
}

WAVE_CLASSES = ["sleeping-bag"]

SPECIAL_FIX = {
    "the-volunteer": {"held_item": "coffee", "body_accessory": "none", "pattern": "two-tone-panel", "footwear": "work-boots"},
    "the-outreach-worker": {"held_item": "thermos", "headwear": "beanie", "body_accessory": "none", "atmosphere": "light-snow"},
    "the-survivor": {"held_item": "coffee", "headwear": "earflap-beanie", "pattern": "patchwork"},
    "the-navigator": {"held_item": "map", "headwear": "bucket-hat", "pattern": "two-tone-panel", "footwear": "work-boots"},
    "the-night-watch": {"eyes": "determined", "atmosphere": "light-snow"},
    "the-campfire-keeper": {"held_item": "coffee", "pattern": "plaid", "footwear": "snow-boots"},
    "the-warm-heart": {"eyes": "happy", "held_item": "coffee", "pattern": "patchwork"},
    "the-first-snow": {"eyes": "happy", "mouth": "smile", "headwear": "knit-cap", "facial": "blush"},
    "the-early-riser": {"footwear": "work-boots"},
    "the-trailblazer": {"held_item": "lantern", "headwear": "baseball-cap", "pattern": "none", "footwear": "work-boots"},
    "the-hope-dealer": {"eyebrows": "raised", "atmosphere": "light-snow", "headwear": "beanie"},
    "the-second-chance": {"headwear": "beanie", "held_item": "map", "footwear": "snow-boots", "body_accessory": "none"},
    "the-not-by-chance": {"eyes": "normal", "pattern": "none", "atmosphere": "light-snow"},
}


def main() -> None:
    data = json.loads(TRAITS.read_text(encoding="utf-8"))
    kept = []
    for t in data["traits"]:
        slot, tid = t["slot"], t["id"]
        allow = KEEP.get(slot)
        if allow is not None and tid not in allow:
            continue
        if slot == "headwear" and tid in HAT_CLASSES:
            t["classes"] = HAT_CLASSES[tid]
        if slot == "arm_pose" and tid == "wave":
            t["classes"] = WAVE_CLASSES
        if slot == "pattern" and tid == "plaid":
            t["classes"] = ["sleeping-bag"]
        if slot == "pattern" and tid == "patchwork":
            t["classes"] = ["sleeping-bag", "small-tent", "large-tent"]
        if slot == "pattern" and tid == "two-tone-panel":
            t["classes"] = ["small-tent", "large-tent"]
        if slot == "pattern" and tid == "stars":
            t["classes"] = ["sleeping-bag"]
        kept.append(t)
    data["traits"] = kept
    TRAITS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    rarity = json.loads(RARITY.read_text(encoding="utf-8"))
    for ch in rarity["specials"]["characters"]:
        fix = SPECIAL_FIX.get(ch["id"])
        if not fix:
            continue
        ch["traits"].update(fix)
    RARITY.write_text(json.dumps(rarity, indent=2) + "\n", encoding="utf-8")
    print("traits", len(kept))


if __name__ == "__main__":
    main()
