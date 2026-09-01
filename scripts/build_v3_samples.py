"""Refinement-pass v3 compositor.

Canonical masters are locked full-character constructions (limbs and faces
painted in place). Isolations exist for the layer architecture and strips.
Hats that the image model inflates are composited at preferred pixel size.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import procedural_contact_shadow  # noqa: E402
from warm_company.matte import chroma_key, fringe_report  # noqa: E402

SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")
LAYERS = ROOT / "layers"
OUT = ROOT / "build" / "review-v3"
CANVAS = (1024, 1024)

# Locked masters and derived assets
SRC = {
    "snug_canon": "82.jpg",
    "snug_body": "86.jpg",
    "snug_coffee": "87.jpg",
    "snug_navy_det": "95.jpg",
    "snug_arms": "102.jpg",
    "snug_legs": "103.jpg",
    "pup_canon": "84.jpg",
    "pup_map": "88.jpg",
    "pup_body": "89.jpg",
    "pup_hat": "96.jpg",
    "pup_arms": "104.jpg",
    "pup_legs": "105.jpg",
    "pup_night": "107.jpg",
    "lodge_canon": "83.jpg",
    "lodge_hat_orange": "110.jpg",
    "lodge_lantern": "99.jpg",
    "lodge_body": "100.jpg",
    "lodge_arms": "106.jpg",
    "lodge_night": "108.jpg",
    "lodge_legs": "109.jpg",
    "beanie": "97.jpg",
    "snow": "91.jpg",
}

SAMPLES = [
    {"id": "snug-01-bare", "title": "Snug — Bare rest", "class_id": "sleeping-bag",
     "bg": "winter-sunrise", "char": "snug_canon", "hat": False, "snow": False, "glow": False},
    {"id": "snug-02-hat", "title": "Snug — Tiny beanie", "class_id": "sleeping-bag",
     "bg": "snowy-camp", "char": "snug_canon", "hat": True, "snow": False, "glow": False},
    {"id": "snug-03-coffee", "title": "Snug — Coffee grip", "class_id": "sleeping-bag",
     "bg": "winter-sunrise", "char": "snug_coffee", "hat": False, "snow": False, "glow": False},
    {"id": "snug-04-night", "title": "Snug — Night snow", "class_id": "sleeping-bag",
     "bg": "cold-blue-night", "char": "snug_navy_det", "hat": True, "snow": True, "glow": False},
    {"id": "pup-01-bare", "title": "Pup — Bare rest", "class_id": "small-tent",
     "bg": "forest-clearing", "char": "pup_canon", "hat": False, "snow": False, "glow": False},
    {"id": "pup-02-hat", "title": "Pup — Peak beanie", "class_id": "small-tent",
     "bg": "winter-sunrise", "char": "pup_hat", "hat": False, "snow": False, "glow": False},
    {"id": "pup-03-map", "title": "Pup — Two-hand map", "class_id": "small-tent",
     "bg": "snowy-camp", "char": "pup_map", "hat": False, "snow": False, "glow": False},
    {"id": "pup-04-night", "title": "Pup — Night snow", "class_id": "small-tent",
     "bg": "cold-blue-night", "char": "pup_night", "hat": False, "snow": True, "glow": False},
    {"id": "lodge-01-bare", "title": "Lodge — D-door rest", "class_id": "large-tent",
     "bg": "snowy-camp", "char": "lodge_canon", "hat": False, "snow": False, "glow": False},
    {"id": "lodge-02-hat", "title": "Lodge — Peak beanie", "class_id": "large-tent",
     "bg": "winter-sunrise", "char": "lodge_hat_orange", "hat": False, "snow": False, "glow": False},
    {"id": "lodge-03-lantern", "title": "Lodge — Lantern grip", "class_id": "large-tent",
     "bg": "forest-clearing", "char": "lodge_lantern", "hat": False, "snow": False, "glow": True},
    {"id": "lodge-04-night", "title": "Lodge — Night snow", "class_id": "large-tent",
     "bg": "cold-blue-night", "char": "lodge_night", "hat": False, "snow": True, "glow": True},
]


def empty() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def bbox(im: Image.Image):
    return im.getchannel("A").getbbox()


def snap_feet(im: Image.Image, spec: dict) -> Image.Image:
    box = bbox(im)
    if not box:
        return im
    # Ignore near-full-canvas leftovers
    if box[2] - box[0] > 1000 and box[3] - box[1] > 1000:
        return im
    dy = spec["character_baseline_y"] - box[3]
    dx = spec["character_center_x"] - (box[0] + box[2]) // 2
    if abs(dx) < 3 and abs(dy) < 3:
        return im
    canvas = empty()
    canvas.paste(im, (dx, dy), im)
    return canvas


def clip_above(im: Image.Image, y_max: int) -> Image.Image:
    """Hide pixels above y_max so rear-leg extras cannot poke out the peak."""
    out = im.copy()
    a = out.getchannel("A")
    mask = Image.new("L", CANVAS, 255)
    ImageDraw.Draw(mask).rectangle([0, 0, 1024, y_max], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    out.putalpha(Image.composite(a, Image.new("L", CANVAS, 0), mask))
    return out


def place_center(im: Image.Image, cx: int, cy: int, max_w: int | None = None, max_h: int | None = None) -> Image.Image:
    box = bbox(im)
    if not box:
        return empty()
    crop = im.crop(box)
    w, h = crop.size
    scale = 1.0
    if max_w:
        scale = min(scale, max_w / w)
    if max_h:
        scale = min(scale, max_h / h)
    if scale != 1.0:
        crop = crop.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    canvas = empty()
    canvas.paste(crop, (int(cx - crop.size[0] / 2), int(cy - crop.size[1] / 2)), crop)
    return canvas


def hat_layer(im: Image.Image, spec: dict) -> Image.Image:
    pref = spec["headwear_preferred"]
    peak = spec["peak"]
    # Sit the brim on the peak; keep preferred width as the draw target.
    cy = peak["y"] + pref["h"] // 2 + 28
    return place_center(im, spec["character_center_x"], cy, max_w=pref["w"], max_h=pref["h"] + 36)


def mul_opacity(im: Image.Image, t: float) -> Image.Image:
    a = im.getchannel("A").point(lambda p: int(p * t))
    out = im.copy()
    out.putalpha(a)
    return out


def punch_face(im: Image.Image, spec: dict) -> Image.Image:
    door = spec.get("face_door") or spec["face_oval"]
    mask = Image.new("L", CANVAS, 255)
    draw = ImageDraw.Draw(mask)
    pad = 48
    draw.rounded_rectangle(
        [door["x"] - pad, door["y"] - pad, door["x"] + door["w"] + pad, door["y"] + door["h"] + pad],
        radius=70,
        fill=0,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    a = im.getchannel("A")
    out = im.copy()
    out.putalpha(Image.composite(a, Image.new("L", CANVAS, 0), mask))
    return out


def lantern_glow(spec: dict) -> Image.Image:
    layer = empty()
    draw = ImageDraw.Draw(layer)
    hx, hy = spec["right_hand_default"]["x"] - 40, spec["right_hand_default"]["y"] - 20
    for radius, alpha in ((140, 16), (88, 24), (48, 36)):
        draw.ellipse([hx - radius, hy - radius, hx + radius, hy + radius], fill=(255, 176, 72, alpha))
    return layer.filter(ImageFilter.GaussianBlur(16))


def composite(sample: dict, lib: dict) -> Image.Image:
    spec = config.class_spec(sample["class_id"])
    canvas = empty()
    bg = Image.open(LAYERS / "shared" / "backgrounds" / f"{sample['bg']}.png").convert("RGBA")
    if bg.size != CANVAS:
        bg = bg.resize(CANVAS, Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, bg)
    if sample["snow"]:
        canvas = Image.alpha_composite(canvas, mul_opacity(lib["snow"], 0.42))
    canvas = Image.alpha_composite(canvas, procedural_contact_shadow(sample["class_id"]))
    canvas = Image.alpha_composite(canvas, lib[sample["char"]])
    if sample["hat"]:
        canvas = Image.alpha_composite(canvas, hat_layer(lib["beanie"], spec))
    if sample["glow"]:
        canvas = Image.alpha_composite(canvas, lantern_glow(spec))
    if sample["snow"]:
        canvas = Image.alpha_composite(canvas, punch_face(mul_opacity(lib["snow"], 0.22), spec))
    return canvas


def strip(title: str, parts: list[tuple[str, Image.Image]], final: Image.Image) -> Image.Image:
    thumb = 160
    items = parts + [("composite", final)]
    font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 13)
    sheet = Image.new("RGB", (12 + len(items) * (thumb + 10), thumb + 44), (18, 24, 32))
    d = ImageDraw.Draw(sheet)
    d.text((12, 6), title, fill=(240, 236, 228), font=font)
    x = 12
    for name, im in items:
        if name in ("composite", "background"):
            cell = Image.new("RGBA", (thumb, thumb), (20, 24, 30, 255))
        else:
            cell = Image.new("RGBA", (thumb, thumb), (255, 0, 255, 48))
        vis = im.convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
        cell = Image.alpha_composite(cell, vis)
        sheet.paste(cell.convert("RGB"), (x, 28))
        d.text((x, 28 + thumb + 2), name, fill=(200, 206, 212), font=font)
        x += thumb + 10
    return sheet


def contact(rows: list[tuple[str, Image.Image]]) -> Image.Image:
    thumb = 240
    mini = 128
    cols = 4
    font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 14)
    titlef = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)
    small = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 12)
    w = cols * thumb + 5 * 12
    h = 56 + 3 * (thumb + 32) + 24 + mini + 28
    sheet = Image.new("RGB", (w, h), (16, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.text((12, 12), "Warm Company — refinement pass v3 (12 samples)", fill=(244, 240, 232), font=titlef)
    for i, (title, im) in enumerate(rows):
        r, c = divmod(i, cols)
        x = 12 + c * (thumb + 12)
        y = 48 + r * (thumb + 32)
        sheet.paste(im.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS), (x, y))
        d.text((x, y + thumb + 6), title, fill=(220, 226, 232), font=font)
    y = 48 + 3 * (thumb + 32) + 4
    d.text((12, y), "128 px readability check", fill=(180, 186, 196), font=small)
    y += 18
    x = 12
    for _, im in rows:
        sheet.paste(im.convert("RGB").resize((mini, mini), Image.Resampling.LANCZOS), (x, y))
        x += mini + 8
    return sheet


def persist_production(lib: dict) -> None:
    mapping = {
        "sleeping-bag/body/ember-rust.png": lib["snug_body"],
        "sleeping-bag/arms-rear/rest.png": lib["snug_arms"],
        "sleeping-bag/legs-rear/short-legs.png": lib["snug_legs"],
        "sleeping-bag/headwear/beanie.png": hat_layer(lib["beanie"], config.class_spec("sleeping-bag")),
        "small-tent/body/forest-green.png": lib["pup_body"],
        "small-tent/arms-rear/rest.png": lib["pup_arms"],
        "small-tent/legs-rear/short-legs.png": lib["pup_legs"],
        "large-tent/body/royal-blue.png": lib["lodge_body"],
        "large-tent/arms-rear/rest.png": lib["lodge_arms"],
        "large-tent/legs-rear/short-legs.png": lib["lodge_legs"],
        "shared/atmosphere-rear/light-snow.png": lib["snow"],
        "shared/atmosphere/light-snow.png": mul_opacity(lib["snow"], 0.45),
    }
    for rel, im in mapping.items():
        path = LAYERS / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, "PNG")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lib: dict[str, Image.Image] = {}
    for name, src in SRC.items():
        print("key", name)
        im = chroma_key(Image.open(SESSION / src))
        if name.endswith("_legs"):
            cls = {"snug_legs": "sleeping-bag", "pup_legs": "small-tent", "lodge_legs": "large-tent"}[name]
            spec = config.class_spec(cls)
            im = snap_feet(im, spec)
            im = clip_above(im, spec["hem_y"] - 120)
        if name in ("snug_canon", "snug_coffee", "snug_navy_det", "pup_canon", "pup_map",
                    "pup_hat", "pup_night", "lodge_canon", "lodge_hat_orange",
                    "lodge_lantern", "lodge_night"):
            cls = {
                "snug_canon": "sleeping-bag", "snug_coffee": "sleeping-bag", "snug_navy_det": "sleeping-bag",
                "pup_canon": "small-tent", "pup_map": "small-tent", "pup_hat": "small-tent", "pup_night": "small-tent",
                "lodge_canon": "large-tent", "lodge_hat_orange": "large-tent",
                "lodge_lantern": "large-tent", "lodge_night": "large-tent",
            }[name]
            im = snap_feet(im, config.class_spec(cls))
        lib[name] = im
        report = fringe_report(im)
        dest = OUT / "layers" / f"{name}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "PNG")
        print(" ", report)

    persist_production(lib)

    results = []
    by_id = {}
    for sample in SAMPLES:
        print("composite", sample["id"])
        im = composite(sample, lib)
        im.save(OUT / f"{sample['id']}.png", "PNG")
        results.append((sample["title"], im))
        by_id[sample["id"]] = im

    contact(results).save(OUT / "contact-sheet.png", "PNG")

    spec_s = config.class_spec("sleeping-bag")
    spec_p = config.class_spec("small-tent")
    spec_l = config.class_spec("large-tent")
    bg = Image.open(LAYERS / "shared/backgrounds/winter-sunrise.png").convert("RGBA").resize(CANVAS)
    strip("Snug reconstruction (bare + preferred hat)", [
        ("background", bg),
        ("rear legs", lib["snug_legs"]),
        ("body", lib["snug_body"]),
        ("rear arms", lib["snug_arms"]),
        ("canonical", lib["snug_canon"]),
        ("hat preferred", hat_layer(lib["beanie"], spec_s)),
    ], by_id["snug-02-hat"]).save(OUT / "strip-snug.png", "PNG")
    strip("Pup reconstruction (map pose uses locked canonical edit)", [
        ("background", bg),
        ("rear legs", lib["pup_legs"]),
        ("rear arms", lib["pup_arms"]),
        ("body door", lib["pup_body"]),
        ("canonical", lib["pup_canon"]),
        ("map hold", lib["pup_map"]),
    ], by_id["pup-03-map"]).save(OUT / "strip-pup.png", "PNG")
    strip("Lodge reconstruction (D-door canonical + lantern hold)", [
        ("background", bg),
        ("rear legs", lib["lodge_legs"]),
        ("rear arms", lib["lodge_arms"]),
        ("body D-door", lib["lodge_body"]),
        ("canonical", lib["lodge_canon"]),
        ("lantern grip", lib["lodge_lantern"]),
    ], by_id["lodge-03-lantern"]).save(OUT / "strip-lodge.png", "PNG")
    print("done", OUT)


if __name__ == "__main__":
    main()
