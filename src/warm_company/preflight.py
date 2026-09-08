"""Operator preflight: fail closed before a mint-quality generate."""

from __future__ import annotations

import re
import time
import uuid
from typing import Any

SAFE_ID_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")


def unsafe_id(value: object) -> bool:
    text = str(value or "")
    return not bool(SAFE_ID_RE.fullmatch(text)) or ".." in text or "/" in text or "\\" in text

from . import config
from .compatibility import orphan_rule_problems
from .dignity import dignity_problems
from .generate import ROLL_SLOTS, generate_collection
from .metadata import metadata_problems
from .resolve import definition_problems
from .validate_collection import validate_result
from .validate_layers import validate_library

from .generate import DEV_SEED


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
    if col.get("organization") != "Not By Chance Outreach":
        problems.append("organization must remain Not By Chance Outreach")
    if supply != 800:
        problems.append(f"collection supply {supply} != 800")
    if counted != supply:
        problems.append(f"class supplies {counted} != collection supply {supply}")
    if tuple(class_ids) != config.CLASS_IDS:
        problems.append(f"class ids {class_ids} != {list(config.CLASS_IDS)}")
    seed = (col.get("production_seed") or {}).get("value")
    if not seed:
        problems.append("production_seed.value is empty")
    try:
        uuid.UUID(str(col["chip0007"]["collection_id"]))
    except (KeyError, ValueError, TypeError):
        problems.append("chip0007.collection_id is not a UUID")
    if col.get("logo_status") != "deferred-until-phase-10":
        problems.append("logo_status must remain deferred-until-phase-10")
    logo_slot = next((row for row in config.layer_stack()["stack"] if row.get("slot") == "logo"), None)
    if not logo_slot or not logo_slot.get("deferred"):
        problems.append("logo stack slot must be deferred")
    from .paths import LAYERS

    logo_pngs = list((LAYERS / "shared" / "logo").glob("*.png")) if (LAYERS / "shared" / "logo").exists() else []
    if logo_pngs:
        problems.append(f"logo PNGs present before Phase 10: {logo_pngs[0].name}")
    urls = col.get("urls") or {}
    for key, value in urls.items():
        if key == "note":
            continue
        if value not in (None, [], ""):
            problems.append(f"url {key} is populated before it exists: {value!r}")
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
        if unsafe_id(key[0]) or unsafe_id(key[1]):
            problems.append(f"unsafe trait id {key[0]}/{key[1]}")
    needed = (
        "sole_baseline_y",
        "left_leg_origin",
        "right_leg_origin",
        "left_lower_leg_center",
        "right_lower_leg_center",
        "left_foot_center",
        "right_foot_center",
        "foot_replace_h",
    )
    for class_id in config.CLASS_IDS:
        try:
            anatomy = config.class_anatomy(class_id)
        except KeyError as exc:
            problems.append(str(exc))
            continue
        for key in needed:
            if key not in anatomy:
                problems.append(f"{class_id} anatomy missing {key}")
    for spec in config.rarity()["specials"]["characters"]:
        if unsafe_id(spec.get("id")):
            problems.append(f"unsafe special id {spec.get('id')}")
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


def special_catalog_problems() -> list[str]:
    problems: list[str] = []
    specials = config.rarity()["specials"]["characters"]
    expected = int(config.rarity()["specials"].get("count") or 0)
    if len(specials) != expected:
        problems.append(f"specials listed {len(specials)} != count {expected}")
    if expected != 13:
        problems.append(f"specials count {expected} != 13")
    ids = [row.get("id") for row in specials]
    names = [row.get("name") for row in specials]
    if len(ids) != len(set(ids)):
        problems.append("duplicate special ids")
    if len(names) != len(set(names)):
        problems.append("duplicate special names")
    for row in specials:
        if not row.get("story"):
            problems.append(f"special {row.get('id')} missing story")
        if not isinstance(row.get("traits"), dict) or not row.get("traits"):
            problems.append(f"special {row.get('id')} missing traits")
    return problems


def status_report() -> dict[str, Any]:
    """Cheap operator snapshot. Does not generate the collection."""
    from .fundraiser import campaign_totals, fundraiser_problems
    from .generate import DEV_COLLECTION_FINGERPRINT, DEV_SEED
    from .library import required_paths
    from .paths import BUILD, ROOT, build_writable
    from .provenance import build_manifest, last_generation_drift
    from .validate_layers import duplicate_layer_pairs

    seed = config.production_seed()
    seed_status = (config.collection().get("production_seed") or {}).get("status")
    mint_problems = mint_seed_problems(seed, mint=True)
    required = list(required_paths())
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    integrity = (
        config_integrity_problems()
        + special_catalog_problems()
        + orphan_rule_problems()
        + dignity_problems()
        + definition_problems()
        + fundraiser_problems()
    )
    manifest = build_manifest(seed, 9)
    drift = last_generation_drift(seed, 9)
    from .generate import generation_pair_problems

    pair_problems = generation_pair_problems()
    from .backup import latest_backup_report

    last_backup = latest_backup_report()
    writable = build_writable()
    if not writable:
        integrity = list(integrity) + ["build directory is not writable"]
    return {
        "ok": not missing and not integrity,
        "problems": integrity + [f"missing {path}" for path in missing],
        "seed": seed,
        "seed_status": seed_status,
        "mint_allowed": not mint_problems,
        "mint_problems": mint_problems,
        "supply": config.collection()["supply"],
        "class_counts": {row["id"]: row["supply"] for row in config.collection()["classes"]},
        "dev_seed": DEV_SEED,
        "dev_collection_fingerprint": DEV_COLLECTION_FINGERPRINT,
        "tree_digest": manifest["tree_digest"],
        "layer_count": manifest["layer_count"],
        "required_layers": len(required),
        "missing_layers": missing,
        "git_revision": manifest.get("git_revision"),
        "runtime": manifest.get("runtime"),
        "ci_python": "3.11",
        "python_mismatch": not str((manifest.get("runtime") or {}).get("python") or "").startswith("3.11"),
        "requirements_sha256": (manifest.get("runtime") or {}).get("requirements_sha256"),
        "specials": int(config.rarity()["specials"]["count"]),
        "generator_version": manifest["generator_version"],
        "campaign": campaign_totals(),
        "duplicate_layer_pairs": duplicate_layer_pairs(),
        "build_writable": writable,
        "generation_present": drift["generation_present"],
        "generation_stale": drift["generation_stale"],
        "generation_problems": drift["generation_problems"],
        "stored_tree_digest": drift["stored_tree_digest"],
        "ready_to_composite": bool(
            drift["generation_present"]
            and not drift["generation_stale"]
            and not missing
            and not integrity
            and not pair_problems
        ),
        "generation_pair_problems": pair_problems,
        "last_backup": last_backup,
        "bak_snapshot": (BUILD / "dna" / "tokens.json.bak").is_file(),
    }


def run_preflight(*, seed: str | None = None, phase: int = 9, mint: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
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
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }
    problems.extend(config_integrity_problems())
    problems.extend(special_catalog_problems())
    problems.extend(orphan_rule_problems())
    problems.extend(dignity_problems())
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
        "duration_ms": int((time.perf_counter() - started) * 1000),
    }
