"""Labeled candidate-inventory contact sheets and a 100-token review pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import config  # noqa: E402
from warm_company.composite import composite_token  # noqa: E402
from warm_company.generate import generate_collection  # noqa: E402
from warm_company.library import required_paths  # noqa: E402
from warm_company.paths import BUILD, LAYERS  # noqa: E402
from warm_company.review import review_token  # noqa: E402

OUT = BUILD / "review-inventory"
OUT.mkdir(parents=True, exist_ok=True)


def font(size: int):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def thumb(im: Image.Image, size: int) -> Image.Image:
    return im.convert("RGB").resize((size, size), Image.Resampling.LANCZOS)


def sheet(title: str, cells: list[tuple[str, Image.Image]], cols: int = 4, size: int = 220) -> Image.Image:
    f = font(18)
    fs = font(13)
    rows = (len(cells) + cols - 1) // cols
    w = 24 + cols * (size + 12)
    h = 56 + rows * (size + 32)
    img = Image.new("RGB", (max(w, 400), max(h, 120)), (18, 22, 30))
    d = ImageDraw.Draw(img)
    d.text((16, 12), title, fill=(240, 236, 228), font=f)
    for i, (label, im) in enumerate(cells):
        r, c = divmod(i, cols)
        x, y = 16 + c * (size + 12), 48 + r * (size + 32)
        img.paste(thumb(im, size), (x, y))
        d.text((x, y + size + 4), label[:28], fill=(200, 206, 212), font=fs)
    return img


def compose(class_id: str, **traits: str) -> Image.Image:
    return composite_token(review_token(class_id, **traits), missing="allow")


def traits_in(slot: str, class_id: str | None = None) -> list[dict]:
    rows = []
    for t in config.traits()["traits"]:
        if t["slot"] != slot or t["id"] == "none":
            continue
        if class_id and "shared" not in (t.get("classes") or []) and class_id not in (t.get("classes") or []):
            continue
        rows.append(t)
    return rows


def main() -> None:
    # A backgrounds
    cells = []
    for t in traits_in("background"):
        p = LAYERS / "shared" / "backgrounds" / f"{t['id']}.png"
        if p.exists():
            cells.append((t["name"], Image.open(p)))
    sheet("A. Backgrounds", cells, cols=4, size=240).save(OUT / "A-backgrounds.png")

    # B C D bodies
    for class_id, title, fname in (
        ("sleeping-bag", "B. Snug body colors / treatments", "B-snug-bodies.png"),
        ("small-tent", "C. Pup body colors / treatments", "C-pup-bodies.png"),
        ("large-tent", "D. Lodge body colors / treatments", "D-lodge-bodies.png"),
    ):
        cells = []
        for t in traits_in("body", class_id):
            cells.append((t["name"], compose(class_id, body=t["id"])))
        for t in traits_in("pattern", class_id):
            cells.append((f"pattern:{t['name']}", compose(class_id, pattern=t["id"])))
        for t in traits_in("structural", class_id):
            cells.append((f"struct:{t['name']}", compose(class_id, structural=t["id"])))
        sheet(title, cells, cols=4, size=200).save(OUT / fname)

    # E faces on canonical hood/door of each class
    cells = []
    for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
        for t in traits_in("eyes", class_id):
            cells.append((f"{label} eyes/{t['name']}", compose(class_id, eyes=t["id"])))
        for t in traits_in("mouth", class_id):
            cells.append((f"{label} mouth/{t['name']}", compose(class_id, mouth=t["id"])))
        for t in traits_in("facial", class_id):
            cells.append((f"{label} facial/{t['name']}", compose(class_id, facial=t["id"])))
    sheet("E. Expressions on hood/door (not floating crops)", cells, cols=5, size=180).save(OUT / "E-faces.png")

    # F arms
    cells = []
    for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
        for t in traits_in("arm_pose", class_id):
            extra = {}
            if t["id"] in {"hold-item"}:
                extra = {"held_item": "coffee", "arm_pose": "hold-item"}
            elif t["id"] == "hold-two-hand":
                extra = {"held_item": "map", "arm_pose": "hold-two-hand"}
            else:
                extra = {"arm_pose": t["id"]}
            cells.append((f"{label} {t['name']}", compose(class_id, **extra)))
    sheet("F. Arms and poses", cells, cols=4, size=200).save(OUT / "F-arms.png")

    # G footwear
    cells = []
    for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
        for t in traits_in("footwear", class_id):
            cells.append((f"{label} {t['name']}", compose(class_id, footwear=t["id"])))
    sheet("G. Footwear on each class", cells, cols=3, size=200).save(OUT / "G-footwear.png")

    # H headwear on three classes
    cells = []
    for t in traits_in("headwear"):
        for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
            if "shared" not in t["classes"] and class_id not in t["classes"]:
                continue
            cells.append((f"{label} {t['name']}", compose(class_id, headwear=t["id"])))
    sheet("H. Headwear on each class", cells, cols=3, size=210).save(OUT / "H-headwear.png")

    # I handhelds — each class, with the matching hold pose
    cells = []
    for class_id, label in (("sleeping-bag", "Snug"), ("small-tent", "Pup"), ("large-tent", "Lodge")):
        for t in traits_in("held_item", class_id):
            pose = "hold-two-hand" if t.get("two_handed") else "hold-item"
            cells.append((f"{label} {t['name']}", compose(class_id, held_item=t["id"], arm_pose=pose)))
    sheet("I. Handheld items with the holding pose", cells, cols=4, size=200).save(OUT / "I-handheld.png")

    # J accessories — body accessories were pruned as clip-art; show remaining ground/rear env
    cells = []
    for t in traits_in("body_accessory"):
        extra = {"body_accessory": t["id"]}
        if t["id"] == "backpack-straps":
            extra["rear_accessory"] = "backpack"
        cells.append((f"body {t['name']}", compose("sleeping-bag", **extra)))
    for t in traits_in("ground_accessory"):
        cells.append((f"ground {t['name']}", compose("sleeping-bag", ground_accessory=t["id"])))
    for t in traits_in("rear_environment"):
        cells.append((f"rear {t['name']}", compose("sleeping-bag", rear_environment=t["id"])))
    if not cells:
        cells.append(("none retained", compose("sleeping-bag")))
    sheet("J. Accessories (body pruned; ground + rear env)", cells, cols=4, size=200).save(OUT / "J-accessories.png")

    # K atmosphere
    cells = []
    for t in traits_in("atmosphere"):
        cells.append((t["name"], compose("sleeping-bag", atmosphere=t["id"], background="cold-blue-night", body="navy-night")))
    sheet("K. Atmosphere over night Snug", cells, cols=3, size=240).save(OUT / "K-atmosphere.png")

    # L specials
    cells = []
    for spec in config.rarity()["specials"]["characters"]:
        traits = dict(spec["traits"])
        tok = {"class_id": spec["class"], "traits": {**review_token(spec["class"])["traits"], **traits}, "token_id": 0}
        cells.append((spec["name"], composite_token(tok, missing="allow")))
    sheet("L. Specials", cells, cols=4, size=220).save(OUT / "L-specials.png")

    # M master index
    exclude_map: dict[str, list[str]] = {}
    for rule in config.compatibility().get("rules", []):
        if "excludes" in rule:
            slot = rule["excludes"].get("slot", "")
            ids = rule["excludes"].get("ids") or []
            for tid in ids:
                exclude_map.setdefault(f"{slot}/{tid}", []).append(rule["id"])
    lines = [
        "# Warm Company candidate trait index",
        "",
        "| Category | Name | Id | Classes | Weight | Band | Dependencies | Exclusions | PNG path(s) |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    from warm_company.library import required_paths as req
    for t in config.traits()["traits"]:
        if t.get("not_a_layer"):
            continue
        paths = req(t)
        rel = ", ".join(str(p.relative_to(ROOT)).replace("\\", "/") for p in paths[:6])
        deps = t.get("requires_pose") or t.get("files") or ""
        excl = ", ".join(exclude_map.get(f"{t['slot']}/{t['id']}", []))
        lines.append(
            f"| {t['slot']} | {t['name']} | `{t['id']}` | {', '.join(t.get('classes') or [])} | {t.get('weight', 0)} | {t.get('band', '')} | {deps} | {excl} | {rel} |"
        )
    lines.extend(
        [
            "",
            "## Human-review flags (pre-approval)",
            "",
            "- Dusty Rose: confirm it reads pink, not mauve, especially on Pup/Lodge.",
            "- Body colors are fabric recolors of one silhouette per class; Snug plaid/patchwork and Pup two-tone-panel are the non-recolor treatments.",
            "- Factory clip-art (thermos, PIL eyebrows/sunglasses/stars/steady-snow/tiny-campfire, rest-copied hold rear-arms) was dropped, not redrawn.",
            "- Pose-master grips only: Snug coffee, Pup map, Lodge lantern. Held items are class-restricted to those three.",
            "- Body accessories: none retained.",
            "- Eyebrows: none only (Lodge eyes already include brow marks).",
            "- Rest-pose rear arms still crop hard against the body (Snug/Pup).",
            "- Some hats are class-restricted (bucket Pup-only, trapper/crown/halo Lodge-only).",
            "- Quiet Overpass background: dignified empty infrastructure; confirm it is not too literal.",
            "- Wild Purple on tents is not a pink substitute; easy to cut.",
        ]
    )
    (OUT / "M-trait-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 100 review composites
    result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
    by_class = {"sleeping-bag": [], "small-tent": [], "large-tent": []}
    for tok in result["tokens"]:
        by_class[tok["class_id"]].append(tok)
    picked = by_class["sleeping-bag"][:50] + by_class["small-tent"][:25] + by_class["large-tent"][:25]
    cells = []
    for tok in picked:
        im = composite_token(tok, missing="allow")
        label = f"#{tok['token_id']} {tok['dna'][:8]}"
        cells.append((label, im))
    # two sheets of 50
    sheet("N. Review 1–50 (Snug)", cells[:50], cols=5, size=180).save(OUT / "N-review-100-a.png")
    sheet("N. Review 51–100 (Pup + Lodge)", cells[50:], cols=5, size=180).save(OUT / "N-review-100-b.png")
    print("wrote", OUT, "cells", len(cells))


if __name__ == "__main__":
    main()
