# Trait matrix

Canonical file: `config/traits.json`.

Principles:

- Do not inflate the library with near-duplicates.
- Class-lock structure and fabric language.
- `none` is a real trait on optional slots.
- `phase` gates what the generator may use: 3 = first composites, 6 = expansion, 9 = full library.
- Weight 0 means "not rolled; only forced" (backpack straps).

## Slots

| Slot | Optional | Scope | Phase 3 minimum |
| --- | --- | --- | --- |
| background | no | shared | 4 scenes |
| rear_environment | yes | shared | none |
| rear_accessory | yes | class | none |
| arm_pose | no | class | rest, hold-item |
| held_item | yes | class | none, coffee, hot chocolate, thermos |
| body | no | class | 4 colors per class |
| pattern | yes | class | solid; bag quilt; tent panels |
| structural | no | class | baffles / A-frame / cabin poles |
| legs | no | class | short-legs |
| footwear | no | class | basic shoes, work boots, snow boots |
| face | no | class | standard-face |
| eyes | no | class | normal, happy, sleepy, determined |
| eyebrows | no | class | neutral, raised, concerned |
| mouth | no | class | smile, grin, determined |
| facial | yes | class | none, blush |
| body_accessory | yes | class | none, scarf |
| headwear | yes | class | none, beanie, knit cap |
| ground_accessory | yes | shared | none |
| atmosphere | yes | shared | clear, light snow |
| special | yes | token | none (injected later) |

## Shared backgrounds (full library)

Winter Sunrise, Snowy Camp, Forest Clearing, Cold Blue Night, Winter Sunset, Warm Dawn, Starry Winter Night, Campground, Appalachian Ridge, City Edge, Quiet Overpass, Abstract Snowfield, First Light, Light Snowfall scene.

Quiet Overpass is the dignified version of "underpass-inspired." No spectacle.

## Body colors

**All classes:** Trail Olive, Ember Rust, Navy Night, Camp Orange, Storm Charcoal, Aurora Cloth (legendary), North Star Navy (legendary).

**Snugs extra:** Burgundy, Mustard Seed, Cream Fleece, Sky Flannel, Plum Preserve.

**Tents extra:** Forest Green, Royal Blue, Sand Tan, Camp Red, Granite Gray, Alpine Teal, Wild Purple, Sun Yellow, Olive/Tan, Navy/Orange.

## Patterns

**Snugs:** solid, horizontal quilt, vertical quilt, plaid, stars, moons, patchwork, soft camo, trail geometry, mission patches.

**Tents:** solid, panels, two-tone panels, patchwork, soft camo, well-loved, mission patches.

Well-loved and patchwork mean *care*, not dirt.

## Structure (class locked)

- Snug: baffles+zipper, hood drawstring, fancy zipper pull.
- Pup: A-frame poles, guy lines, door window.
- Lodge: cabin poles+ridge, guy lines, vestibule, extra panels.

## Expression kits

Eyes: normal, happy, sleepy, determined, surprised, worried, squint, side-eye, starry, heart, sunglasses-ready.

Brows: neutral, raised, concerned, mischievous, determined.

Mouths: smile, grin, open laugh, smirk, surprised, teeth, tongue, chattering, determined, soft O.

Facial: none, cold blush, freckles, snow-kissed, glasses, sunglasses, mustache.

## Gear

Headwear: none, beanie, knit cap, baseball cap, bucket hat, trapper, earmuffs, headband, hood (Snug only), Santa-style winter hat, camp crown, north-star halo, earflap beanie.

Held: none, coffee, hot chocolate, thermos, flashlight, lantern, heart, hand warmer, soup cup, compass, map (two-hand), spare blanket (two-hand), walking stick, heart sign, umbrella.

Footwear: basic shoes, work boots, snow boots, hiking boots, sneakers, slippers (Snug only), mismatched, bare cartoon feet.

Ground: none, mug in snow, ground lantern, pack, tiny campfire, hare tracks.

Weather: clear, light snow, steady snow, breath fog, sparkle frost, north-star field, heavy snow.

## What will not be in the library

- Weapons
- Alcohol
- Begging-sign text
- "Dirty rare" overlays
- Photoreal people
- Extra character silhouettes
- Randomly different bag widths or tent peaks
- A logo mark on every trait (the collection mark is z=23, later)

## Phase counts (approximate unique ids)

The generator does not need hundreds of near-twin hats. It needs enough *sentences*. Phase 3 is sized for 30 test composites. Phase 9 is sized for 800 unique DNA with room to spare; the uniqueness constraint is combinatorial, not "we must draw 800 hats."
