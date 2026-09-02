"""Adversarial and pairwise combinatorial QA for the resource planner."""

from __future__ import annotations

from collections import Counter
from typing import Any

from . import config
from .generate import roll_traits
from .resolve import resolve_plan
from .review import review_token
from .rng import SeededStream


def all_non_none(class_id: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for trait in config.traits()["traits"]:
        if trait["id"] == "none" or trait.get("not_a_layer"):
            continue
        classes = trait.get("classes") or []
        if "shared" not in classes and class_id not in classes:
            continue
        rows.append((trait["slot"], trait["id"]))
    return rows


def plan_for(class_id: str, **extra: str) -> dict[str, Any]:
    tok = review_token(class_id, **extra)
    return resolve_plan(class_id, tok["traits"])


def pairwise_report(class_id: str) -> dict[str, Any]:
    pairs = all_non_none(class_id)
    legal = illegal = 0
    samples: list[dict[str, Any]] = []
    for i, (slot_a, id_a) in enumerate(pairs):
        for slot_b, id_b in pairs[i:]:
            extra = {slot_a: id_a}
            extra[slot_b] = id_b
            plan = plan_for(class_id, **extra)
            if plan["ok"]:
                legal += 1
            else:
                illegal += 1
                if len(samples) < 25:
                    samples.append({"a": f"{slot_a}/{id_a}", "b": f"{slot_b}/{id_b}", "violations": plan["violations"]})
    return {
        "class_id": class_id,
        "traits": len(pairs),
        "pairs": legal + illegal,
        "legal": legal,
        "illegal": illegal,
        "illegal_samples": samples,
    }


def stress_class(class_id: str, n: int = 1000, seed: str = "logic-qa") -> dict[str, Any]:
    rng = SeededStream(f"{seed}|{class_id}")
    counts = Counter()
    unresolved = 0
    hand_v = leg_v = foot_v = 0
    for i in range(n):
        traits = roll_traits(class_id, 9, rng.fork(str(i)))
        plan = resolve_plan(class_id, traits)
        counts["tested"] += 1
        if plan["hands"] > 2:
            hand_v += 1
        if plan["legs"] > 2:
            leg_v += 1
        if plan["feet"] > 2:
            foot_v += 1
        if not plan["ok"]:
            unresolved += 1
            counts["fail"] += 1
        else:
            counts["ok"] += 1
    return {
        "class_id": class_id,
        "tested": n,
        "ok": counts["ok"],
        "unresolved": unresolved,
        "hand_violations": hand_v,
        "leg_violations": leg_v,
        "foot_violations": foot_v,
    }


def full_audit(n_per_class: int = 1000) -> dict[str, Any]:
    pairwise = [pairwise_report(cid) for cid in config.CLASS_IDS]
    stress = [stress_class(cid, n=n_per_class) for cid in config.CLASS_IDS]
    unresolved = sum(row["unresolved"] for row in stress)
    hand_v = sum(row["hand_violations"] for row in stress)
    leg_v = sum(row["leg_violations"] for row in stress)
    foot_v = sum(row["foot_violations"] for row in stress)
    return {
        "pairwise": pairwise,
        "stress": stress,
        "combinations_tested": sum(row["tested"] for row in stress),
        "pairwise_pairs": sum(row["pairs"] for row in pairwise),
        "unresolved_physical_resource_violations": unresolved,
        "hand_violations": hand_v,
        "leg_violations": leg_v,
        "foot_violations": foot_v,
        "ok": unresolved == 0 and hand_v == 0 and leg_v == 0 and foot_v == 0,
    }
