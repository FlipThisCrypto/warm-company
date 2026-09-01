from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from . import config
from .paths import BUILD, LAYERS, ROOT, TEMPLATES, ensure_build

CANVAS = (1024, 1024)
REQUIRED_MODE_TRANSPARENT = {"RGBA"}


def _bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A")
    return alpha.getbbox()


def inspect_png(path: Path, *, expect_transparent: bool) -> dict:
    report: dict = {"path": str(path.relative_to(ROOT)), "ok": True, "errors": [], "warnings": []}
    try:
        image = Image.open(path)
    except Exception as exc:  # noqa: BLE001
        report["ok"] = False
        report["errors"].append(f"cannot open: {exc}")
        return report
    report["size"] = list(image.size)
    report["mode"] = image.mode
    if image.size != CANVAS:
        report["ok"] = False
        report["errors"].append(f"size {image.size} != {CANVAS}")
    if expect_transparent:
        if image.mode != "RGBA":
            report["ok"] = False
            report["errors"].append(f"mode {image.mode} != RGBA")
        else:
            extrema = image.getchannel("A").getextrema()
            report["alpha_minmax"] = list(extrema)
            if extrema[0] >= 250:
                report["ok"] = False
                report["errors"].append("expected transparency but alpha is essentially opaque")
            if extrema[1] <= 0:
                report["ok"] = False
                report["errors"].append("image is fully transparent")
            bbox = _bbox(image.convert("RGBA"))
            report["bbox"] = list(bbox) if bbox else None
            if bbox:
                x0, y0, x1, y1 = bbox
                if x0 < 8 or y0 < 8 or x1 > 1016 or y1 > 1016:
                    report["warnings"].append("pixels extremely close to the canvas edge")
    else:
        rgba = image.convert("RGBA")
        extrema = rgba.getchannel("A").getextrema()
        report["alpha_minmax"] = list(extrema)
        if extrema[0] < 250:
            report["ok"] = False
            report["errors"].append("background must be opaque")
    # Crude watermark / text hunt: not possible reliably. Flag obvious white mats.
    if expect_transparent and image.mode == "RGBA":
        corners = [image.getpixel((2, 2)), image.getpixel((1021, 2)), image.getpixel((2, 1021)), image.getpixel((1021, 1021))]
        if all(px[3] > 200 and px[0] > 240 and px[1] > 240 and px[2] > 240 for px in corners):
            report["ok"] = False
            report["errors"].append("white matte detected in corners; likely a non-transparent background")
    return report


def occupancy_check(path: Path, class_id: str) -> list[str]:
    rel = path.relative_to(LAYERS).parts
    slot_folder = rel[1] if len(rel) > 1 else ""
    body_slots = {"body", "patterns", "structural", "face", "legs"}
    mask_name = "occupancy.png" if slot_folder in body_slots else "allowed-full.png"
    mask_path = TEMPLATES / class_id / mask_name
    if not mask_path.exists():
        return [f"{mask_name} not generated yet"]
    art = Image.open(path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    if art.size != CANVAS or mask.size != CANVAS:
        return ["occupancy mask size mismatch"]
    art_alpha = art.getchannel("A")
    # Dilate occupancy conceptually by using a threshold.
    errors = []
    # Sample: if art has visible pixels where mask is near 0, warn.
    outside = 0
    inside = 0
    art_px = art_alpha.tobytes()
    mask_px = mask.tobytes()
    for a, m in zip(art_px, mask_px):
        if a > 24:
            if m < 12:
                outside += 1
            else:
                inside += 1
    if inside == 0:
        errors.append("no overlap with occupancy mask")
    elif outside / (inside + outside) > 0.08:
        errors.append(f"{outside} opaque pixels sit outside occupancy ({outside / (inside + outside):.1%})")
    return errors


def validate_library() -> dict:
    ensure_build()
    pngs = [path for path in LAYERS.rglob("*.png") if path.is_file()]
    reports = []
    errors = 0
    for path in sorted(pngs):
        rel = path.relative_to(LAYERS).parts
        is_background = len(rel) >= 2 and rel[0] == "shared" and rel[1] == "backgrounds"
        item = inspect_png(path, expect_transparent=not is_background)
        if not is_background and rel[0] in config.CLASS_IDS:
            occ = occupancy_check(path, rel[0])
            item["warnings"].extend(occ)
        if not item["ok"]:
            errors += 1
        reports.append(item)
    summary = {
        "png_count": len(pngs),
        "error_count": errors,
        "ok": errors == 0,
        "note": "Phase 0 expects png_count == 0. Empty is valid until art production begins.",
        "reports": reports,
    }
    (BUILD / "reports" / "layer_validation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary
