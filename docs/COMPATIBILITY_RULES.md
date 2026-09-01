# Compatibility rules

Canonical file: `config/compatibility.json`.

Visual collisions are solved **in the engine**, not in a spreadsheet after mint.

The engine applies `forces`, then checks `excludes`, `requires`, and `classes_only`. A token that still fails is discarded and rerolled (max 80 attempts). Duplicate DNA is also discarded.

## Operators

| Operator | Meaning |
| --- | --- |
| `forces` | Overwrite a slot. Sunglasses force sunglasses-ready eyes. |
| `excludes` | These values cannot co-exist with the condition. |
| `requires` | The other slot must be one of these ids. |
| `classes_only` | The triggering trait is illegal on other classes. Also enforced by trait class lists. |

## Dignity (always on)

These are product rules, not just technical ones:

- No trait may depict poverty as costume, joke, or rarity flex.
- No cardboard-sign gags, trash piles, or "homeless starter kit" loadouts.
- Patchwork and well-loved wear mean care and use.
- Worried / chattering expressions are weather, not identity.

## Rule catalog (human index)

**Hands and objects**

- Any held item requires `hold-item` or `hold-two-hand`.
- Map and spare blanket force two-handed hold.
- One-hand items force `hold-item`.
- Empty hands cannot stay in a grip pose.
- Wave and akimbo force `held_item=none`.

**Split assets**

- `rear_accessory=backpack` forces `body_accessory=backpack-straps`.
- Straps cannot appear without the pack.

**Heads**

- Hood is Snug-only (tents wear hats on the peak).
- Umbrella excludes santa hat, crown, halo, trapper (canopy vs tall crown).
- Wave excludes halo (raised hand occupies the arc).

**Faces**

- Sunglasses force sunglasses-ready eyes and exclude starry / heart / side-eye / sleepy.
- Clear glasses exclude starry, heart, and sunglasses-ready eyes.
- Concerned brows exclude open-laugh, tongue, grin.
- Sleepy eyes exclude open-laugh and teeth.
- Surprised eyes exclude smirk, determined mouth, chatter.
- Chatter excludes heart and starry eyes.
- Mustache excludes tongue and open-laugh.

**World**

- Heavy snow excludes extra snow-kissed facial (redundant; reads as dirt).
- Held lantern excludes ground lantern.
- Vestibule excludes tiny campfire and pack-on-ground (front ground is occupied).
- North Star Navy body requires a quiet/dark field (night, first light, abstract snow).
- Aurora cloth excludes the ordinary campground scene.

**Class locks**

- Quilt / plaid / stars / moons / trail geometry → Snug only.
- Tent panels / well-loved → tents only.
- Baffles / zipper / drawstring → Snug only.
- A-frame poles / door window → Pup only.
- Cabin poles / vestibule / extra panels → Lodge only.
- Guy lines → both tents.
- Slippers → Snug only.

## Adding a rule

1. Write it in `config/compatibility.json` with an `id` and a `reason`.
2. Add a unit test if it is load-bearing (sunglasses, two-hand items, backpack).
3. Re-run `python -m warm_company generate` and confirm 800 unique legal DNA.
4. Do not "just be careful while drawing."
