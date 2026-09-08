"""Portable DNA backup: tokens, jsonl, provenance, summary. No images."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from .generate import collection_fingerprint, generation_pair_problems, read_generation_json
from .paths import BUILD, ensure_build

BACKUP_MEMBERS = (
    "dna/tokens.json",
    "dna/collection.jsonl",
    "dna/provenance.json",
    "reports/generation_summary.json",
)


def backup_dir() -> Path:
    ensure_build()
    path = BUILD / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_backup(dest: Path | None = None) -> Path:
    missing = [rel for rel in BACKUP_MEMBERS if not (BUILD / rel).is_file()]
    if missing:
        raise ValueError(f"cannot backup; missing {missing[0]}")
    pair = generation_pair_problems()
    if pair:
        raise ValueError(pair[0])
    payload = read_generation_json(BUILD / "dna" / "tokens.json")
    digest = collection_fingerprint(payload)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = dest or (backup_dir() / f"dna-{stamp}.zip")
    dest.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_utc": stamp,
        "collection_fingerprint": digest,
        "tree_digest": (payload.get("provenance") or {}).get("tree_digest"),
        "supply": payload.get("supply") or len(payload.get("tokens") or []),
        "members": list(BACKUP_MEMBERS),
    }
    tmp = dest.with_name(dest.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in BACKUP_MEMBERS:
            zf.write(BUILD / rel, rel)
        zf.writestr("backup_manifest.json", json.dumps(manifest, indent=2))
    tmp.replace(dest)
    return dest


def verify_backup(path: Path) -> list[str]:
    problems: list[str] = []
    if not path.is_file():
        return [f"backup missing: {path}"]
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            for rel in (*BACKUP_MEMBERS, "backup_manifest.json"):
                if rel not in names:
                    problems.append(f"backup missing member {rel}")
            if problems:
                return problems
            tokens = json.loads(zf.read("dna/tokens.json"))
            jsonl = zf.read("dna/collection.jsonl").decode("utf-8")
            manifest = json.loads(zf.read("backup_manifest.json"))
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"backup unreadable: {exc}"]
    if not isinstance(tokens, dict) or not isinstance(tokens.get("tokens"), list):
        problems.append("backup tokens.json is not a generation object")
        return problems
    rows = [(int(t["token_id"]), t.get("class_id"), t.get("dna")) for t in tokens["tokens"]]
    jsonl_rows = []
    for i, line in enumerate(jsonl.splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        jsonl_rows.append((int(row["token_id"]), row.get("class_id"), row.get("dna")))
    if rows != jsonl_rows:
        problems.append("backup tokens.json does not match collection.jsonl")
    digest = collection_fingerprint(tokens)
    if manifest.get("collection_fingerprint") and manifest["collection_fingerprint"] != digest:
        problems.append("backup_manifest fingerprint does not match tokens.json")
    return problems


def restore_backup(path: Path) -> list[str]:
    """Replace build/dna from a verified zip. Leaves previous files if verify fails."""
    from .paths import atomic_write_text

    problems = verify_backup(path)
    if problems:
        return problems
    with zipfile.ZipFile(path) as zf:
        for rel in BACKUP_MEMBERS:
            payload = zf.read(rel).decode("utf-8")
            atomic_write_text(BUILD / rel, payload)
    return generation_pair_problems()
