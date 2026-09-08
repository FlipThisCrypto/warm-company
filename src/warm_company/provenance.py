"""Bind a generation to the config and layer files that produced it.

DNA is deterministic from seed + config. Pixels are deterministic from DNA +
layer PNGs. A mint that cannot detect later edits to either is not safe.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__, config
from .paths import BUILD, CONFIG, LAYERS, ROOT

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

# Python that can change rolls without touching config JSON.
DNA_SOURCES = (
    "src/warm_company/generate.py",
    "src/warm_company/rng.py",
    "src/warm_company/compatibility.py",
    "src/warm_company/resolve.py",
    "src/warm_company/config.py",
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


def source_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in DNA_SOURCES:
        path = ROOT / rel
        out[rel] = sha256_file(path) if path.is_file() else "missing"
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
    sources = source_hashes()
    layers = layer_hashes()
    core = {
        "seed": seed,
        "phase": int(phase),
        "generator_version": __version__,
        "configs": configs,
        "sources": sources,
        "layers": layers,
        "supply": int(config.collection()["supply"]),
    }
    try:
        import PIL
        pillow = getattr(PIL, "__version__", "unknown")
    except Exception:  # noqa: BLE001
        pillow = "missing"
    return {
        **core,
        "tree_digest": tree_digest(core),
        "layer_count": len(layers),
        "git_revision": git_revision(),
        "runtime": {"pillow": pillow, "python": sys.version.split()[0]},
        "note": "tree_digest covers seed, phase, generator_version, config hashes, source hashes, layer hashes, supply. git_revision and runtime are informational.",
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
    stored_sources = stored.get("sources") or {}
    live_sources = live.get("sources") or {}
    for rel in DNA_SOURCES:
        if stored_sources.get(rel) != live_sources.get(rel):
            problems.append(f"source drift {rel}")
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


def load_stored_manifest() -> dict[str, Any] | None:
    path = BUILD / "dna" / "provenance.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


_UNSET = object()


def last_generation_drift(seed: str, phase: int = 9, stored: Any = _UNSET) -> dict[str, Any]:
    """Compare the last written provenance file to the live tree. Cheap; no generate."""
    if stored is _UNSET:
        stored = load_stored_manifest()
    live = build_manifest(seed, phase)
    if stored is None:
        return {
            "generation_present": False,
            "generation_stale": False,
            "generation_problems": [],
            "stored_tree_digest": None,
            "live_tree_digest": live["tree_digest"],
        }
    problems = compare_manifest(stored, live)
    return {
        "generation_present": True,
        "generation_stale": bool(problems),
        "generation_problems": problems,
        "stored_tree_digest": stored.get("tree_digest"),
        "live_tree_digest": live["tree_digest"],
    }
