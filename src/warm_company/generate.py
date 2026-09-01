from __future__ import annotations

import json
from typing import Any

from . import compatibility, config
from .paths import BUILD, ensure_build
from .rng import SeededStream, dna_hash

MAX_TOKEN_ATTEMPTS = 80
ROLL_SLOTS = [
    "background",
    "rear_environment",
    "rear_accessory",
    "arm_pose",
    "held_item",
    "body",
    "pattern",
    "structural",
    "legs",
    "footwear",
    "face",
    "eyes",
    "eyebrows",
    "mouth",
    "facial",
    "body_accessory",
    "headwear",
    "ground_accessory",
    "atmosphere",
    "special",
]


def _choose(slot: str, class_id: str, phase: int, rng: SeededStream) -> str:
    rows = config.traits_for(slot, class_id, phase)
    if not rows:
        raise RuntimeError(f"no traits available for {class_id}/{slot} at phase {phase}")
    return rng.weighted([row["id"] for row in rows], [int(row["weight"]) for row in rows])


def roll_traits(class_id: str, phase: int, rng: SeededStream) -> dict[str, str]:
    last_error = "unknown"
    for _ in range(MAX_TOKEN_ATTEMPTS):
        traits = {slot: _choose(slot, class_id, phase, rng) for slot in ROLL_SLOTS}
        traits = compatibility.apply_forces(traits)
        problems = compatibility.violations(class_id, traits)
        if not problems:
            return traits
        last_error = "; ".join(problems)
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
    problems = compatibility.violations(class_id, traits)
    if problems:
        raise RuntimeError(f"special {spec['id']} is illegal on {class_id}: {problems}")
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

    result = {
        "seed": seed,
        "phase": phase,
        "supply": len(minted),
        "class_counts": counts,
        "unique_dna": len(seen),
        "duplicate_retries": failures,
        "special_count": special_count,
        "tokens": minted,
    }
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


def write_generation(result: dict[str, Any]) -> None:
    ensure_build()
    tokens_path = BUILD / "dna" / "tokens.json"
    slim = [{k: v for k, v in token.items()} for token in result["tokens"]]
    payload = {k: v for k, v in result.items() if k != "tokens"}
    payload["tokens"] = slim
    tokens_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    jsonl = BUILD / "dna" / "collection.jsonl"
    with jsonl.open("w", encoding="utf-8") as handle:
        for token in result["tokens"]:
            handle.write(json.dumps(token, sort_keys=True) + "\n")
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
    (BUILD / "reports" / "generation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
