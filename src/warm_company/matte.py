"""Knock out generation mattes with despill and fringe QA.

Production matte is MAGENTA #FF00FF. Cyan leftover from v1 is still keyed.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

CANVAS = (1024, 1024)
KEY_MAGENTA = (255, 0, 255)
KEY_CYAN = (0, 255, 255)


def _resize_to_canvas(image: Image.Image) -> Image.Image:
    if image.size == CANVAS:
        return image
    return image.resize(CANVAS, Image.Resampling.LANCZOS)


def _corner_median(pixels, w: int, h: int) -> tuple[int, int, int]:
    samples: list[tuple[int, int, int]] = []
    for ox, oy in ((2, 2), (w - 8, 2), (2, h - 8), (w - 8, h - 8)):
        for dy in range(6):
            for dx in range(6):
                samples.append(pixels[ox + dx, oy + dy][:3])
    n = len(samples) // 2
    return (
        sorted(s[0] for s in samples)[n],
        sorted(s[1] for s in samples)[n],
        sorted(s[2] for s in samples)[n],
    )


def chroma_key(
    image: Image.Image,
    keys: tuple[tuple[int, int, int], ...] = (KEY_MAGENTA, KEY_CYAN),
    threshold: int = 48,
    corner_fallback: bool = True,
) -> Image.Image:
    """Soft-key magenta/cyan/dusty-rose mattes, despill remaining edge, contract 1px."""
    image = _resize_to_canvas(image.convert("RGBA"))
    pixels = image.load()
    w, h = image.size
    extra = list(keys)
    bg = None
    if corner_fallback:
        bg = _corner_median(pixels, w, h)
        extra.append(bg)
        # Grainy generation mattes need a wider first pass than #FF00FF.
        threshold = max(threshold, 64)

    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pixels[x, y]
            mag = (pr + pb) / 2 - pg
            cyn = (pg + pb) / 2 - pr
            # True chroma keys plus dusty rose/paper-grain magenta used by Imagine.
            is_mag = pr > 150 and pb > 150 and pg < 130 and mag > 40
            is_rose = pr > 140 and pg < 125 and pb > 70 and pr > pg + 35 and mag > 28
            is_cyn = pg > 150 and pb > 150 and pr < 110 and cyn > 40
            dist = min(abs(pr - kr) + abs(pg - kg) + abs(pb - kb) for kr, kg, kb in extra)
            if dist <= threshold or is_mag or is_rose or is_cyn:
                pixels[x, y] = (pr, pg, pb, 0)
                continue
            if dist <= threshold * 2:
                t = dist / (threshold * 2)
                t = max(0.0, min(1.0, t))
                na = int(pa * t)
                if mag > cyn:
                    pg2 = pg
                    pr2 = pr - int((pr - pg) * 0.55)
                    pb2 = pb - int((pb - pg) * 0.55)
                else:
                    pr2 = pr
                    pg2 = pg - int((pg - pr) * 0.55)
                    pb2 = pb - int((pb - pr) * 0.55)
                pixels[x, y] = (max(0, pr2), max(0, pg2), max(0, pb2), na)
            else:
                if mag > 18:
                    pr = pr - int(mag * 0.25)
                    pb = pb - int(mag * 0.25)
                    pixels[x, y] = (max(0, pr), pg, max(0, pb), pa)
                elif cyn > 18:
                    pg = pg - int(cyn * 0.25)
                    pb = pb - int(cyn * 0.25)
                    pixels[x, y] = (pr, max(0, pg), max(0, pb), pa)
    # Contract 1px of leftover matte fringe, then restore 1px of natural AA.
    alpha = image.getchannel("A")
    contracted = alpha.filter(ImageFilter.MinFilter(3))
    restored = contracted.filter(ImageFilter.MaxFilter(3))
    # Keep the more conservative of original vs restored on near-zero pixels.
    image.putalpha(ImageChops.darker(alpha, restored.filter(ImageFilter.GaussianBlur(0.6))))
    return image


def fringe_report(image: Image.Image) -> dict:
    """Count remaining cyan/magenta contamination on opaque-ish pixels."""
    image = image.convert("RGBA")
    px = image.load()
    w, h = image.size
    cyan = magenta = 0
    opaque = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 24:
                continue
            opaque += 1
            if (g + b) / 2 - r > 40 and a < 220:
                cyan += 1
            if (r + b) / 2 - g > 40 and a < 220:
                magenta += 1
    return {
        "opaque_px": opaque,
        "cyan_fringe_px": cyan,
        "magenta_fringe_px": magenta,
        "ok": cyan < 80 and magenta < 80,
    }


def strip_key_fringe(image: Image.Image) -> Image.Image:
    """Knock down cyan/magenta antialias leftover without eating umber outlines."""
    image = image.convert("RGBA")
    box = image.getchannel("A").getbbox()
    if not box:
        return image
    px = image.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a < 16 or a > 236:
                continue
            mag = (r + b) / 2 - g
            cyn = (g + b) / 2 - r
            if cyn > 28 and g > 130 and r < 130:
                px[x, y] = (r, max(0, g - 40), max(0, b - 40), int(a * 0.2))
            elif mag > 36 and r > 150 and g < 140:
                px[x, y] = (max(0, r - 40), g, max(0, b - 40), int(a * 0.25))
    return image


def clip_to_mask(image: Image.Image, mask: Image.Image, dilate: int = 7) -> Image.Image:
    mask = _resize_to_canvas(mask.convert("L"))
    if dilate:
        mask = mask.filter(ImageFilter.MaxFilter(dilate if dilate % 2 else dilate + 1))
    out = image.copy()
    out.putalpha(ImageChops.darker(image.getchannel("A"), mask))
    return out


def process_file(src: Path, dest: Path, mask: Path | None = None) -> Path:
    keyed = chroma_key(Image.open(src))
    if mask and mask.exists():
        keyed = clip_to_mask(keyed, Image.open(mask))
    dest.parent.mkdir(parents=True, exist_ok=True)
    keyed.save(dest, "PNG")
    return dest
