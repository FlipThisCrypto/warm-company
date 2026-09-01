"""Final 50-iteration review artifacts: canonical sheet, stress, strips, before/after."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company.composite import composite_token  # noqa: E402
from warm_company.review import STRIP_TOKENS, reconstruction_strip  # noqa: E402

OUT = ROOT / "build" / "review-final"
CANVAS = (1024, 1024)
BASELINE = "d7d466a35c1281276cb900eba7fbf9075d728962"


def token(class_id: str, **traits: str) -> dict:
    base = {
        "background": "winter-sunrise",
        "rear_environment": "none",
        "rear_accessory": "none",
        "arm_pose": "rest",
        "held_item": "none",
        "body": {"sleeping-bag": "ember-rust", "small-tent": "forest-green", "large-tent": "royal-blue"}[class_id],
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


def font(size: int):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", size)
    except OSError:
        return ImageFont.load_default()


def character_only(class_id: str, **traits: str) -> Image.Image:
    return composite_token(token(class_id, **traits), missing="allow", skip_slots=("background", "rear_atmosphere", "atmosphere"))


def silhouette(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    ink = Image.new("RGBA", im.size, (28, 24, 22, 255))
    ink.putalpha(a)
    paper = Image.new("RGBA", im.size, (236, 232, 224, 255))
    return Image.alpha_composite(paper, ink)


def grayscale_on_bg(im: Image.Image) -> Image.Image:
    rgb = Image.new("RGB", im.size, (24, 26, 30))
    rgb.paste(im.convert("RGB"), mask=im.getchannel("A"))
    return ImageOps.grayscale(rgb).convert("RGB")


def labeled_row(title: str, images: list[tuple[str, Image.Image]], thumb: int = 220) -> Image.Image:
    f = font(16)
    w = 24 + len(images) * (thumb + 16)
    h = 48 + thumb + 28
    sheet = Image.new("RGB", (w, h), (16, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.text((12, 8), title, fill=(240, 236, 228), font=f)
    x = 12
    for name, im in images:
        vis = im.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS)
        sheet.paste(vis, (x, 36))
        d.text((x, 36 + thumb + 4), name, fill=(200, 206, 212), font=font(13))
        x += thumb + 16
    return sheet


def stack_sheets(sheets: list[Image.Image]) -> Image.Image:
    w = max(s.size[0] for s in sheets)
    h = sum(s.size[1] for s in sheets) + 8 * (len(sheets) - 1)
    out = Image.new("RGB", (w, h), (16, 20, 28))
    y = 0
    for s in sheets:
        out.paste(s, (0, y))
        y += s.size[1] + 8
    return out


def git_show(path: str) -> Image.Image | None:
    try:
        data = subprocess.check_output(["git", "show", f"{BASELINE}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError:
        return None
    from io import BytesIO

    return Image.open(BytesIO(data)).convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    snug = composite_token(token("sleeping-bag"), missing="allow")
    pup = composite_token(token("small-tent"), missing="allow")
    lodge = composite_token(token("large-tent"), missing="allow")
    snug.save(OUT / "snug-bare.png")
    pup.save(OUT / "pup-bare.png")
    lodge.save(OUT / "lodge-bare.png")

    family = labeled_row("Bare / default — true relative scale", [
        ("Snug", snug),
        ("Pup", pup),
        ("Lodge", lodge),
    ])
    gray = labeled_row("Grayscale", [
        ("Snug", grayscale_on_bg(snug)),
        ("Pup", grayscale_on_bg(pup)),
        ("Lodge", grayscale_on_bg(lodge)),
    ])
    sil = labeled_row("Silhouette", [
        ("Snug", silhouette(character_only("sleeping-bag"))),
        ("Pup", silhouette(character_only("small-tent"))),
        ("Lodge", silhouette(character_only("large-tent"))),
    ])
    mini = labeled_row("128px thumbnail", [
        ("Snug", snug.resize((128, 128), Image.Resampling.LANCZOS).resize((220, 220), Image.Resampling.NEAREST)),
        ("Pup", pup.resize((128, 128), Image.Resampling.LANCZOS).resize((220, 220), Image.Resampling.NEAREST)),
        ("Lodge", lodge.resize((128, 128), Image.Resampling.LANCZOS).resize((220, 220), Image.Resampling.NEAREST)),
    ])
    stack_sheets([family, gray, sil, mini]).save(OUT / "canonical-sheet.png")

    stress = [
        ("snug-hat-snow", composite_token(token("sleeping-bag", headwear="beanie", atmosphere="light-snow", background="cold-blue-night", body="navy-night"), missing="allow")),
        ("snug-coffee", composite_token(token("sleeping-bag", held_item="coffee", arm_pose="hold-item"), missing="allow")),
        ("pup-hat", composite_token(token("small-tent", headwear="beanie"), missing="allow")),
        ("pup-map", composite_token(token("small-tent", held_item="map", arm_pose="hold-two-hand"), missing="allow")),
        ("lodge-hat-orange", composite_token(token("large-tent", headwear="beanie", body="camp-orange"), missing="allow")),
        ("lodge-lantern-night", composite_token(token("large-tent", held_item="lantern", arm_pose="hold-item", atmosphere="light-snow", background="cold-blue-night"), missing="allow")),
    ]
    for name, im in stress:
        im.save(OUT / f"{name}.png")
    labeled_row("Stress sample — simple and difficult legal combos", stress, thumb=200).save(OUT / "stress-sheet.png")

    reconstruction_strip("Snug reconstruction", STRIP_TOKENS["snug"]).save(OUT / "strip-snug.png")
    reconstruction_strip("Pup reconstruction", STRIP_TOKENS["pup"]).save(OUT / "strip-pup.png")
    reconstruction_strip("Lodge reconstruction", STRIP_TOKENS["lodge"]).save(OUT / "strip-lodge.png")

    before = git_show("build/review-v3/contact-sheet.png")
    after_preview = ROOT / "build" / "preview" / "sheet.png"
    after = Image.open(after_preview).convert("RGB") if after_preview.exists() else family
    if before is not None:
        tw = 480
        bh = int(before.size[1] * tw / before.size[0])
        ah = int(after.size[1] * tw / after.size[0])
        sheet = Image.new("RGB", (24 + tw * 2, 48 + max(bh, ah)), (16, 20, 28))
        d = ImageDraw.Draw(sheet)
        d.text((12, 10), "Before (d7d466a review-v3) vs after (compositor path)", fill=(240, 236, 228), font=font(16))
        sheet.paste(before.resize((tw, bh), Image.Resampling.LANCZOS), (12, 40))
        sheet.paste(after.resize((tw, ah), Image.Resampling.LANCZOS), (24 + tw, 40))
        sheet.save(OUT / "before-after.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
