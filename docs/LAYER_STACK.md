# Layer stack

Canonical file: `config/layer_stack.json`.

The compositor is a painter's algorithm. Lower z is drawn first. Every file is 1024×1024. Rear-leg and footwear pairs are registered to class anatomy in `config/anchors.json` (two distinct feet on the class foot anchors, soles on the shared baseline). Overlay boots replace contained feet.

## Final stack (v2)

Limb roots live **behind** the body so the silhouette hides the seam. Headwear is drawn to `headwear_preferred` in `anchors.json`, never filling the legal maximum zone. Hats already inside the legal zone are not crushed to beanie size.

| Z | Slot | Scope | Notes |
| --: | --- | --- | --- |
| 01 | background | shared | **Only opaque layer.** Full scene. |
| 02 | rear_atmosphere | shared | Most snow/weather density. Optional. |
| 03 | rear_environment | shared | Distant pines, campfire glow, ridge. Optional. |
| 04 | contact_shadow | procedural | Ellipse from foot anchors. Not an illustrated file by default. |
| 05 | rear_accessory | class | Backpack body, bedroll, rain fly. Behind the character. |
| 06 | rear_arm | class | Shoulder/root. Body paints over the attachment. |
| 07 | rear_held | class | Lantern handle, shaft, or other rear half of a held object. |
| 08 | rear_leg | class | Extra thigh length that the hem/footbox occludes. |
| 09 | body | class | Master silhouette + local fabric color. |
| 10 | pattern | class | Quilting, plaid, panels, stars. Pre-clipped to the body mask during registration. |
| 11 | structural | class | Poles, zipper, baffles, guy lines, vestibule, door trim. On top of pattern so structure always reads. |
| 12 | face | class | Hood opening (Snug) or door panel (Pup/Lodge). Lodge is a D-door, never a circle. |
| 13 | eyes | class | Anchored, live on the door/hood. |
| 14 | eyebrows | class | Anchored. |
| 15 | mouth | class | Anchored. |
| 16 | facial | class | Blush, glasses, sunglasses, snow-kissed, mustache. |
| 17 | legs | class | Visible lower leg in front of the hem. |
| 18 | footwear | class | Soles on Y=896. |
| 19 | front_arm | class | Forearm/hand that must overlap torso or a prop. |
| 20 | front_held | class | Mug, lantern body, map. Hands grip; objects do not float beside fists. |
| 21 | light_effect | class | Optional. Lantern-glow is a small warm transparent overlay, not 3D lighting. |
| 22 | body_accessory | class | Scarf, sash, patch, backpack straps. |
| 23 | headwear | class | Preferred draw size, not the legal zone. Human-scale on tents. |
| 24 | ground_accessory | shared | Mug in snow, tiny campfire, hare tracks. |
| 25 | atmosphere | shared | A few front flakes only. **Face/door punched out.** |
| 26 | logo | shared | **Does not exist until Phase 10.** |

## Split assets (plan them now)

Some traits are one id in metadata and two or three files on disk.

| Trait | Files | Why |
| --- | --- | --- |
| rest / hold-item / hold-two-hand | `arms-rear` + optional `arms` | Shoulder is always rear. Hands that overlap torso or a prop are front. |
| lantern | `handheld-rear` + `handheld` + optional `light` | Handle behind the fist, lantern body in front, small warm glow. |
| short-legs | `legs-rear` + optional `legs` | Thigh hidden by hem/footbox; visible lower leg and footwear in front. |
| Backpack | `rear_accessory/backpack.png` + `accessories/backpack-straps.png` | Pack behind, straps in front of the body. Forced pairing. |
| Walking stick | `handheld-rear` + `handheld` | Shaft can pass behind the hip. |
| Heart sign | `handheld-rear` + `handheld` | Board may sit slightly behind the forearm. Pictogram heart only. No slogans. |
| Umbrella | `handheld-rear` (canopy) + `handheld` (shaft) | Canopy behind/above the peak, shaft in the hand. |

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
  arms/ arms-rear/ legs/ legs-rear/ footwear/
  headwear/ handheld/ handheld-rear/ light/
  accessories/ accessories-rear/
```

Shared:

```
layers/shared/backgrounds/
layers/shared/rear-environment/
layers/shared/ground/
layers/shared/atmosphere-rear/
layers/shared/atmosphere/
layers/shared/logo/          # empty until Phase 10
```

File name = trait id, kebab-case, `.png`. Example: `layers/sleeping-bag/eyes/happy.png`.
