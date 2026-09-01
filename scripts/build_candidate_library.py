"""Build the candidate production layer library and import illustrated backgrounds."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.library import build_all, save_png  # noqa: E402
from warm_company.paths import LAYERS  # noqa: E402

SESSION = Path(r"C:\Users\richa\.grok\sessions\R%3A%5C\01a05d66-64a7-7ee3-a89c-377f340855c5\images")

# image_gen order from this session
BACKGROUNDS = {
    "campground": "118.jpg",
    "appalachian-ridge": "119.jpg",
    "warm-dawn": "120.jpg",
    "starry-night": "121.jpg",
    "winter-sunset": "122.jpg",
    "abstract-snow": "123.jpg",
    "light-snowfall-scene": "124.jpg",
    "underpass-quiet": "125.jpg",
    "first-light": "126.jpg",
    "city-edge": "127.jpg",
}


def import_backgrounds() -> None:
    dest_dir = LAYERS / "shared" / "backgrounds"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for trait_id, name in BACKGROUNDS.items():
        src = SESSION / name
        if not src.exists():
            print("missing illustrated bg", name)
            continue
        im = Image.open(src).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
        opaque = im.convert("RGBA")
        opaque.putalpha(255)
        save_png(opaque, dest_dir / f"{trait_id}.png")
        print("bg", trait_id)


def main() -> None:
    import_backgrounds()
    summary = build_all(overwrite=False)
    print(summary)


if __name__ == "__main__":
    main()
