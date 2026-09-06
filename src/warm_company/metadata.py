from __future__ import annotations

import json
from typing import Any

from . import config
from .paths import BUILD, atomic_write_text, ensure_build

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


def _string_values(obj: Any) -> list[str]:
    found: list[str] = []
    if isinstance(obj, str):
        found.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            found.extend(_string_values(value))
    elif isinstance(obj, list):
        for value in obj:
            found.extend(_string_values(value))
    return found


def chip0007_problems(payload: dict[str, Any]) -> list[str]:
    """Legal and schema checks for one CHIP-0007 document."""
    problems: list[str] = []
    if payload.get("format") != "CHIP-0007":
        problems.append("format must be CHIP-0007")
    if payload.get("sensitive_content") is not False:
        problems.append("sensitive_content must be false")
    if payload.get("series_total") != 800:
        problems.append("series_total must be 800")
    data = payload.get("data") or {}
    if data.get("legal_title_to_physical_item") is not False:
        problems.append("legal_title_to_physical_item must be false")
    if data.get("symbolic_item") is not True:
        problems.append("symbolic_item must be true")
    description = str(payload.get("description") or "")
    if "does not convey legal title" not in description.lower():
        problems.append("description must state the NFT does not convey legal title")
    for key in ("uri", "image", "animation_url", "icon", "banner", "website"):
        if payload.get(key):
            problems.append(f"unexpected live URL field {key}")
    for text in _string_values(payload):
        lower = text.lower()
        if "ipfs://" in lower or "https://nftstorage" in lower or "https://arweave" in lower:
            problems.append(f"invented content URL: {text[:80]}")
    return problems


def metadata_problems(tokens: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    for token in tokens:
        payload = chip0007(token)
        for item in chip0007_problems(payload):
            problems.append(f"#{token.get('token_id')} {item}")
            if len(problems) >= 20:
                return problems
    return problems


def write_metadata(tokens: list[dict[str, Any]]) -> None:
    ensure_build()
    out = BUILD / "metadata"
    out.mkdir(parents=True, exist_ok=True)
    for token in tokens:
        payload = chip0007(token)
        path = out / f"{token['token_id']:04d}.json"
        atomic_write_text(path, json.dumps(payload, indent=2))
