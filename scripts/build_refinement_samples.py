"""Updated 12-sample refinement gate + reconstruction strips via production compositor."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.composite import composite_token  # noqa: E402
from warm_company.review import STRIP_TOKENS, reconstruction_strip, review_token  # noqa: E402

OUT = ROOT / "build" / "review-v3"
CANVAS = (1024, 1024)

SAMPLES = [
    ("snug-01-bare", "Snug — Bare rest", "sleeping-bag", {
        "background": "winter-sunrise",
    }),
    ("snug-02-hat", "Snug — Tiny beanie", "sleeping-bag", {
        "background": "snowy-camp",
        "headwear": "beanie",
    }),
    ("snug-03-coffee", "Snug — Coffee grip", "sleeping-bag", {
        "background": "winter-sunrise",
        "arm_pose": "hold-item",
        "held_item": "coffee",
        "eyes": "happy",
        "mouth": "smile",
        "facial": "blush",
    }),
    ("snug-04-night", "Snug — Night snow", "sleeping-bag", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "headwear": "beanie",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "eyebrows": "determined",
        "mouth": "determined",
    }),
    ("pup-01-bare", "Pup — Bare rest", "small-tent", {
        "background": "forest-clearing",
        "body": "forest-green",
    }),
    ("pup-02-hat", "Pup — Peak beanie", "small-tent", {
        "background": "winter-sunrise",
        "body": "forest-green",
        "headwear": "beanie",
    }),
    ("pup-03-map", "Pup — Two-hand map", "small-tent", {
        "background": "snowy-camp",
        "body": "forest-green",
        "arm_pose": "hold-two-hand",
        "held_item": "map",
        "eyes": "happy",
        "mouth": "smile",
    }),
    ("pup-04-night", "Pup — Night snow", "small-tent", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "headwear": "beanie",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "eyebrows": "determined",
        "mouth": "determined",
    }),
    ("lodge-01-bare", "Lodge — D-door rest", "large-tent", {
        "background": "snowy-camp",
        "body": "royal-blue",
    }),
    ("lodge-02-hat", "Lodge — Peak beanie", "large-tent", {
        "background": "winter-sunrise",
        "body": "camp-orange",
        "headwear": "beanie",
    }),
    ("lodge-03-lantern", "Lodge — Lantern grip", "large-tent", {
        "background": "forest-clearing",
        "body": "royal-blue",
        "arm_pose": "hold-item",
        "held_item": "lantern",
    }),
    ("lodge-04-night", "Lodge — Night snow", "large-tent", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "eyebrows": "determined",
        "mouth": "determined",
    }),
]


def font(size: int):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def contact(rows: list[tuple[str, Image.Image]]) -> Image.Image:
    thumb = 240
    mini = 128
    cols = 4
    w = cols * thumb + 5 * 12
    h = 56 + 3 * (thumb + 32) + 24 + mini + 28
    sheet = Image.new("RGB", (w, h), (16, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.text((12, 12), "Warm Company — refinement pass (12 samples, production compositor)", fill=(244, 240, 232), font=font(18))
    for i, (title, im) in enumerate(rows):
        r, c = divmod(i, cols)
        x = 12 + c * (thumb + 12)
        y = 48 + r * (thumb + 32)
        sheet.paste(im.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS), (x, y))
        d.text((x, y + thumb + 6), title, fill=(220, 226, 232), font=font(14))
    y = 48 + 3 * (thumb + 32) + 4
    d.text((12, y), "128 px readability check", fill=(180, 186, 196), font=font(12))
    y += 18
    x = 12
    for _, im in rows:
        sheet.paste(im.convert("RGB").resize((mini, mini), Image.Resampling.LANCZOS), (x, y))
        x += mini + 8
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, Image.Image]] = []
    for sample_id, title, class_id, extra in SAMPLES:
        token = review_token(class_id, **extra)
        image = composite_token(token, missing="allow")
        if image.size != CANVAS:
            raise SystemExit(f"{sample_id} is {image.size}, expected {CANVAS}")
        dest = OUT / f"{sample_id}.png"
        image.save(dest, "PNG")
        rows.append((title, image))
        print("wrote", dest)
    contact(rows).save(OUT / "contact-sheet.png", "PNG")
    print("sheet", OUT / "contact-sheet.png")
    reconstruction_strip("Snug reconstruction", STRIP_TOKENS["snug"]).save(OUT / "strip-snug.png", "PNG")
    reconstruction_strip("Pup reconstruction", STRIP_TOKENS["pup"]).save(OUT / "strip-pup.png", "PNG")
    reconstruction_strip("Lodge reconstruction", STRIP_TOKENS["lodge"]).save(OUT / "strip-lodge.png", "PNG")
    print("strips", OUT / "strip-snug.png")


if __name__ == "__main__":
    main()
