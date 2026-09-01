"""Candidate production-layer factory.

Recolors locked canonical body isolations, draws expression/structure/gear
at published anchors, and fills missing PNGs so config and disk reconcile.
Does not invent per-asset coordinates.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance

from . import config
from .paths import LAYERS, ROOT

CANVAS = (1024, 1024)
UMBER = (58, 42, 34)
CREAM = (245, 228, 200)

BODY_COLORS: dict[str, tuple[int, int, int]] = {
    "trail-olive": (92, 110, 62),
    "ember-rust": (176, 92, 48),
    "navy-night": (42, 62, 110),
    "camp-orange": (214, 118, 48),
    "burgundy-quilt": (128, 42, 58),
    "mustard-seed": (196, 148, 52),
    "cream-fleece": (232, 214, 186),
    "sky-flannel": (110, 156, 196),
    "plum-preserve": (110, 58, 92),
    "storm-charcoal": (72, 76, 82),
    "forest-green": (52, 112, 68),
    "royal-blue": (48, 78, 156),
    "sand-tan": (196, 162, 112),
    "camp-red": (168, 48, 48),
    "granite-gray": (120, 124, 128),
    "alpine-teal": (42, 128, 132),
    "wild-purple": (112, 72, 148),
    "sun-yellow": (228, 186, 52),
    "dusty-rose": (201, 92, 118),
    "aurora": (72, 148, 132),
    "north-star-navy": (28, 42, 88),
}

MASTERS = {
    "sleeping-bag": LAYERS / "sleeping-bag" / "body" / "ember-rust.png",
    "small-tent": LAYERS / "small-tent" / "body" / "forest-green.png",
    "large-tent": LAYERS / "large-tent" / "body" / "royal-blue.png",
}

ARM_MASTERS = {
    "sleeping-bag": LAYERS / "sleeping-bag" / "arms-rear" / "rest.png",
    "small-tent": LAYERS / "small-tent" / "arms-rear" / "rest.png",
    "large-tent": LAYERS / "large-tent" / "arms-rear" / "rest.png",
}

LEG_MASTERS = {
    "sleeping-bag": LAYERS / "sleeping-bag" / "legs-rear" / "short-legs.png",
    "small-tent": LAYERS / "small-tent" / "legs-rear" / "short-legs.png",
    "large-tent": LAYERS / "large-tent" / "legs-rear" / "short-legs.png",
}


def empty() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def save_png(im: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGBA").save(path, "PNG")
    return path


def fabric_mask(im: Image.Image) -> Image.Image:
    """Opaque non-cream, non-outline pixels (the cloth)."""
    im = im.convert("RGBA")
    try:
        import numpy as np
        arr = np.array(im)
        r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
        luma = (r.astype(np.uint16) + g + b) / 3
        sat = np.maximum(np.maximum(r, g), b).astype(np.int16) - np.minimum(np.minimum(r, g), b)
        keep = (a >= 40) & (luma >= 48) & ~((luma > 210) & (sat < 28))
        m = np.where(keep, a, 0).astype(np.uint8)
        return Image.fromarray(m, "L")
    except ImportError:
        px = im.load()
        mask = Image.new("L", im.size, 0)
        mp = mask.load()
        box = im.getchannel("A").getbbox() or (0, 0, 1024, 1024)
        for y in range(box[1], box[3]):
            for x in range(box[0], box[2]):
                r, g, b, a = px[x, y]
                if a < 40:
                    continue
                luma = (r + g + b) / 3
                sat = max(r, g, b) - min(r, g, b)
                if luma < 48:
                    continue
                if luma > 210 and sat < 28:
                    continue
                mp[x, y] = a
        return mask


def recolor_fabric(im: Image.Image, target: tuple[int, int, int], strength: float = 0.82) -> Image.Image:
    im = im.convert("RGBA")
    mask = fabric_mask(im)
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None:
        arr = np.array(im)
        m = np.array(mask)
        fabric = m > 20
        if not fabric.any():
            return im
        strong = m > 180
        src = arr[strong][:, :3].mean(axis=0) if strong.any() else arr[fabric][:, :3].mean(axis=0)
        delta = (np.array(target, dtype=np.float32) - src.astype(np.float32)) * strength
        t = (m[fabric].astype(np.float32) / 255.0)[:, None]
        rgb = arr[fabric][:, :3].astype(np.float32) + delta * t
        arr[fabric, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        return Image.fromarray(arr, "RGBA")
    samples: list[tuple[int, int, int]] = []
    px = im.load()
    mp = mask.load()
    box = mask.getbbox() or (0, 0, 1024, 1024)
    for y in range(box[1], box[3], 6):
        for x in range(box[0], box[2], 6):
            if mp[x, y] > 180:
                samples.append(px[x, y][:3])
    if not samples:
        return im
    n = len(samples) // 2
    src = (
        sorted(s[0] for s in samples)[n],
        sorted(s[1] for s in samples)[n],
        sorted(s[2] for s in samples)[n],
    )
    dr, dg, db = target[0] - src[0], target[1] - src[1], target[2] - src[2]
    out = im.copy()
    op = out.load()
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            m = mp[x, y]
            if m < 20:
                continue
            r, g, b, a = op[x, y]
            t = strength * (m / 255)
            op[x, y] = (
                max(0, min(255, int(r + dr * t))),
                max(0, min(255, int(g + dg * t))),
                max(0, min(255, int(b + db * t))),
                a,
            )
    return out


def two_tone(im: Image.Image, top: tuple[int, int, int], bot: tuple[int, int, int], split_y: int) -> Image.Image:
    a = recolor_fabric(im, top)
    b = recolor_fabric(im, bot)
    mask = Image.new("L", CANVAS, 0)
    ImageDraw.Draw(mask).rectangle([0, split_y, 1024, 1024], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    return Image.composite(b, a, mask)


def grain(im: Image.Image, amount: int = 8) -> Image.Image:
    rng = random.Random(7)
    noise = Image.new("L", im.size, 0)
    n = noise.load()
    for y in range(0, 1024, 2):
        for x in range(0, 1024, 2):
            v = rng.randint(0, amount)
            n[x, y] = v
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    overlay = Image.merge("RGBA", (noise, noise, noise, noise.point(lambda p: min(40, p * 3))))
    return Image.alpha_composite(im.convert("RGBA"), overlay)


def paint_eyes(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    lx, ly = spec["eye_left"]["x"], spec["eye_left"]["y"]
    rx, ry = spec["eye_right"]["x"], spec["eye_right"]["y"]
    w, h = spec["eye_size"]["w"], spec["eye_size"]["h"]
    umber = UMBER

    def pair(fn):
        fn(lx, ly)
        fn(rx, ry)

    if kind in {"normal", "happy"}:
        if kind == "happy" or class_id == "sleeping-bag" and kind == "normal":
            def closed(x, y):
                d.arc([x - 22, y - 14, x + 22, y + 18], 200, 340, fill=umber, width=6)
            if kind == "happy" or class_id == "sleeping-bag":
                pair(closed)
                if kind == "normal" and class_id != "sleeping-bag":
                    pass
            if kind == "happy":
                return im
            if class_id == "sleeping-bag":
                return im
        def open_eye(x, y):
            d.ellipse([x - w // 2, y - h // 2, x + w // 2, y + h // 2], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.ellipse([x - 10, y - 10, x + 10, y + 12], fill=(62, 42, 28, 255))
            d.ellipse([x - 4, y - 8, x + 2, y - 2], fill=(250, 248, 240, 255))
        pair(open_eye)
        return im
    if kind == "sleepy":
        def sl(x, y):
            d.arc([x - 22, y - 6, x + 22, y + 16], 200, 340, fill=umber, width=5)
            d.line([x - 18, y + 2, x + 18, y + 6], fill=umber, width=3)
        pair(sl)
        return im
    if kind == "determined":
        def det(x, y):
            d.ellipse([x - 18, y - 12, x + 18, y + 16], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.ellipse([x - 8, y - 6, x + 8, y + 10], fill=(40, 28, 20, 255))
            d.line([x - 24, y - 16, x + 20, y - 8], fill=umber, width=5)
        pair(det)
        return im
    if kind == "surprised":
        def sur(x, y):
            d.ellipse([x - 16, y - 20, x + 16, y + 16], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.ellipse([x - 7, y - 8, x + 7, y + 8], fill=(40, 28, 20, 255))
        pair(sur)
        return im
    if kind == "worried":
        def wor(x, y, flip=1):
            d.ellipse([x - 16, y - 12, x + 16, y + 14], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.ellipse([x - 7, y - 4, x + 7, y + 10], fill=(40, 28, 20, 255))
            d.arc([x - 20, y - 28, x + 16, y - 4], 200 if flip > 0 else 0, 330 if flip > 0 else 160, fill=umber, width=4)
        wor(lx, ly, 1)
        wor(rx, ry, -1)
        return im
    if kind == "squint":
        def sq(x, y):
            d.line([x - 20, y, x + 20, y], fill=umber, width=6)
            d.line([x - 16, y + 6, x + 16, y + 4], fill=umber, width=3)
        pair(sq)
        return im
    if kind == "side-eye":
        def se(x, y):
            d.ellipse([x - 18, y - 12, x + 18, y + 14], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.ellipse([x + 2, y - 6, x + 14, y + 8], fill=(40, 28, 20, 255))
        pair(se)
        return im
    if kind == "starry":
        def st(x, y):
            d.ellipse([x - 16, y - 14, x + 16, y + 14], outline=umber, width=4, fill=(250, 246, 238, 255))
            d.polygon([(x, y - 10), (x + 3, y - 2), (x + 10, y - 2), (x + 4, y + 2), (x + 6, y + 10), (x, y + 5), (x - 6, y + 10), (x - 4, y + 2), (x - 10, y - 2), (x - 3, y - 2)], fill=(196, 148, 48, 255), outline=umber)
        pair(st)
        return im
    if kind == "heart":
        def hv(x, y):
            d.ellipse([x - 10, y - 8, x, y + 4], fill=(176, 48, 72, 255), outline=umber)
            d.ellipse([x, y - 8, x + 10, y + 4], fill=(176, 48, 72, 255), outline=umber)
            d.polygon([(x - 12, y), (x + 12, y), (x, y + 14)], fill=(176, 48, 72, 255), outline=umber)
        pair(hv)
        return im
    if kind == "sunglasses-compatible":
        def sg(x, y):
            d.ellipse([x - 14, y - 8, x + 14, y + 10], fill=(30, 32, 36, 40))
        pair(sg)
        return im
    return paint_eyes(class_id, "normal")


def paint_brows(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    y = spec["brow_baseline_y"]
    lx, rx = spec["eye_left"]["x"], spec["eye_right"]["x"]
    def brow(x, tilt=0, arch=0):
        d.line([x - 18, y + tilt, x + 18, y + tilt + arch], fill=UMBER, width=5)
    if kind == "neutral":
        brow(lx, 0, 0)
        brow(rx, 0, 0)
    elif kind == "raised":
        brow(lx, -8, -4)
        brow(rx, -8, -4)
    elif kind == "concerned":
        brow(lx, 2, 8)
        brow(rx, 2, -8)
    elif kind == "mischievous":
        brow(lx, -2, 6)
        brow(rx, -10, -2)
    elif kind == "determined":
        brow(lx, 4, 6)
        brow(rx, 4, -6)
    else:
        brow(lx)
        brow(rx)
    return im


def paint_mouth(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    x, y = spec["mouth_center"]["x"], spec["mouth_center"]["y"]
    if kind == "smile":
        d.arc([x - 28, y - 18, x + 28, y + 22], 20, 160, fill=UMBER, width=5)
    elif kind == "grin":
        d.arc([x - 32, y - 16, x + 32, y + 28], 15, 165, fill=UMBER, width=6)
        d.arc([x - 20, y - 4, x + 20, y + 16], 20, 160, fill=(250, 240, 230, 255), width=3)
    elif kind == "open-laugh":
        d.ellipse([x - 16, y - 4, x + 16, y + 22], outline=UMBER, width=4, fill=(40, 24, 24, 255))
        d.arc([x - 10, y + 4, x + 10, y + 16], 20, 160, fill=(180, 80, 90, 255), width=3)
    elif kind == "smirk":
        d.arc([x - 8, y - 10, x + 28, y + 16], 20, 140, fill=UMBER, width=5)
    elif kind == "surprised":
        d.ellipse([x - 10, y - 6, x + 10, y + 16], outline=UMBER, width=4, fill=(40, 24, 24, 255))
    elif kind == "teeth":
        d.arc([x - 26, y - 12, x + 26, y + 20], 20, 160, fill=UMBER, width=5)
        d.rectangle([x - 14, y, x + 14, y + 8], fill=(250, 246, 238, 255), outline=UMBER)
    elif kind == "tongue":
        d.arc([x - 22, y - 10, x + 22, y + 18], 20, 160, fill=UMBER, width=5)
        d.ellipse([x - 8, y + 4, x + 8, y + 20], fill=(196, 88, 100, 255), outline=UMBER)
    elif kind == "chatter":
        d.line([(x - 16, y), (x - 8, y + 6), (x, y), (x + 8, y + 6), (x + 16, y)], fill=UMBER, width=4)
    elif kind == "determined":
        d.line([x - 18, y + 4, x + 18, y + 4], fill=UMBER, width=5)
    elif kind == "small-o":
        d.ellipse([x - 8, y - 2, x + 8, y + 14], outline=UMBER, width=4)
    else:
        d.arc([x - 28, y - 18, x + 28, y + 22], 20, 160, fill=UMBER, width=5)
    return im


def paint_facial(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    door = spec.get("face_door") or spec["face_oval"]
    cx, cy = spec["face_center"]["x"], spec["face_center"]["y"]
    if kind == "blush":
        d.ellipse([cx - 70, cy + 10, cx - 40, cy + 34], fill=(220, 120, 130, 90))
        d.ellipse([cx + 40, cy + 10, cx + 70, cy + 34], fill=(220, 120, 130, 90))
    elif kind == "freckles":
        rng = random.Random(3)
        for _ in range(14):
            x = rng.randint(door["x"] + 20, door["x"] + door["w"] - 20)
            y = rng.randint(door["y"] + 40, door["y"] + min(140, door["h"] - 20))
            d.ellipse([x, y, x + 3, y + 3], fill=(140, 82, 60, 180))
    elif kind == "snow-kissed":
        rng = random.Random(5)
        for _ in range(10):
            x = rng.randint(door["x"], door["x"] + door["w"])
            y = rng.randint(door["y"], door["y"] + 80)
            d.ellipse([x, y, x + 4, y + 4], fill=(250, 250, 255, 180))
    elif kind == "glasses":
        lx, rx = spec["eye_left"]["x"], spec["eye_right"]["x"]
        y = spec["eye_baseline_y"]
        d.ellipse([lx - 22, y - 16, lx + 22, y + 18], outline=UMBER, width=4)
        d.ellipse([rx - 22, y - 16, rx + 22, y + 18], outline=UMBER, width=4)
        d.line([lx + 22, y, rx - 22, y], fill=UMBER, width=3)
    elif kind == "sunglasses":
        lx, rx = spec["eye_left"]["x"], spec["eye_right"]["x"]
        y = spec["eye_baseline_y"]
        d.ellipse([lx - 24, y - 14, lx + 24, y + 16], fill=(30, 28, 32, 230), outline=UMBER)
        d.ellipse([rx - 24, y - 14, rx + 24, y + 16], fill=(30, 28, 32, 230), outline=UMBER)
        d.line([lx + 24, y, rx - 24, y], fill=UMBER, width=4)
    elif kind == "mustache":
        x, y = spec["mouth_center"]["x"], spec["mouth_center"]["y"] - 10
        d.arc([x - 28, y - 8, x - 2, y + 12], 20, 180, fill=UMBER, width=5)
        d.arc([x + 2, y - 8, x + 28, y + 12], 0, 160, fill=UMBER, width=5)
    return im


def paint_pattern(class_id: str, kind: str, body: Image.Image) -> Image.Image:
    im = empty()
    if kind in {"none", "solid"}:
        return im
    mask = fabric_mask(body)
    d = ImageDraw.Draw(im)
    box = mask.getbbox() or (200, 200, 800, 800)
    rng = random.Random(hash(kind) & 255)
    if kind == "horizontal-quilt":
        for y in range(box[1] + 20, box[3] - 20, 36):
            d.line([box[0], y, box[2], y], fill=(*UMBER, 90), width=2)
    elif kind == "vertical-quilt":
        for x in range(box[0] + 20, box[2] - 20, 36):
            d.line([x, box[1], x, box[3]], fill=(*UMBER, 90), width=2)
    elif kind == "plaid":
        for y in range(box[1], box[3], 28):
            d.line([box[0], y, box[2], y], fill=(40, 40, 80, 70), width=6)
        for x in range(box[0], box[2], 28):
            d.line([x, box[1], x, box[3]], fill=(80, 40, 40, 70), width=6)
    elif kind == "stars":
        for _ in range(18):
            x = rng.randint(box[0] + 30, box[2] - 30)
            y = rng.randint(box[1] + 40, box[3] - 40)
            d.polygon([(x, y - 8), (x + 3, y - 2), (x + 8, y - 2), (x + 4, y + 2), (x + 5, y + 8), (x, y + 4), (x - 5, y + 8), (x - 4, y + 2), (x - 8, y - 2), (x - 3, y - 2)], fill=(220, 200, 120, 140), outline=UMBER)
    elif kind == "moons":
        for _ in range(10):
            x = rng.randint(box[0] + 40, box[2] - 40)
            y = rng.randint(box[1] + 40, box[3] - 40)
            d.ellipse([x, y, x + 18, y + 18], fill=(230, 220, 180, 130), outline=UMBER)
            d.ellipse([x + 6, y - 2, x + 22, y + 14], fill=(0, 0, 0, 0))
    elif kind == "patchwork":
        for _ in range(9):
            x = rng.randint(box[0] + 20, box[2] - 80)
            y = rng.randint(box[1] + 40, box[3] - 80)
            d.rectangle([x, y, x + 48, y + 40], outline=UMBER, width=2)
            d.line([x + 6, y + 6, x + 14, y + 14], fill=UMBER, width=2)
    elif kind == "camo-soft":
        for _ in range(22):
            x = rng.randint(box[0], box[2])
            y = rng.randint(box[1], box[3])
            col = rng.choice([(70, 90, 50, 80), (90, 80, 50, 80), (50, 70, 50, 80)])
            d.ellipse([x, y, x + rng.randint(20, 50), y + rng.randint(14, 36)], fill=col)
    elif kind == "geometric-trail":
        for y in range(box[1] + 30, box[3] - 30, 48):
            for x in range(box[0] + 30, box[2] - 30, 48):
                d.polygon([(x, y), (x + 16, y + 8), (x, y + 16)], outline=UMBER)
    elif kind == "panels":
        d.line([(box[0] + box[2]) // 2, box[1], (box[0] + box[2]) // 2, box[3]], fill=(*UMBER, 110), width=3)
        d.line([box[0] + 40, box[1] + 80, box[2] - 40, box[1] + 80], fill=(*UMBER, 90), width=3)
    elif kind == "two-tone-panel":
        d.polygon([(box[0], (box[1] + box[3]) // 2), (box[2], (box[1] + box[3]) // 2 + 40), (box[2], box[3]), (box[0], box[3])], fill=(255, 255, 255, 40))
    elif kind == "weathered-care":
        for _ in range(12):
            x = rng.randint(box[0], box[2])
            y = rng.randint(box[1], box[3])
            d.arc([x, y, x + 30, y + 16], 0, 180, fill=(255, 255, 255, 50), width=2)
    elif kind == "mission-patch-field":
        x = (box[0] + box[2]) // 2 - 20
        y = box[1] + 90
        d.rounded_rectangle([x, y, x + 40, y + 28], radius=6, outline=UMBER, width=3, fill=(40, 80, 60, 120))
    out = im
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return out


def paint_structural(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    box = spec["bounding_box"]
    if class_id == "sleeping-bag":
        zx = box["x"] + box["w"] - 48
        if kind in {"basic-baffles", "chest-zipper-pull", "hood-drawstring"}:
            d.line([zx, box["y"] + 180, zx, spec["hem_y"] - 20], fill=UMBER, width=3)
            for y in range(box["y"] + 200, spec["hem_y"] - 30, 28):
                d.rectangle([zx - 4, y, zx + 4, y + 10], outline=UMBER, width=2)
        if kind == "hood-drawstring":
            c = spec["silhouette"]["hood_center"]
            d.arc([c["x"] - 70, c["y"] - 40, c["x"] + 70, c["y"] + 50], 200, 340, fill=UMBER, width=3)
            d.line([c["x"] - 40, c["y"] + 40, c["x"] - 40, c["y"] + 70], fill=UMBER, width=3)
        if kind == "chest-zipper-pull":
            d.ellipse([zx - 8, box["y"] + 210, zx + 10, box["y"] + 230], outline=UMBER, width=3, fill=(196, 148, 48, 255))
    elif class_id == "small-tent":
        peak = spec["peak"]
        if kind in {"a-frame-poles", "guy-lines", "door-window"}:
            d.line([peak["x"] - 4, peak["y"], box["x"] + 20, spec["hem_y"]], fill=(90, 70, 50, 255), width=6)
            d.line([peak["x"] + 4, peak["y"], box["x"] + box["w"] - 20, spec["hem_y"]], fill=(90, 70, 50, 255), width=6)
        if kind == "guy-lines":
            d.line([box["x"] + 40, spec["hem_y"] - 40, box["x"] - 10, spec["character_baseline_y"]], fill=UMBER, width=2)
            d.line([box["x"] + box["w"] - 40, spec["hem_y"] - 40, box["x"] + box["w"] + 10, spec["character_baseline_y"]], fill=UMBER, width=2)
        if kind == "door-window":
            door = spec["face_door"]
            d.ellipse([door["x"] + 80, door["y"] + 40, door["x"] + 130, door["y"] + 90], outline=UMBER, width=3)
    else:
        peak = spec["peak"]
        if kind in {"cabin-poles", "extra-panels", "vestibule", "guy-lines"}:
            d.line([peak["x"], peak["y"], box["x"] + 40, spec["hem_y"]], fill=(70, 80, 100, 255), width=5)
            d.line([peak["x"], peak["y"], box["x"] + box["w"] - 40, spec["hem_y"]], fill=(70, 80, 100, 255), width=5)
            d.line([box["x"] + 80, box["y"] + 160, box["x"] + box["w"] - 80, box["y"] + 160], fill=UMBER, width=3)
        if kind == "vestibule":
            d.polygon([(box["x"] + 180, spec["hem_y"]), (512, spec["hem_y"] + 30), (box["x"] + box["w"] - 180, spec["hem_y"])], outline=UMBER, fill=(200, 210, 220, 60))
        if kind == "extra-panels":
            d.line([box["x"] + 120, box["y"] + 200, box["x"] + 120, spec["hem_y"] - 10], fill=UMBER, width=3)
            d.line([box["x"] + box["w"] - 120, box["y"] + 200, box["x"] + box["w"] - 120, spec["hem_y"] - 10], fill=UMBER, width=3)
        if kind == "guy-lines":
            d.line([box["x"] + 60, spec["hem_y"] - 20, box["x"] - 20, spec["character_baseline_y"]], fill=UMBER, width=2)
    return im


def paint_hat(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    z = spec["headwear_preferred"]
    x, y, w, h = z["x"], z["y"], z["w"], z["h"]
    if kind == "none":
        return im
    colors = {
        "beanie": (180, 70, 70),
        "knit-cap": (70, 90, 140),
        "earflap-beanie": (160, 90, 60),
        "baseball-cap": (50, 90, 70),
        "bucket-hat": (196, 170, 110),
        "trapper-hat": (120, 80, 50),
        "earmuffs": (200, 90, 100),
        "headband": (80, 120, 90),
        "hood": (176, 92, 48),
        "santa-hat": (180, 40, 48),
        "crown": (212, 168, 64),
        "halo": (240, 220, 140),
    }
    col = colors.get(kind, (180, 80, 70))
    if kind in {"beanie", "knit-cap", "earflap-beanie"}:
        d.rounded_rectangle([x + 8, y + 18, x + w - 8, y + h], radius=18, fill=col, outline=UMBER, width=4)
        d.ellipse([x + w // 2 - 10, y + 4, x + w // 2 + 10, y + 24], fill=(240, 230, 210), outline=UMBER, width=3)
        for i in range(3):
            d.line([x + 16, y + 28 + i * 10, x + w - 16, y + 28 + i * 10], fill=(*UMBER, 80), width=2)
        if kind == "earflap-beanie":
            d.ellipse([x - 6, y + h - 20, x + 28, y + h + 28], fill=col, outline=UMBER, width=3)
            d.ellipse([x + w - 28, y + h - 20, x + w + 6, y + h + 28], fill=col, outline=UMBER, width=3)
    elif kind == "baseball-cap":
        d.ellipse([x + 10, y + 8, x + w - 10, y + h - 8], fill=col, outline=UMBER, width=4)
        d.polygon([(x + w // 2, y + h - 16), (x + w + 16, y + h - 6), (x + w // 2 + 10, y + h + 6)], fill=col, outline=UMBER)
    elif kind == "bucket-hat":
        d.ellipse([x - 8, y + h - 24, x + w + 8, y + h + 8], fill=col, outline=UMBER, width=4)
        d.ellipse([x + 16, y + 8, x + w - 16, y + h - 8], fill=col, outline=UMBER, width=4)
    elif kind == "trapper-hat":
        d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h], radius=12, fill=col, outline=UMBER, width=4)
        d.ellipse([x - 4, y + 20, x + 30, y + h + 10], fill=(230, 220, 200), outline=UMBER, width=3)
        d.ellipse([x + w - 30, y + 20, x + w + 4, y + h + 10], fill=(230, 220, 200), outline=UMBER, width=3)
    elif kind == "earmuffs":
        d.ellipse([x, y + 20, x + 36, y + h], fill=col, outline=UMBER, width=3)
        d.ellipse([x + w - 36, y + 20, x + w, y + h], fill=col, outline=UMBER, width=3)
        d.arc([x + 10, y, x + w - 10, y + 50], 200, 340, fill=UMBER, width=4)
    elif kind == "headband":
        d.arc([x + 8, y + 20, x + w - 8, y + h + 10], 200, 340, fill=col, width=10)
        d.arc([x + 8, y + 20, x + w - 8, y + h + 10], 200, 340, fill=UMBER, width=2)
    elif kind == "hood":
        d.arc([x - 10, y, x + w + 10, y + h + 40], 200, 340, fill=col, width=14)
    elif kind == "santa-hat":
        d.polygon([(x + 8, y + h - 6), (x + w - 8, y + h - 6), (x + w // 2 + 20, y)], fill=col, outline=UMBER)
        d.ellipse([x, y + h - 18, x + w, y + h + 10], fill=(245, 240, 230), outline=UMBER, width=3)
        d.ellipse([x + w // 2 + 10, y - 8, x + w // 2 + 34, y + 16], fill=(245, 240, 230), outline=UMBER, width=3)
    elif kind == "crown":
        pts = [(x, y + h - 8), (x + 16, y + 8), (x + 32, y + h - 16), (x + w // 2, y), (x + w - 32, y + h - 16), (x + w - 16, y + 8), (x + w, y + h - 8)]
        d.polygon(pts, fill=col, outline=UMBER)
    elif kind == "halo":
        d.ellipse([x + 8, y + 8, x + w - 8, y + h - 4], outline=(240, 210, 100, 200), width=6)
    return im


def paint_held(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    hx, hy = spec["right_hand_default"]["x"], spec["right_hand_default"]["y"]
    lx, ly = spec["left_hand_default"]["x"], spec["left_hand_default"]["y"]
    if kind == "none":
        return im
    if kind in {"coffee", "hot-chocolate", "soup-cup"}:
        col = {"coffee": (120, 70, 40), "hot-chocolate": (90, 50, 30), "soup-cup": (210, 140, 70)}[kind]
        d.rounded_rectangle([hx - 22, hy - 28, hx + 18, hy + 18], radius=6, fill=col, outline=UMBER, width=3)
        d.arc([hx + 12, hy - 16, hx + 32, hy + 8], 270, 90, fill=UMBER, width=3)
        if kind != "soup-cup":
            d.ellipse([hx - 16, hy - 34, hx + 12, hy - 22], fill=(250, 250, 255, 80))
    elif kind == "thermos":
        d.rounded_rectangle([hx - 14, hy - 48, hx + 14, hy + 16], radius=6, fill=(50, 80, 90), outline=UMBER, width=3)
        d.rectangle([hx - 10, hy - 56, hx + 10, hy - 46], fill=(180, 80, 50), outline=UMBER, width=2)
    elif kind == "flashlight":
        d.rounded_rectangle([hx - 8, hy - 10, hx + 36, hy + 8], radius=4, fill=(80, 80, 70), outline=UMBER, width=3)
        d.polygon([(hx + 36, hy - 10), (hx + 50, hy - 16), (hx + 50, hy + 14), (hx + 36, hy + 8)], fill=(220, 200, 80), outline=UMBER)
    elif kind == "lantern":
        d.rounded_rectangle([hx - 16, hy - 36, hx + 16, hy + 12], radius=4, fill=(196, 140, 48), outline=UMBER, width=3)
        d.arc([hx - 12, hy - 52, hx + 12, hy - 32], 0, 180, fill=UMBER, width=3)
        d.ellipse([hx - 10, hy - 28, hx + 10, hy - 4], fill=(255, 210, 80, 180))
    elif kind == "heart":
        d.ellipse([hx - 16, hy - 20, hx, hy], fill=(180, 48, 72), outline=UMBER)
        d.ellipse([hx, hy - 20, hx + 16, hy], fill=(180, 48, 72), outline=UMBER)
        d.polygon([(hx - 18, hy - 8), (hx + 18, hy - 8), (hx, hy + 16)], fill=(180, 48, 72), outline=UMBER)
    elif kind == "hand-warmer":
        d.ellipse([hx - 20, hy - 16, hx + 20, hy + 16], fill=(220, 90, 70), outline=UMBER, width=3)
    elif kind == "compass":
        d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=(230, 220, 190), outline=UMBER, width=3)
        d.polygon([(hx, hy - 10), (hx + 4, hy), (hx, hy + 10), (hx - 4, hy)], fill=(180, 40, 40))
    elif kind == "map":
        d.rounded_rectangle([lx + 20, ly - 50, hx - 20, hy + 20], radius=4, fill=(220, 200, 150), outline=UMBER, width=3)
        d.line([lx + 40, ly - 20, hx - 40, hy - 10], fill=(80, 100, 70), width=2)
    elif kind == "blanket":
        d.rounded_rectangle([lx + 10, ly - 30, hx - 10, hy + 10], radius=8, fill=(140, 70, 70), outline=UMBER, width=3)
    elif kind == "walking-stick":
        d.line([hx, hy - 80, hx - 8, hy + 40], fill=(120, 80, 40), width=6)
        d.ellipse([hx - 8, hy - 90, hx + 10, hy - 72], outline=UMBER, width=3)
    elif kind in {"sign-heart"}:
        d.rounded_rectangle([hx - 36, hy - 70, hx + 36, hy - 10], radius=4, fill=(240, 230, 210), outline=UMBER, width=3)
        d.ellipse([hx - 14, hy - 58, hx, hy - 42], fill=(180, 48, 72))
        d.ellipse([hx, hy - 58, hx + 14, hy - 42], fill=(180, 48, 72))
        d.polygon([(hx - 16, hy - 48), (hx + 16, hy - 48), (hx, hy - 28)], fill=(180, 48, 72))
        d.line([hx, hy - 10, hx, hy + 16], fill=UMBER, width=4)
    elif kind == "umbrella":
        d.pieslice([hx - 40, hy - 90, hx + 40, hy - 20], 0, 180, fill=(70, 100, 140), outline=UMBER)
        d.line([hx, hy - 20, hx, hy + 20], fill=UMBER, width=4)
    return im


def paint_rear_held(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    hx, hy = spec["right_hand_default"]["x"], spec["right_hand_default"]["y"]
    if kind == "lantern":
        d.arc([hx - 12, hy - 52, hx + 12, hy - 32], 180, 360, fill=UMBER, width=3)
    elif kind == "walking-stick":
        d.line([hx - 6, hy - 40, hx - 10, hy + 10], fill=(100, 70, 40), width=5)
    elif kind == "sign-heart":
        d.line([hx - 2, hy - 20, hx - 2, hy + 10], fill=UMBER, width=3)
    elif kind == "umbrella":
        d.ellipse([hx - 36, hy - 88, hx + 36, hy - 40], fill=(70, 100, 140, 180), outline=UMBER)
    return im


def paint_light(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    if kind not in {"lantern", "flashlight"}:
        return im
    d = ImageDraw.Draw(im)
    hx, hy = spec["right_hand_default"]["x"] - 10, spec["right_hand_default"]["y"] - 20
    for r, a in ((90, 18), (50, 28), (24, 40)):
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 186, 80, a))
    return im.filter(ImageFilter.GaussianBlur(10))


def paint_footwear(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    lf, rf = spec["left_foot_anchor"], spec["right_foot_anchor"]
    y = spec["character_baseline_y"]
    colors = {
        "basic-shoes": (80, 60, 50),
        "work-boots": (90, 62, 40),
        "snow-boots": (230, 230, 235),
        "hiking-boots": (70, 80, 50),
        "sneakers": (50, 90, 140),
        "slippers": (180, 90, 90),
        "mismatched": None,
        "bare-feet": (220, 170, 140),
    }
    def boot(x, col, h=28, w=22):
        d.rounded_rectangle([x - w, y - h, x + w, y + 4], radius=8, fill=col, outline=UMBER, width=3)
        d.ellipse([x - w - 4, y - 10, x + w + 8, y + 6], fill=col, outline=UMBER, width=3)
    if kind == "mismatched":
        boot(lf["x"], (80, 90, 160), 26, 20)
        boot(rf["x"], (180, 80, 70), 26, 20)
    elif kind == "bare-feet":
        for foot in (lf, rf):
            d.ellipse([foot["x"] - 16, y - 18, foot["x"] + 16, y + 4], fill=colors["bare-feet"], outline=UMBER, width=3)
    elif kind in colors:
        col = colors[kind]
        h = 36 if "boot" in kind else 24
        boot(lf["x"], col, h)
        boot(rf["x"], col, h)
    return im


def paint_accessory(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    z = spec["body_accessory_zone"]
    cx = spec["character_center_x"]
    if kind == "scarf":
        d.arc([cx - 70, spec["face_center"]["y"] + 40, cx + 70, spec["face_center"]["y"] + 120], 200, 340, fill=(160, 50, 50), width=14)
        d.rectangle([cx + 40, spec["face_center"]["y"] + 80, cx + 62, spec["face_center"]["y"] + 160], fill=(160, 50, 50), outline=UMBER)
    elif kind == "sash":
        d.line([z["x"] + 20, z["y"], z["x"] + z["w"] - 20, z["y"] + z["h"] - 20], fill=(180, 40, 50), width=16)
    elif kind == "patch":
        d.rounded_rectangle([cx - 20, z["y"] + 40, cx + 20, z["y"] + 70], radius=4, fill=(40, 90, 60), outline=UMBER, width=3)
    elif kind == "lantern-hook":
        d.arc([spec["right_arm_anchor"]["x"] - 20, spec["right_arm_anchor"]["y"] - 20, spec["right_arm_anchor"]["x"] + 10, spec["right_arm_anchor"]["y"] + 10], 0, 270, fill=UMBER, width=3)
    elif kind == "backpack-straps":
        d.line([cx - 40, z["y"], cx - 50, z["y"] + 80], fill=UMBER, width=6)
        d.line([cx + 40, z["y"], cx + 50, z["y"] + 80], fill=UMBER, width=6)
    elif kind == "name-tag":
        d.rounded_rectangle([cx - 16, z["y"] + 30, cx + 16, z["y"] + 50], radius=3, fill=(240, 230, 210), outline=UMBER, width=2)
    return im


def paint_rear_accessory(class_id: str, kind: str) -> Image.Image:
    spec = config.class_spec(class_id)
    im = empty()
    d = ImageDraw.Draw(im)
    z = spec["rear_accessory_zone"]
    if kind == "backpack":
        d.rounded_rectangle([z["x"] + 40, z["y"] + 20, z["x"] + z["w"] - 40, z["y"] + z["h"] - 40], radius=12, fill=(70, 80, 60), outline=UMBER, width=4)
    elif kind == "bedroll":
        d.rounded_rectangle([z["x"] + 20, z["y"] + 80, z["x"] + z["w"] - 20, z["y"] + 130], radius=16, fill=(140, 90, 60), outline=UMBER, width=3)
    elif kind == "extra-fly":
        peak = spec["peak"]
        d.polygon([(peak["x"], peak["y"] - 10), (z["x"], z["y"] + 80), (z["x"] + z["w"], z["y"] + 80)], fill=(40, 70, 90, 120), outline=UMBER)
    return im


def paint_ground(kind: str) -> Image.Image:
    im = empty()
    d = ImageDraw.Draw(im)
    if kind == "mug-in-snow":
        d.rounded_rectangle([140, 860, 180, 900], radius=4, fill=(120, 70, 40), outline=UMBER, width=3)
    elif kind == "small-lantern":
        d.rounded_rectangle([820, 850, 852, 900], radius=3, fill=(196, 140, 48), outline=UMBER, width=3)
    elif kind == "pack-on-ground":
        d.rounded_rectangle([700, 860, 780, 910], radius=8, fill=(70, 80, 60), outline=UMBER, width=3)
    elif kind == "tiny-campfire":
        d.polygon([(500, 900), (512, 860), (524, 900)], fill=(220, 90, 40), outline=UMBER)
        d.ellipse([496, 894, 528, 910], fill=(40, 30, 20))
    elif kind == "snow-hare-tracks":
        for i, x in enumerate(range(200, 360, 28)):
            d.ellipse([x, 880 + (i % 2) * 8, x + 8, 888 + (i % 2) * 8], fill=UMBER)
    return im


def paint_atmosphere(kind: str, rear: bool) -> Image.Image:
    im = empty()
    d = ImageDraw.Draw(im)
    rng = random.Random(11 if rear else 23)
    n = {"light-snow": 40, "steady-snow": 90, "heavy-snow": 140, "breath-fog": 8, "sparkle-frost": 30, "north-star-field": 24}.get(kind, 0)
    if kind in {"light-snow", "steady-snow", "heavy-snow"}:
        for _ in range(n):
            x, y = rng.randint(20, 1000), rng.randint(20, 980)
            r = rng.randint(2, 5 if rear else 3)
            d.ellipse([x, y, x + r, y + r], fill=(255, 255, 255, 160 if rear else 200))
    elif kind == "breath-fog":
        d.ellipse([480, 360, 620, 430], fill=(230, 235, 240, 50))
        im = im.filter(ImageFilter.GaussianBlur(12))
    elif kind == "sparkle-frost":
        for _ in range(n):
            x, y = rng.randint(40, 980), rng.randint(40, 700)
            d.line([x - 4, y, x + 4, y], fill=(255, 250, 220, 180), width=1)
            d.line([x, y - 4, x, y + 4], fill=(255, 250, 220, 180), width=1)
    elif kind == "north-star-field":
        for _ in range(n):
            x, y = rng.randint(40, 980), rng.randint(20, 280)
            d.ellipse([x, y, x + 3, y + 3], fill=(255, 240, 180, 200))
        d.polygon([(900, 40), (906, 54), (922, 54), (910, 64), (914, 80), (900, 70), (886, 80), (890, 64), (878, 54), (894, 54)], fill=(255, 230, 140, 200))
    return im


def paint_rear_environment(kind: str) -> Image.Image:
    im = empty()
    d = ImageDraw.Draw(im)
    if kind == "distant-pines":
        for x, h in ((80, 140), (130, 180), (900, 160), (950, 120)):
            d.polygon([(x, 640), (x + 24, 640 - h), (x + 48, 640)], fill=(30, 50, 40, 140), outline=UMBER)
    elif kind == "campfire-glow":
        d.ellipse([430, 700, 600, 860], fill=(255, 140, 40, 40))
        im = im.filter(ImageFilter.GaussianBlur(18))
    elif kind == "ridge-line":
        d.polygon([(0, 620), (200, 540), (400, 600), (700, 520), (1024, 600), (1024, 640), (0, 640)], fill=(80, 90, 110, 80), outline=UMBER)
    return im


def raise_arm(im: Image.Image, class_id: str, which: str = "right") -> Image.Image:
    spec = config.class_spec(class_id)
    box = im.getchannel("A").getbbox()
    if not box:
        return im
    mid = (box[0] + box[2]) // 2
    if which == "right":
        crop = im.crop((mid, box[1], box[2], box[3]))
        dest = empty()
        dest.paste(im, (0, 0), im)
        lifted = Image.new("RGBA", crop.size, (0, 0, 0, 0))
        lifted.paste(crop, (0, -40), crop)
        dest.paste(Image.new("RGBA", crop.size, (0, 0, 0, 0)), (mid, box[1]))
        dest.alpha_composite(lifted, (mid, box[1] - 40))
        return dest
    return im


def front_hold_from_rest(rest: Image.Image) -> Image.Image:
    """Keep only the lower-outer mitten as a front hand."""
    box = rest.getchannel("A").getbbox()
    if not box:
        return rest
    im = empty()
    # right half lower portion
    crop = rest.crop((512, 480, 1024, 860))
    im.paste(crop, (512, 480), crop)
    return im


def ensure_body(class_id: str, trait_id: str) -> Path:
    dest = LAYERS / class_id / "body" / f"{trait_id}.png"
    master = Image.open(MASTERS[class_id]).convert("RGBA")
    spec = config.class_spec(class_id)
    if trait_id == "two-tone-olive-tan":
        im = two_tone(master, BODY_COLORS["trail-olive"], BODY_COLORS["sand-tan"], spec["hem_y"] - 120)
    elif trait_id == "two-tone-navy-orange":
        im = two_tone(master, BODY_COLORS["navy-night"], BODY_COLORS["camp-orange"], spec["hem_y"] - 120)
    elif trait_id in BODY_COLORS:
        im = recolor_fabric(master, BODY_COLORS[trait_id])
        if trait_id == "aurora":
            im = ImageEnhance.Color(im).enhance(1.25)
        if trait_id == "north-star-navy":
            d = ImageDraw.Draw(im)
            rng = random.Random(9)
            mask = fabric_mask(im)
            for _ in range(12):
                x, y = rng.randint(300, 720), rng.randint(200, 700)
                if mask.getpixel((x, y)) > 80:
                    d.polygon([(x, y - 5), (x + 2, y), (x + 5, y), (x + 2, y + 2), (x + 3, y + 5), (x, y + 3), (x - 3, y + 5), (x - 2, y + 2), (x - 5, y), (x - 2, y)], fill=(230, 210, 140, 160))
    else:
        im = master
    save_png(im, dest)
    return dest


def slot_path(class_id: str, compositor_slot: str, trait_id: str) -> Path:
    folder = config.slot_folder(compositor_slot, class_id)
    name = f"{trait_id}-glow.png" if compositor_slot == "light_effect" else f"{trait_id}.png"
    return ROOT / folder / name


def compositor_slots_for(trait: dict) -> list[str]:
    if trait.get("not_a_layer") or trait["id"] == "none":
        return []
    if trait.get("files"):
        return list(trait["files"])
    table = config.layer_stack().get("split_assets", {}).get(trait["slot"], {})
    if isinstance(table, dict) and trait["id"] in table and isinstance(table[trait["id"]], list):
        return list(table[trait["id"]])
    default = {
        "background": ["background"],
        "rear_environment": ["rear_environment"],
        "rear_accessory": ["rear_accessory"],
        "body": ["body"],
        "pattern": ["pattern"],
        "structural": ["structural"],
        "footwear": ["footwear"],
        "face": ["face"],
        "eyes": ["eyes"],
        "eyebrows": ["eyebrows"],
        "mouth": ["mouth"],
        "facial": ["facial"],
        "body_accessory": ["body_accessory"],
        "headwear": ["headwear"],
        "ground_accessory": ["ground_accessory"],
        "held_item": ["front_held"],
        "arm_pose": ["rear_arm"],
        "legs": ["rear_leg"],
        "atmosphere": ["atmosphere"],
    }
    return list(default.get(trait["slot"], []))


def classes_for(trait: dict) -> list[str]:
    classes = trait.get("classes") or []
    shared_slots = {"background", "rear_environment", "atmosphere", "ground_accessory"}
    if trait["slot"] in shared_slots or "shared" in classes:
        if trait["slot"] in shared_slots:
            return ["_shared"]
        return list(config.CLASS_IDS)
    return [c for c in classes if c in config.CLASS_IDS]


def required_paths(trait: dict | None = None) -> list[Path]:
    rows = [trait] if trait else [t for t in config.traits()["traits"]]
    paths: list[Path] = []
    for row in rows:
        if row.get("not_a_layer") or row["id"] == "none":
            continue
        slots = compositor_slots_for(row)
        for class_id in classes_for(row):
            cid = "sleeping-bag" if class_id == "_shared" else class_id
            for cslot in slots:
                paths.append(slot_path(cid, cslot, row["id"]))
    return paths


def build_all(*, overwrite: bool = False) -> dict:
    """Create every missing PNG required by rollable traits. Returns counts."""
    written = 0
    skipped = 0
    notes: list[str] = []
    needed = {path.resolve() for path in required_paths()}

    def maybe(path: Path, builder) -> None:
        nonlocal written, skipped
        if path.resolve() not in needed:
            return
        if path.exists() and not overwrite and path.stat().st_size > 2000:
            skipped += 1
            return
        im = builder()
        if im is None:
            return
        save_png(im, path)
        written += 1

    # Bodies
    for trait in config.traits()["traits"]:
        if trait["slot"] != "body" or trait["id"] == "none":
            continue
        for class_id in trait["classes"]:
            if class_id == "shared":
                continue
            dest = LAYERS / class_id / "body" / f"{trait['id']}.png"
            maybe(dest, lambda cid=class_id, tid=trait["id"]: Image.open(ensure_body(cid, tid)))

    # Force dusty-rose even if not yet in JSON
    for class_id in config.CLASS_IDS:
        dest = LAYERS / class_id / "body" / "dusty-rose.png"
        maybe(dest, lambda cid=class_id: Image.open(ensure_body(cid, "dusty-rose")))

    # Expressions, facial
    for class_id in config.CLASS_IDS:
        for kind in ("normal", "happy", "sleepy", "determined", "surprised", "worried", "squint", "side-eye", "starry", "heart", "sunglasses-compatible"):
            maybe(LAYERS / class_id / "eyes" / f"{kind}.png", lambda c=class_id, k=kind: paint_eyes(c, k))
        for kind in ("neutral", "raised", "concerned", "mischievous", "determined"):
            maybe(LAYERS / class_id / "eyebrows" / f"{kind}.png", lambda c=class_id, k=kind: paint_brows(c, k))
        for kind in ("smile", "grin", "open-laugh", "smirk", "surprised", "teeth", "tongue", "chatter", "determined", "small-o"):
            maybe(LAYERS / class_id / "mouths" / f"{kind}.png", lambda c=class_id, k=kind: paint_mouth(c, k))
        for kind in ("blush", "freckles", "snow-kissed", "glasses", "sunglasses", "mustache"):
            maybe(LAYERS / class_id / "facial" / f"{kind}.png", lambda c=class_id, k=kind: paint_facial(c, k))

    # Patterns + structural using master body
    for class_id in config.CLASS_IDS:
        body = Image.open(MASTERS[class_id]).convert("RGBA")
        for kind in ("horizontal-quilt", "vertical-quilt", "plaid", "stars", "moons", "patchwork", "camo-soft", "geometric-trail", "panels", "two-tone-panel", "weathered-care", "mission-patch-field"):
            maybe(LAYERS / class_id / "patterns" / f"{kind}.png", lambda c=class_id, k=kind, b=body: paint_pattern(c, k, b))
        for kind in ("basic-baffles", "hood-drawstring", "chest-zipper-pull", "a-frame-poles", "guy-lines", "door-window", "cabin-poles", "vestibule", "extra-panels"):
            maybe(LAYERS / class_id / "structural" / f"{kind}.png", lambda c=class_id, k=kind: paint_structural(c, k))

    # Arms
    for class_id in config.CLASS_IDS:
        rest = Image.open(ARM_MASTERS[class_id]).convert("RGBA")
        maybe(LAYERS / class_id / "arms-rear" / "rest.png", lambda r=rest: r)
        maybe(LAYERS / class_id / "arms-rear" / "hold-item.png", lambda r=rest: r)
        maybe(LAYERS / class_id / "arms-rear" / "hold-two-hand.png", lambda r=rest: r)
        maybe(LAYERS / class_id / "arms-rear" / "akimbo.png", lambda r=rest: r)
        maybe(LAYERS / class_id / "arms-rear" / "wave.png", lambda r=rest, c=class_id: raise_arm(r, c, "right"))
        hold_front = LAYERS / class_id / "arms" / "hold-item.png"
        if hold_front.exists():
            hf = Image.open(hold_front).convert("RGBA")
        else:
            hf = front_hold_from_rest(rest)
        maybe(LAYERS / class_id / "arms" / "hold-item.png", lambda h=hf: h)
        maybe(LAYERS / class_id / "arms" / "hold-two-hand.png", lambda h=hf: h)
        maybe(LAYERS / class_id / "arms" / "wave.png", lambda r=rest, c=class_id: raise_arm(r, c, "right"))
        maybe(LAYERS / class_id / "arms" / "rest.png", lambda r=rest: r)

    # Held, light, hats, accessories, footwear
    for class_id in config.CLASS_IDS:
        for kind in ("coffee", "hot-chocolate", "thermos", "flashlight", "lantern", "heart", "hand-warmer", "soup-cup", "compass", "map", "blanket", "walking-stick", "sign-heart", "umbrella"):
            maybe(LAYERS / class_id / "handheld" / f"{kind}.png", lambda c=class_id, k=kind: paint_held(c, k))
            maybe(LAYERS / class_id / "handheld-rear" / f"{kind}.png", lambda c=class_id, k=kind: paint_rear_held(c, k))
        maybe(LAYERS / class_id / "light" / "lantern-glow.png", lambda c=class_id: paint_light(c, "lantern"))
        maybe(LAYERS / class_id / "light" / "flashlight-glow.png", lambda c=class_id: paint_light(c, "flashlight"))
        for kind in ("beanie", "knit-cap", "baseball-cap", "bucket-hat", "trapper-hat", "earmuffs", "headband", "hood", "santa-hat", "crown", "halo", "earflap-beanie"):
            maybe(LAYERS / class_id / "headwear" / f"{kind}.png", lambda c=class_id, k=kind: paint_hat(c, k))
        for kind in ("scarf", "sash", "patch", "lantern-hook", "backpack-straps", "name-tag"):
            maybe(LAYERS / class_id / "accessories" / f"{kind}.png", lambda c=class_id, k=kind: paint_accessory(c, k))
        for kind in ("backpack", "bedroll", "extra-fly"):
            maybe(LAYERS / class_id / "accessories-rear" / f"{kind}.png", lambda c=class_id, k=kind: paint_rear_accessory(c, k))
        for kind in ("basic-shoes", "work-boots", "snow-boots", "hiking-boots", "sneakers", "slippers", "mismatched", "bare-feet"):
            maybe(LAYERS / class_id / "footwear" / f"{kind}.png", lambda c=class_id, k=kind: paint_footwear(c, k))
        # keep existing rear legs
        maybe(LAYERS / class_id / "legs-rear" / "short-legs.png", lambda c=class_id: Image.open(LEG_MASTERS[c]).convert("RGBA"))

    # Shared atmosphere / ground / rear env
    for kind in ("light-snow", "steady-snow", "heavy-snow", "breath-fog", "sparkle-frost", "north-star-field"):
        maybe(LAYERS / "shared" / "atmosphere-rear" / f"{kind}.png", lambda k=kind: paint_atmosphere(k, True))
        maybe(LAYERS / "shared" / "atmosphere" / f"{kind}.png", lambda k=kind: paint_atmosphere(k, False))
    for kind in ("distant-pines", "campfire-glow", "ridge-line"):
        maybe(LAYERS / "shared" / "rear-environment" / f"{kind}.png", lambda k=kind: paint_rear_environment(k))
    for kind in ("mug-in-snow", "small-lantern", "pack-on-ground", "tiny-campfire", "snow-hare-tracks"):
        maybe(LAYERS / "shared" / "ground" / f"{kind}.png", lambda k=kind: paint_ground(k))

    return {"written": written, "skipped": skipped, "notes": notes}
