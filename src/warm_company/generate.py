from __future__ import annotations

import hashlib
import json
from typing import Any

from . import compatibility, config
from .resolve import resolve_plan
from pathlib import Path

from .paths import BUILD, atomic_write_text, ensure_build
from .rng import SeededStream, dna_hash

MAX_TOKEN_ATTEMPTS = 80
DEV_SEED = "warm-company-dev-seed-v0"
DEV_COLLECTION_FINGERPRINT = "81da0c01e76da56d89c41d16f1d4cacf3c513d20d8a208faa0e9e798ff02189b"
ROLL_SLOTS = [
    "body",
    "pattern",
    "structural",
    "arm_pose",
    "held_item",
    "legs",
    "footwear",
    "face",
    "eyes",
    "eyebrows",
    "mouth",
    "facial",
    "headwear",
    "rear_accessory",
    "body_accessory",
    "ground_accessory",
    "rear_environment",
    "atmosphere",
    "background",
    "special",
]


def _choose(slot: str, class_id: str, phase: int, rng: SeededStream) -> str:
    rows = config.traits_for(slot, class_id, phase)
    if not rows:
        raise RuntimeError(f"no traits available for {class_id}/{slot} at phase {phase}")
    return rng.weighted([row["id"] for row in rows], [int(row["weight"]) for row in rows])


def roll_traits(class_id: str, phase: int, rng: SeededStream) -> dict[str, str]:
    last_error = "unknown"
    traits = {slot: "none" for slot in ROLL_SLOTS}
    for slot in ROLL_SLOTS:
        pick = _choose(slot, class_id, phase, rng)
        trial = dict(traits)
        trial[slot] = pick
        trial = compatibility.apply_forces(trial)
        plan = resolve_plan(class_id, trial)
        if plan["ok"] or slot not in " ".join(plan["violations"]):
            traits = trial
        else:
            for _ in range(8):
                trial[slot] = _choose(slot, class_id, phase, rng)
                trial = compatibility.apply_forces(trial)
                plan = resolve_plan(class_id, trial)
                if plan["ok"] or slot not in " ".join(plan["violations"]):
                    traits = trial
                    break
            else:
                traits = compatibility.apply_forces(traits)
    plan = resolve_plan(class_id, traits)
    if plan["ok"]:
        return traits
    for _ in range(MAX_TOKEN_ATTEMPTS):
        traits = {slot: _choose(slot, class_id, phase, rng) for slot in ROLL_SLOTS}
        traits = compatibility.apply_forces(traits)
        plan = resolve_plan(class_id, traits)
        if plan["ok"]:
            return traits
        last_error = "; ".join(plan["violations"])
    raise RuntimeError(f"could not roll a legal {class_id} token: {last_error}")


def _sanitize(class_id: str, traits: dict[str, str]) -> dict[str, str]:
    """Repair leftover forced traits after an authored overlay."""
    cleaned = dict(traits)
    if cleaned.get("rear_accessory") != "backpack" and cleaned.get("body_accessory") == "backpack-straps":
        cleaned["body_accessory"] = "none"
    if cleaned.get("held_item", "none") == "none" and cleaned.get("arm_pose") in {"hold-item", "hold-two-hand"}:
        cleaned["arm_pose"] = "rest"
    if cleaned.get("held_item", "none") != "none" and cleaned.get("arm_pose") in {"rest", "wave", "akimbo"}:
        held = config.trait_by_id("held_item", cleaned["held_item"])
        cleaned["arm_pose"] = "hold-two-hand" if held and held.get("two_handed") else "hold-item"
    cleaned = compatibility.apply_forces(cleaned)
    return cleaned


def _special_complete(class_id: str, spec: dict[str, Any], phase: int, rng: SeededStream) -> dict[str, str]:
    """Fill unspecified slots of a coordinated special, then force the authored ones."""
    traits = roll_traits(class_id, phase, rng)
    traits.update(spec["traits"])
    traits["special"] = spec["id"]
    traits = _sanitize(class_id, traits)
    traits.update(spec["traits"])
    traits["special"] = spec["id"]
    traits = _sanitize(class_id, traits)
    plan = resolve_plan(class_id, traits)
    if plan["violations"]:
        raise RuntimeError(f"special {spec['id']} is illegal on {class_id}: {plan['violations']}")
    return traits


