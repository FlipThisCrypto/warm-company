from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
LAYERS = ROOT / "layers"
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
PROMPTS = ROOT / "prompts"
REFERENCES = ROOT / "references"
TESTS = ROOT / "tests"


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write a complete file or leave the previous version intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding=encoding)
    tmp.replace(path)


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def path_escapes(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return False
    except ValueError:
        return True


def lock_path(name: str) -> Path:
    return BUILD / f".{name}.lock"


class BuildLockHeld(RuntimeError):
    """Another operator command still owns the build directory."""


@contextmanager
def exclusive_build(name: str, *, stale_after_s: int = 6 * 3600) -> Iterator[Path]:
    """One generate/composite at a time. Steal a lock whose pid is dead or stale."""
    ensure_build()
    path = lock_path(name)
    if path.is_file():
        try:
            pid = int((path.read_text(encoding="utf-8").strip() or "0").split()[0])
        except ValueError:
            pid = 0
        age = time.time() - path.stat().st_mtime
        if pid_is_alive(pid) and age < stale_after_s:
            raise BuildLockHeld(f"{name} already running (pid {pid}, lock {path})")
        path.unlink(missing_ok=True)
    path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def build_writable() -> bool:
    ensure_build()
    probe = BUILD / ".write-probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def ensure_build() -> None:
    for sub in (
        "images",
        "metadata",
        "reports",
        "contact-sheets",
        "blueprints",
        "dna",
        "prompts",
        "qa",
    ):
        (BUILD / sub).mkdir(parents=True, exist_ok=True)
