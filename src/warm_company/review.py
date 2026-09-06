"""Review-sheet helpers. Reconstruction strips bind to one token."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .composite import CANVAS, _open_rgba, _prepare_layer, composite_token, is_blank_face_panel, resolved_stack

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
        "structural": "none",
        "legs": "short-legs",
        "footwear": "basic-shoes" if class_id == "sleeping-bag" else "work-boots",
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

# 12-sample refinement gate. Extra trait dicts overlay review_token defaults.
REFINEMENT_SAMPLES: list[tuple[str, str, str, dict[str, str]]] = [
    ("snug-01-bare", "Snug — Bare rest", "sleeping-bag", {"background": "winter-sunrise"}),
    ("snug-02-hat", "Snug — Tiny beanie", "sleeping-bag", {"background": "snowy-camp", "headwear": "beanie"}),
    ("snug-03-coffee", "Snug — Coffee grip", "sleeping-bag", {
        "background": "winter-sunrise",
        "arm_pose": "hold-item",
        "held_item": "coffee",
        "eyes": "happy",
        "mouth": "smile",
        "facial": "blush",
    }),
    ("snug-04-night", "Snug — Night snow", "sleeping-bag", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "headwear": "beanie",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "mouth": "determined",
    }),
    ("pup-01-bare", "Pup — Bare rest", "small-tent", {"background": "forest-clearing", "body": "forest-green"}),
    ("pup-02-hat", "Pup — Peak beanie", "small-tent", {
        "background": "winter-sunrise",
        "body": "forest-green",
        "headwear": "beanie",
    }),
    ("pup-03-map", "Pup — Two-hand map", "small-tent", {
        "background": "snowy-camp",
        "body": "forest-green",
        "arm_pose": "hold-two-hand",
        "held_item": "map",
        "eyes": "happy",
        "mouth": "smile",
    }),
    ("pup-04-night", "Pup — Night snow", "small-tent", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "headwear": "beanie",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "mouth": "smile",
    }),
    ("lodge-01-bare", "Lodge — D-door rest", "large-tent", {"background": "snowy-camp", "body": "royal-blue"}),
    ("lodge-02-hat", "Lodge — Peak beanie", "large-tent", {
        "background": "winter-sunrise",
        "body": "camp-orange",
        "headwear": "beanie",
    }),
    ("lodge-03-lantern", "Lodge — Lantern grip", "large-tent", {
        "background": "forest-clearing",
        "body": "royal-blue",
        "arm_pose": "hold-item",
        "held_item": "lantern",
    }),
    ("lodge-04-night", "Lodge — Night snow", "large-tent", {
        "background": "cold-blue-night",
        "body": "navy-night",
        "atmosphere": "light-snow",
        "eyes": "determined",
        "mouth": "determined",
    }),
]


def refinement_tokens() -> list[tuple[str, str, dict]]:
    rows: list[tuple[str, str, dict]] = []
    for sample_id, title, class_id, extra in REFINEMENT_SAMPLES:
        rows.append((sample_id, title, review_token(class_id, **extra)))
    return rows


def _strip_layer_visible(class_id: str, slot: str, source: Path | str) -> bool:
    if source in ("procedural", "procedural-glow"):
        return False
    path = Path(source)
    if not path.exists():
        return False
    if slot == "face":
        with Image.open(path) as im:
            if is_blank_face_panel(im.convert("RGBA"), class_id):
                return False
    return True


def visible_stack_slots(token: dict) -> list[str]:
    """PNG layer slots a reconstruction strip shows, in compositor order."""
    slots: list[str] = []
    for slot, source in resolved_stack(token["class_id"], token["traits"]):
        if _strip_layer_visible(token["class_id"], slot, source):
            slots.append(slot)
    return slots


def reconstruction_composite(token: dict) -> Image.Image:
    return composite_token(token, missing="allow")


def reconstruction_layer(token: dict, slot: str, source: Path | str) -> Image.Image | None:
    """Layer as the compositor paints it, including foot registration."""
    image = _open_rgba(Path(source))
    return _prepare_layer(slot, image, token["class_id"], traits=token["traits"])


def reconstruction_strip(title: str, token: dict) -> Image.Image:
    """Show prepared stack layers, then the composite of the same token."""
    final = reconstruction_composite(token)
    thumb = 140
    parts: list[tuple[str, Image.Image]] = []
    for slot, source in resolved_stack(token["class_id"], token["traits"]):
        if not _strip_layer_visible(token["class_id"], slot, source):
            continue
        prepared = reconstruction_layer(token, slot, source)
        if prepared is None:
            continue
        parts.append((slot, prepared))
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
