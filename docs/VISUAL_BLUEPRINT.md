# Visual blueprint — three master silhouettes

This is the Phase-0 geometry proposal. It is **not** production character art. Shapes are occupancy envelopes rendered from `config/anchors.json`.

Render / refresh:

```
python -m warm_company blueprints
```

Then open `docs/blueprints/index.html`.

| File | What it is |
| --- | --- |
| `templates/sleeping-bag/blueprint.png` | Labeled Snug |
| `templates/small-tent/blueprint.png` | Labeled Pup |
| `templates/large-tent/blueprint.png` | Labeled Lodge |
| `templates/world/family-lineup.png` | The three 1024 canvases in a row, shared horizon and baseline |
| `templates/world/scale-comparison.png` | All three occupancy envelopes overlaid at true size |
| `templates/{class}/occupancy.png` | Registration mask |
| `templates/{class}/guides.png` | High-contrast overlay for `image_edit` |
| `templates/{class}/blueprint.svg` | Exact SVG of anchors |

---

## Family at a glance

Same ground. Different objects.

```
Y=112   ■ Snug crown
        |
Y=176   |              ■ Lodge peak
        |              |
Y=256   |              |         ■ Pup peak
        |              |         |
        |   FACE       |  FACE   |
Y=376   |   Snug       |  Lodge  |
        |              |         |  FACE Pup
Y=512   |              |         |
        |              |         |
Y=640   horizon ---------------------------------
        |              |         |
Y=768   ground plane
        |              |         |
Y=896   =============== feet on one line ========
        Snug 432 wide  Lodge 720  Pup 576
```

|  | Snug | Pup | Lodge |
| --- | ---: | ---: | ---: |
| Width | 432 (42%) | 576 (56%) | 720 (70%) |
| Height | 784 (77%) | 640 (63%) | 720 (70%) |
| Top Y | 112 | 256 | 176 |
| Face Y | 376 | 512 | 464 |
| Stance | 128 | 224 | 304 |

The Lodge is immediately the larger tent beside the Pup: 144px wider, 80px taller, wider door, ridge and side walls. The Snug is a different *kind* of object — a tall capsule — so it can be the tallest without competing with the Lodge on "tent-ness."

---

## Sleeping Bag / Snug

```
Character center X = 512
Character baseline Y = 896
Bounding box = (296, 112) 432×784
Face center = (512, 376)
Eye center Y = 360
Left arm anchor = (304, 472)
Right arm anchor = (720, 472)
Left foot anchor = (448, 896)
Right foot anchor = (576, 896)
```

Hood-face. Short legs. Slightly goofy. Hats on the crown, brim Y=216.

## Small Tent / Pup

```
Character center X = 512
Character baseline Y = 896
Bounding box = (224, 256) 576×640
Face center = (512, 512)
Eye center Y = 488
Left arm anchor = (240, 560)
Right arm anchor = (784, 560)
Left foot anchor = (400, 896)
Right foot anchor = (624, 896)
```

Tent first. Door-face. Hats on the peak, brim Y=320 (above the door).

## Large Tent / Lodge

```
Character center X = 512
Character baseline Y = 896
Bounding box = (152, 176) 720×720
Face center = (512, 464)
Eye center Y = 440
Left arm anchor = (176, 536)
Right arm anchor = (848, 536)
Left foot anchor = (360, 896)
Right foot anchor = (664, 896)
```

Cabin-dome, ridge at Y=320, larger door. Hats on the peak/ridge, brim Y=256.

---

## Zones every layer must respect

For each class the blueprint paints:

- **Magenta occupancy** — body + default arms. New silhouettes are illegal.
- **Gold face oval** — eyes, brows, mouth, facial extras live here.
- **Violet headwear** — peak or hood only.
- **Cyan handheld rects** — items in hands, not in the face.
- **Red logo safe** — top-right, kept quiet until Phase 10.
- **Brown baseline** — feet.

If a proposed trait cannot live in its zone without colliding, it is the wrong trait, not a reason to move the zone.

---

## Approval question for Phase 0

Does this family of envelopes match the mission on a thumbnail?

- Can you tell Snug / Pup / Lodge apart in 128px grayscale?
- Do they still feel like one illustrated world?
- Is the Lodge obviously the 6-person tent next to the Pup?
- Is the top-right calm enough for a later signature mark?

If yes, lock `config/anchors.json` and do not let Phase 1 art renegotiate it.
