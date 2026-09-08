"""Chroma-key an isolated hat and park it on the wearing-shot bbox."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.matte import chroma_key, fringe_report, strip_key_fringe  # noqa: E402

CANVAS = (1024, 1024)
SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")


def place(src: Path, dest: Path, box: tuple[int, int, int, int]) -> None:
    hat = chroma_key(Image.open(src), threshold=80)
    hat = strip_key_fringe(hat)
    a = hat.getchannel("A")
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.5))
    hat.putalpha(a)
    hb = hat.getchannel("A").getbbox()
    if not hb:
        raise SystemExit(f"empty hat {src}")
    crop = hat.crop(hb)
    x0, y0, x1, y1 = box
    tw, th = max(8, x1 - x0), max(8, y1 - y0)
    crop = crop.resize((tw, th), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.paste(crop, (x0, y0), crop)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)
    bb = canvas.getchannel("A").getbbox()
    print(f"{dest.name} placed {tw}x{th} at {box} out={bb} fringe={fringe_report(canvas)['magenta_fringe_px']}")


# Isolated extract -> dest, wearing-shot bbox (where the hat sat on the character)
JOBS = [
    ("177.jpg", "sleeping-bag/headwear/beanie.png", (276, 12, 748, 392)),
    ("180.jpg", "small-tent/headwear/beanie.png", (250, 48, 774, 420)),
    ("179.jpg", "small-tent/headwear/bucket-hat.png", (190, 110, 834, 400)),
    ("181.jpg", "large-tent/headwear/beanie.png", (250, 40, 774, 400)),
]


def main() -> None:
    for src_name, rel, box in JOBS:
        place(SESSION / src_name, ROOT / "layers" / rel, box)


if __name__ == "__main__":
    main()
