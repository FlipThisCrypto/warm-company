"""Assemble exact Grok Image prompts from the frozen style prefix + geometry."""

from __future__ import annotations

import json
from typing import Any

from . import config
from .paths import BUILD, PROMPTS, ensure_build

LAYER_INSTRUCTIONS: dict[str, str] = {
    "canonical": (
        "Draw the complete canonical character of this class in the default rest pose, "
        "no headwear, no handheld item, standard face, normal eyes, neutral brows, smile, "
        "basic shoes, default body color, default structural details. This image becomes "
        "the master reference for every later layer of this class."
    ),
    "body": "Paint only the body/fabric silhouette of the character, no face features, no arms, no legs, no accessories.",
    "pattern": "Paint only the fabric pattern, already clipped to the body silhouette, no new seams that move structure.",
    "structural": "Paint only structural details (poles, zipper, baffles, door trim, guy lines) registered to the master silhouette.",
    "face": "Paint only the face base panel (bag hood opening or tent door panel) with no eyes, brows, or mouth.",
    "eyes": "Paint only the eyes, already placed on the class eye anchors. No other facial features.",
    "eyebrows": "Paint only the eyebrows on the class brow baseline. No other facial features.",
    "mouth": "Paint only the mouth on the class mouth baseline. No other facial features.",
    "facial": "Paint only this facial extra (blush, glasses, etc.) registered to the face oval.",
    "front_arm": "Paint only the front forearm/hand for this pose. The hand must grip any held object. Do not draw a disconnected tube.",
    "rear_arm": "Paint only the arm including extra shoulder that will sit BEHIND the body. Same canvas position as the canonical. Magenta #FF00FF background. Do not add extra quilt pads or disconnected panels.",
    "rear_leg": "Paint only the legs with extra length above the hem that the body will hide. Soles on the shared baseline. Magenta #FF00FF background. No tent poles.",
    "legs": "Paint only the visible lower cartoon legs in front of the hem, ending on the shared baseline.",
    "footwear": "Paint only the footwear, soles kissing the shared baseline at the foot anchors. No floating shoes. Connect to the visible legs.",
    "headwear": "Paint only a human-scale hat at the PREFERRED headwear size, never filling the legal maximum zone. Tents: perch on the peak, slightly absurd, do not hide structure. Sleeping bags: sit on the hood, much smaller than the hood.",
    "front_held": "Paint only the held item actually gripped in the hand, correct occlusion, same line weight as the canonical. Not a product photo.",
    "rear_held": "Paint only the portion of the held item that must sit behind the hand or body (for example a lantern handle).",
    "light_effect": "Paint only a small warm transparent glow, localized, not a 3D relight of the character.",
    "body_accessory": "Paint only the front body accessory in the body accessory zone.",
    "rear_accessory": "Paint only the rear accessory sitting behind the body.",
    "background": "Paint a complete 1024x1024 winter environment. Keep the character occupancy zone quiet. No figures.",
    "atmosphere": "Paint only weather/atmosphere particles. Leave the inflated face oval fully empty (alpha zero).",
    "ground_accessory": "Paint only a small ground object sitting on the snow in the ground accessory zone, not covering feet.",
}


def geometry_block(class_id: str | None) -> str:
    world = config.anchors()["world"]
    lines = [
        f"Canvas exactly 1024x1024 pixels, 1:1, origin top-left.",
        f"Shared world: center X={world['center_x']}, baseline Y={world['baseline_y']}, "
        f"horizon Y={world['horizon_y']}, ground plane Y={world['ground_plane_y']}.",
        f"Safe margin 48px. Hard margin 24px. Logo safe zone top-right x=832 y=40 w=168 h=128 stays visually quiet.",
        f"Warm key light from upper left, shadows fall down-right.",
    ]
    if class_id:
        spec = config.class_spec(class_id)
        box = spec["bounding_box"]
        lines += [
            f"Class {spec['label']} ({spec['family_name']}): bounding box x={box['x']} y={box['y']} w={box['w']} h={box['h']}.",
            f"Character center X={spec['character_center_x']}, baseline Y={spec['character_baseline_y']}.",
            f"Peak=({spec['peak']['x']},{spec['peak']['y']}). Face center=({spec['face_center']['x']},{spec['face_center']['y']}).",
            f"Eye baseline Y={spec['eye_baseline_y']}; left eye=({spec['eye_left']['x']},{spec['eye_left']['y']}); "
            f"right eye=({spec['eye_right']['x']},{spec['eye_right']['y']}).",
            f"Mouth baseline Y={spec['mouth_baseline_y']} at ({spec['mouth_center']['x']},{spec['mouth_center']['y']}).",
            f"Left arm anchor=({spec['left_arm_anchor']['x']},{spec['left_arm_anchor']['y']}); "
            f"right arm anchor=({spec['right_arm_anchor']['x']},{spec['right_arm_anchor']['y']}).",
            f"Left foot=({spec['left_foot_anchor']['x']},{spec['left_foot_anchor']['y']}); "
            f"right foot=({spec['right_foot_anchor']['x']},{spec['right_foot_anchor']['y']}).",
            f"Headwear legal zone x={spec['headwear_zone']['x']} y={spec['headwear_zone']['y']} "
            f"w={spec['headwear_zone']['w']} h={spec['headwear_zone']['h']}.",
            f"Headwear PREFERRED draw size x={spec['headwear_preferred']['x']} y={spec['headwear_preferred']['y']} "
            f"w={spec['headwear_preferred']['w']} h={spec['headwear_preferred']['h']}, brim Y={spec['headwear_brim_y']}.",
            f"Hem Y={spec['hem_y']}. Arm roots behind body={spec['arm_root_behind']}. Face shape={spec['face_shape']}.",
            spec["silhouette"]["construction"],
        ]
    return " ".join(lines)


