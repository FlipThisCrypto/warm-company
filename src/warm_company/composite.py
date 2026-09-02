"""Painter's algorithm compositor driven by config/layer_stack.json.

Limb roots load behind the body. Headwear is clamped to headwear_preferred.
Atmosphere punches the face/door. Lantern may emit a procedural warm glow
when an illustrated light layer is absent.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import config
from .matte import strip_key_fringe
from .paths import BUILD, ROOT, ensure_build

CANVAS = (1024, 1024)

# Compositor slot -> trait slot when driven_by is omitted from JSON.
SLOT_TRAIT = {
    "rear_atmosphere": "atmosphere",
    "rear_arm": "arm_pose",
    "front_arm": "arm_pose",
    "rear_held": "held_item",
    "front_held": "held_item",
    "light_effect": "held_item",
    "rear_leg": "legs",
}

SECONDARY_SLOTS = {
    "rear_arm",
    "rear_held",
    "rear_leg",
    "rear_atmosphere",
    "light_effect",
    "rear_accessory",
}

# Cartoon feet already painted on rear_leg. These ids are not distinct boot overlays.
DEFAULT_FOOTWEAR = {"basic-shoes", "sneakers", "bare-feet"}

# Canonical hold edits are full-character PNG masters. Stacking rest limbs +
# clip-art props on top of them produces a second mug / extra human hand.
POSE_MASTER_SKIP = {
    "rear_arm",
    "rear_held",
    "rear_leg",
    "body",
    "pattern",
    "structural",
    "face",
    "eyes",
    "eyebrows",
    "mouth",
    "facial",
    "legs",
    "footwear",
}

_POSE_MASTER_CACHE: dict[str, bool] = {}


def _open_rgba(path: Path) -> Image.Image:
    image = Image.open(path)
    if image.size != CANVAS:
        raise ValueError(f"{path} is {image.size}, expected {CANVAS}")
    return image.convert("RGBA")


def empty() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def mul_opacity(im: Image.Image, t: float) -> Image.Image:
    a = im.getchannel("A").point(lambda p: int(p * t))
    out = im.copy()
    out.putalpha(a)
    return out


def procedural_contact_shadow(class_id: str) -> Image.Image:
    spec = config.class_spec(class_id)
    world = config.anchors()["world"]["contact_shadow"]
    layer = empty()
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


def procedural_lantern_glow(class_id: str) -> Image.Image:
    spec = config.class_spec(class_id)
    layer = empty()
    draw = ImageDraw.Draw(layer)
    hx = spec["right_hand_default"]["x"] - 40
    hy = spec["right_hand_default"]["y"] - 20
    for radius, alpha in ((140, 16), (88, 24), (48, 36)):
        draw.ellipse([hx - radius, hy - radius, hx + radius, hy + radius], fill=(255, 176, 72, alpha))
    return layer.filter(ImageFilter.GaussianBlur(16))


def punch_face(im: Image.Image, class_id: str) -> Image.Image:
    spec = config.class_spec(class_id)
    door = spec.get("face_door") or spec["face_oval"]
    mask = Image.new("L", CANVAS, 255)
    draw = ImageDraw.Draw(mask)
    pad = 48
    draw.rounded_rectangle(
        [door["x"] - pad, door["y"] - pad, door["x"] + door["w"] + pad, door["y"] + door["h"] + pad],
        radius=70,
        fill=0,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    out = im.copy()
    a = im.getchannel("A")
    out.putalpha(Image.composite(a, Image.new("L", CANVAS, 0), mask))
    return out


def clamp_headwear(im: Image.Image, class_id: str) -> Image.Image:
    """Scale a hat down to headwear_preferred if it fills the legal zone."""
    spec = config.class_spec(class_id)
    pref = spec["headwear_preferred"]
    peak = spec["peak"]
    alpha = im.getchannel("A")
    box = alpha.getbbox()
    if not box:
        return im
    w, h = box[2] - box[0], box[3] - box[1]
    max_w = pref["w"]
    max_h = pref["h"] + 40
    if w <= max_w + 12 and h <= max_h + 12:
        return im
    crop = im.crop(box)
    scale = min(max_w / w, max_h / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = empty()
    cx = spec["character_center_x"]
    cy = peak["y"] + pref["h"] // 2 + 20
    canvas.paste(crop, (int(cx - nw / 2), int(cy - nh / 2)), crop)
    return canvas


def layer_path(class_id: str, slot: str, trait_id: str) -> Path | None:
    if trait_id in (None, "none"):
        return None
    folder = ROOT / config.slot_folder(slot, class_id)
    return folder / f"{trait_id}.png"


def is_pose_master(path: Path) -> bool:
    """True when a layer is a full-character canonical hold, not an arm crop."""
    key = str(path)
    cached = _POSE_MASTER_CACHE.get(key)
    if cached is not None:
        return cached
    if not path.exists():
        _POSE_MASTER_CACHE[key] = False
        return False
    with Image.open(path) as im:
        alpha = im.getchannel("A")
        box = alpha.getbbox()
        if not box:
            _POSE_MASTER_CACHE[key] = False
            return False
        width, height = box[2] - box[0], box[3] - box[1]
        opaque = sum(alpha.histogram()[80:])
    ok = width >= 380 and height >= 620 and opaque >= 180_000
    _POSE_MASTER_CACHE[key] = ok
    return ok


def pose_master_slot(class_id: str, traits: dict[str, str]) -> str | None:
    """Which compositor slot carries a canonical hold edit, if any.

    A pose master is item-specific. Snug hold-item.png is the coffee canonical,
    so it must not replace lantern or thermos.
    """
    held = traits.get("held_item") or "none"
    pose = traits.get("arm_pose") or "rest"
    if held == "lantern":
        path = layer_path(class_id, "front_held", "lantern")
        if path is not None and is_pose_master(path):
            return "front_held"
        return None
    if held == "coffee" and pose == "hold-item":
        path = layer_path(class_id, "front_arm", "hold-item")
        if path is not None and is_pose_master(path):
            return "front_arm"
        return None
    if held == "map" and pose == "hold-two-hand":
        path = layer_path(class_id, "front_arm", "hold-two-hand")
        if path is not None and is_pose_master(path):
            return "front_arm"
        return None
    return None


def _trait_id_for(layer: dict, traits: dict[str, str]) -> tuple[str | None, str]:
    slot = layer["slot"]
    driven = layer.get("driven_by") or SLOT_TRAIT.get(slot, slot)
    return traits.get(driven), driven


def split_files(driven_slot: str, trait_id: str) -> list[str] | None:
    """Which compositor slots a metadata trait occupies. layer_stack wins."""
    table = config.layer_stack().get("split_assets", {}).get(driven_slot)
    if isinstance(table, dict) and trait_id in table:
        files = table[trait_id]
        if isinstance(files, list):
            return files
    row = config.trait_by_id(driven_slot, trait_id)
    if row and row.get("files"):
        return list(row["files"])
    return None


def slot_is_active(compositor_slot: str, driven_slot: str, trait_id: str | None) -> bool:
    if not trait_id or trait_id == "none":
        return False
    files = split_files(driven_slot, trait_id)
    if files is not None:
        return compositor_slot in files
    if compositor_slot in SECONDARY_SLOTS:
        if compositor_slot == "rear_atmosphere":
            return True
        if compositor_slot == "rear_leg":
            return True
        return False
    return True


def resolved_stack(class_id: str, traits: dict[str, str]) -> list[tuple[str, Path | str]]:
    """Return compositing sources in z order from layer_stack.json."""
    from .resolve import resolve_plan

    stack: list[tuple[str, Path | str]] = []
    master = pose_master_slot(class_id, traits)
    suppress = set(resolve_plan(class_id, traits).get("suppress") or [])
    for layer in config.layer_stack()["stack"]:
        slot = layer["slot"]
        if layer.get("deferred"):
            continue
        if slot in suppress:
            continue
        if slot == "contact_shadow" or layer.get("source") == "procedural":
            stack.append((slot, "procedural"))
            continue
        trait_id, driven = _trait_id_for(layer, traits)
        if not slot_is_active(slot, driven, trait_id):
            continue
        if master:
            if slot in POSE_MASTER_SKIP:
                continue
            if master == "front_arm" and slot == "front_held":
                continue
            if master == "front_held" and slot in {"front_arm", "rear_arm"}:
                continue
        # hold-item.png may be the coffee canonical. Do not paint it for thermos/lantern.
        if (
            slot == "front_arm"
            and (traits.get("arm_pose") or "rest") == "hold-item"
            and (traits.get("held_item") or "none") != "coffee"
        ):
            path_probe = layer_path(class_id, "front_arm", "hold-item")
            if path_probe is not None and is_pose_master(path_probe):
                continue
        if (
            slot == "front_arm"
            and (traits.get("arm_pose") or "rest") == "hold-two-hand"
            and (traits.get("held_item") or "none") != "map"
        ):
            path_probe = layer_path(class_id, "front_arm", "hold-two-hand")
            if path_probe is not None and is_pose_master(path_probe):
                continue
        if (
            slot == "footwear"
            and trait_id in DEFAULT_FOOTWEAR
            and slot_is_active("rear_leg", "legs", traits.get("legs"))
        ):
            continue
        if slot == "light_effect" and trait_id in {"lantern", "flashlight"}:
            path = layer_path(class_id, slot, f"{trait_id}-glow")
            if path is not None and not path.exists():
                stack.append((slot, "procedural-glow"))
                continue
            if path is not None:
                stack.append((slot, path))
                continue
        path = layer_path(class_id, slot, trait_id)  # type: ignore[arg-type]
        if path is None:
            continue
        stack.append((slot, path))
    return stack


def layer_has_ink(im: Image.Image, luma_max: int = 96) -> bool:
    """True if the layer contains dark linework, not just a cream fill."""
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    step = 4
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            if a < 80:
                continue
            if (r + g + b) / 3 <= luma_max:
                return True
    return False


def is_blank_face_panel(im: Image.Image, class_id: str) -> bool:
    """Skip cream door/hood fills; the body already owns that panel."""
    if layer_has_ink(im):
        return False
    spec = config.class_spec(class_id)
    door = spec.get("face_door") or spec["face_oval"]
    box = im.getchannel("A").getbbox()
    if not box:
        return True
    w, h = box[2] - box[0], box[3] - box[1]
    return w >= door["w"] * 0.6 and h >= door["h"] * 0.45


UMBER = (58, 42, 34)


def umber_ink(im: Image.Image, target: tuple[int, int, int] = UMBER) -> Image.Image:
    """Restyle pure-black feature strokes toward the collection umber."""
    out = im.convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            if r < 48 and g < 48 and b < 48:
                px[x, y] = (*target, a)
    return out


def clip_to_face_region(im: Image.Image, class_id: str) -> Image.Image:
    """Keep eyes/mouth/facial inside the hood or door."""
    spec = config.class_spec(class_id)
    door = spec.get("face_door") or spec["face_oval"]
    mask = Image.new("L", CANVAS, 0)
    pad = 12
    ImageDraw.Draw(mask).rounded_rectangle(
        [door["x"] - pad, door["y"] - pad, door["x"] + door["w"] + pad, door["y"] + door["h"] + pad],
        radius=60,
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    out = im.copy()
    out.putalpha(Image.composite(im.getchannel("A"), Image.new("L", CANVAS, 0), mask))
    return out


def median_opaque_rgb(im: Image.Image) -> tuple[int, int, int] | None:
    px = im.convert("RGBA").load()
    w, h = im.size
    rs: list[int] = []
    gs: list[int] = []
    bs: list[int] = []
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            r, g, b, a = px[x, y]
            if a > 180:
                rs.append(r)
                gs.append(g)
                bs.append(b)
    if not rs:
        return None
    n = len(rs) // 2
    return (sorted(rs)[n], sorted(gs)[n], sorted(bs)[n])


def tint_toward(im: Image.Image, target: tuple[int, int, int], strength: float = 0.72) -> Image.Image:
    src = median_opaque_rgb(im)
    if src is None:
        return im
    dr, dg, db = target[0] - src[0], target[1] - src[1], target[2] - src[2]
    out = im.convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            px[x, y] = (
                max(0, min(255, int(r + dr * strength))),
                max(0, min(255, int(g + dg * strength))),
                max(0, min(255, int(b + db * strength))),
                a,
            )
    return out


def _prepare_layer(
    slot: str,
    image: Image.Image,
    class_id: str,
    body_rgb: tuple[int, int, int] | None = None,
    *,
    pose_master: bool = False,
) -> Image.Image | None:
    if slot == "face" and is_blank_face_panel(image, class_id):
        return None
    image = strip_key_fringe(image)
    if slot in {"eyes", "eyebrows", "mouth", "facial"}:
        image = umber_ink(image)
        image = clip_to_face_region(image, class_id)
    if slot == "rear_atmosphere":
        image = mul_opacity(image, 0.5)
        image = punch_face(image, class_id)
    elif slot == "atmosphere":
        image = mul_opacity(image, 0.28)
        image = punch_face(image, class_id)
    if slot == "headwear":
        image = clamp_headwear(image, class_id)
    if pose_master and body_rgb:
        from .library import recolor_fabric

        image = recolor_fabric(image, body_rgb, class_id=class_id)
    elif slot == "rear_arm" and class_id != "sleeping-bag" and body_rgb:
        image = tint_toward(image, body_rgb)
    return image


def composite_with_report(
    token: dict,
    *,
    missing: str = "error",
    skip_slots: tuple[str, ...] = (),
) -> tuple[Image.Image, dict]:
    """Composite and report painted / skipped / missing slots."""
    class_id = token["class_id"]
    traits = token["traits"]
    canvas = empty()
    missing_files: list[str] = []
    painted: list[str] = []
    skipped: list[str] = []
    body_path = layer_path(class_id, "body", traits.get("body", "none"))
    body_rgb = median_opaque_rgb(_open_rgba(body_path)) if body_path and body_path.exists() else None
    from .library import BODY_COLORS

    body_rgb = BODY_COLORS.get(traits.get("body", "")) or body_rgb
    master = pose_master_slot(class_id, traits)
    for slot, source in resolved_stack(class_id, traits):
        if slot in skip_slots:
            skipped.append(slot)
            continue
        if source == "procedural":
            canvas = Image.alpha_composite(canvas, procedural_contact_shadow(class_id))
            painted.append(slot)
            continue
        if source == "procedural-glow":
            canvas = Image.alpha_composite(canvas, procedural_lantern_glow(class_id))
            painted.append(slot)
            continue
        path = Path(source)
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)))
            continue
        layer = _prepare_layer(
            slot,
            _open_rgba(path),
            class_id,
            body_rgb=body_rgb,
            pose_master=master is not None and slot == master,
        )
        if layer is None:
            skipped.append(slot)
            continue
        canvas = Image.alpha_composite(canvas, layer)
        painted.append(slot)
    if missing_files and missing == "error":
        raise FileNotFoundError("missing layers:\n" + "\n".join(missing_files))
    return canvas, {"painted": painted, "skipped": skipped, "missing": missing_files}


def composite_token(token: dict, *, missing: str = "error", skip_slots: tuple[str, ...] = ()) -> Image.Image:
    image, _report = composite_with_report(token, missing=missing, skip_slots=skip_slots)
    return image


def write_token_png(token: dict, image: Image.Image) -> Path:
    ensure_build()
    path = BUILD / "images" / f"{token['token_id']:04d}.png"
    image.convert("RGBA").save(path, "PNG")
    return path
