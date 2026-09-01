"""Deterministic RNG. SHA-256 counter stream, language-independent."""

from __future__ import annotations

import hashlib
from typing import Sequence, TypeVar

T = TypeVar("T")


class SeededStream:
    """Yield 256-bit integers from sha256(f'{seed}:{counter}').

    Python's `random.Random` is not used. A seed string plus this counter
    must reproduce the same collection on any machine with the same configs.
    """

    def __init__(self, seed: str) -> None:
        if not seed:
            raise ValueError("seed must be a non-empty string")
        self.seed = seed
        self.counter = 0

    def next_int(self) -> int:
        payload = f"{self.seed}:{self.counter}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        self.counter += 1
        return int.from_bytes(digest, "big")

    def randint(self, n: int) -> int:
        """Uniform integer in [0, n). Rejection sampling avoids modulo bias."""
        if n <= 0:
            raise ValueError("n must be positive")
        limit = (1 << 256) // n * n
        while True:
            value = self.next_int()
            if value < limit:
                return value % n

    def choice(self, items: Sequence[T]) -> T:
        if not items:
            raise ValueError("choice() on empty sequence")
        return items[self.randint(len(items))]

    def weighted(self, items: Sequence[T], weights: Sequence[int]) -> T:
        if len(items) != len(weights):
            raise ValueError("items and weights length mismatch")
        total = sum(weights)
        if total <= 0:
            raise ValueError("weights must sum to a positive integer")
        pick = self.randint(total)
        running = 0
        for item, weight in zip(items, weights):
            running += weight
            if pick < running:
                return item
        return items[-1]

    def fork(self, label: str) -> "SeededStream":
        """Independent child stream. Does not advance this stream."""
        child_seed = hashlib.sha256(f"{self.seed}|{label}".encode("utf-8")).hexdigest()
        return SeededStream(child_seed)


def dna_hash(class_id: str, traits: dict[str, str]) -> str:
    parts = [class_id] + [f"{slot}={traits[slot]}" for slot in sorted(traits)]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
