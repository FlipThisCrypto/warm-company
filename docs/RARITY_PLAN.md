# Rarity plan

Canonical files: `config/rarity.json`, `config/traits.json` (weights).

## Model

Rarity is **trait-weighted**, not "every NFT is Common / Rare / Legendary."

Every token is one of 800 equally important winter items. A halo does not make a Lodge more morally valuable than a Snug in basic shoes. Do not market homelessness, survival, or "grit" as a rarity flex.

After generation the audit reports:

- trait counts and percentages per class
- class counts (must be 400 / 200 / 200)
- combination uniqueness
- duplicate DNA check
- information-content scores as a collector curiosity, **not** a rigid tier stamp on the artwork

## Band targets (per trait, not per token)

| Band | Target share of trait rolls | Role |
| --- | --- | --- |
| Common | 45–60% | Readable everyday gear and faces |
| Uncommon | 20–30% | Personality |
| Rare | 10–15% | Stories |
| Epic | 3–7% | Loud accessories |
| Legendary | 1–2% | Aurora, North Star, halo, First Light, a few atmospheres |

Weights in `traits.json` are integers. The generator uses them directly with an unbiased integer stream.

## Class guarantees

Not weighted. Hard quotas.

| Class | Count |
| --- | --- |
| Sleeping Bag / Snug | 400 |
| Small Tent / Pup | 200 |
| Large Tent / Lodge | 200 |

Mint order is a seeded shuffle of the 800, so a public mint is not 400 bags in a row. Class identity remains in metadata.

## Coordinated specials (13)

These are authored sentences, injected by replacing an ordinary token of the required class so supply stays exact.

| Special | Class | Sentence |
| --- | --- | --- |
| The Volunteer | Pup | Heart sign, sash, dawn |
| The Outreach Worker | Lodge | Thermos, city edge, work boots |
| The Survivor | Snug | Patchwork, snow boots, hand warmer |
| The Navigator | Pup | Map, forest, hiking boots |
| The Night Watch | Lodge | Lantern, starry night |
| The Campfire Keeper | Snug | Sunset, soup, tiny campfire |
| The Warm Heart | Snug | Heart eyes, heart in hand |
| The First Snow | Snug | Cream fleece, wonder, light snow |
| The Early Riser | Pup | Sunrise, coffee, sleepy eyes |
| The Trailblazer | Lodge | Walking stick, forest, camo-soft |
| The Hope Dealer | Pup | Lantern, camp crown, first light |
| The Second Chance | Snug | Patchwork, spare blanket, mismatched shoes |
| The Not By Chance | Lodge | North-star cloth, halo, night field — still one of 200 six-person tents |

13 / 800 = 1.625%, inside the legendary/special band.

## Scoring (audit only)

For each token:

```
score = sum over slots of  -log2( count(trait in that class) / class_supply )
```

Reported in `build/reports/rarity_report.md`. Optional marketplace display is a later decision. Default recommendation: show traits, not a trophy label.

## Duplicate policy

DNA is `sha256(class + sorted slot=value pairs)`. Collision → reroll. The collection validator fails the build if unique DNA ≠ 800.

## What rarity is not

- Not a reason to draw a "dirtier" version of the same tent.
- Not a reason to ship 40 near-identical beanies.
- Not a secondary-sale royalty. See FUNDRAISER_MODEL.md.
