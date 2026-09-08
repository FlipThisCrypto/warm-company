"""Pull a hat off a wearing-shot by differencing against the bare body."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.matte import chroma_key, fringe_report, strip_key_fringe  # noqa: E402

CANVAS = (1024, 1024)

# Do not pick up body-repaint noise below the hat.
Y_MAX = {
    "sleeping-bag": 410,
    "small-tent": 500,
    "large-tent": 430,
}


def _luma_diff(a: Image.Image, b: Image.Image) -> Image.Image:
    """Per-pixel max channel difference as L."""
    a = a.convert("RGB")
    b = b.convert("RGB")
    bands = []
    for ac, bc in zip(a.split(), b.split(), strict=True):
        bands.append(ImageChops.difference(ac, bc))
    return ImageChops.lighter(ImageChops.lighter(bands[0], bands[1]), bands[2])


def extract(wearing_src: Path, body_src: Path, dest: Path, class_id: str, thresh: int = 36) -> None:
    wearing = chroma_key(Image.open(wearing_src), threshold=80)
    wearing = strip_key_fringe(wearing)
    body = Image.open(body_src).convert("RGBA")
    if body.size != CANVAS:
        body = body.resize(CANVAS, Image.Resampling.NEAREST)

    y_max = Y_MAX[class_id]
    clip = Image.new("L", CANVAS, 0)
    clip.paste(Image.new("L", (CANVAS[0], y_max), 255), (0, 0))

    diff = _luma_diff(wearing, body)
    wa = wearing.getchannel("A")
    ba = body.getchannel("A")

    # New silhouette (hat extends past the body) OR recolored body (hat over fabric).
    new_sil = ImageChops.subtract(wa, ba)
    recolor = diff.point(lambda p, t=thresh: 255 if p >= t else 0)
    recolor = ImageChops.multiply(recolor, wa.point(lambda p: 255 if p > 40 else 0))
    mask = ImageChops.lighter(new_sil, recolor)
    mask = ImageChops.multiply(mask, clip)
    mask = mask.filter(ImageFilter.MedianFilter(5))
    mask = mask.filter(ImageFilter.MaxFilter(3))
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))

    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.paste(wearing, (0, 0))
    out.putalpha(ImageChops.multiply(wearing.getchannel("A"), mask))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    out.save(dest)
    box = out.getchannel("A").getbbox()
    w = box[2] - box[0] if box else 0
    h = box[3] - box[1] if box else 0
    print(f"{dest.name} bbox={box} {w}x{h} fringe={fringe_report(out)}")


MAP = [
    ("160.jpg", "sleeping-bag", "knit-cap.png"),
    ("161.jpg", "sleeping-bag", "baseball-cap.png"),
    ("162.jpg", "sleeping-bag", "beanie.png"),
    ("163.jpg", "sleeping-bag", "earflap-beanie.png"),
    ("164.jpg", "sleeping-bag", "santa-hat.png"),
    ("165.jpg", "small-tent", "bucket-hat.png"),
    ("166.jpg", "small-tent", "knit-cap.png"),
    ("168.jpg", "small-tent", "beanie.png"),
    ("167.jpg", "large-tent", "baseball-cap.png"),
    ("169.jpg", "large-tent", "beanie.png"),
    ("170.jpg", "large-tent", "crown.png"),
    ("171.jpg", "large-tent", "halo.png"),
    ("172.jpg", "large-tent", "trapper-hat.png"),
]

CLASS_DIR = {
    "sleeping-bag": ROOT / "layers" / "sleeping-bag" / "headwear",
    "small-tent": ROOT / "layers" / "small-tent" / "headwear",
    "large-tent": ROOT / "layers" / "large-tent" / "headwear",
}

BODY = {
    "sleeping-bag": ROOT / "build" / "headwear-loop" / "bases" / "snug-bare.png",
    "small-tent": ROOT / "build" / "headwear-loop" / "bases" / "pup-bare.png",
    "large-tent": ROOT / "build" / "headwear-loop" / "bases" / "lodge-bare.png",
}


def main() -> None:
    session = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images"
    )
    for src_name, class_id, dest_name in MAP:
        src = session / src_name
        if not src.exists():
            print("MISSING", src)
            continue
        extract(src, BODY[class_id], CLASS_DIR[class_id] / dest_name, class_id)


if __name__ == "__main__":
    main()
