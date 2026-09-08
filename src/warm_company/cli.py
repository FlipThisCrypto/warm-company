from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, config
from .paths import BUILD, ensure_build


def _load_tokens(path: Path | None = None) -> dict:
    from .generate import read_generation_json

    path = path or (BUILD / "dna" / "tokens.json")
    if not path.exists():
        raise SystemExit(f"no generation found at {path}; run generate first")
    try:
        return read_generation_json(path)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def cmd_generate(args: argparse.Namespace) -> int:
    from .fundraiser import token_goods_usd
    from .generate import generate_collection, write_generation
    from .preflight import mint_seed_problems
    from .validate_collection import validate_result
    from .rarity_report import build_report

    seed = args.seed or config.production_seed()
    mint_problems = mint_seed_problems(seed, mint=bool(args.mint))
    if mint_problems:
        print(json.dumps({"ok": False, "problems": mint_problems, "mint": True}, indent=2))
        return 1
    from .paths import BuildLockHeld, exclusive_build

    try:
        if args.dry_run:
            result = generate_collection(seed=args.seed, phase=args.phase, inject_specials=not args.no_specials)
        else:
            with exclusive_build("generate"):
                result = generate_collection(seed=args.seed, phase=args.phase, inject_specials=not args.no_specials)
                write_generation(result)
    except BuildLockHeld as exc:
        print(json.dumps({"ok": False, "problems": [str(exc)]}, indent=2))
        return 1
    report = validate_result(result)
    rarity = build_report(result)
    print(json.dumps({
        "ok": report["ok"],
        "supply": result["supply"],
        "class_counts": result["class_counts"],
        "unique_dna": result["unique_dna"],
        "special_count": result["special_count"],
        "duplicate_retries": result["duplicate_retries"],
        "seed": result["seed"],
        "phase": result["phase"],
        "tree_digest": (result.get("provenance") or {}).get("tree_digest"),
        "collection_fingerprint": result.get("collection_fingerprint"),
        "token_goods_usd": token_goods_usd(result),
        "provenance_ok": report.get("provenance_ok"),
        "rarest": rarity["rarest_tokens"][:5],
        "dry_run": bool(args.dry_run),
        "wrote": not bool(args.dry_run),
    }, indent=2))
    return 0 if report["ok"] else 1


def cmd_metadata(args: argparse.Namespace) -> int:
    from .metadata import write_metadata

    gate = composite_gate_problems(force=bool(args.force))
    if gate:
        print(json.dumps({"ok": False, "problems": gate}, indent=2))
        return 1
    result = _load_tokens()
    counts = write_metadata(result["tokens"], resume=bool(args.resume))
    print(json.dumps({"ok": True, **counts, "out": str(BUILD / "metadata")}, indent=2))
    return 0


def cmd_validate_layers(_: argparse.Namespace) -> int:
    from .validate_layers import validate_library

    summary = validate_library()
    print(json.dumps({k: summary[k] for k in ("png_count", "error_count", "ok", "note")}, indent=2))
    return 0 if summary["ok"] else 1


def cmd_validate_collection(_: argparse.Namespace) -> int:
    from .validate_collection import validate_result

    report = validate_result(_load_tokens())
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def cmd_rarity(_: argparse.Namespace) -> int:
    from .rarity_report import build_report

    report = build_report(_load_tokens())
    print(f"wrote {BUILD / 'reports' / 'rarity_report.md'}")
    print(f"duplicate_check={report['duplicate_check']} specials={report['special_count']}")
    return 0


def cmd_contact_sheet(_: argparse.Namespace) -> int:
    from .contact_sheet import render_all

    paths = render_all(_load_tokens())
    for path in paths:
        print(path)
    return 0


def cmd_blueprints(_: argparse.Namespace) -> int:
    from .blueprints import render_all

    paths = render_all()
    for path in paths:
        print(path)
    print("docs/blueprints/index.html")
    return 0


def cmd_prompts(args: argparse.Namespace) -> int:
    from .prompts import export_prompt_library

    rows = export_prompt_library(phase=args.phase)
    print(f"exported {len(rows)} prompts")
    return 0


def requested_token_missing(tokens: list, token_id: int | None) -> bool:
    if token_id is None:
        return False
    return all(int(row.get("token_id") or 0) != int(token_id) for row in tokens)


def composite_missing_report(count: int, rows: list[dict], skipped: int = 0) -> dict:
    return {
        "composited": count,
        "skipped": skipped,
        "missing_token_count": len(rows),
        "tokens_with_missing": rows,
    }


def composite_gate_problems(*, force: bool) -> list[str]:
    """Refuse to paint pixels from a stale or split generation unless forced."""
    if force:
        return []
    from .generate import generation_pair_problems
    from .provenance import last_generation_drift

    problems = generation_pair_problems()
    drift = last_generation_drift(config.production_seed(), 9)
    if drift["generation_stale"]:
        problems.append("last generation is stale vs live tree; regenerate or pass --force")
    return problems


def cmd_composite(args: argparse.Namespace) -> int:
    from .composite import (
        composite_disk_problems,
        composite_with_report,
        existing_token_png_ok,
        token_png_path,
        write_token_png,
    )
    from .paths import BUILD, BuildLockHeld, atomic_write_text, exclusive_build

    gate = composite_gate_problems(force=bool(args.force))
    if gate:
        print(json.dumps({"ok": False, "problems": gate}, indent=2))
        return 1

    # Count the tokens this run will attempt (limit/token-id shrink the set).
    pending = 1 if args.token_id else (args.limit or 800)
    disk = composite_disk_problems(int(pending))
    if disk:
        print(json.dumps({"ok": False, "problems": disk}, indent=2))
        return 1
    try:
        with exclusive_build("composite"):
            result = _load_tokens()
            if requested_token_missing(result["tokens"], args.token_id):
                print(json.dumps({"ok": False, "problems": [f"token_id {args.token_id} not in generation"]}, indent=2))
                return 1
            missing = "allow" if args.allow_missing else "error"
            count = 0
            skipped = 0
            missing_rows: list[dict] = []
            for token in result["tokens"]:
                if args.token_id and token["token_id"] != args.token_id:
                    continue
                dest = token_png_path(token["token_id"])
                if args.resume and existing_token_png_ok(dest):
                    skipped += 1
                    if args.limit and (count + skipped) >= args.limit:
                        break
                    continue
                try:
                    image, report = composite_with_report(token, missing=missing)
                except FileNotFoundError as exc:
                    print(exc, file=sys.stderr)
                    return 1
                write_token_png(token, image)
                if report["missing"]:
                    missing_rows.append({"token_id": token.get("token_id"), "missing": report["missing"]})
                    if args.report_missing:
                        print(f"#{token.get('token_id')} missing: {', '.join(report['missing'])}")
                count += 1
                if args.limit and (count + skipped) >= args.limit:
                    break
            report_payload = composite_missing_report(count, missing_rows, skipped)
            report_payload["tree_digest"] = (result.get("provenance") or {}).get("tree_digest")
            report_payload["collection_fingerprint"] = result.get("collection_fingerprint")
            atomic_write_text(
                BUILD / "reports" / "composite_missing.json",
                json.dumps(report_payload, indent=2),
            )
            print(f"composited {count} tokens skipped {skipped}")
            if missing_rows:
                print(
                    f"missing layers on {len(missing_rows)} tokens; "
                    f"see {BUILD / 'reports' / 'composite_missing.json'}"
                )
            return 0
    except BuildLockHeld as exc:
        print(json.dumps({"ok": False, "problems": [str(exc)]}, indent=2))
        return 1


