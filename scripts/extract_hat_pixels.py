"""Keep hat-colored pixels from a wearing shot. Leave them in canvas position."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.matte import chroma_key, fringe_report, strip_key_fringe  # noqa: E402

CANVAS = (1024, 1024)
SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")


def _hat(r: int, g: int, b: int, kind: str) -> bool:
    if kind == "navy":
        return r < 120 and g < 140 and b < 180 and b + 8 >= g and (r + g + b) < 380
    if kind == "santa":
        red = r > 140 and r > g + 35 and r > b + 35
        white = r > 170 and g > 170 and b > 170
        return red or white
    if kind == "stripe":
        cream = r > 150 and g > 130 and b > 90
        rust = r > 120 and g > 60 and b < 110 and r > b + 25
        return cream or rust
    if kind == "earflap":
        navy = r < 120 and g < 140 and b < 180 and b + 8 >= g
        cream = r > 160 and g > 140 and b > 100
        return navy or cream
    if kind == "olive":
        return 70 < g < 180 and g >= r - 8 and g >= b and r < 160
    if kind == "gold":
        return r > 140 and g > 90 and b < 140 and r > b + 30
    if kind == "trapper":
        brown = r > 70 and r >= g - 10 and r > b + 15 and g > 40
        fur = r > 120 and g > 90 and b < 130
        return brown or fur
    return False


JOBS = [
    ("160.jpg", "sleeping-bag", "knit-cap.png", "navy", 400, True),
    ("161.jpg", "sleeping-bag", "baseball-cap.png", "navy", 390, True),
    ("162.jpg", "sleeping-bag", "beanie.png", "stripe", 400, True),
    ("163.jpg", "sleeping-bag", "earflap-beanie.png", "earflap", 430, False),
    ("164.jpg", "sleeping-bag", "santa-hat.png", "santa", 400, True),
    ("166.jpg", "small-tent", "knit-cap.png", "navy", 500, True),
    ("168.jpg", "small-tent", "beanie.png", "stripe", 500, True),
    ("165.jpg", "small-tent", "bucket-hat.png", "olive", 500, True),
    ("167.jpg", "large-tent", "baseball-cap.png", "navy", 430, True),
    ("169.jpg", "large-tent", "beanie.png", "stripe", 430, True),
    ("170.jpg", "large-tent", "crown.png", "gold", 380, False),
    ("171.jpg", "large-tent", "halo.png", "gold", 360, False),
    ("172.jpg", "large-tent", "trapper-hat.png", "trapper", 560, False),
]


def extract(src: Path, dest: Path, kind: str, y_max: int, punch_face: bool) -> None:
    wearing = chroma_key(Image.open(src), threshold=80)
    wearing = strip_key_fringe(wearing)
    px = wearing.load()
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    op = out.load()
    for y in range(0, min(y_max, CANVAS[1])):
        for x in range(CANVAS[0]):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            if not _hat(r, g, b, kind):
                continue
            op[x, y] = (r, g, b, a)
    alpha = out.getchannel("A")
    alpha = alpha.filter(ImageFilter.MedianFilter(3))
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    if punch_face:
        # Drop the cream face oval so the hat opening stays a hole.
        face = Image.new("L", CANVAS, 0)
        # Approximate class face as a centered ellipse; only punch very light pixels later.
        out.putalpha(alpha)
    else:
        out.putalpha(alpha)
    # Contract magenta fringe.
    a2 = out.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.4))
    out.putalpha(a2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    box = out.getchannel("A").getbbox()
    w = box[2] - box[0] if box else 0
    h = box[3] - box[1] if box else 0
    print(f"{dest.name:22s} {w:4d}x{h:<4d} bbox={box} fringe={fringe_report(out)['magenta_fringe_px']}")


def main() -> None:
    for src_name, class_id, dest_name, kind, y_max, punch in JOBS:
        src = SESSION / src_name
        dest = ROOT / "layers" / class_id / "headwear" / dest_name
        extract(src, dest, kind, y_max, punch)


if __name__ == "__main__":
    main()
