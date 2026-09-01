from __future__ import annotations

import json
from typing import Any

from . import config
from .paths import BUILD, ensure_build

SKIP_IF_NONE = {
    "rear_environment",
    "rear_accessory",
    "held_item",
    "pattern",
    "facial",
    "body_accessory",
    "headwear",
    "ground_accessory",
    "atmosphere",
    "special",
}

SLOT_LABELS = {
    "background": "Background",
    "rear_environment": "Rear Environment",
    "rear_accessory": "Rear Accessory",
    "arm_pose": "Arm Pose",
    "held_item": "Held Item",
    "body": "Body",
    "pattern": "Pattern",
    "structural": "Structural Detail",
    "legs": "Legs",
    "footwear": "Footwear",
    "face": "Face",
    "eyes": "Eyes",
    "eyebrows": "Eyebrows",
    "mouth": "Mouth",
    "facial": "Facial Detail",
    "body_accessory": "Body Accessory",
    "headwear": "Headwear",
    "ground_accessory": "Ground Accessory",
    "atmosphere": "Weather",
    "special": "Special",
}


def token_name(token: dict[str, Any]) -> str:
    template = config.collection()["naming"]["token"]
    return template.format(token_id=token["token_id"])


def token_description(token: dict[str, Any]) -> str:
    class_id = token["class_id"]
    spec = config.class_spec(class_id)
    template = config.collection()["naming"]["description_template"]
    return template.format(
        token_id=token["token_id"],
        family_name=spec["family_name"],
        class_label=spec["label"],
        represents_lower=spec["represents"].lower(),
    )


def chip0007(token: dict[str, Any]) -> dict[str, Any]:
    col = config.collection()
    spec = config.class_spec(token["class_id"])
    attributes: list[dict[str, Any]] = [
        {"trait_type": "Character Class", "value": spec["label"]},
        {"trait_type": "Family", "value": spec["family_name"]},
        {"trait_type": "Represents", "value": spec["represents"]},
    ]
    for slot, trait_id in token["traits"].items():
        if slot not in SLOT_LABELS:
            continue
        if trait_id == "none" and slot in SKIP_IF_NONE:
            continue
        attributes.append(
            {
                "trait_type": SLOT_LABELS[slot],
                "value": config.trait_name(slot, trait_id),
            }
        )
    collection_attrs = [
        {
            "type": "description",
            "value": (
                "Warm Company is a charitable generative collection of exactly 800 "
                "illustrated winter-shelter companions created for Not By Chance Outreach. "
                "Each NFT symbolically represents one physical winter item the campaign "
                "intends to purchase. Ownership of an NFT does not convey legal title to a "
                "specific physical tent or sleeping bag."
            ),
        },
        {"type": "organization", "value": col["organization"]},
        {"type": "supply", "value": "800"},
        {"type": "blockchain", "value": "Chia"},
    ]
    # URLs are omitted until they exist. Do not invent them.
    return {
        "format": "CHIP-0007",
        "name": token_name(token),
        "description": token_description(token),
        "minting_tool": col["chip0007"]["minting_tool"],
        "sensitive_content": False,
        "series_number": int(token["token_id"]),
        "series_total": 800,
        "attributes": attributes,
        "collection": {
            "name": col["chip0007"]["collection_name"],
            "id": col["chip0007"]["collection_id"],
            "attributes": collection_attrs,
        },
        "data": {
            "dna": token["dna"],
            "class_id": token["class_id"],
            "symbolic_item": True,
            "legal_title_to_physical_item": False,
            "special": bool(token.get("special")),
            "special_id": token.get("special_id"),
        },
    }


def write_metadata(tokens: list[dict[str, Any]]) -> None:
    ensure_build()
    out = BUILD / "metadata"
    out.mkdir(parents=True, exist_ok=True)
    for token in tokens:
        payload = chip0007(token)
        path = out / f"{token['token_id']:04d}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
