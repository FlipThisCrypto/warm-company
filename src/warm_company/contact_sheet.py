from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import config
from .paths import BUILD, ROOT, ensure_build

THUMB = 192
GUTTER = 12
LABEL_H = 36
COLS = 10


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _class_color(class_id: str) -> tuple[int, int, int]:
    return {
        "sleeping-bag": (196, 92, 38),
        "small-tent": (47, 107, 79),
        "large-tent": (44, 95, 138),
    }[class_id]


def schematic_thumb(token: dict, size: int = THUMB) -> Image.Image:
    """Readable stand-in used before production layers exist."""
    image = Image.new("RGB", (size, size), (236, 241, 245))
    draw = ImageDraw.Draw(image)
    color = _class_color(token["class_id"])
    spec = config.class_spec(token["class_id"])
    bbox = spec["bounding_box"]
    scale = size / 1024
    box = [
        bbox["x"] * scale,
        bbox["y"] * scale,
        (bbox["x"] + bbox["w"]) * scale,
        (bbox["y"] + bbox["h"]) * scale,
    ]
    draw.rounded_rectangle(box, radius=12, fill=color)
    face = spec["face_center"]
    fr = 14
    draw.ellipse(
        [face["x"] * scale - fr, face["y"] * scale - fr, face["x"] * scale + fr, face["y"] * scale + fr],
        fill=(255, 248, 240),
    )
    if token.get("special"):
        draw.rectangle([4, 4, size - 5, size - 5], outline=(212, 175, 55), width=3)
    return image


def _cell_image(token: dict) -> Image.Image:
    png = BUILD / "images" / f"{token['token_id']:04d}.png"
    if png.exists():
        return Image.open(png).convert("RGB").resize((THUMB, THUMB), Image.Resampling.LANCZOS)
    return schematic_thumb(token)


def render_sheet(tokens: list[dict], title: str, dest: Path) -> Path:
    ensure_build()
    cols = min(COLS, max(1, len(tokens)))
    rows = (len(tokens) + cols - 1) // cols
    header = 48
    width = cols * THUMB + (cols + 1) * GUTTER
    height = header + rows * (THUMB + LABEL_H + GUTTER) + GUTTER
    sheet = Image.new("RGB", (width, height), (18, 24, 32))
    draw = ImageDraw.Draw(sheet)
    title_font = _font(22)
    label_font = _font(12)
    draw.text((GUTTER, 12), title, fill=(244, 240, 232), font=title_font)
    for index, token in enumerate(tokens):
        r, c = divmod(index, cols)
        x = GUTTER + c * (THUMB + GUTTER)
        y = header + r * (THUMB + LABEL_H + GUTTER)
        sheet.paste(_cell_image(token), (x, y))
        label = f"#{token['token_id']:04d} {config.class_spec(token['class_id'])['family_name']}"
        if token.get("special"):
            label += " ★"
        draw.text((x, y + THUMB + 8), label, fill=(220, 226, 232), font=label_font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "PNG")
    return dest


def render_all(result: dict) -> list[Path]:
    tokens = result["tokens"]
    out = BUILD / "contact-sheets"
    paths = [
        render_sheet(tokens, "Warm Company — entire collection", out / "all.png"),
        render_sheet(
            [t for t in tokens if t["class_id"] == "sleeping-bag"],
            "Warm Company — Snugs (Sleeping Bags)",
            out / "sleeping-bag.png",
        ),
        render_sheet(
            [t for t in tokens if t["class_id"] == "small-tent"],
            "Warm Company — Pups (3-Person Tents)",
            out / "small-tent.png",
        ),
        render_sheet(
            [t for t in tokens if t["class_id"] == "large-tent"],
            "Warm Company — Lodges (6-Person Tents)",
            out / "large-tent.png",
        ),
        render_sheet(
            [t for t in tokens if t.get("special")],
            "Warm Company — coordinated specials",
            out / "specials.png",
        ),
    ]
    return paths
