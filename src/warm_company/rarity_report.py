from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

from . import config
from .paths import BUILD, ensure_build


def score_token(token: dict, class_counts: dict[str, Counter]) -> float:
    total = 0.0
    class_id = token["class_id"]
    supply = config.class_spec(class_id)["supply"]
    for slot, value in token["traits"].items():
        count = class_counts[class_id][slot][value]
        p = max(count / supply, 1 / supply)
        total += -math.log2(p)
    return total


def build_report(result: dict) -> dict:
    ensure_build()
    class_counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    band_counts: Counter = Counter()
    for token in result["tokens"]:
        for slot, value in token["traits"].items():
            class_counts[token["class_id"]][slot][value] += 1
            row = config.trait_by_id(slot, value)
            if row:
                band_counts[row.get("band", "common")] += 1

    token_rows = []
    for token in result["tokens"]:
        token_rows.append(
            {
                "token_id": token["token_id"],
                "class_id": token["class_id"],
                "special": bool(token.get("special")),
                "special_name": token.get("special_name"),
                "score": round(score_token(token, class_counts), 4),
                "dna": token["dna"],
            }
        )
    token_rows.sort(key=lambda row: row["score"], reverse=True)

    slot_tables = {}
    for class_id, slots in class_counts.items():
        supply = config.class_spec(class_id)["supply"]
        slot_tables[class_id] = {}
        for slot, counter in slots.items():
            slot_tables[class_id][slot] = [
                {
                    "id": trait_id,
                    "name": config.trait_name(slot, trait_id),
                    "count": count,
                    "pct": round(100.0 * count / supply, 2),
                }
                for trait_id, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
            ]

    report = {
        "seed": result["seed"],
        "phase": result["phase"],
        "supply": result["supply"],
        "class_counts": result["class_counts"],
        "unique_dna": result["unique_dna"],
        "duplicate_check": "pass" if result["unique_dna"] == result["supply"] else "FAIL",
        "special_count": result["special_count"],
        "trait_band_observations": dict(band_counts),
        "slot_tables": slot_tables,
        "rarest_tokens": token_rows[:25],
        "most_common_tokens": list(reversed(token_rows[-25:])),
        "model": config.rarity()["model"],
        "scoring": config.rarity()["scoring"],
    }
    (BUILD / "reports" / "rarity_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    _write_markdown(report)
    return report


def _write_markdown(report: dict) -> None:
    lines = [
        f"# Rarity report",
        "",
        f"- Seed: `{report['seed']}`",
        f"- Phase: {report['phase']}",
        f"- Supply: {report['supply']}",
        f"- Class counts: `{report['class_counts']}`",
        f"- Unique DNA: {report['unique_dna']} ({report['duplicate_check']})",
        f"- Specials: {report['special_count']}",
        "",
        "## Rarest tokens by information score",
        "",
        "| Token | Class | Special | Score |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["rarest_tokens"][:15]:
        lines.append(
            f"| {row['token_id']:04d} | {row['class_id']} | {row.get('special_name') or ''} | {row['score']} |"
        )
    lines += ["", "_This score is an audit tool. It is not a rigid NFT rarity tier._", ""]
    (BUILD / "reports" / "rarity_report.md").write_text("\n".join(lines), encoding="utf-8")