def class_template(class_id: str) -> str:
    spec = config.class_spec(class_id)
    if class_id == "sleeping-bag":
        return (
            f"A tall, narrow anthropomorphic winter sleeping bag character named a {spec['family_name']}. "
            "Mummy-bag silhouette with a rounded hood, visible quilting baffles, a zipper suggestion on the viewer's right, "
            "a face integrated into the upper-middle hood opening, short goofy legs and cartoon arms. "
            "It should feel friendly and slightly goofy, and remain the narrowest, tallest member of the family."
        )
    if class_id == "small-tent":
        return (
            f"A compact anthropomorphic 3-person tent character named a {spec['family_name']}. "
            "It must read as a tent FIRST and a character second: soft A-frame with a hint of dome, "
            "front D-shaped door holding the face, two visible poles, a low snow skirt, arms from the side walls, "
            "feet under the hem. Clearly smaller than the six-person Lodge."
        )
    return (
        f"A substantial anthropomorphic 6-person tent character named a {spec['family_name']}. "
        "Wider and taller than the Pup, with side walls, a ridge pole, a larger D-door that holds the face, "
        "more paneling, a wider footprint, arms from the side walls, feet under the hem. "
        "Immediately reads as the larger tent when standing beside a Pup."
    )


def assemble(
    *,
    kind: str,
    class_id: str | None = None,
    layer_instruction: str,
    extra: str = "",
    transparent: bool = True,
) -> str:
    style = config.prompts()["master_style_prefix"]
    parts = [style]
    if class_id:
        parts.append(class_template(class_id))
    parts.append(layer_instruction)
    if extra:
        parts.append(extra)
    parts.append(geometry_block(class_id))
    if transparent:
        parts.append(config.prompts()["transparency_instruction"])
    else:
        parts.append(config.prompts()["background_instruction"])
    parts.append("Avoid: " + config.prompts()["negative_constraints"] + ".")
    return " ".join(parts)


def prompt_for_trait(class_id: str | None, slot: str, trait: dict[str, Any]) -> dict[str, Any]:
    transparent = slot != "background"
    instruction = LAYER_INSTRUCTIONS.get(slot, f"Paint only the {slot} trait '{trait['name']}'.")
    extra = f"Trait: {trait['name']}. {trait.get('notes') or ''} Render this specific variant, not a generic stand-in."
    if slot == "background":
        class_id = None
    return {
        "id": f"{class_id or 'shared'}/{slot}/{trait['id']}",
        "class_id": class_id,
        "slot": slot,
        "trait_id": trait["id"],
        "name": trait["name"],
        "transparent": transparent,
        "use_image_edit_from_canonical": slot != "background" and slot != "canonical",
        "prompt": assemble(
            kind=slot,
            class_id=class_id,
            layer_instruction=instruction,
            extra=extra,
            transparent=transparent,
        ),
    }


def export_prompt_library(phase: int = 9) -> list[dict[str, Any]]:
    ensure_build()
    rows: list[dict[str, Any]] = []
    for class_id in config.CLASS_IDS:
        rows.append(
            {
                "id": f"{class_id}/canonical/master",
                "class_id": class_id,
                "slot": "canonical",
                "trait_id": "master",
                "name": f"Canonical {config.class_spec(class_id)['label']}",
                "transparent": True,
                "use_image_edit_from_canonical": False,
                "prompt": assemble(
                    kind="canonical",
                    class_id=class_id,
                    layer_instruction=LAYER_INSTRUCTIONS["canonical"],
                    extra=f"Default body color is {('trail-olive' if class_id != 'sleeping-bag' else 'ember-rust')}.",
                    transparent=True,
                ),
            }
        )
    for trait in config.traits()["traits"]:
        if trait.get("phase", 3) > phase:
            continue
        if trait["id"] == "none":
            continue
        classes = trait.get("classes") or []
        slot = trait["slot"]
        if "shared" in classes or slot in {"background", "rear_environment", "ground_accessory", "atmosphere"}:
            rows.append(prompt_for_trait(None, slot, trait))
        else:
            for class_id in config.CLASS_IDS:
                if class_id in classes:
                    rows.append(prompt_for_trait(class_id, slot, trait))
    (BUILD / "prompts" / "library.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (PROMPTS / "library.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    master = {
        "master_style_prefix": config.prompts()["master_style_prefix"],
        "negative_constraints": config.prompts()["negative_constraints"],
        "transparency_instruction": config.prompts()["transparency_instruction"],
        "canonical_lock": config.prompts()["canonical_lock"],
        "count": len(rows),
    }
    (PROMPTS / "MASTER_STYLE.md").write_text(
        "# Master style prefix\n\n" + config.prompts()["master_style_prefix"] + "\n",
        encoding="utf-8",
    )
    canon_dir = PROMPTS / "canonical"
    canon_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        if row["slot"] == "canonical":
            (canon_dir / f"{row['class_id']}.txt").write_text(row["prompt"] + "\n", encoding="utf-8")
    (BUILD / "prompts" / "meta.json").write_text(json.dumps(master, indent=2), encoding="utf-8")
    return rows
