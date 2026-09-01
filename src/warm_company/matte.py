"""Knock out generation mattes and force 1024x1024 RGBA."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

CANVAS = (1024, 1024)
KEY_CYAN = (0, 255, 255)
KEY_MAGENTA = (255, 0, 255)


def _resize_to_canvas(image: Image.Image) -> Image.Image:
    if image.size == CANVAS:
        return image
    return image.resize(CANVAS, Image.Resampling.LANCZOS)


def chroma_key(
    image: Image.Image,
    keys: tuple[tuple[int, int, int], ...] = (KEY_CYAN, KEY_MAGENTA),
    threshold: int = 48,
    corner_fallback: bool = True,
) -> Image.Image:
    image = _resize_to_canvas(image.convert("RGBA"))
    pixels = image.load()
    w, h = image.size

    extra_keys = list(keys)
    if corner_fallback:
        corners = [
            pixels[2, 2][:3],
            pixels[w - 3, 2][:3],
            pixels[2, h - 3][:3],
            pixels[w - 3, h - 3][:3],
        ]
        # If three corners agree, treat that as the matte.
        counts: dict[tuple[int, int, int], int] = {}
        for rgb in corners:
            snapped = (rgb[0] // 8 * 8, rgb[1] // 8 * 8, rgb[2] // 8 * 8)
            counts[snapped] = counts.get(snapped, 0) + 1
        common = max(counts, key=counts.get)
        if counts[common] >= 3:
            extra_keys.append(corners[0])

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            for kr, kg, kb in extra_keys:
                if abs(r - kr) + abs(g - kg) + abs(b - kb) <= threshold * 3:
                    pixels[x, y] = (r, g, b, 0)
                    break
            else:
                # Near-key despill
                if g > 180 and b > 180 and r < 90:
                    pixels[x, y] = (r, g, b, 0)
                elif r > 200 and b > 200 and g < 90:
                    pixels[x, y] = (r, g, b, 0)
    return image


def clip_to_mask(image: Image.Image, mask: Image.Image, dilate: int = 7) -> Image.Image:
    mask = _resize_to_canvas(mask.convert("L"))
    if dilate:
        mask = mask.filter(ImageFilter.MaxFilter(dilate if dilate % 2 else dilate + 1))
    out = image.copy()
    out.putalpha(_min_alpha(image.getchannel("A"), mask))
    return out


def _min_alpha(a: Image.Image, b: Image.Image) -> Image.Image:
    pa, pb = a.load(), b.load()
    out = Image.new("L", a.size, 0)
    po = out.load()
    w, h = a.size
    for y in range(h):
        for x in range(w):
            po[x, y] = min(pa[x, y], pb[x, y])
    return out


def process_file(src: Path, dest: Path, mask: Path | None = None) -> Path:
    image = Image.open(src)
    keyed = chroma_key(image)
    if mask and mask.exists():
        keyed = clip_to_mask(keyed, Image.open(mask))
    dest.parent.mkdir(parents=True, exist_ok=True)
    keyed.save(dest, "PNG")
    return dest
