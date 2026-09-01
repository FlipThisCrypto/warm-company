from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops

from . import config
from .matte import fringe_report
from .paths import BUILD, LAYERS, ROOT, TEMPLATES, ensure_build

CANVAS = (1024, 1024)
REQUIRED_MODE_TRANSPARENT = {"RGBA"}

FOLDER_TO_SLOT = {
    "body": "body",
    "patterns": "pattern",
    "structural": "structural",
    "face": "face",
    "eyes": "eyes",
    "eyebrows": "eyebrows",
    "mouths": "mouth",
    "facial": "facial",
    "arms": "arm_pose",
    "arms-rear": "arm_pose",
    "legs": "legs",
    "legs-rear": "legs",
    "footwear": "footwear",
    "headwear": "headwear",
    "handheld": "held_item",
    "handheld-rear": "held_item",
    "accessories": "body_accessory",
    "accessories-rear": "rear_accessory",
    "light": "held_item",
    "backgrounds": "background",
    "atmosphere": "atmosphere",
    "atmosphere-rear": "atmosphere",
    "rear-environment": "rear_environment",
    "ground": "ground_accessory",
}


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
    art_bin = art_alpha.point(lambda a: 255 if a > 24 else 0)
    inside_mask = mask.point(lambda m: 255 if m >= 12 else 0)
    outside_mask = mask.point(lambda m: 255 if m < 12 else 0)
    inside = ImageChops.multiply(art_bin, inside_mask).histogram()[255]
    outside = ImageChops.multiply(art_bin, outside_mask).histogram()[255]
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
    known_ids: dict[str, set[str]] = {}
    for trait in config.traits()["traits"]:
        known_ids.setdefault(trait["slot"], set()).add(trait["id"])
    for path in sorted(pngs):
        rel = path.relative_to(LAYERS).parts
        is_background = len(rel) >= 2 and rel[0] == "shared" and rel[1] == "backgrounds"
        expect_transparent = not is_background
        item = inspect_png(path, expect_transparent=expect_transparent)
        folder = rel[1] if len(rel) > 1 else ""
        slot = FOLDER_TO_SLOT.get(folder)
        if slot and path.stem not in known_ids.get(slot, set()) and not path.stem.endswith("-glow"):
            item["ok"] = False
            item["errors"].append(f"PNG {path.name} is not a trait id in slot {slot}")
        if not is_background and rel[0] in config.CLASS_IDS:
            occ = occupancy_check(path, rel[0])
            item["warnings"].extend(occ)
            if folder == "headwear" and item.get("bbox"):
                spec = config.class_spec(rel[0])
                pref_w = spec["headwear_preferred"]["w"]
                bw = item["bbox"][2] - item["bbox"][0]
                if bw > pref_w * 1.45:
                    item["warnings"].append(
                        f"headwear bbox width {bw}px exceeds preferred {pref_w}px"
                    )
        if expect_transparent and item["ok"] and path.suffix.lower() == ".png":
            try:
                fringe = fringe_report(Image.open(path))
                item["fringe"] = {k: fringe[k] for k in ("cyan_fringe_px", "magenta_fringe_px", "ok")}
                if not fringe["ok"]:
                    item["warnings"].append(
                        f"extraction fringe cyan={fringe['cyan_fringe_px']} magenta={fringe['magenta_fringe_px']}"
                    )
            except Exception as exc:  # noqa: BLE001
                item["warnings"].append(f"fringe check failed: {exc}")
        if not item["ok"]:
            errors += 1
        reports.append(item)
    summary = {
        "png_count": len(pngs),
        "error_count": errors,
        "ok": errors == 0,
        "note": "Every PNG must be 1024x1024. Extra files that are not trait ids are errors. Fringe is a warning until the library is fully recleaned.",
        "reports": reports,
    }
    (BUILD / "reports" / "layer_validation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary
