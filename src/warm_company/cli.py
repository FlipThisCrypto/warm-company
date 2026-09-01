from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, config
from .paths import BUILD, ensure_build


def _load_tokens(path: Path | None = None) -> dict:
    path = path or (BUILD / "dna" / "tokens.json")
    if not path.exists():
        raise SystemExit(f"no generation found at {path}; run generate first")
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_generate(args: argparse.Namespace) -> int:
    from .generate import generate_collection, write_generation
    from .validate_collection import validate_result
    from .rarity_report import build_report

    result = generate_collection(seed=args.seed, phase=args.phase, inject_specials=not args.no_specials)
    write_generation(result)
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
        "rarest": rarity["rarest_tokens"][:5],
    }, indent=2))
    return 0 if report["ok"] else 1


def cmd_metadata(args: argparse.Namespace) -> int:
    from .metadata import write_metadata

    result = _load_tokens()
    write_metadata(result["tokens"])
    print(f"wrote {len(result['tokens'])} CHIP-0007 files to {BUILD / 'metadata'}")
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


def cmd_composite(args: argparse.Namespace) -> int:
    from .composite import composite_with_report, write_token_png

    result = _load_tokens()
    missing = "allow" if args.allow_missing else "error"
    count = 0
    for token in result["tokens"]:
        if args.token_id and token["token_id"] != args.token_id:
            continue
        try:
            image, report = composite_with_report(token, missing=missing)
        except FileNotFoundError as exc:
            print(exc, file=sys.stderr)
            return 1
        write_token_png(token, image)
        if args.report_missing and report["missing"]:
            print(f"#{token.get('token_id')} missing: {', '.join(report['missing'])}")
        count += 1
        if args.limit and count >= args.limit:
            break
    print(f"composited {count} tokens")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="warm-company", description="Warm Company generative pipeline")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Deterministic DNA generation (no images required)")
    gen.add_argument("--seed", default=None)
    gen.add_argument("--phase", type=int, default=9)
    gen.add_argument("--no-specials", action="store_true")
    gen.set_defaults(func=cmd_generate)

    meta = sub.add_parser("metadata", help="Write CHIP-0007 JSON for the last generation")
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

    comp = sub.add_parser("composite", help="Composite tokens (requires layer PNGs)")
    comp.add_argument("--token-id", type=int, default=None)
    comp.add_argument("--limit", type=int, default=None)
    comp.add_argument("--allow-missing", action="store_true")
    comp.add_argument("--report-missing", action="store_true")
    comp.set_defaults(func=cmd_composite)
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_build()
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
