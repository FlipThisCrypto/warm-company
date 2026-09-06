"""1:1 mapping from tokens to the winter-goods budget."""

from __future__ import annotations

from typing import Any

from . import config

GOODS_USD = 12_000.0
CONTINGENCY_RATE = 0.10


def campaign_totals() -> dict[str, float]:
    goods = 0.0
    lines: dict[str, float] = {}
    for row in config.collection()["classes"]:
        line = int(row["supply"]) * float(row["physical_unit_cost_usd"])
        lines[row["id"]] = line
        goods += line
    return {
        "goods_usd": goods,
        "contingency_usd": round(goods * CONTINGENCY_RATE, 2),
        "gross_usd": round(goods * (1 + CONTINGENCY_RATE), 2),
        "lines_usd": lines,
    }


def token_goods_usd(result: dict[str, Any]) -> float:
    costs = {row["id"]: float(row["physical_unit_cost_usd"]) for row in config.collection()["classes"]}
    return sum(costs[token["class_id"]] for token in result["tokens"])


def fundraiser_problems(result: dict[str, Any] | None = None) -> list[str]:
    problems: list[str] = []
    totals = campaign_totals()
    if abs(totals["goods_usd"] - GOODS_USD) > 0.001:
        problems.append(f"class cost table {totals['goods_usd']} != {GOODS_USD}")
    if abs(totals["gross_usd"] - 13_200.0) > 0.001:
        problems.append(f"gross campaign {totals['gross_usd']} != 13200")
    if result is not None:
        rolled = token_goods_usd(result)
        if abs(rolled - totals["goods_usd"]) > 0.001:
            problems.append(f"token goods rollup {rolled} != {totals['goods_usd']}")
    return problems
