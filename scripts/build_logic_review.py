"""Final combinatorial QA contact sheets and audit reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import composite_token  # noqa: E402
from warm_company.generate import generate_collection, roll_traits  # noqa: E402
from warm_company.logic_qa import full_audit  # noqa: E402
from warm_company.resolve import resolve_plan  # noqa: E402
from warm_company.review import review_token  # noqa: E402
from warm_company.rng import SeededStream  # noqa: E402

OUT = ROOT / "build" / "logic-review-final"


def font(size: int):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def sheet(title: str, cells: list[tuple[str, Image.Image]], cols: int = 5, size: int = 180) -> Image.Image:
    rows = max(1, (len(cells) + cols - 1) // cols)
    img = Image.new("RGB", (24 + cols * (size + 10), 52 + rows * (size + 28)), (16, 20, 28))
    d = ImageDraw.Draw(img)
    d.text((12, 10), title, fill=(240, 236, 228), font=font(18))
    for i, (label, im) in enumerate(cells):
        r, c = divmod(i, cols)
        x, y = 12 + c * (size + 10), 44 + r * (size + 28)
        vis = im.convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
        img.paste(vis, (x, y))
        d.text((x, y + size + 2), label[:26], fill=(200, 206, 212), font=font(11))
    return img


def render(class_id: str, **extra: str) -> tuple[Image.Image, dict]:
    tok = review_token(class_id, **extra)
    plan = resolve_plan(class_id, tok["traits"])
    im = composite_token(tok, missing="allow")
    return im, plan


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = SeededStream("logic-review-final")
    by_class: dict[str, list[tuple[str, Image.Image]]] = {cid: [] for cid in config.CLASS_IDS}
    for class_id in config.CLASS_IDS:
        for i in range(50):
            traits = roll_traits(class_id, 9, rng.fork(f"{class_id}:{i}"))
            tok = {"class_id": class_id, "traits": traits, "token_id": i}
            im = composite_token(tok, missing="allow")
            plan = resolve_plan(class_id, traits)
            label = f"{class_id[:4]} {traits.get('held_item','none')[:6]} h{plan['hands']}"
            by_class[class_id].append((label, im))
    sheet("QA Snug (50)", by_class["sleeping-bag"]).save(OUT / "contact-snug.png")
    sheet("QA Pup (50)", by_class["small-tent"]).save(OUT / "contact-pup.png")
    sheet("QA Lodge (50)", by_class["large-tent"]).save(OUT / "contact-lodge.png")

    held = [
        ("Snug coffee", *render("sleeping-bag", held_item="coffee", arm_pose="hold-item")[:1]),
        ("Pup map", *render("small-tent", held_item="map", arm_pose="hold-two-hand")[:1]),
        ("Lodge lantern", *render("large-tent", held_item="lantern", arm_pose="hold-item")[:1]),
    ]
    sheet("Held-item interactions", [(a, b) for a, b in held], cols=3, size=280).save(OUT / "held-items.png")

    hats: list[tuple[str, Image.Image]] = []
    for t in config.traits()["traits"]:
        if t["slot"] != "headwear" or t["id"] == "none":
            continue
        for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
            if "shared" not in t["classes"] and class_id not in t["classes"]:
                continue
            im, _plan = render(class_id, headwear=t["id"])
            hats.append((f"{label} {t['name']}", im))
    sheet("Headwear fit by class", hats, cols=3, size=210).save(OUT / "headwear-fit.png")

    feet: list[tuple[str, Image.Image]] = []
    for t in config.traits()["traits"]:
        if t["slot"] != "footwear" or t["id"] == "none":
            continue
        for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
            if class_id not in t["classes"]:
                continue
            im, _plan = render(class_id, footwear=t["id"])
            feet.append((f"{label} {t['name']}", im))
    sheet("Footwear fit by class", feet, cols=3, size=210).save(OUT / "footwear-fit.png")

    poses: list[tuple[str, Image.Image]] = []
    pose_extra = {
        "rest": {},
        "wave": {},
        "hold-item": {"held_item": "coffee"},
        "hold-two-hand": {"held_item": "map"},
    }
    for t in config.traits()["traits"]:
        if t["slot"] != "arm_pose" or t["id"] == "none":
            continue
        for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
            if class_id not in t["classes"]:
                continue
            extra = dict(pose_extra.get(t["id"], {}))
            extra["arm_pose"] = t["id"]
            if t["id"] == "hold-item" and class_id == "large-tent":
                extra["held_item"] = "lantern"
            if t["id"] == "hold-item" and class_id == "sleeping-bag":
                extra["held_item"] = "coffee"
            im, _plan = render(class_id, **extra)
            poses.append((f"{label} {t['name']}", im))
    sheet("Arm poses", poses, cols=4, size=210).save(OUT / "arm-poses.png")

    ground = [
        ("none", render("sleeping-bag")[0]),
        ("campfire-glow", render("sleeping-bag", rear_environment="campfire-glow")[0]),
        ("Lodge lantern + glow", render("large-tent", held_item="lantern", arm_pose="hold-item", rear_environment="campfire-glow")[0]),
        ("snow + beanie", render("sleeping-bag", atmosphere="light-snow", headwear="beanie", background="cold-blue-night")[0]),
    ]
    sheet("Ground / atmosphere interactions", ground, cols=2, size=280).save(OUT / "ground-interactions.png")

    specials = []
    for spec in config.rarity()["specials"]["characters"]:
        traits = {**review_token(spec["class"])["traits"], **spec["traits"]}
        tok = {"class_id": spec["class"], "traits": traits, "token_id": 0}
        specials.append((spec["name"], composite_token(tok, missing="allow")))
    sheet("Specials", specials, cols=4, size=220).save(OUT / "specials.png")

    worst = [
        ("empty grip blocked", render("sleeping-bag")[0]),
        ("coffee composite", render("sleeping-bag", held_item="coffee", arm_pose="hold-item")[0]),
        ("map composite", render("small-tent", held_item="map", arm_pose="hold-two-hand")[0]),
        ("lantern composite", render("large-tent", held_item="lantern", arm_pose="hold-item")[0]),
        ("wave", render("sleeping-bag", arm_pose="wave")[0]),
        ("snow boots overlay", render("sleeping-bag", footwear="snow-boots")[0]),
        ("halo Lodge", render("large-tent", headwear="halo")[0]),
        ("earflap Snug", render("sleeping-bag", headwear="earflap-beanie")[0]),
        ("extra-panels Lodge", render("large-tent", structural="extra-panels")[0]),
        ("max-ish Snug", render("sleeping-bag", headwear="beanie", atmosphere="light-snow", facial="blush", footwear="work-boots")[0]),
    ]
    sheet("Stress / formerly failing cases", worst, cols=5, size=180).save(OUT / "worst-cases.png")

    audit = full_audit(n_per_class=1000)
    (OUT / "resolved-resource-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    pairwise = {"classes": audit["pairwise"]}
    (OUT / "pairwise-compatibility-report.json").write_text(json.dumps(pairwise, indent=2) + "\n", encoding="utf-8")
    print("audit unresolved", audit["unresolved_physical_resource_violations"], "ok", audit["ok"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
