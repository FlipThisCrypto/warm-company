"""Exact-pixel blueprints derived from config/anchors.json. Never freehand these."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config
from .paths import BUILD, DOCS, TEMPLATES, ensure_build

CANVAS = 1024
COLORS = {
    "sleeping-bag": (196, 92, 38, 230),
    "small-tent": (47, 107, 79, 230),
    "large-tent": (44, 95, 138, 230),
}
ZONE_COLORS = {
    "face": (240, 196, 90, 90),
    "headwear": (168, 92, 196, 80),
    "handheld_l": (80, 168, 196, 70),
    "handheld_r": (80, 168, 196, 70),
    "logo": (220, 80, 80, 70),
    "ground": (120, 160, 110, 70),
}


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _world_bg() -> Image.Image:
    world = config.anchors()["world"]
    img = Image.new("RGBA", (CANVAS, CANVAS), (226, 234, 240, 255))
    draw = ImageDraw.Draw(img)
    # sky / ground
    draw.rectangle([0, world["horizon_y"], CANVAS, CANVAS], fill=(244, 247, 250, 255))
    draw.rectangle([0, world["ground_plane_y"], CANVAS, CANVAS], fill=(236, 242, 247, 255))
    # grids
    for x in range(0, CANVAS, 8):
        draw.line([(x, 0), (x, CANVAS)], fill=(210, 218, 226, 255) if x % 64 else (190, 200, 210, 255))
    for y in range(0, CANVAS, 8):
        draw.line([(0, y), (CANVAS, y)], fill=(210, 218, 226, 255) if y % 64 else (190, 200, 210, 255))
    # horizon / baseline / margins
    draw.line([(0, world["horizon_y"]), (CANVAS, world["horizon_y"])], fill=(90, 130, 170, 255), width=2)
    draw.line([(0, world["baseline_y"]), (CANVAS, world["baseline_y"])], fill=(140, 70, 50, 255), width=3)
    m = world["margin_safe"]
    draw.rectangle([m, m, CANVAS - m - 1, CANVAS - m - 1], outline=(80, 80, 80, 180), width=1)
    logo = world["logo_safe_primary"]
    draw.rectangle(
        [logo["x"], logo["y"], logo["x"] + logo["w"], logo["y"] + logo["h"]],
        outline=(200, 70, 70, 255),
        width=2,
    )
    return img


def _draw_sleeping_bag(draw: ImageDraw.ImageDraw, fill, outline) -> None:
    spec = config.class_spec("sleeping-bag")
    sil = spec["silhouette"]
    hood = sil["hood_center"]
    r = sil["hood_radius"]
    draw.pieslice([hood["x"] - r, hood["y"] - r, hood["x"] + r, hood["y"] + r], 180, 360, fill=fill, outline=outline)
    body = [
        (sil["taper_top"]["left"], sil["taper_top"]["y"]),
        (sil["taper_top"]["right"], sil["taper_top"]["y"]),
        (sil["taper_bottom"]["right"], sil["taper_bottom"]["y"]),
        (512 + 80, sil["bag_bottom_y"]),
        (512 - 80, sil["bag_bottom_y"]),
        (sil["taper_bottom"]["left"], sil["taper_bottom"]["y"]),
    ]
    draw.polygon(body, fill=fill, outline=outline)
    # legs
    lf = spec["left_foot_anchor"]
    rf = spec["right_foot_anchor"]
    for foot in (lf, rf):
        draw.rounded_rectangle(
            [foot["x"] - 22, 848, foot["x"] + 22, foot["y"]],
            radius=12,
            fill=fill,
            outline=outline,
        )


def _draw_small_tent(draw: ImageDraw.ImageDraw, fill, outline) -> None:
    spec = config.class_spec("small-tent")
    sil = spec["silhouette"]
    peak = sil["peak"]
    left = sil["left_base"]
    right = sil["right_base"]
    # dome-ish triangle with shoulder bulge
    pts = [
        (peak["x"], peak["y"]),
        (right["x"] - 40, 420),
        (right["x"], left["y"]),
        (left["x"], left["y"]),
        (left["x"] + 40, 420),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    draw.polygon(
        [(peak["x"], peak["y"] + 8), (sil["door"]["x"], sil["door"]["y"] + sil["door"]["h"]),
         (sil["door"]["x"] + sil["door"]["w"], sil["door"]["y"] + sil["door"]["h"])],
        outline=outline,
    )
    lf = spec["left_foot_anchor"]
    rf = spec["right_foot_anchor"]
    for foot in (lf, rf):
        draw.rounded_rectangle([foot["x"] - 24, 848, foot["x"] + 24, foot["y"]], radius=12, fill=fill, outline=outline)


def _draw_large_tent(draw: ImageDraw.ImageDraw, fill, outline) -> None:
    spec = config.class_spec("large-tent")
    sil = spec["silhouette"]
    pts = [
        (sil["peak"]["x"], sil["peak"]["y"]),
        (sil["right_shoulder"]["x"], sil["right_shoulder"]["y"]),
        (sil["right_base"]["x"], sil["right_base"]["y"]),
        (sil["left_base"]["x"], sil["left_base"]["y"]),
        (sil["left_shoulder"]["x"], sil["left_shoulder"]["y"]),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    lf = spec["left_foot_anchor"]
    rf = spec["right_foot_anchor"]
    for foot in (lf, rf):
        draw.rounded_rectangle([foot["x"] - 26, 848, foot["x"] + 26, foot["y"]], radius=12, fill=fill, outline=outline)


DRAWERS = {
    "sleeping-bag": _draw_sleeping_bag,
    "small-tent": _draw_small_tent,
    "large-tent": _draw_large_tent,
}


def occupancy(class_id: str) -> Image.Image:
    img = Image.new("L", (CANVAS, CANVAS), 0)
    draw = ImageDraw.Draw(img)
    DRAWERS[class_id](draw, fill=255, outline=255)
    spec = config.class_spec(class_id)
    for hand, anchor in (
        (spec["left_hand_default"], spec["left_arm_anchor"]),
        (spec["right_hand_default"], spec["right_arm_anchor"]),
    ):
        draw.line([(anchor["x"], anchor["y"]), (hand["x"], hand["y"])], fill=255, width=48)
        draw.ellipse([hand["x"] - 28, hand["y"] - 28, hand["x"] + 28, hand["y"] + 28], fill=255)
    return img.filter(ImageFilter.MaxFilter(5))


def allowed_full(class_id: str) -> Image.Image:
    """Union of body occupancy plus headwear, handheld, and ground-foot zones."""
    spec = config.class_spec(class_id)
    img = occupancy(class_id).convert("L")
    draw = ImageDraw.Draw(img)
    for key in ("headwear_zone", "handheld_left_zone", "handheld_right_zone", "face_oval"):
        z = spec[key]
        draw.rectangle([z["x"], z["y"], z["x"] + z["w"], z["y"] + z["h"]], fill=255)
    for foot in (spec["left_foot_anchor"], spec["right_foot_anchor"]):
        draw.ellipse([foot["x"] - 40, foot["y"] - 36, foot["x"] + 40, foot["y"] + 20], fill=255)
    return img


def _cross(draw, x, y, color, r=8, width=2):
    draw.line([(x - r, y), (x + r, y)], fill=color, width=width)
    draw.line([(x, y - r), (x, y + r)], fill=color, width=width)
    draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=color)


def _label(draw, font, xy, text, fill=(20, 24, 28, 255)):
    draw.text(xy, text, font=font, fill=fill)


def blueprint(class_id: str) -> Image.Image:
    spec = config.class_spec(class_id)
    img = _world_bg()
    overlay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw_o = ImageDraw.Draw(overlay)
    DRAWERS[class_id](draw_o, fill=COLORS[class_id], outline=(40, 28, 22, 255))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    font = _font(16)
    small = _font(13)
    # zones
    for key, color_key in (
        ("face_oval", "face"),
        ("headwear_zone", "headwear"),
        ("handheld_left_zone", "handheld_l"),
        ("handheld_right_zone", "handheld_r"),
        ("body_accessory_zone", "ground"),
    ):
        z = spec[key]
        c = ZONE_COLORS[color_key if color_key != "ground" else "ground"]
        zone = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        ImageDraw.Draw(zone).rectangle([z["x"], z["y"], z["x"] + z["w"], z["y"] + z["h"]], fill=c)
        img = Image.alpha_composite(img, zone)
        draw = ImageDraw.Draw(img)
    bbox = spec["bounding_box"]
    draw.rectangle(
        [bbox["x"], bbox["y"], bbox["x"] + bbox["w"], bbox["y"] + bbox["h"]],
        outline=(20, 20, 20, 255),
        width=2,
    )
    _cross(draw, spec["character_center_x"], spec["face_center"]["y"], (20, 20, 20, 255))
    _cross(draw, spec["eye_left"]["x"], spec["eye_left"]["y"], (20, 20, 80, 255))
    _cross(draw, spec["eye_right"]["x"], spec["eye_right"]["y"], (20, 20, 80, 255))
    _cross(draw, spec["mouth_center"]["x"], spec["mouth_center"]["y"], (80, 20, 20, 255))
    _cross(draw, spec["left_arm_anchor"]["x"], spec["left_arm_anchor"]["y"], (20, 80, 40, 255))
    _cross(draw, spec["right_arm_anchor"]["x"], spec["right_arm_anchor"]["y"], (20, 80, 40, 255))
    _cross(draw, spec["left_hand_default"]["x"], spec["left_hand_default"]["y"], (20, 80, 40, 255))
    _cross(draw, spec["right_hand_default"]["x"], spec["right_hand_default"]["y"], (20, 80, 40, 255))
    _cross(draw, spec["left_foot_anchor"]["x"], spec["left_foot_anchor"]["y"], (80, 40, 20, 255))
    _cross(draw, spec["right_foot_anchor"]["x"], spec["right_foot_anchor"]["y"], (80, 40, 20, 255))
    _cross(draw, spec["peak"]["x"], spec["peak"]["y"], (20, 20, 20, 255))
    title = f"{spec['label']}  /  {spec['family_name']}  /  {spec['represents']}"
    _label(draw, _font(22), (56, 36), title)
    _label(draw, small, (56, 66), f"bbox ({bbox['x']},{bbox['y']}) {bbox['w']}×{bbox['h']}   baseline Y={spec['character_baseline_y']}")
    legend = [
        f"center X={spec['character_center_x']}",
        f"face ({spec['face_center']['x']},{spec['face_center']['y']})",
        f"eyes Y={spec['eye_baseline_y']}  L({spec['eye_left']['x']},{spec['eye_left']['y']}) R({spec['eye_right']['x']},{spec['eye_right']['y']})",
        f"mouth Y={spec['mouth_baseline_y']}",
        f"arms L({spec['left_arm_anchor']['x']},{spec['left_arm_anchor']['y']}) R({spec['right_arm_anchor']['x']},{spec['right_arm_anchor']['y']})",
        f"feet L({spec['left_foot_anchor']['x']},{spec['left_foot_anchor']['y']}) R({spec['right_foot_anchor']['x']},{spec['right_foot_anchor']['y']})",
        f"headwear brim Y={spec['headwear_brim_y']}",
    ]
    panel = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([44, 820, 430, 948], radius=8, fill=(255, 255, 255, 210))
    img = Image.alpha_composite(img, panel)
    draw = ImageDraw.Draw(img)
    y = 828
    for line in legend:
        _label(draw, small, (56, y), line, fill=(30, 34, 40, 255))
        y += 16
    world = config.anchors()["world"]
    _label(draw, small, (840, 48), "LOGO SAFE", fill=(160, 40, 40, 255))
    _label(draw, small, (56, world["horizon_y"] - 18), f"horizon Y={world['horizon_y']}")
    _label(draw, small, (700, world["baseline_y"] - 18), f"baseline Y={world['baseline_y']}")
    return img


def guides(class_id: str) -> Image.Image:
    """High-contrast overlay intended for image_edit reference."""
    spec = config.class_spec(class_id)
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    mask = occupancy(class_id).convert("L")
    tint = Image.new("RGBA", (CANVAS, CANVAS), (255, 0, 180, 50))
    img.paste(tint, mask=mask)
    draw = ImageDraw.Draw(img)
    bbox = spec["bounding_box"]
    draw.rectangle([bbox["x"], bbox["y"], bbox["x"] + bbox["w"], bbox["y"] + bbox["h"]], outline=(255, 0, 180, 255), width=3)
    z = spec["face_oval"]
    draw.ellipse([z["x"], z["y"], z["x"] + z["w"], z["y"] + z["h"]], outline=(0, 255, 180, 255), width=3)
    for pt, color in (
        (spec["eye_left"], (0, 220, 255, 255)),
        (spec["eye_right"], (0, 220, 255, 255)),
        (spec["mouth_center"], (255, 220, 0, 255)),
        (spec["left_arm_anchor"], (80, 255, 80, 255)),
        (spec["right_arm_anchor"], (80, 255, 80, 255)),
        (spec["left_foot_anchor"], (255, 140, 0, 255)),
        (spec["right_foot_anchor"], (255, 140, 0, 255)),
        (spec["peak"], (255, 255, 255, 255)),
    ):
        _cross(draw, pt["x"], pt["y"], color, r=10, width=3)
    hz = spec["headwear_zone"]
    draw.rectangle([hz["x"], hz["y"], hz["x"] + hz["w"], hz["y"] + hz["h"]], outline=(180, 80, 255, 255), width=2)
    return img


def scale_comparison() -> Image.Image:
    img = _world_bg()
    for class_id, alpha in (("large-tent", 90), ("small-tent", 110), ("sleeping-bag", 150)):
        layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        r, g, b, _ = COLORS[class_id]
        DRAWERS[class_id](draw, fill=(r, g, b, alpha), outline=(r, g, b, 255))
        img = Image.alpha_composite(img, layer)
    draw = ImageDraw.Draw(img)
    font = _font(20)
    draw.text((56, 36), "Relative scale — same baseline Y=896", font=font, fill=(20, 24, 28, 255))
    draw.text((56, 68), "Snug 432×784   Pup 576×640   Lodge 720×720", font=_font(14), fill=(20, 24, 28, 255))
    return img


def family_lineup() -> Image.Image:
    panels = [blueprint(cid) for cid in config.CLASS_IDS]
    sheet = Image.new("RGBA", (CANVAS * 3, CANVAS), (226, 234, 240, 255))
    for i, panel in enumerate(panels):
        sheet.paste(panel, (i * CANVAS, 0))
    return sheet


def _svg_for(class_id: str) -> str:
    spec = config.class_spec(class_id)
    bbox = spec["bounding_box"]
    color = {"sleeping-bag": "#C45C26", "small-tent": "#2F6B4F", "large-tent": "#2C5F8A"}[class_id]
    def pt(p):
        return f"{p['x']},{p['y']}"
    anchors = [
        ("center X", spec["character_center_x"], spec["character_baseline_y"] - 40),
        ("face", spec["face_center"]["x"], spec["face_center"]["y"]),
        ("eye L", spec["eye_left"]["x"], spec["eye_left"]["y"]),
        ("eye R", spec["eye_right"]["x"], spec["eye_right"]["y"]),
        ("mouth", spec["mouth_center"]["x"], spec["mouth_center"]["y"]),
        ("arm L", spec["left_arm_anchor"]["x"], spec["left_arm_anchor"]["y"]),
        ("arm R", spec["right_arm_anchor"]["x"], spec["right_arm_anchor"]["y"]),
        ("hand L", spec["left_hand_default"]["x"], spec["left_hand_default"]["y"]),
        ("hand R", spec["right_hand_default"]["x"], spec["right_hand_default"]["y"]),
        ("foot L", spec["left_foot_anchor"]["x"], spec["left_foot_anchor"]["y"]),
        ("foot R", spec["right_foot_anchor"]["x"], spec["right_foot_anchor"]["y"]),
        ("peak", spec["peak"]["x"], spec["peak"]["y"]),
    ]
    marks = []
    for name, x, y in anchors:
        marks.append(
            f'<g><circle cx="{x}" cy="{y}" r="5" fill="#1a1a1a"/><text x="{x + 8}" y="{y - 8}" font-size="12" font-family="Segoe UI, Arial">{html.escape(name)} ({x},{y})</text></g>'
        )
    world = config.anchors()["world"]
    logo = world["logo_safe_primary"]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <rect width="1024" height="1024" fill="#e2eaf0"/>
  <rect x="0" y="{world['horizon_y']}" width="1024" height="{1024 - world['horizon_y']}" fill="#f4f7fa"/>
  <line x1="0" y1="{world['horizon_y']}" x2="1024" y2="{world['horizon_y']}" stroke="#5a82aa" stroke-width="2"/>
  <line x1="0" y1="{world['baseline_y']}" x2="1024" y2="{world['baseline_y']}" stroke="#8c4632" stroke-width="3"/>
  <rect x="{bbox['x']}" y="{bbox['y']}" width="{bbox['w']}" height="{bbox['h']}" fill="none" stroke="#111" stroke-width="2" stroke-dasharray="6 4"/>
  <rect x="{spec['face_oval']['x']}" y="{spec['face_oval']['y']}" width="{spec['face_oval']['w']}" height="{spec['face_oval']['h']}" rx="80" fill="#f0c45a55" stroke="#c9a227"/>
  <rect x="{spec['headwear_zone']['x']}" y="{spec['headwear_zone']['y']}" width="{spec['headwear_zone']['w']}" height="{spec['headwear_zone']['h']}" fill="#a85cc450" stroke="#7a3d96"/>
  <rect x="{logo['x']}" y="{logo['y']}" width="{logo['w']}" height="{logo['h']}" fill="none" stroke="#c85050" stroke-width="2"/>
  <text x="56" y="48" font-size="22" font-family="Segoe UI, Arial">{html.escape(spec['label'])} / {html.escape(spec['family_name'])}</text>
  <text x="56" y="72" font-size="13" font-family="Segoe UI, Arial">bbox ({bbox['x']},{bbox['y']}) {bbox['w']}×{bbox['h']}  fill {color}</text>
  {''.join(marks)}
</svg>
"""


