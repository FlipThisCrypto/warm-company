from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import config
from .paths import BUILD, LAYERS, ROOT, ensure_build

CANVAS = (1024, 1024)


def _open_rgba(path: Path) -> Image.Image:
    image = Image.open(path)
    if image.size != CANVAS:
        raise ValueError(f"{path} is {image.size}, expected {CANVAS}")
    return image.convert("RGBA")


def procedural_contact_shadow(class_id: str) -> Image.Image:
    spec = config.class_spec(class_id)
    world = config.anchors()["world"]["contact_shadow"]
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    left = spec["left_foot_anchor"]["x"]
    right = spec["right_foot_anchor"]["x"]
    bbox = spec["bounding_box"]
    cx = (left + right) / 2
    width = max(bbox["w"] * 0.62, right - left + 90)
    height = 36
    y = spec["character_baseline_y"] + int(world["offset_y"])
    color = tuple(world["color"]) + (int(255 * world["opacity"]),)
    box = [cx - width / 2, y - height / 2, cx + width / 2, y + height / 2]
    draw.ellipse(box, fill=color)
    return layer.filter(ImageFilter.GaussianBlur(radius=float(world["blur_px"])))


def layer_path(class_id: str, slot: str, trait_id: str) -> Path | None:
    if trait_id in (None, "none"):
        return None
    folder = ROOT / config.slot_folder(slot, class_id)
    path = folder / f"{trait_id}.png"
    return path


def resolved_stack(class_id: str, traits: dict[str, str]) -> list[tuple[str, Path | str]]:
    """Return compositing sources in z order. 'shadow' is procedural."""
    stack = []
    mapping = {
        "background": ("background", traits.get("background")),
        "rear_environment": ("rear_environment", traits.get("rear_environment")),
        "contact_shadow": ("contact_shadow", "procedural"),
        "rear_accessory": ("rear_accessory", traits.get("rear_accessory")),
        "rear_arm": ("rear_arm", traits.get("arm_pose") if traits.get("arm_pose") == "wave" else None),
        "rear_held": ("rear_held", traits.get("held_item")),
        "body": ("body", traits.get("body")),
        "pattern": ("pattern", traits.get("pattern")),
        "structural": ("structural", traits.get("structural")),
        "legs": ("legs", traits.get("legs")),
        "footwear": ("footwear", traits.get("footwear")),
        "face": ("face", traits.get("face")),
        "eyes": ("eyes", traits.get("eyes")),
        "eyebrows": ("eyebrows", traits.get("eyebrows")),
        "mouth": ("mouth", traits.get("mouth")),
        "facial": ("facial", traits.get("facial")),
        "front_arm": ("front_arm", traits.get("arm_pose")),
        "front_held": ("front_held", traits.get("held_item")),
        "body_accessory": ("body_accessory", traits.get("body_accessory")),
        "headwear": ("headwear", traits.get("headwear")),
        "ground_accessory": ("ground_accessory", traits.get("ground_accessory")),
        "atmosphere": ("atmosphere", traits.get("atmosphere")),
        "logo": ("logo", None),  # deferred
    }
    trait_row = config.trait_by_id
    for layer in config.layer_stack()["stack"]:
        slot = layer["slot"]
        if slot == "contact_shadow":
            stack.append((slot, "procedural"))
            continue
        if layer.get("deferred"):
            continue
        source_slot, trait_id = mapping.get(slot, (slot, traits.get(slot)))
        if not trait_id or trait_id == "none":
            continue
        # Split assets: only load rear_held when the trait declares that file.
        if slot in {"rear_held", "rear_arm", "rear_accessory"}:
            row = trait_row("held_item" if "held" in slot else ("arm_pose" if "arm" in slot else "rear_accessory"), trait_id if slot != "rear_held" else traits.get("held_item", "none"))
            if slot == "rear_held":
                held = trait_row("held_item", traits.get("held_item", "none"))
                files = (held or {}).get("files") or ["front_held"]
                if "rear_held" not in files:
                    continue
            if slot == "rear_arm":
                pose = trait_row("arm_pose", traits.get("arm_pose", "rest"))
                files = (pose or {}).get("files") or ["front_arm"]
                if "rear_arm" not in files:
                    continue
        path = layer_path(class_id, slot, trait_id)
        if path is None:
            continue
        stack.append((slot, path))
    return stack


def composite_token(token: dict, *, missing: str = "error") -> Image.Image:
    class_id = token["class_id"]
    traits = token["traits"]
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    missing_files: list[str] = []
    for slot, source in resolved_stack(class_id, traits):
        if source == "procedural":
            canvas = Image.alpha_composite(canvas, procedural_contact_shadow(class_id))
            continue
        path = Path(source)
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)))
            continue
        canvas = Image.alpha_composite(canvas, _open_rgba(path))
    if missing_files and missing == "error":
        raise FileNotFoundError("missing layers:\n" + "\n".join(missing_files))
    return canvas


def write_token_png(token: dict, image: Image.Image) -> Path:
    ensure_build()
    path = BUILD / "images" / f"{token['token_id']:04d}.png"
    image.convert("RGBA").save(path, "PNG")
    return path
