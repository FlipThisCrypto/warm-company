"""Composite a small production-path preview using composite_token."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.composite import composite_token  # noqa: E402

OUT = ROOT / "build" / "preview"
CANVAS = (1024, 1024)


def token(class_id: str, **traits: str) -> dict:
    base = {
        "background": "winter-sunrise",
        "rear_environment": "none",
        "rear_accessory": "none",
        "arm_pose": "rest",
        "held_item": "none",
        "body": "ember-rust",
        "pattern": "none",
        "structural": "basic-baffles",
        "legs": "short-legs",
        "footwear": "basic-shoes",
        "face": "standard-face",
        "eyes": "normal",
        "eyebrows": "none",
        "mouth": "smile",
        "facial": "none",
        "body_accessory": "none",
        "headwear": "none",
        "ground_accessory": "none",
        "atmosphere": "none",
        "special": "none",
    }
    if class_id == "small-tent":
        base["body"] = "forest-green"
    if class_id == "large-tent":
        base["body"] = "royal-blue"
    base.update(traits)
    return {"class_id": class_id, "traits": base, "token_id": 0}


SAMPLES = [
    ("snug-bare", "sleeping-bag", {}),
    ("snug-hat", "sleeping-bag", {"headwear": "beanie"}),
    ("snug-night", "sleeping-bag", {"body": "navy-night", "background": "cold-blue-night", "atmosphere": "light-snow", "headwear": "beanie"}),
    ("pup-bare", "small-tent", {}),
    ("pup-hat", "small-tent", {"headwear": "beanie"}),
    ("pup-map", "small-tent", {"held_item": "map", "arm_pose": "hold-two-hand"}),
    ("lodge-bare", "large-tent", {}),
    ("lodge-hat", "large-tent", {"headwear": "beanie", "body": "camp-orange"}),
    ("lodge-lantern", "large-tent", {"held_item": "lantern", "arm_pose": "hold-item"}),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for name, class_id, extra in SAMPLES:
        im = composite_token(token(class_id, **extra), missing="allow")
        path = OUT / f"{name}.png"
        im.save(path, "PNG")
        thumbs.append((name, im))
        print("wrote", path)
    cols = 3
    tw = 240
    sheet = Image.new("RGB", (12 + cols * (tw + 12), 48 + 3 * (tw + 28)), (16, 20, 28))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    d.text((12, 10), "Warm Company — compositor preview", fill=(240, 236, 228), font=font)
    for i, (name, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x, y = 12 + c * (tw + 12), 40 + r * (tw + 28)
        sheet.paste(im.convert("RGB").resize((tw, tw), Image.Resampling.LANCZOS), (x, y))
        d.text((x, y + tw + 4), name, fill=(200, 206, 212), font=font)
    sheet.save(OUT / "sheet.png", "PNG")
    print("sheet", OUT / "sheet.png")


if __name__ == "__main__":
    main()
