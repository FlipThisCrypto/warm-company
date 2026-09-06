"""Operator preflight: fail closed before a mint-quality generate."""

from __future__ import annotations

from typing import Any

from . import config
from .generate import ROLL_SLOTS, generate_collection
from .metadata import metadata_problems
from .resolve import definition_problems
from .validate_collection import validate_result
from .validate_layers import validate_library

DEV_SEED = "warm-company-dev-seed-v0"


def mint_seed_problems(seed: str, *, mint: bool) -> list[str]:
    """Refuse a production mint that still uses the development placeholder seed."""
    if not mint:
        return []
    problems: list[str] = []
    if not seed or len(seed) < 16:
        problems.append("mint seed is missing or shorter than 16 characters")
    if seed == DEV_SEED:
        problems.append("refusing well-known development seed for mint")
    status = (config.collection().get("production_seed") or {}).get("status")
    if status == "placeholder-not-for-mint":
        problems.append("production_seed.status is still placeholder-not-for-mint")
    return problems


def config_integrity_problems() -> list[str]:
    problems: list[str] = []
    col = config.collection()
    supply = int(col.get("supply") or 0)
    classes = col.get("classes") or []
    class_ids = [row.get("id") for row in classes]
    counted = sum(int(row.get("supply") or 0) for row in classes)
    if supply != 800:
        problems.append(f"collection supply {supply} != 800")
    if counted != supply:
        problems.append(f"class supplies {counted} != collection supply {supply}")
    if tuple(class_ids) != config.CLASS_IDS:
        problems.append(f"class ids {class_ids} != {list(config.CLASS_IDS)}")
    seed = (col.get("production_seed") or {}).get("value")
    if not seed:
        problems.append("production_seed.value is empty")
    slot_ids = {row["id"] for row in config.slots()}
    for slot in ROLL_SLOTS:
        if slot not in slot_ids:
            problems.append(f"roll slot {slot} missing from traits.json slots")
    seen: set[tuple[str, str]] = set()
    for trait in config.traits()["traits"]:
        key = (trait.get("slot"), trait.get("id"))
        if None in key:
            problems.append("trait missing slot or id")
            continue
        if key in seen:
            problems.append(f"duplicate trait {key[0]}/{key[1]}")
        seen.add(key)
    for class_id in config.CLASS_IDS:
        try:
            config.class_anatomy(class_id)
        except KeyError as exc:
            problems.append(str(exc))
    for spec in config.rarity()["specials"]["characters"]:
        if spec.get("class") not in config.CLASS_IDS:
            problems.append(f"special {spec.get('id')} unknown class {spec.get('class')}")
        for slot, value in (spec.get("traits") or {}).items():
            if slot == "special":
                if value != spec.get("id"):
                    problems.append(f"special {spec.get('id')} trait special={value}")
                continue
            if slot not in slot_ids:
                problems.append(f"special {spec.get('id')} unknown slot {slot}")
            elif value != "none" and config.trait_by_id(slot, value) is None:
                problems.append(f"special {spec.get('id')} unknown {slot}/{value}")
    return problems


def run_preflight(*, seed: str | None = None, phase: int = 9, mint: bool = False) -> dict[str, Any]:
    problems: list[str] = []
    seed = seed or config.production_seed()
    mint_problems = mint_seed_problems(seed, mint=mint)
    problems.extend(mint_problems)
    if mint_problems:
        return {
            "ok": False,
            "problems": problems,
            "supply": None,
            "unique_dna": None,
            "special_count": None,
            "tree_digest": None,
            "png_count": None,
            "layer_ok": None,
            "provenance_ok": None,
            "seed": seed,
            "phase": phase,
            "mint": mint,
        }
    problems.extend(config_integrity_problems())
    problems.extend(definition_problems())
    layers = validate_library()
    if not layers.get("ok"):
        problems.append(f"layer library errors {layers.get('error_count')}")
    result = generate_collection(seed=seed, phase=phase)
    report = validate_result(result)
    if not report.get("ok"):
        problems.extend(report.get("problems") or [])
    problems.extend(metadata_problems(result["tokens"]))
    return {
        "ok": not problems,
        "problems": problems,
        "supply": result["supply"],
        "unique_dna": result["unique_dna"],
        "special_count": result["special_count"],
        "tree_digest": (result.get("provenance") or {}).get("tree_digest"),
        "png_count": layers.get("png_count"),
        "layer_ok": layers.get("ok"),
        "provenance_ok": report.get("provenance_ok"),
        "seed": result["seed"],
        "phase": result["phase"],
        "mint": mint,
    }
