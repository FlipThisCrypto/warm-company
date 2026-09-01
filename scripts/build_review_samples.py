"""Ingest Imagine layers, register them to anchors, composite 9 review samples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import procedural_contact_shadow  # noqa: E402
from warm_company.matte import chroma_key  # noqa: E402

SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")
LAYERS = ROOT / "layers"
OUT = ROOT / "build" / "review-samples"
CANVAS = (1024, 1024)

RAW = {
    "sleeping-bag/body/ember-rust.png": "15.jpg",
    "sleeping-bag/body/trail-olive.png": "40.jpg",
    "sleeping-bag/body/navy-night.png": "38.jpg",
    "small-tent/body/forest-green.png": "17.jpg",
    "small-tent/body/camp-orange.png": "36.jpg",
    "small-tent/body/navy-night.png": "41.jpg",
    "large-tent/body/forest-green.png": "42.jpg",
    "large-tent/body/camp-orange.png": "39.jpg",
    "large-tent/body/navy-night.png": "43.jpg",
    "sleeping-bag/face/standard-face.png": "21.jpg",
    "small-tent/face/standard-face.png": "19.jpg",
    "large-tent/face/standard-face.png": "20.jpg",
    "sleeping-bag/eyes/sleepy.png": "22.jpg",
    "sleeping-bag/eyes/happy.png": "23.jpg",
    "sleeping-bag/eyes/determined.png": "49.jpg",
    "small-tent/eyes/happy.png": "23.jpg",
    "small-tent/eyes/normal.png": "23.jpg",
    "small-tent/eyes/sleepy.png": "22.jpg",
    "small-tent/eyes/determined.png": "49.jpg",
    "large-tent/eyes/happy.png": "24.jpg",
    "large-tent/eyes/normal.png": "24.jpg",
    "large-tent/eyes/determined.png": "49.jpg",
    "sleeping-bag/mouths/smile.png": "32.jpg",
    "sleeping-bag/mouths/grin.png": "33.jpg",
    "sleeping-bag/mouths/determined.png": "32.jpg",
    "small-tent/mouths/smile.png": "30.jpg",
    "small-tent/mouths/grin.png": "33.jpg",
    "large-tent/mouths/smile.png": "33.jpg",
    "large-tent/mouths/grin.png": "33.jpg",
    "large-tent/mouths/determined.png": "32.jpg",
    "sleeping-bag/arms/rest.png": "25.jpg",
    "sleeping-bag/arms/hold-item.png": "25.jpg",
    "small-tent/arms/rest.png": "26.jpg",
    "small-tent/arms/hold-item.png": "26.jpg",
    "large-tent/arms/rest.png": "27.jpg",
    "large-tent/arms/hold-item.png": "27.jpg",
    "sleeping-bag/legs/short-legs.png": "28.jpg",
    "small-tent/legs/short-legs.png": "29.jpg",
    "large-tent/legs/short-legs.png": "31.jpg",
    "sleeping-bag/footwear/basic-shoes.png": "28.jpg",
    "sleeping-bag/footwear/snow-boots.png": "48.jpg",
    "sleeping-bag/footwear/work-boots.png": "48.jpg",
    "small-tent/footwear/sneakers.png": "29.jpg",
    "small-tent/footwear/work-boots.png": "48.jpg",
    "small-tent/footwear/snow-boots.png": "48.jpg",
    "large-tent/footwear/work-boots.png": "31.jpg",
    "large-tent/footwear/snow-boots.png": "48.jpg",
    "sleeping-bag/headwear/beanie.png": "37.jpg",
    "sleeping-bag/headwear/knit-cap.png": "47.jpg",
    "small-tent/headwear/beanie.png": "37.jpg",
    "small-tent/headwear/knit-cap.png": "47.jpg",
    "large-tent/headwear/beanie.png": "37.jpg",
    "sleeping-bag/handheld/coffee.png": "35.jpg",
    "sleeping-bag/handheld/lantern.png": "44.jpg",
    "small-tent/handheld/coffee.png": "35.jpg",
    "small-tent/handheld/thermos.png": "50.jpg",
    "large-tent/handheld/coffee.png": "35.jpg",
    "large-tent/handheld/lantern.png": "44.jpg",
    "shared/atmosphere/light-snow.png": "51.jpg",
    "sleeping-bag/facial/blush.png": "22.jpg",
}


def empty() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def load_keyed(name: str) -> Image.Image:
    return chroma_key(Image.open(SESSION / name))


def translate(image: Image.Image, dx: int, dy: int) -> Image.Image:
    canvas = empty()
    canvas.paste(image, (dx, dy), image)
    return canvas


def bbox(image: Image.Image):
    return image.getchannel("A").getbbox()


def place_center(image: Image.Image, cx: int, cy: int, max_h: int | None = None) -> Image.Image:
    box = bbox(image)
    if not box:
        return empty()
    cropped = image.crop(box)
    if max_h and cropped.size[1] > max_h:
        ratio = max_h / cropped.size[1]
        cropped = cropped.resize(
            (max(1, int(cropped.size[0] * ratio)), max_h),
            Image.Resampling.LANCZOS,
        )
    canvas = empty()
    x = int(cx - cropped.size[0] / 2)
    y = int(cy - cropped.size[1] / 2)
    canvas.paste(cropped, (x, y), cropped)
    return canvas


def place_hat(image: Image.Image, spec: dict) -> Image.Image:
    zone = spec["headwear_zone"]
    max_h = min(zone["h"] + 36, 220)
    return place_center(image, 512, zone["y"] + zone["h"] // 2 + 8, max_h=max_h)


def place_item(image: Image.Image, spec: dict) -> Image.Image:
    hand = spec["right_hand_default"]
    return place_center(image, hand["x"] - 20, hand["y"] - 20, max_h=180)


def place_boots(image: Image.Image, spec: dict) -> Image.Image:
    left = spec["left_foot_anchor"]
    right = spec["right_foot_anchor"]
    cx = (left["x"] + right["x"]) // 2
    return place_center(image, cx, spec["character_baseline_y"] - 40, max_h=110)


def snap_feet(image: Image.Image, spec: dict) -> Image.Image:
    box = bbox(image)
    if not box:
        return image
    dy = spec["character_baseline_y"] - box[3]
    dx = spec["character_center_x"] - (box[0] + box[2]) // 2
    return translate(image, dx, dy)


def snap_face_feature(image: Image.Image, spec: dict, key: str = "face_center") -> Image.Image:
    box = bbox(image)
    if not box:
        return image
    target = spec[key]
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    return translate(image, int(target["x"] - cx), int(target["y"] - cy))


def punch_face(image: Image.Image, spec: dict) -> Image.Image:
    oval = spec["face_oval"]
    mask = Image.new("L", CANVAS, 255)
    draw = ImageDraw.Draw(mask)
    pad = 28
    draw.ellipse(
        [oval["x"] - pad, oval["y"] - pad, oval["x"] + oval["w"] + pad, oval["y"] + oval["h"] + pad],
        fill=0,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    out = image.copy()
    alpha = out.getchannel("A")
    out.putalpha(_mul(alpha, mask))
    return out


def _mul(a: Image.Image, b: Image.Image) -> Image.Image:
    pa, pb = a.load(), b.load()
    out = Image.new("L", a.size)
    po = out.load()
    w, h = a.size
    for y in range(h):
        for x in range(w):
            po[x, y] = (pa[x, y] * pb[x, y]) // 255
    return out


def prepare_library() -> dict[str, Image.Image]:
    lib = {}
    for dest, src in RAW.items():
        path = SESSION / src
        if not path.exists():
            print("missing", src)
            continue
        image = load_keyed(src)
        class_id = dest.split("/")[0]
        spec = config.class_spec(class_id) if class_id in config.CLASS_IDS else None
        if spec and "/eyes/" in dest:
            max_h = 78 if "determined" in dest else 110
            image = place_center(image, spec["face_center"]["x"], spec["face_center"]["y"] - 8, max_h=max_h)
        elif spec and "/mouths/" in dest:
            max_h = 28 if "grin" in dest else 36
            image = place_center(image, spec["mouth_center"]["x"], spec["mouth_center"]["y"], max_h=max_h)
        elif spec and "/face/" in dest and class_id == "sleeping-bag":
            image = snap_face_feature(image, spec, "face_center")
        elif spec and "/legs/" in dest:
            image = snap_feet(image, spec)
        elif spec and "/footwear/" in dest and "boots" in dest:
            image = place_boots(image, spec)
        elif spec and "/footwear/" in dest:
            image = snap_feet(image, spec)
        elif spec and "/headwear/" in dest:
            image = place_hat(image, spec)
        elif spec and "/handheld/" in dest:
            image = place_item(image, spec)
        elif dest.endswith("light-snow.png"):
            # keep flakes; face punch happens per composite
            pass
        dest_path = LAYERS / dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest_path, "PNG")
        lib[dest] = image
        print("saved", dest, "bbox", bbox(image))
    return lib


def layer_for(class_id: str, slot_folder: str, trait: str, lib: dict) -> Image.Image | None:
    if trait in (None, "none"):
        return None
    key = f"{class_id}/{slot_folder}/{trait}.png"
    if key in lib:
        return lib[key]
    path = LAYERS / key
    if path.exists():
        return Image.open(path).convert("RGBA")
    if slot_folder == "background":
        bg = LAYERS / "shared" / "backgrounds" / f"{trait}.png"
        if bg.exists():
            return Image.open(bg).convert("RGBA")
    if slot_folder == "atmosphere":
        at = LAYERS / "shared" / "atmosphere" / f"{trait}.png"
        if at.exists():
            return Image.open(at).convert("RGBA")
        if f"shared/atmosphere/{trait}.png" in lib:
            return lib[f"shared/atmosphere/{trait}.png"]
    print("  skip missing", key)
    return None


def composite_sample(sample: dict, lib: dict) -> Image.Image:
    class_id = sample["class_id"]
    spec = config.class_spec(class_id)
    t = sample["traits"]
    canvas = empty()

    bg = layer_for("shared", "backgrounds", t["background"], lib)
    if bg is None:
        bg = Image.open(LAYERS / "shared" / "backgrounds" / f"{t['background']}.png").convert("RGBA")
    if bg.mode != "RGBA":
        bg = bg.convert("RGBA")
    if bg.size != CANVAS:
        bg = bg.resize(CANVAS, Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, bg)
    canvas = Image.alpha_composite(canvas, procedural_contact_shadow(class_id))

    def add(folder, trait, punch=False):
        nonlocal canvas
        layer = layer_for(class_id, folder, trait, lib)
        if layer is None:
            return
        if punch:
            layer = punch_face(layer, spec)
        if layer.size != CANVAS:
            layer = layer.resize(CANVAS, Image.Resampling.LANCZOS)
        canvas = Image.alpha_composite(canvas, layer.convert("RGBA"))

    add("body", t["body"])
    add("face", t["face"])
    add("eyes", t["eyes"])
    if not (class_id == "sleeping-bag" and t["eyes"] == "sleepy"):
        add("mouths", t["mouth"])
    footwear = t.get("footwear", "none")
    if "boots" in footwear:
        add("footwear", footwear)
    else:
        add("legs", t.get("legs", "short-legs"))
    arm = layer_for(class_id, "arms", t["arm_pose"], lib)
    if arm is not None:
        arm = tint_layer(arm, ARM_TINTS.get((class_id, t["body"])))
        canvas = Image.alpha_composite(canvas, arm.convert("RGBA"))
    add("handheld", t.get("held_item", "none"))
    add("headwear", t.get("headwear", "none"))
    if t.get("atmosphere") not in (None, "none"):
        add("atmosphere", t["atmosphere"], punch=True)
    return canvas


ARM_TINTS = {
    ("sleeping-bag", "navy-night"): (50, 62, 110),
    ("sleeping-bag", "trail-olive"): (86, 108, 58),
    ("small-tent", "camp-orange"): (210, 110, 40),
    ("small-tent", "navy-night"): (50, 62, 110),
    ("large-tent", "forest-green"): (46, 92, 58),
    ("large-tent", "camp-orange"): (210, 110, 40),
    ("large-tent", "navy-night"): (50, 62, 110),
}


def tint_layer(image: Image.Image, color: tuple[int, int, int] | None) -> Image.Image:
    if not color:
        return image
    rgb = image.convert("RGB")
    fill = Image.new("RGB", image.size, color)
    blended = Image.blend(rgb, fill, 0.55)
    out = blended.convert("RGBA")
    out.putalpha(image.getchannel("A"))
    return out


def contact_sheet(images: list[tuple[str, Image.Image]]) -> Image.Image:
    thumb = 280
    cols = 3
    rows = 3
    gutter = 16
    header = 48
    font = ImageFont.load_default()
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
        title_font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22)
    except OSError:
        title_font = font
    w = cols * thumb + (cols + 1) * gutter
    h = header + rows * (thumb + 36) + gutter
    sheet = Image.new("RGB", (w, h), (18, 24, 32))
    draw = ImageDraw.Draw(sheet)
    draw.text((gutter, 12), "Warm Company — 9 layer-reconstructed review samples", fill=(244, 240, 232), font=title_font)
    for i, (title, im) in enumerate(images):
        r, c = divmod(i, cols)
        x = gutter + c * (thumb + gutter)
        y = header + r * (thumb + 36)
        sheet.paste(im.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS), (x, y))
        draw.text((x, y + thumb + 8), title, fill=(220, 226, 232), font=font)
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (LAYERS / "shared" / "atmosphere").mkdir(parents=True, exist_ok=True)
    lib = prepare_library()
    recipes = json.loads((ROOT / "config" / "review_samples.json").read_text(encoding="utf-8"))
    results = []
    for sample in recipes["samples"]:
        print("composite", sample["id"])
        image = composite_sample(sample, lib)
        dest = OUT / f"{sample['id']}.png"
        image.save(dest, "PNG")
        results.append((sample["title"], image))
        print(" wrote", dest)
    sheet = contact_sheet(results)
    sheet.save(OUT / "contact-sheet.png", "PNG")
    print("contact sheet", OUT / "contact-sheet.png")


if __name__ == "__main__":
    main()