def cmd_backup(args: argparse.Namespace) -> int:
    from .backup import restore_backup, verify_backup, write_backup
    from .paths import BuildLockHeld, exclusive_build

    if args.verify:
        problems = verify_backup(Path(args.verify))
        print(json.dumps({"ok": not problems, "problems": problems, "path": args.verify}, indent=2))
        return 0 if not problems else 1
    if args.restore_bak:
        from .generate import restore_previous_generation

        try:
            with exclusive_build("generate"):
                problems = restore_previous_generation()
        except BuildLockHeld as exc:
            print(json.dumps({"ok": False, "problems": [str(exc)]}, indent=2))
            return 1
        print(json.dumps({"ok": not problems, "problems": problems, "source": "bak"}, indent=2))
        return 0 if not problems else 1
    if args.restore:
        try:
            with exclusive_build("generate"):
                problems = restore_backup(Path(args.restore))
        except BuildLockHeld as exc:
            print(json.dumps({"ok": False, "problems": [str(exc)]}, indent=2))
            return 1
        print(json.dumps({"ok": not problems, "problems": problems, "path": args.restore}, indent=2))
        return 0 if not problems else 1
    try:
        path = write_backup()
    except ValueError as exc:
        print(json.dumps({"ok": False, "problems": [str(exc)]}, indent=2))
        return 1
    print(json.dumps({"ok": True, "path": str(path)}, indent=2))
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    from .preflight import status_report

    report = status_report()
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def cmd_preflight(args: argparse.Namespace) -> int:
    from .preflight import run_preflight

    report = run_preflight(seed=args.seed, phase=args.phase, mint=bool(args.mint))
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def cmd_provenance(_: argparse.Namespace) -> int:
    from .provenance import build_manifest

    manifest = build_manifest(config.production_seed(), 9)
    print(json.dumps({
        "tree_digest": manifest["tree_digest"],
        "seed": manifest["seed"],
        "phase": manifest["phase"],
        "generator_version": manifest["generator_version"],
        "layer_count": manifest["layer_count"],
        "git_revision": manifest["git_revision"],
        "configs": manifest["configs"],
        "sources": manifest["sources"],
    }, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="warm-company", description="Warm Company generative pipeline")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Deterministic DNA generation (no images required)")
    gen.add_argument("--seed", default=None)
    gen.add_argument("--phase", type=int, default=9)
    gen.add_argument("--no-specials", action="store_true")
    gen.add_argument("--mint", action="store_true", help="Refuse the development placeholder seed")
    gen.add_argument("--dry-run", action="store_true", help="Roll DNA and validate without writing build/dna")
    gen.set_defaults(func=cmd_generate)

    meta = sub.add_parser("metadata", help="Write CHIP-0007 JSON for the last generation")
    meta.add_argument("--resume", action="store_true", help="Skip tokens that already have valid CHIP-0007 JSON")
    meta.add_argument("--force", action="store_true", help="Write metadata even if last generate is stale")
    meta.set_defaults(func=cmd_metadata)

    vl = sub.add_parser("validate-layers", help="Inspect layer PNGs")
    vl.set_defaults(func=cmd_validate_layers)

    vc = sub.add_parser("validate-collection", help="Audit the last generation")
    vc.set_defaults(func=cmd_validate_collection)

    rar = sub.add_parser("rarity", help="Write rarity report")
    rar.set_defaults(func=cmd_rarity)

    cs = sub.add_parser("contact-sheet", help="Build contact sheets (schematic until art exists)")
    cs.set_defaults(func=cmd_contact_sheet)

    bp = sub.add_parser("blueprints", help="Render coordinate blueprints from anchors.json")
    bp.set_defaults(func=cmd_blueprints)

    pr = sub.add_parser("prompts", help="Export the Grok Image prompt library")
    pr.add_argument("--phase", type=int, default=9)
    pr.set_defaults(func=cmd_prompts)

    st = sub.add_parser("status", help="Snapshot seed, mint lock, layers, and tree digest without generating")
    st.set_defaults(func=cmd_status)

    pf = sub.add_parser("preflight", help="Fail-closed mint check: config, layers, generate, provenance")
    pf.add_argument("--seed", default=None)
    pf.add_argument("--phase", type=int, default=9)
    pf.add_argument("--mint", action="store_true", help="Refuse the development placeholder seed")
    pf.set_defaults(func=cmd_preflight)

    prov = sub.add_parser("provenance", help="Hash the config + layer tree that a generation must bind to")
    prov.set_defaults(func=cmd_provenance)

    bak = sub.add_parser("backup", help="Zip last DNA+provenance, or verify a zip with --verify")
    bak.add_argument("--verify", default=None, help="Path to a DNA backup zip to verify")
    bak.add_argument("--restore", default=None, help="Replace build/dna from a verified backup zip")
    bak.add_argument("--restore-bak", action="store_true", help="Restore DNA from the previous *.bak snapshot")
    bak.set_defaults(func=cmd_backup)

    comp = sub.add_parser("composite", help="Composite tokens (requires layer PNGs)")
    comp.add_argument("--token-id", type=int, default=None)
    comp.add_argument("--limit", type=int, default=None)
    comp.add_argument("--allow-missing", action="store_true")
    comp.add_argument("--report-missing", action="store_true")
    comp.add_argument("--resume", action="store_true", help="Skip tokens that already have a complete 1024 PNG")
    comp.add_argument("--force", action="store_true", help="Composite even if last generate is stale")
    comp.set_defaults(func=cmd_composite)
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_build()
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
