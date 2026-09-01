"""Install v3 canonical hold edits as production pose-master PNGs.

Coffee, map, and lantern grips are full-character Imagine edits. They replace
failed arm crops / clip-art props so the compositor can skip stacked stickers.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "build" / "review-v3" / "layers"
LAYERS = ROOT / "layers"

COPIES = {
    V3 / "snug_coffee.png": LAYERS / "sleeping-bag" / "arms" / "hold-item.png",
    V3 / "pup_map.png": LAYERS / "small-tent" / "arms" / "hold-two-hand.png",
    V3 / "lodge_lantern.png": LAYERS / "large-tent" / "handheld" / "lantern.png",
}


def main() -> None:
    for src, dest in COPIES.items():
        if not src.exists():
            raise SystemExit(f"missing pose master source: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        print("installed", dest.relative_to(ROOT), "from", src.name)


if __name__ == "__main__":
    main()
