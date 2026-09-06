"""Dignity scan of rollable names. Policy notes may mention banned words; labels may not."""

from __future__ import annotations

from . import config

# Substrings matched against trait/special id and display name only.
FORBIDDEN = (
    "homeless",
    "beggar",
    "begging",
    "cardboard-sign",
    "cardboard_sign",
    "poverty",
    "junkie",
    "derelict",
    "hobo",
    "starter-kit",
    "starter_kit",
    "trash-pile",
    "trash_pile",
)


def label_problems(kind: str, identity: str, name: str) -> list[str]:
    blob = f"{identity} {name}".lower()
    problems: list[str] = []
    for term in FORBIDDEN:
        if term in blob:
            problems.append(f"dignity {kind} {identity}: contains {term}")
    return problems


def dignity_problems() -> list[str]:
    problems: list[str] = []
    for trait in config.traits()["traits"]:
        problems.extend(label_problems("trait", f"{trait.get('slot')}/{trait.get('id')}", str(trait.get("name") or "")))
    for spec in config.rarity()["specials"]["characters"]:
        problems.extend(label_problems("special", str(spec.get("id") or ""), str(spec.get("name") or "")))
    return problems