def generate_collection(
    seed: str | None = None,
    phase: int = 9,
    inject_specials: bool = True,
) -> dict[str, Any]:
    seed = seed or config.production_seed()
    col = config.collection()
    rng = SeededStream(seed)
    seen: set[str] = set()
    tokens: list[dict[str, Any]] = []
    failures = 0

    for class_info in col["classes"]:
        class_id = class_info["id"]
        quota = int(class_info["supply"])
        class_rng = rng.fork(f"class:{class_id}")
        produced = 0
        attempts = 0
        while produced < quota:
            attempts += 1
            if attempts > quota * MAX_TOKEN_ATTEMPTS:
                raise RuntimeError(f"exhausted retries filling class {class_id}")
            traits = roll_traits(class_id, phase, class_rng)
            digest = dna_hash(class_id, traits)
            if digest in seen:
                failures += 1
                continue
            seen.add(digest)
            produced += 1
            tokens.append(
                {
                    "pre_id": len(tokens) + 1,
                    "class_id": class_id,
                    "traits": traits,
                    "dna": digest,
                    "special": False,
                }
            )

    if inject_specials:
        specials = config.rarity()["specials"]["characters"]
        # Replace the last ordinary token of the required class so supply stays exact.
        by_class: dict[str, list[int]] = {cid: [] for cid in config.CLASS_IDS}
        for index, token in enumerate(tokens):
            if not token["special"]:
                by_class[token["class_id"]].append(index)
        special_rng = rng.fork("specials")
        for spec in specials:
            class_id = spec["class"]
            if spec.get("phase", 9) > phase:
                continue
            candidates = by_class[class_id]
            if not candidates:
                raise RuntimeError(f"no token available to replace for special {spec['id']}")
            target = candidates.pop()
            traits = _special_complete(class_id, spec, phase, special_rng)
            digest = dna_hash(class_id, traits)
            if digest in seen and tokens[target]["dna"] != digest:
                # Extremely unlikely; perturb by rerolling fill slots once more.
                traits = _special_complete(class_id, spec, phase, special_rng)
                digest = dna_hash(class_id, traits)
            seen.discard(tokens[target]["dna"])
            if digest in seen:
                raise RuntimeError(f"special {spec['id']} collided with an existing DNA")
            seen.add(digest)
            tokens[target] = {
                "pre_id": tokens[target]["pre_id"],
                "class_id": class_id,
                "traits": traits,
                "dna": digest,
                "special": True,
                "special_id": spec["id"],
                "special_name": spec["name"],
            }

    shuffle_rng = SeededStream(f"{seed}|{col['shuffle_seed_suffix']}")
    order = list(range(len(tokens)))
    # Fisher-Yates with our stream so mint order is mixed but reproducible.
    for i in range(len(order) - 1, 0, -1):
        j = shuffle_rng.randint(i + 1)
        order[i], order[j] = order[j], order[i]

    minted: list[dict[str, Any]] = []
    for token_id, source_index in enumerate(order, start=1):
        token = dict(tokens[source_index])
        token["token_id"] = token_id
        minted.append(token)

    minted.sort(key=lambda item: item["token_id"])
    counts = {cid: 0 for cid in config.CLASS_IDS}
    special_count = 0
    for token in minted:
        counts[token["class_id"]] += 1
        if token.get("special"):
            special_count += 1

    from .provenance import build_manifest

    result = {
        "seed": seed,
        "phase": phase,
        "supply": len(minted),
        "class_counts": counts,
        "unique_dna": len(seen),
        "duplicate_retries": failures,
        "special_count": special_count,
        "tokens": minted,
        "provenance": build_manifest(seed, phase),
    }
    result["collection_fingerprint"] = collection_fingerprint(result)
    _assert_invariants(result)
    return result