def _html_page() -> str:
    rows = []
    for class_id in config.CLASS_IDS:
        spec = config.class_spec(class_id)
        bbox = spec["bounding_box"]
        rows.append(
            f"""
<section>
  <h2>{html.escape(spec['label'])} — {html.escape(spec['family_name'])}</h2>
  <p>Represents <strong>{html.escape(spec['represents'])}</strong>. Supply {spec['supply']}. {html.escape(spec['role'])}</p>
  <img src="../../templates/{class_id}/blueprint.png" width="512" height="512" alt="{class_id} blueprint"/>
  <img src="../../templates/{class_id}/guides.png" width="512" height="512" alt="{class_id} guides"/>
  <table>
    <tr><th>Character center X</th><td>{spec['character_center_x']}</td></tr>
    <tr><th>Character baseline Y</th><td>{spec['character_baseline_y']}</td></tr>
    <tr><th>Bounding box</th><td>x={bbox['x']} y={bbox['y']} w={bbox['w']} h={bbox['h']} ({spec['width_pct']}% × {spec['height_pct']}%)</td></tr>
    <tr><th>Peak</th><td>({spec['peak']['x']}, {spec['peak']['y']})</td></tr>
    <tr><th>Face center</th><td>({spec['face_center']['x']}, {spec['face_center']['y']})</td></tr>
    <tr><th>Eye center Y</th><td>{spec['eye_baseline_y']}</td></tr>
    <tr><th>Left eye</th><td>({spec['eye_left']['x']}, {spec['eye_left']['y']})</td></tr>
    <tr><th>Right eye</th><td>({spec['eye_right']['x']}, {spec['eye_right']['y']})</td></tr>
    <tr><th>Mouth baseline Y</th><td>{spec['mouth_baseline_y']}</td></tr>
    <tr><th>Left arm anchor</th><td>({spec['left_arm_anchor']['x']}, {spec['left_arm_anchor']['y']})</td></tr>
    <tr><th>Right arm anchor</th><td>({spec['right_arm_anchor']['x']}, {spec['right_arm_anchor']['y']})</td></tr>
    <tr><th>Left foot anchor</th><td>({spec['left_foot_anchor']['x']}, {spec['left_foot_anchor']['y']})</td></tr>
    <tr><th>Right foot anchor</th><td>({spec['right_foot_anchor']['x']}, {spec['right_foot_anchor']['y']})</td></tr>
    <tr><th>Headwear zone</th><td>x={spec['headwear_zone']['x']} y={spec['headwear_zone']['y']} w={spec['headwear_zone']['w']} h={spec['headwear_zone']['h']}</td></tr>
  </table>
</section>
"""
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<title>Warm Company — Visual blueprints</title>
<style>
  body {{ font: 16px/1.45 "Segoe UI", system-ui, sans-serif; background:#111820; color:#eef2f5; margin: 24px; }}
  img {{ background:#e2eaf0; margin: 0 12px 12px 0; border-radius: 8px; }}
  table {{ border-collapse: collapse; margin: 12px 0 32px; }}
  td, th {{ border: 1px solid #2a3540; padding: 6px 10px; text-align: left; }}
  th {{ width: 220px; color: #9ab; }}
  h1,h2 {{ font-weight: 600; }}
  a {{ color: #8fc; }}
</style></head>
<body>
<h1>Warm Company visual blueprints</h1>
<p>Generated from <code>config/anchors.json</code>. If a number disagrees with a picture, the JSON wins and the picture must be regenerated.</p>
<p><img src="../../templates/world/family-lineup.png" width="100%" alt="family lineup"/></p>
<p><img src="../../templates/world/scale-comparison.png" width="512" height="512" alt="scale comparison"/></p>
{''.join(rows)}
</body></html>
"""


def render_all() -> list[Path]:
    ensure_build()
    written: list[Path] = []
    for class_id in config.CLASS_IDS:
        dest_dir = TEMPLATES / class_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        occ = occupancy(class_id)
        occ.save(dest_dir / "occupancy.png")
        allowed_full(class_id).save(dest_dir / "allowed-full.png")
        bp = blueprint(class_id)
        bp.save(dest_dir / "blueprint.png")
        g = guides(class_id)
        g.save(dest_dir / "guides.png")
        (dest_dir / "blueprint.svg").write_text(_svg_for(class_id), encoding="utf-8")
        bp.save(BUILD / "blueprints" / f"{class_id}-blueprint.png")
        written += [dest_dir / "occupancy.png", dest_dir / "blueprint.png", dest_dir / "guides.png"]
    world = TEMPLATES / "world"
    world.mkdir(parents=True, exist_ok=True)
    lineup = family_lineup()
    lineup.save(world / "family-lineup.png")
    lineup.save(BUILD / "blueprints" / "family-lineup.png")
    scale = scale_comparison()
    scale.save(world / "scale-comparison.png")
    scale.save(BUILD / "blueprints" / "scale-comparison.png")
    _world_bg().save(world / "frame.png")
    html_path = DOCS / "blueprints" / "index.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(_html_page(), encoding="utf-8")
    # dump a flattened coordinate table for docs
    table = {
        "world": config.anchors()["world"],
        "classes": {cid: {
            k: config.class_spec(cid)[k]
            for k in (
                "character_center_x",
                "character_baseline_y",
                "bounding_box",
                "peak",
                "face_center",
                "eye_baseline_y",
                "eye_left",
                "eye_right",
                "mouth_baseline_y",
                "mouth_center",
                "left_arm_anchor",
                "right_arm_anchor",
                "left_foot_anchor",
                "right_foot_anchor",
                "headwear_zone",
                "handheld_left_zone",
                "handheld_right_zone",
            )
        } for cid in config.CLASS_IDS},
    }
    (BUILD / "blueprints" / "coordinates.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
    return written
