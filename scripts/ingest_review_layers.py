"""Chroma-key Imagine outputs into 1024 RGBA layer files."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.matte import chroma_key  # noqa: E402

SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")
LAYERS = ROOT / "layers"

# src jpg -> dest relative to layers/
MAP = {
    "15.jpg": "sleeping-bag/body/ember-rust.png",
    "17.jpg": "small-tent/body/forest-green.png",
    "16.jpg": "large-tent/body/royal-blue.png",
    "21.jpg": "sleeping-bag/face/standard-face.png",
    "19.jpg": "small-tent/face/standard-face.png",
    "20.jpg": "large-tent/face/standard-face.png",
    "22.jpg": "sleeping-bag/eyes/sleepy.png",
    "23.jpg": "small-tent/eyes/happy.png",
    "24.jpg": "large-tent/eyes/happy.png",
    "25.jpg": "sleeping-bag/arms/rest.png",
    "26.jpg": "small-tent/arms/rest.png",
    "27.jpg": "large-tent/arms/rest.png",
    "28.jpg": "sleeping-bag/legs/short-legs.png",
    "29.jpg": "small-tent/legs/short-legs.png",
    "31.jpg": "large-tent/legs/short-legs.png",
    "32.jpg": "sleeping-bag/mouths/smile.png",
    "30.jpg": "small-tent/mouths/smile.png",
}


def ingest(src_name: str, dest_rel: str) -> Path:
    src = SESSION / src_name
    dest = LAYERS / dest_rel
    image = chroma_key(Image.open(src))
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, "PNG")
    bbox = image.getchannel("A").getbbox()
    print(f"{dest_rel}  bbox={bbox}")
    return dest


if __name__ == "__main__":
    for src_name, dest_rel in MAP.items():
        if (SESSION / src_name).exists():
            ingest(src_name, dest_rel)
