from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import CONFIG

CLASS_IDS = ("sleeping-bag", "small-tent", "large-tent")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=None)
def collection() -> dict[str, Any]:
    return load_json(CONFIG / "collection.json")


@lru_cache(maxsize=None)
def anchors() -> dict[str, Any]:
    return load_json(CONFIG / "anchors.json")


@lru_cache(maxsize=None)
def traits() -> dict[str, Any]:
    return load_json(CONFIG / "traits.json")


@lru_cache(maxsize=None)
def rarity() -> dict[str, Any]:
    return load_json(CONFIG / "rarity.json")


@lru_cache(maxsize=None)
def compatibility() -> dict[str, Any]:
    return load_json(CONFIG / "compatibility.json")


@lru_cache(maxsize=None)
def layer_stack() -> dict[str, Any]:
    return load_json(CONFIG / "layer_stack.json")


@lru_cache(maxsize=None)
def prompts() -> dict[str, Any]:
    return load_json(CONFIG / "prompts.json")


@lru_cache(maxsize=None)
def resources() -> dict[str, Any]:
    return load_json(CONFIG / "resources.json")


def class_spec(class_id: str) -> dict[str, Any]:
    spec = anchors()["classes"].get(class_id)
    if spec is None:
        raise KeyError(f"unknown class {class_id}")
    return spec


def slots() -> list[dict[str, Any]]:
    return list(traits()["slots"])


def traits_for(slot: str, class_id: str, phase: int, *, include_zero_weight: bool = False) -> list[dict[str, Any]]:
    rows = []
    for trait in traits()["traits"]:
        if trait["slot"] != slot:
            continue
        if trait.get("phase", 3) > phase:
            continue
        classes = trait.get("classes") or []
        if "shared" not in classes and class_id not in classes:
            continue
        if not include_zero_weight and int(trait.get("weight", 0)) <= 0:
            continue
        rows.append(trait)
    return rows


def trait_by_id(slot: str, trait_id: str) -> dict[str, Any] | None:
    for trait in traits()["traits"]:
        if trait["slot"] == slot and trait["id"] == trait_id:
            return trait
    return None


def trait_name(slot: str, trait_id: str) -> str:
    row = trait_by_id(slot, trait_id)
    if row:
        return str(row["name"])
    specials = {item["id"]: item["name"] for item in rarity()["specials"]["characters"]}
    if slot == "special" and trait_id in specials:
        return specials[trait_id]
    if trait_id == "none":
        return "None"
    return trait_id


def slot_folder(slot: str, class_id: str) -> str:
    for layer in layer_stack()["stack"]:
        if layer["slot"] == slot:
            return str(layer["folder"]).replace("{class}", class_id)
    fallback = {
        "body": f"layers/{class_id}/body",
        "pattern": f"layers/{class_id}/patterns",
        "background": "layers/shared/backgrounds",
    }
    return fallback.get(slot, f"layers/{class_id}/{slot}")


def production_seed() -> str:
    return str(collection()["production_seed"]["value"])
