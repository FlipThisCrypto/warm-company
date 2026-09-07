"""Chroma-key an Imagine hat onto a 1024 RGBA layer PNG."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.matte import chroma_key, fringe_report, strip_key_fringe  # noqa: E402


def ingest(src: Path, dest: Path) -> None:
    im = chroma_key(Image.open(src), threshold=80)
    im = strip_key_fringe(im)
    alpha = im.getchannel("A").filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.6))
    im.putalpha(alpha)
    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    box = alpha.getbbox()
    rep = fringe_report(im)
    w = box[2] - box[0] if box else 0
    h = box[3] - box[1] if box else 0
    try:
        rel = dest.relative_to(ROOT)
    except ValueError:
        rel = dest
    print(f"{rel} bbox={box} {w}x{h} fringe={rep}")


if __name__ == "__main__":
    ingest(Path(sys.argv[1]), Path(sys.argv[2]))
