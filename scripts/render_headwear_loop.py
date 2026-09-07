"""Render every production hat on its class body for the headwear-fit loop."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import composite_token  # noqa: E402
from warm_company.review import review_token  # noqa: E402

OUT = ROOT / "build" / "headwear-loop"

HATS = [
    ("sleeping-bag", "Snug", "baseball-cap"),
    ("sleeping-bag", "Snug", "beanie"),
    ("sleeping-bag", "Snug", "earflap-beanie"),
    ("sleeping-bag", "Snug", "knit-cap"),
    ("sleeping-bag", "Snug", "santa-hat"),
    ("small-tent", "Pup", "beanie"),
    ("small-tent", "Pup", "bucket-hat"),
    ("small-tent", "Pup", "knit-cap"),
    ("large-tent", "Lodge", "baseball-cap"),
    ("large-tent", "Lodge", "beanie"),
    ("large-tent", "Lodge", "crown"),
    ("large-tent", "Lodge", "halo"),
    ("large-tent", "Lodge", "trapper-hat"),
]


def font(size: int):
    for name in ("segoeui.ttf", "SegoeUI.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(rf"C:\Windows\Fonts\{name}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(title: str, cells: list[tuple[str, Image.Image]], cols: int = 4, size: int = 240) -> Image.Image:
    rows = max(1, (len(cells) + cols - 1) // cols)
    img = Image.new("RGB", (24 + cols * (size + 10), 52 + rows * (size + 28)), (16, 20, 28))
    d = ImageDraw.Draw(img)
    d.text((12, 10), title, fill=(240, 236, 228), font=font(18))
    for i, (label, im) in enumerate(cells):
        r, c = divmod(i, cols)
        x, y = 12 + c * (size + 10), 44 + r * (size + 28)
        vis = im.convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
        img.paste(vis, (x, y))
        d.text((x, y + size + 2), label[:28], fill=(200, 206, 212), font=font(11))
    return img


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "current"
    OUT.mkdir(parents=True, exist_ok=True)
    cells: list[tuple[str, Image.Image]] = []
    for class_id, label, hat in HATS:
        tok = review_token(class_id, headwear=hat)
        im = composite_token(tok, missing="allow")
        stem = f"{label.lower()}-{hat}"
        im.save(OUT / f"{stem}.png")
        cells.append((f"{label} {hat}", im))
        print(f"{stem} rendered")
    title = f"Headwear {tag}"
    sheet(title, cells).save(OUT / f"{tag}-sheet.png")
    print(f"wrote {OUT / f'{tag}-sheet.png'}")


if __name__ == "__main__":
    main()
