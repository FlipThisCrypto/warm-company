"""Refinement-pass compositor: split limbs, preferred hats, magenta despill, 12 samples."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import procedural_contact_shadow  # noqa: E402
from warm_company.matte import chroma_key, fringe_report  # noqa: E402

SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")
LAYERS = ROOT / "layers"
OUT = ROOT / "build" / "review-v2"
CANVAS = (1024, 1024)

# Imagine outputs for this pass
SRC = {
    "snug_body": "59.jpg",
    "snug_body_navy": "79.jpg",
    "snug_arms": "61.jpg",
    "snug_legs": "64.jpg",
    "snug_face": "68.jpg",
    "snug_coffee": "76.jpg",
    "pup_body": "57.jpg",
    "pup_body_orange": "78.jpg",
    "pup_arms": "60.jpg",
    "pup_legs": "63.jpg",
    "pup_face": "67.jpg",
    "pup_map": "77.jpg",
    "lodge_body": "58.jpg",
    "lodge_body_orange": "81.jpg",
    "lodge_arms": "62.jpg",
    "lodge_legs": "65.jpg",
    "lodge_face": "66.jpg",
    "lodge_lantern": "75.jpg",
    "determined": "80.jpg",
    "beanie": "70.jpg",
    "knit": "69.jpg",
    "snow": "72.jpg",
}

SAMPLES = [
    {"id": "snug-01-bare", "title": "Snug — Bare rest", "class_id": "sleeping-bag",
     "bg": "winter-sunrise", "body": "snug_body", "arms": "snug_arms", "legs": "snug_legs",
     "face": "snug_face", "hat": None, "held": None, "snow": False, "determined": False},
    {"id": "snug-02-hat", "title": "Snug — Tiny beanie", "class_id": "sleeping-bag",
     "bg": "snowy-camp", "body": "snug_body", "arms": "snug_arms", "legs": "snug_legs",
     "face": "snug_face", "hat": "beanie", "held": None, "snow": False, "determined": False},
    {"id": "snug-03-coffee", "title": "Snug — Coffee grip", "class_id": "sleeping-bag",
     "bg": "winter-sunrise", "body": "snug_body", "arms": "snug_arms", "legs": "snug_legs",
     "face": "snug_face", "hat": None, "held": "snug_coffee", "snow": False, "determined": False,
     "crop_arms": "left"},
    {"id": "snug-04-night", "title": "Snug — Night snow", "class_id": "sleeping-bag",
     "bg": "cold-blue-night", "body": "snug_body_navy", "arms": "snug_arms", "legs": "snug_legs",
     "face": "snug_face", "hat": "knit", "held": None, "snow": True, "determined": True},
    {"id": "pup-01-bare", "title": "Pup — Bare rest", "class_id": "small-tent",
     "bg": "forest-clearing", "body": "pup_body", "arms": "pup_arms", "legs": "pup_legs",
     "face": "pup_face", "hat": None, "held": None, "snow": False, "determined": False},
    {"id": "pup-02-hat", "title": "Pup — Peak beanie", "class_id": "small-tent",
     "bg": "winter-sunrise", "body": "pup_body", "arms": "pup_arms", "legs": "pup_legs",
     "face": "pup_face", "hat": "beanie", "held": None, "snow": False, "determined": False},
    {"id": "pup-03-map", "title": "Pup — Two-hand map", "class_id": "small-tent",
     "bg": "snowy-camp", "body": "pup_body", "arms": None, "legs": "pup_legs",
     "face": "pup_face", "hat": None, "held": "pup_map", "snow": False, "determined": False},
    {"id": "pup-04-night", "title": "Pup — Night snow", "class_id": "small-tent",
     "bg": "cold-blue-night", "body": "pup_body", "arms": "pup_arms", "legs": "pup_legs",
     "face": "pup_face", "hat": "knit", "held": None, "snow": True, "determined": True},
    {"id": "lodge-01-bare", "title": "Lodge — D-door rest", "class_id": "large-tent",
     "bg": "snowy-camp", "body": "lodge_body", "arms": "lodge_arms", "legs": "lodge_legs",
     "face": "lodge_face", "hat": None, "held": None, "snow": False, "determined": False},
    {"id": "lodge-02-hat", "title": "Lodge — Peak beanie", "class_id": "large-tent",
     "bg": "winter-sunrise", "body": "lodge_body_orange", "arms": "lodge_arms", "legs": "lodge_legs",
     "face": "lodge_face", "hat": "beanie", "held": None, "snow": False, "determined": False},
    {"id": "lodge-03-lantern", "title": "Lodge — Lantern grip", "class_id": "large-tent",
     "bg": "forest-clearing", "body": "lodge_body", "arms": "lodge_arms", "legs": "lodge_legs",
     "face": "lodge_face", "hat": None, "held": "lodge_lantern", "snow": False, "determined": False,
     "crop_arms": "left", "glow": True},
    {"id": "lodge-04-night", "title": "Lodge — Night snow", "class_id": "large-tent",
     "bg": "cold-blue-night", "body": "lodge_body", "arms": "lodge_arms", "legs": "lodge_legs",
     "face": "lodge_face", "hat": None, "held": "lodge_lantern", "snow": True, "determined": True,
     "crop_arms": "left", "glow": True},
]


def empty() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def key(name: str) -> Image.Image:
    return chroma_key(Image.open(SESSION / SRC[name]))


def bbox(im: Image.Image):
    return im.getchannel("A").getbbox()


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


def snap_feet(im: Image.Image, spec: dict) -> Image.Image:
    box = bbox(im)
    if not box:
        return im
    dy = spec["character_baseline_y"] - box[3]
    dx = spec["character_center_x"] - (box[0] + box[2]) // 2
    canvas = empty()
    canvas.paste(im, (dx, dy), im)
    return canvas


def left_only(im: Image.Image) -> Image.Image:
    canvas = empty()
    canvas.paste(im.crop((0, 0, 512, 1024)), (0, 0))
    return canvas


def punch_face(im: Image.Image, spec: dict) -> Image.Image:
    door = spec.get("face_door") or spec["face_oval"]
    mask = Image.new("L", CANVAS, 255)
    draw = ImageDraw.Draw(mask)
    pad = 36
    draw.rounded_rectangle(
        [door["x"] - pad, door["y"] - pad, door["x"] + door["w"] + pad, door["y"] + door["h"] + pad],
        radius=80,
        fill=0,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    out = im.copy()
    a = out.getchannel("A")
    pa, pm = a.load(), mask.load()
    po = Image.new("L", CANVAS)
    px = po.load()
    for y in range(1024):
        for x in range(1024):
            px[x, y] = (pa[x, y] * pm[x, y]) // 255
    out.putalpha(po)
    return out


def lantern_glow(spec: dict) -> Image.Image:
    layer = empty()
    draw = ImageDraw.Draw(layer)
    hx, hy = spec["right_hand_default"]["x"], spec["right_hand_default"]["y"]
    for radius, alpha in ((160, 18), (100, 28), (60, 40)):
        draw.ellipse([hx - radius, hy - radius, hx + radius, hy + radius], fill=(255, 176, 72, alpha))
    return layer.filter(ImageFilter.GaussianBlur(18))


def hat_layer(im: Image.Image, spec: dict) -> Image.Image:
    pref = spec["headwear_preferred"]
    peak = spec["peak"]
    return place_center(im, 512, peak["y"] + pref["h"] // 2 - 8, max_w=pref["w"], max_h=pref["h"] + 24)


def mul_opacity(im: Image.Image, t: float) -> Image.Image:
    a = im.getchannel("A").point(lambda p: int(p * t))
    out = im.copy()
    out.putalpha(a)
    return out


def composite(sample: dict, lib: dict) -> Image.Image:
    spec = config.class_spec(sample["class_id"])
    canvas = empty()
    bg = Image.open(LAYERS / "shared" / "backgrounds" / f"{sample['bg']}.png").convert("RGBA")
    if bg.size != CANVAS:
        bg = bg.resize(CANVAS, Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, bg)
    if sample["snow"]:
        canvas = Image.alpha_composite(canvas, mul_opacity(lib["snow"], 0.55))
    canvas = Image.alpha_composite(canvas, procedural_contact_shadow(sample["class_id"]))

    # rear limbs
    if sample.get("arms") and sample["class_id"] != "sleeping-bag":
        arms = lib[sample["arms"]]
        if sample.get("crop_arms") == "left":
            arms = left_only(arms)
        canvas = Image.alpha_composite(canvas, arms)
    if sample.get("legs"):
        canvas = Image.alpha_composite(canvas, lib[sample["legs"]])

    canvas = Image.alpha_composite(canvas, lib[sample["body"]])

    face = lib[sample["face"]]
    if sample["determined"]:
        det = place_center(lib["determined"], spec["face_center"]["x"], spec["face_center"]["y"], max_w=180, max_h=110)
        canvas = Image.alpha_composite(canvas, det)
    else:
        canvas = Image.alpha_composite(canvas, face)

    if sample["class_id"] == "sleeping-bag" and sample.get("arms") and not sample.get("held"):
        canvas = Image.alpha_composite(canvas, lib[sample["arms"]])
    if sample["class_id"] == "sleeping-bag" and sample.get("crop_arms") == "left":
        canvas = Image.alpha_composite(canvas, left_only(lib["snug_arms"]))

    if sample.get("held") == "snug_coffee":
        canvas = Image.alpha_composite(
            canvas,
            place_center(lib["snug_coffee"], spec["right_hand_default"]["x"] - 40, spec["right_hand_default"]["y"] - 10, max_h=170),
        )
    elif sample.get("held") == "pup_map":
        canvas = Image.alpha_composite(
            canvas,
            place_center(lib["pup_map"], 512, spec["mouth_center"]["y"] + 70, max_w=340, max_h=220),
        )
    elif sample.get("held") == "lodge_lantern":
        canvas = Image.alpha_composite(canvas, lib["lodge_lantern"])
        if sample.get("glow"):
            canvas = Image.alpha_composite(canvas, lantern_glow(spec))

    if sample.get("hat"):
        canvas = Image.alpha_composite(canvas, hat_layer(lib[sample["hat"]], spec))

    if sample["snow"]:
        front = punch_face(mul_opacity(lib["snow"], 0.28), spec)
        canvas = Image.alpha_composite(canvas, front)
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
        cell = Image.new("RGBA", (thumb, thumb), (255, 0, 255, 40) if name != "composite" and name != "background" else (20, 24, 30, 255))
        if name == "background":
            cell = Image.new("RGBA", (thumb, thumb), (20, 24, 30, 255))
        vis = im.convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
        cell = Image.alpha_composite(cell, vis)
        sheet.paste(cell.convert("RGB"), (x, 28))
        d.text((x, 28 + thumb + 2), name, fill=(200, 206, 212), font=font)
        x += thumb + 10
    return sheet


def contact(rows: list[tuple[str, Image.Image]]) -> Image.Image:
    thumb = 240
    cols = 4
    font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 14)
    titlef = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)
    w = cols * thumb + 5 * 12
    h = 56 + 3 * (thumb + 32)
    sheet = Image.new("RGB", (w, h), (16, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.text((12, 12), "Warm Company — refinement pass (12 samples)", fill=(244, 240, 232), font=titlef)
    for i, (title, im) in enumerate(rows):
        r, c = divmod(i, cols)
        x = 12 + c * (thumb + 12)
        y = 48 + r * (thumb + 32)
        sheet.paste(im.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS), (x, y))
        d.text((x, y + thumb + 6), title, fill=(220, 226, 232), font=font)
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lib = {}
    reports = {}
    for name in SRC:
        print("key", name)
        im = key(name)
        if name.endswith("_legs"):
            cls = {"snug_legs": "sleeping-bag", "pup_legs": "small-tent", "lodge_legs": "large-tent"}[name]
            im = snap_feet(im, config.class_spec(cls))
        if name.endswith("_face"):
            cls = {"snug_face": "sleeping-bag", "pup_face": "small-tent", "lodge_face": "large-tent"}[name]
            spec = config.class_spec(cls)
            im = place_center(im, spec["face_center"]["x"], spec["face_center"]["y"], max_w=210, max_h=150)
        lib[name] = im
        reports[name] = fringe_report(im)
        dest = OUT / "layers" / f"{name}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "PNG")
        print(" ", reports[name])

    # persist production layer files
    mapping = {
        "sleeping-bag/body/ember-rust.png": lib["snug_body"],
        "sleeping-bag/body/navy-night.png": lib["snug_body_navy"],
        "sleeping-bag/arms/rest.png": lib["snug_arms"],
        "sleeping-bag/legs-rear/short-legs.png": lib["snug_legs"],
        "small-tent/body/forest-green.png": lib["pup_body"],
        "small-tent/body/camp-orange.png": lib["pup_body_orange"],
        "small-tent/arms-rear/rest.png": lib["pup_arms"],
        "small-tent/legs-rear/short-legs.png": lib["pup_legs"],
        "large-tent/body/royal-blue.png": lib["lodge_body"],
        "large-tent/body/camp-orange.png": lib["lodge_body_orange"],
        "large-tent/arms-rear/rest.png": lib["lodge_arms"],
        "large-tent/legs-rear/short-legs.png": lib["lodge_legs"],
        "shared/atmosphere-rear/light-snow.png": lib["snow"],
    }
    for rel, im in mapping.items():
        path = LAYERS / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, "PNG")

    results = []
    for sample in SAMPLES:
        print("composite", sample["id"])
        im = composite(sample, lib)
        im.save(OUT / f"{sample['id']}.png", "PNG")
        results.append((sample["title"], im))

    contact(results).save(OUT / "contact-sheet.png", "PNG")

    # reconstruction strips
    spec_s = config.class_spec("sleeping-bag")
    spec_p = config.class_spec("small-tent")
    spec_l = config.class_spec("large-tent")
    bg = Image.open(LAYERS / "shared/backgrounds/winter-sunrise.png").convert("RGBA").resize(CANVAS)
    strip("Snug reconstruction", [
        ("background", bg),
        ("rear legs", lib["snug_legs"]),
        ("body", lib["snug_body"]),
        ("face", lib["snug_face"]),
        ("front arms", lib["snug_arms"]),
        ("hat", hat_layer(lib["beanie"], spec_s)),
    ], results[1][1]).save(OUT / "strip-snug.png", "PNG")
    strip("Pup reconstruction", [
        ("background", bg),
        ("rear arms", lib["pup_arms"]),
        ("rear legs", lib["pup_legs"]),
        ("body", lib["pup_body"]),
        ("face", lib["pup_face"]),
        ("map+hands", place_center(lib["pup_map"], 512, 600, max_w=340, max_h=220)),
    ], results[6][1]).save(OUT / "strip-pup.png", "PNG")
    strip("Lodge reconstruction", [
        ("background", bg),
        ("rear arms", lib["lodge_arms"]),
        ("rear legs", lib["lodge_legs"]),
        ("body D-door", lib["lodge_body"]),
        ("face", lib["lodge_face"]),
        ("lantern grip", lib["lodge_lantern"]),
    ], results[10][1]).save(OUT / "strip-lodge.png", "PNG")
    print("done", OUT)


if __name__ == "__main__":
    main()
