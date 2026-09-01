"""Review-sheet helpers. Reconstruction strips bind to one token."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .composite import CANVAS, composite_token, resolved_stack

ROOT = Path(__file__).resolve().parents[2]


def review_token(class_id: str, **traits: str) -> dict:
    base = {
        "background": "winter-sunrise",
        "rear_environment": "none",
        "rear_accessory": "none",
        "arm_pose": "rest",
        "held_item": "none",
        "body": {
            "sleeping-bag": "ember-rust",
            "small-tent": "forest-green",
            "large-tent": "royal-blue",
        }[class_id],
        "pattern": "none",
        "structural": "basic-baffles",
        "legs": "short-legs",
        "footwear": "basic-shoes",
        "face": "standard-face",
        "eyes": "normal",
        "eyebrows": "none",
        "mouth": "smile",
        "facial": "none",
        "body_accessory": "none",
        "headwear": "none",
        "ground_accessory": "none",
        "atmosphere": "none",
        "special": "none",
    }
    base.update(traits)
    return {"class_id": class_id, "traits": base, "token_id": 0}


# One token per reconstruction strip. The composite image MUST be this token.
STRIP_TOKENS: dict[str, dict] = {
    "snug": review_token("sleeping-bag", headwear="beanie"),
    "pup": review_token("small-tent"),
    "lodge": review_token("large-tent", held_item="lantern", arm_pose="hold-item"),
}


def visible_stack_slots(token: dict) -> list[str]:
    """PNG layer slots a reconstruction strip shows, in compositor order."""
    slots: list[str] = []
    for slot, source in resolved_stack(token["class_id"], token["traits"]):
        if source in ("procedural", "procedural-glow"):
            continue
        if Path(source).exists():
            slots.append(slot)
    return slots


def reconstruction_composite(token: dict) -> Image.Image:
    return composite_token(token, missing="allow")


def reconstruction_strip(title: str, token: dict) -> Image.Image:
    """Show every existing PNG from this token's resolved_stack, then the composite of the same token."""
    final = reconstruction_composite(token)
    thumb = 140
    parts: list[tuple[str, Image.Image]] = []
    for slot, source in resolved_stack(token["class_id"], token["traits"]):
        if source in ("procedural", "procedural-glow"):
            continue
        path = Path(source)
        if path.exists():
            parts.append((slot, Image.open(path).convert("RGBA")))
    assert [name for name, _ in parts] == visible_stack_slots(token)
    items = parts + [("composite", final)]
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 12)
    except OSError:
        f = ImageFont.load_default()
    sheet = Image.new("RGB", (12 + len(items) * (thumb + 8), thumb + 40), (18, 24, 32))
    d = ImageDraw.Draw(sheet)
    d.text((10, 4), title, fill=(240, 236, 228), font=f)
    x = 10
    for name, im in items:
        cell = Image.new("RGBA", (thumb, thumb), (40, 8, 40, 255) if name != "composite" else (20, 24, 30, 255))
        vis = im.convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
        cell = Image.alpha_composite(cell, vis)
        sheet.paste(cell.convert("RGB"), (x, 22))
        d.text((x, 22 + thumb + 2), name[:16], fill=(200, 206, 212), font=f)
        x += thumb + 8
    return sheet
