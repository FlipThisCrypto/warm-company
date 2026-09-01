"""Geometry enforcement. The image model draws; this module refuses drift.

Workflow:
1. Generate or edit art against a guide overlay.
2. Remove any remaining matte.
3. Measure bbox / occupancy IoU against the class template.
4. Optionally translate by a few pixels to snap to anchors (never scale freely).
5. Write the registered 1024x1024 PNG plus a sidecar JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops

from . import config
from .paths import BUILD, ROOT, TEMPLATES, ensure_build

CANVAS = (1024, 1024)


def measure(path: Path, class_id: str) -> dict:
    spec = config.class_spec(class_id)
    image = Image.open(path).convert("RGBA")
    if image.size != CANVAS:
        raise ValueError(f"{path} is {image.size}")
    bbox = image.getchannel("A").getbbox()
    occ_path = TEMPLATES / class_id / "occupancy.png"
    iou = None
    if occ_path.exists() and bbox:
        mask = Image.open(occ_path).convert("L")
        art = image.getchannel("A").point(lambda a: 255 if a > 24 else 0)
        occ = mask.point(lambda a: 255 if a > 12 else 0)
        inter = ImageChops.multiply(art, occ)
        union = ImageChops.add(art, occ)
        inter_n = inter.histogram()[255]
        union_n = union.histogram()[255]
        iou = (inter_n / union_n) if union_n else 0.0
    expected = spec["bounding_box"]
    delta = None
    if bbox:
        delta = {
            "dx0": bbox[0] - expected["x"],
            "dy0": bbox[1] - expected["y"],
            "dx1": bbox[2] - (expected["x"] + expected["w"]),
            "dy1": bbox[3] - (expected["y"] + expected["h"]),
        }
    tol = config.anchors()["registration_tolerances"]
    ok = True
    reasons = []
    if bbox is None:
        ok = False
        reasons.append("empty alpha")
    if iou is not None and iou < tol["occupancy_iou_min"]:
        ok = False
        reasons.append(f"IoU {iou:.3f} < {tol['occupancy_iou_min']}")
    return {
        "path": str(path),
        "class_id": class_id,
        "bbox": list(bbox) if bbox else None,
        "expected_bbox": expected,
        "delta": delta,
        "iou": iou,
        "ok": ok,
        "reasons": reasons,
    }


def snap_translate(path: Path, dx: int, dy: int, dest: Path) -> Path:
    """Integer-pixel translation only. No scaling, no rotation."""
    if abs(dx) > 12 or abs(dy) > 12:
        raise ValueError("snap limited to 12px; larger drift means redraw, not nudge")
    image = Image.open(path).convert("RGBA")
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.paste(image, (dx, dy), image)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "PNG")
    return dest


def write_sidecar(report: dict, dest: Path) -> None:
    ensure_build()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2), encoding="utf-8")
