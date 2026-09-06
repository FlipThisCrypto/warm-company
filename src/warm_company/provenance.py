"""Bind a generation to the config and layer files that produced it.

DNA is deterministic from seed + config. Pixels are deterministic from DNA +
layer PNGs. A mint that cannot detect later edits to either is not safe.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import __version__, config
from .paths import CONFIG, LAYERS, ROOT

# Config files that change DNA or compositing. Review-only JSON is excluded.
DNA_CONFIGS = (
    "collection.json",
    "traits.json",
    "rarity.json",
    "compatibility.json",
    "resources.json",
    "anchors.json",
    "layer_stack.json",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def config_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in DNA_CONFIGS:
        path = CONFIG / name
        if not path.is_file():
            out[name] = "missing"
            continue
        out[name] = sha256_file(path)
    return out


def layer_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    if not LAYERS.is_dir():
        return out
    for path in sorted(LAYERS.rglob("*.png")):
        rel = path.relative_to(ROOT).as_posix()
        out[rel] = sha256_file(path)
    return out


def tree_digest(parts: dict[str, Any]) -> str:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def git_revision() -> str | None:
    head = ROOT / ".git" / "HEAD"
    if not head.is_file():
        return None
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref:"):
        ref = ROOT / ".git" / text.split(" ", 1)[1].strip()
        if ref.is_file():
            return ref.read_text(encoding="utf-8").strip() or None
        return None
    return text or None


def build_manifest(seed: str, phase: int) -> dict[str, Any]:
    configs = config_hashes()
    layers = layer_hashes()
    core = {
        "seed": seed,
        "phase": int(phase),
        "generator_version": __version__,
        "configs": configs,
        "layers": layers,
        "supply": int(config.collection()["supply"]),
    }
    return {
        **core,
        "tree_digest": tree_digest(core),
        "layer_count": len(layers),
        "git_revision": git_revision(),
        "note": "tree_digest covers seed, phase, generator_version, config hashes, layer hashes, supply. git_revision is informational.",
    }


def compare_manifest(stored: dict[str, Any] | None, live: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not stored:
        problems.append("generation has no provenance manifest")
        return problems
    for key in ("seed", "phase", "generator_version", "supply", "tree_digest"):
        if stored.get(key) != live.get(key):
            problems.append(f"provenance {key} {stored.get(key)!r} != live {live.get(key)!r}")
    stored_configs = stored.get("configs") or {}
    live_configs = live.get("configs") or {}
    for name in DNA_CONFIGS:
        if stored_configs.get(name) != live_configs.get(name):
            problems.append(f"config drift {name}")
    stored_layers = stored.get("layers") or {}
    live_layers = live.get("layers") or {}
    if stored_layers != live_layers:
        missing = sorted(set(stored_layers) - set(live_layers))
        extra = sorted(set(live_layers) - set(stored_layers))
        changed = sorted(
            path
            for path in set(stored_layers) & set(live_layers)
            if stored_layers[path] != live_layers[path]
        )
        if missing:
            problems.append(f"layer missing {len(missing)}: {missing[0]}")
        if extra:
            problems.append(f"layer extra {len(extra)}: {extra[0]}")
        if changed:
            problems.append(f"layer changed {len(changed)}: {changed[0]}")
    return problems
