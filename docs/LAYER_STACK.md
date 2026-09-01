# Layer stack

Canonical file: `config/layer_stack.json`.

The compositor is a painter's algorithm. Lower z is drawn first. Every file is 1024×1024. Pixels are already in the right place.

## Final stack

| Z | Slot | Scope | Notes |
| --: | --- | --- | --- |
| 01 | background | shared | **Only opaque layer.** Full scene. |
| 02 | rear_environment | shared | Distant pines, campfire glow, ridge. Optional. |
| 03 | contact_shadow | procedural | Ellipse from foot anchors. Not an illustrated file by default. |
| 04 | rear_accessory | class | Backpack body, bedroll, rain fly. Behind the character. |
| 05 | rear_arm | class | Only for poses that put an arm behind (wave). |
| 06 | rear_held | class | Shaft / board / canopy that must sit behind the body. |
| 07 | body | class | Master silhouette + local fabric color. |
| 08 | pattern | class | Quilting, plaid, panels, stars. Pre-clipped to the body mask during registration. |
| 09 | structural | class | Poles, zipper, baffles, guy lines, vestibule, door trim. On top of pattern so structure always reads. |
| 10 | legs | class | Short cartoon legs. |
| 11 | footwear | class | Soles on Y=896. |
| 12 | face | class | Hood opening or door panel. No features. |
| 13 | eyes | class | Anchored. |
| 14 | eyebrows | class | Anchored. |
| 15 | mouth | class | Anchored. |
| 16 | facial | class | Blush, glasses, sunglasses, snow-kissed, mustache. |
| 17 | front_arm | class | Default rest / hold / akimbo / two-hand / wave. |
| 18 | front_held | class | Mug, lantern, sign handle, etc. |
| 19 | body_accessory | class | Scarf, sash, patch, backpack straps. |
| 20 | headwear | class | Peak or hood. Brim above face. |
| 21 | ground_accessory | shared | Mug in snow, tiny campfire, hare tracks. |
| 22 | atmosphere | shared | Snow, breath fog. **Face oval punched out.** |
| 23 | logo | shared | **Does not exist until Phase 10.** |

## Split assets (plan them now)

Some traits are one id in metadata and two or three files on disk.

| Trait | Files | Why |
| --- | --- | --- |
| Backpack | `rear_accessory/backpack.png` + `accessories/backpack-straps.png` | Pack behind, straps in front of the body. Forced pairing. |
| Walking stick | `handheld-rear` + `handheld` | Shaft can pass behind the hip. |
| Heart sign | `handheld-rear` + `handheld` | Board may sit slightly behind the forearm. Pictogram heart only. No slogans. |
| Umbrella | `handheld-rear` (canopy) + `handheld` (shaft) | Canopy behind/above the peak, shaft in the hand. |
| Wave pose | `arms-rear` + `arms` | One arm goes behind the body on the far side. |

The generator selects **one** trait id. The compositor loads every file that trait declares.

## Occlusion rules worth repeating

- Pattern never hides poles. Structure is a later z.
- Front arm hides a slice of torso; a mug in that hand is in front of the torso.
- Headwear never covers the mouth and should not cover the eyes except via a brim shadow.
- Atmosphere is not allowed to snow-blind the face. Implementation: compositor (or the registered PNG itself) keeps alpha 0 inside the inflated face oval.
- Logo, when it exists, sits in the reserved top-right and covers neither character nor feet.

## What is not a layer

- **Special** is a metadata label plus a coordinated loadout, not a paint layer.
- **Class** is a generation axis, not a layer.
- **Contact shadow** is code unless an illustrated override is later approved.

## Folder mapping

Class-specific art:

```
layers/{sleeping-bag|small-tent|large-tent}/
  body/ patterns/ structural/ face/
  eyes/ eyebrows/ mouths/ facial/
  arms/ arms-rear/ legs/ footwear/
  headwear/ handheld/ handheld-rear/
  accessories/ accessories-rear/
```

Shared:

```
layers/shared/backgrounds/
layers/shared/rear-environment/
layers/shared/ground/
layers/shared/atmosphere/
layers/shared/logo/          # empty until Phase 10
```

File name = trait id, kebab-case, `.png`. Example: `layers/sleeping-bag/eyes/happy.png`.