def _assert_invariants(result: dict[str, Any]) -> None:
    expected = {row["id"]: row["supply"] for row in config.collection()["classes"]}
    if result["class_counts"] != expected:
        raise AssertionError(f"class counts {result['class_counts']} != {expected}")
    if result["supply"] != config.collection()["supply"]:
        raise AssertionError("supply mismatch")
    if result["unique_dna"] != result["supply"]:
        raise AssertionError("duplicate DNA slipped through")
    ids = [token["token_id"] for token in result["tokens"]]
    if ids != list(range(1, result["supply"] + 1)):
        raise AssertionError("token ids are not 1..supply")


def collection_fingerprint(result: dict[str, Any]) -> str:
    """SHA-256 of token_id:class_id:dna lines in mint order."""
    lines = [f"{token['token_id']}:{token['class_id']}:{token['dna']}" for token in result["tokens"]]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def write_generation(result: dict[str, Any]) -> None:
    ensure_build()
    tokens_path = BUILD / "dna" / "tokens.json"
    slim = [{k: v for k, v in token.items()} for token in result["tokens"]]
    payload = {k: v for k, v in result.items() if k != "tokens"}
    payload["tokens"] = slim
    atomic_write_text(tokens_path, json.dumps(payload, indent=2))
    jsonl = BUILD / "dna" / "collection.jsonl"
    jsonl_body = "".join(json.dumps(token, sort_keys=True) + "\n" for token in result["tokens"])
    atomic_write_text(jsonl, jsonl_body)
    summary = {
        "seed": result["seed"],
        "phase": result["phase"],
        "supply": result["supply"],
        "class_counts": result["class_counts"],
        "unique_dna": result["unique_dna"],
        "duplicate_retries": result["duplicate_retries"],
        "special_count": result["special_count"],
        "specials": [
            {
                "token_id": token["token_id"],
                "id": token.get("special_id"),
                "name": token.get("special_name"),
                "class_id": token["class_id"],
            }
            for token in result["tokens"]
            if token.get("special")
        ],
    }
    provenance = result.get("provenance") or {}
    summary["tree_digest"] = provenance.get("tree_digest")
    summary["collection_fingerprint"] = collection_fingerprint(result)
    atomic_write_text(BUILD / "reports" / "generation_summary.json", json.dumps(summary, indent=2))
    atomic_write_text(BUILD / "dna" / "provenance.json", json.dumps(provenance, indent=2))


def generation_pair_problems(
    tokens_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> list[str]:
    """tokens.json and collection.jsonl must describe the same 800 DNA rows."""
    tokens_path = tokens_path or (BUILD / "dna" / "tokens.json")
    jsonl_path = jsonl_path or (BUILD / "dna" / "collection.jsonl")
    if not tokens_path.is_file() and not jsonl_path.is_file():
        return []
    if tokens_path.is_file() != jsonl_path.is_file():
        missing = "collection.jsonl" if tokens_path.is_file() else "tokens.json"
        return [f"generation pair incomplete: missing {missing}"]
    try:
        payload = json.loads(tokens_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"tokens.json unreadable: {exc}"]
    tokens = payload.get("tokens") if isinstance(payload, dict) else None
    if not isinstance(tokens, list):
        return ["tokens.json has no tokens list"]
    json_rows = [(int(t["token_id"]), t.get("class_id"), t.get("dna")) for t in tokens]
    jsonl_rows: list[tuple[int, Any, Any]] = []
    try:
        text = jsonl_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"collection.jsonl unreadable: {exc}"]
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            return [f"collection.jsonl line {i} invalid JSON: {exc}"]
        if not isinstance(row, dict):
            return [f"collection.jsonl line {i} is not an object"]
        try:
            jsonl_rows.append((int(row["token_id"]), row.get("class_id"), row.get("dna")))
        except (KeyError, TypeError, ValueError):
            return [f"collection.jsonl line {i} missing token_id"]
    if len(json_rows) != len(jsonl_rows):
        return [f"generation pair length {len(json_rows)} json vs {len(jsonl_rows)} jsonl"]
    if json_rows != jsonl_rows:
        return ["generation pair token_id/class_id/dna mismatch"]
    return []
