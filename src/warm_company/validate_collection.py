from __future__ import annotations

import json
from collections import Counter, defaultdict

from . import config
from .paths import BUILD, ensure_build


def validate_result(result: dict) -> dict:
    ensure_build()
    problems: list[str] = []
    tokens = result["tokens"]
    if len(tokens) != 800:
        problems.append(f"supply {len(tokens)} != 800")
    counts = Counter(token["class_id"] for token in tokens)
    expected = {row["id"]: row["supply"] for row in config.collection()["classes"]}
    for class_id, supply in expected.items():
        if counts[class_id] != supply:
            problems.append(f"{class_id} count {counts[class_id]} != {supply}")
    dnas = [token["dna"] for token in tokens]
    if len(dnas) != len(set(dnas)):
        problems.append("duplicate DNA present")
    ids = [token["token_id"] for token in tokens]
    if sorted(ids) != list(range(1, len(tokens) + 1)):
        problems.append("token ids are not a permutation of 1..N")
    specials = [token for token in tokens if token.get("special")]
    expected_specials = [
        row["id"]
        for row in config.rarity()["specials"]["characters"]
        if row.get("phase", 9) <= result.get("phase", 9)
    ]
    got = [token.get("special_id") for token in specials]
    if sorted(got) != sorted(expected_specials):
        problems.append(f"specials {got} != {expected_specials}")
    # Combination counts
    combos = Counter(
        tuple(sorted(token["traits"].items())) for token in tokens
    )
    if any(count > 1 for count in combos.values()):
        problems.append("duplicate trait combinations")
    report = {
        "ok": not problems,
        "problems": problems,
        "class_counts": dict(counts),
        "unique_dna": len(set(dnas)),
        "special_count": len(specials),
        "seed": result.get("seed"),
        "phase": result.get("phase"),
    }
    (BUILD / "reports" / "collection_validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def trait_histogram(result: dict) -> dict:
    per_class: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for token in result["tokens"]:
        for slot, value in token["traits"].items():
            per_class[token["class_id"]][slot][value] += 1
    serializable = {
        class_id: {slot: dict(counter) for slot, counter in slots.items()}
        for class_id, slots in per_class.items()
    }
    (BUILD / "reports" / "trait_histogram.json").write_text(
        json.dumps(serializable, indent=2), encoding="utf-8"
    )
    return serializable
