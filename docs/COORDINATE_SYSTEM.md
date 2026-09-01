# Coordinate system

**Canonical file:** `config/anchors.json`
**Origin:** top-left of a 1024×1024 canvas
**Units:** pixels
**Y increases downward**
**Grid:** 8px minor, 64px major. Anchors snap to the 8px grid.

Do not invent per-asset coordinates. Register art to this document.

If a blueprint PNG and this table disagree, regenerate the PNG from `anchors.json`. Do not "fix" the JSON to match a drifted drawing.

---

## Shared world (all classes)

| Item | Value |
| --- | --- |
| Character center X | **512** |
| Character baseline Y (feet) | **896** |
| Horizon Y | **640** |
| Ground plane Y | **768** |
| Hard margin | 24 |
| Safe margin | 48 |
| Inner live area | `(48, 48)` → `(976, 976)` |
| Key light | upper left, 11:00, shadows down-right |
| Logo safe (primary) | `(832, 40) 168×128` top-right |
| Logo safe (alternate) | `(24, 856) 168×144` bottom-left — only if top-right loses a fight |
| Ground accessory zone | `(80, 848) 864×132` |
| Character occupancy union | `(152, 112) 720×784` |

Backgrounds may paint the full canvas. They must not place *important* scenery in any class face oval, in the occupancy union's center mass, or in the primary logo safe.

Contact shadows are drawn by the compositor from foot anchors (ellipse, ~28% opacity, 18px blur, +8px below baseline). Illustrated overrides are allowed later; they are not required for Phase 1.

---

## Sleeping Bag — Snug

Tallest, narrowest, goofiest.

```
Character center X      = 512
Character baseline Y    = 896
Bounding box            = x=296 y=112 w=432 h=784   (42.2% × 76.6%)
Peak / crown            = (512, 112)
Face center             = (512, 376)
Face oval               = x=412 y=292 w=200 h=220
Eye center Y            = 360
Left eye                = (456, 360)
Right eye               = (568, 360)
Eye size                = 52×64
Brow baseline Y         = 328
Mouth baseline Y        = 424
Mouth center            = (512, 424)
Left arm anchor         = (304, 472)
Right arm anchor        = (720, 472)
Left hand default       = (248, 600)
Right hand default      = (776, 600)
Left hand raised        = (256, 280)
Right hand raised       = (768, 280)
Left foot anchor        = (448, 896)
Right foot anchor       = (576, 896)
Stance width            = 128
Headwear zone           = x=360 y=64 w=304 h=168
Headwear brim Y         = 216
Handheld left zone      = x=96 y=500 w=220 h=260
Handheld right zone     = x=708 y=500 w=220 h=260
```

Silhouette: mummy capsule. Hood radius 216 about `(512, 328)`. Tapers from width 432 at the shoulders to ~304 at the bag bottom `(Y=848)`, then short legs to the baseline. Zipper lives on the viewer's right. Face is the hood opening, upper-middle, not a sticker.

---

## Small Tent — Pup

Compact 3-person tent. Tent first, character second.

```
Character center X      = 512
Character baseline Y    = 896
Bounding box            = x=224 y=256 w=576 h=640   (56.3% × 62.5%)
Peak                    = (512, 256)
Face center             = (512, 512)
Face oval               = x=418 y=428 w=188 h=200
Eye center Y            = 488
Left eye                = (456, 488)
Right eye               = (568, 488)
Eye size                = 48×58
Brow baseline Y         = 456
Mouth baseline Y        = 552
Mouth center            = (512, 552)
Left arm anchor         = (240, 560)
Right arm anchor        = (784, 560)
Left hand default       = (184, 640)
Right hand default      = (840, 640)
Left hand raised        = (200, 320)
Right hand raised       = (824, 320)
Left foot anchor        = (400, 896)
Right foot anchor       = (624, 896)
Stance width            = 224
Headwear zone           = x=400 y=176 w=224 h=160
Headwear brim Y         = 320
Handheld left zone      = x=48 y=540 w=200 h=260
Handheld right zone     = x=776 y=540 w=200 h=260
Door                    = x=400 y=400 w=224 h=420
```

Silhouette: soft A-frame with a hint of dome. Base corners `(224, 880)` and `(800, 880)`. Two poles from the peak. Face in the D-door. Hats perch on the peak; brim is above the door.

---

## Large Tent — Lodge

Wider, more wall, larger door. Must read as the bigger tent beside a Pup without a label.

```
Character center X      = 512
Character baseline Y    = 896
Bounding box            = x=152 y=176 w=720 h=720   (70.3% × 70.3%)
Peak                    = (512, 176)
Face center             = (512, 464)
Face oval               = x=400 y=368 w=224 h=232
Eye center Y            = 440
Left eye                = (448, 440)
Right eye               = (576, 440)
Eye size                = 56×68
Brow baseline Y         = 404
Mouth baseline Y        = 512
Mouth center            = (512, 512)
Left arm anchor         = (176, 536)
Right arm anchor        = (848, 536)
Left hand default       = (120, 620)
Right hand default      = (904, 620)
Left hand raised        = (144, 268)
Right hand raised       = (880, 268)
Left foot anchor        = (360, 896)
Right foot anchor       = (664, 896)
Stance width            = 304
Headwear zone           = x=360 y=80 w=304 h=176
Headwear brim Y         = 256
Handheld left zone      = x=48 y=500 w=180 h=280
Handheld right zone     = x=796 y=500 w=180 h=280
Door                    = x=368 y=340 w=288 h=500
Shoulders / ridge       = (280, 320) — (744, 320)
```

Silhouette: cabin-dome. Peak, ridge, vertical-ish side walls, wider skirt. Extra panel seams belong here. Vestibule, if present, occupies front ground and therefore excludes some ground accessories.

---

## Registration tolerances

From `config/anchors.json`:

| Check | Tolerance |
| --- | --- |
| Anchor | 6px |
| Bounding box | 12px |
| Face center | 4px |
| Eye baseline | 3px |
| Foot Y | 4px |
| Occupancy IoU | ≥ 0.82 |
| Snap-translate | ≤ 12px, then redraw |

The image model is not trusted to hit these numbers because a prompt said so. `warm_company.register` measures. Failed layers are not composited.

---

## Why these proportions

The brief's starting ranges were 35–45% / 50–60% / 65–75% width. Locked values 42% / 56% / 70% sit comfortably inside those ranges, snap to the 8px grid, and leave:

- 48px+ of sky above the Snug
- 152px of side margin on the Lodge (enough for a mug, not enough for a second character)
- a shared baseline so a future family portrait is not a photoshop job
- a quiet top-right for a future signature-sized logo

Face Y values are *not* unified on purpose. A door-face on a short tent cannot live at the same Y as a hood-face on a tall bag without lying about the object. Thumbnail identity comes from silhouette first, face second.
