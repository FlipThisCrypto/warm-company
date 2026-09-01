# Collection Design Bible

**Working title:** Warm Company
**Organization:** Not By Chance Outreach
**Chain:** Chia
**Supply:** 800 static 1024×1024 PNG NFTs
**Phase:** 0 — system design. No production layers.

This bible is the constitution. Layer artists, prompt writers, and the generator all obey it. If a later asset disagrees with this document and `config/anchors.json`, the asset is wrong.

---

## 1. Mission, in one paragraph

This collection raises money to buy winter shelter equipment for people experiencing homelessness. Two hundred three-person tents, two hundred six-person tents, and four hundred sleeping bags. Eight hundred physical items. Eight hundred NFTs. Each token is a companion that *symbolically represents* one item the campaign intends to purchase. It is not a warehouse receipt and it does not convey legal title to a particular physical tent or bag unless a later legal structure says so in writing.

The people being helped are represented with dignity. Poverty is not a costume, not a rarity trait, and not a joke.

## 2. Why the characters are what they are

The mascots *are* the gear.

- A **Snug** is a sleeping bag that learned to stand up.
- A **Pup** is a three-person tent (pup tent is real outdoor vocabulary).
- A **Lodge** is a six-person tent, obviously larger.

They share one illustrator, one ground line, one light, one outline language. They do not share one silhouette. Side by side they must read as a family of objects, not three costumes of the same body.

## 3. Collection identity

| Field | Value | Status |
| --- | --- | --- |
| Working title | Warm Company | Proposed |
| Subtitle | 800 illustrated winter-shelter companions | Proposed |
| Family names | Snug / Pup / Lodge | Proposed |
| CHIP-0007 collection UUID | `0d8b7760-aba7-5393-af88-baeaa3aea62f` | Off-chain grouping only |
| Launcher ID / DID / NFT IDs | — | Not invented |
| Logo | — | Phase 10 only |
| Production seed | `warm-company-dev-seed-v0` | Placeholder |

Title candidates and the argument for *Warm Company* live in `config/collection.json`. Alternate names: Camp Kind, Eight Hundred Warm, Shelter Kin, First Light Camp.

## 4. Non-negotiables

1. Supply is exactly 400 / 200 / 200. The generator hard-fails on any other count.
2. Canvas is always 1024×1024. Layers are never cropped to content.
3. Only backgrounds are opaque. Every other layer is RGBA with real alpha.
4. The compositor never repositions art. Registration happens *before* a layer is accepted.
5. Eyes, mouths, hands, hats, poles, and bag width do not drift inside a class.
6. Front-facing characters. Volume comes from shading, not from a 3/4 turn that would break layering.
7. Warm key light from the upper left. Shadows fall down-right. Always.
8. One outline color, one highlight method, one shadow method, one paper grain.
9. Logo is last, designed after we see real composites.
10. Image models draw. Python enforces geometry.

## 5. The 1:1 contract, said carefully

Saying "NFT #0412 *is* tent #0412 in a truck" is a legal claim. We do not make it.

Saying "NFT #0412 is one of 200 Lodges, and the campaign's goal is to buy 200 six-person tents" is the actual contract with the audience.

Metadata carries both `Represents` and an explicit `legal_title_to_physical_item: false` flag in the CHIP-0007 `data` object.

## 6. Creative north star

> An illustrator deliberately drew a family of winter-shelter mascots.

Not: an AI generated hundreds of unrelated cartoon objects.

Charming, thoughtful, cohesive, warm, thumbnail-readable. Not AAA. Not clip art. Not grim. Not a spectacle of homelessness.

Tiny stories are welcome: a Lodge with a lantern on night watch; a Snug with soup and a tiny campfire; a Pup holding a map. Coordinated specials (The Volunteer, The Survivor, The Not By Chance, …) are authored loadouts, not random jackpots.

## 7. Shared world

All three classes stand on **baseline Y = 896**. Horizon is **Y = 640**. Ground plane is **Y = 768**. Center X is **512**. Safe margin 48px. Hard margin 24px.

That is why a Snug, a Pup, and a Lodge can later share backgrounds and occupy the same illustrated winter.

Exact pixels: [COORDINATE_SYSTEM.md](COORDINATE_SYSTEM.md) and `config/anchors.json`.

## 8. Relative scale (locked)

| Class | Bounding box | Width | Height | Face center | Peak |
| --- | --- | --- | --- | --- | --- |
| Snug (sleeping bag) | `(296, 112) 432×784` | 42.2% | 76.6% | `(512, 376)` | `(512, 112)` |
| Pup (small tent) | `(224, 256) 576×640` | 56.3% | 62.5% | `(512, 512)` | `(512, 256)` |
| Lodge (large tent) | `(152, 176) 720×720` | 70.3% | 70.3% | `(512, 464)` | `(512, 176)` |

The bag is the tall goofy sibling. The Pup is compact and lowest in the face. The Lodge is the wide sturdy one. Hats on tents live on the **peak**, brim above the door. Hats on bags live on the **hood**, brim above the eyes. Faces live in the bag opening or the tent door — never as stickers.

## 9. How art will actually be made

After this bible is approved:

1. Render blueprints (already in repo once `python -m warm_company blueprints` is run).
2. Generate **three canonical characters** with Grok Image, using the frozen prompt prefix and the guide overlays as `image_edit` references.
3. Register them to occupancy masks. If they miss by more than a few pixels, redraw, do not "make it work in Photoshop forever."
4. Every subsequent layer is an `image_edit` of the canonical of that class, not a fresh `image_gen`.
5. Python validates canvas, alpha, occupancy, and then composites.

This is the only practical way to make hundreds of AI-assisted PNGs look like one illustrator.

## 10. Document map

| Doc | Job |
| --- | --- |
| ART_DIRECTION.md | Style lock: line, light, color, texture, dignity |
| COORDINATE_SYSTEM.md | Every pixel anchor |
| VISUAL_BLUEPRINT.md | How to read the three silhouettes |
| LAYER_STACK.md | Occlusion order and split assets |
| TRAIT_MATRIX.md | What exists, in which phase |
| COMPATIBILITY_RULES.md | requires / excludes / forces |
| RARITY_PLAN.md | Weights, specials, audit |
| GENERATION_PLAN.md | Phases 0–13 and the software |
| QA_CHECKLIST.md | Gate for every layer and the collection |
| FUNDRAISER_MODEL.md | $12,000 goods, $1,200 contingency, mint vs royalty |
| IMAGE_PROMPT_FRAMEWORK.md | Exact Grok Image prompt assembly |

Configs in `config/` are executable versions of these docs.

## 11. What we are explicitly not doing in Phase 0

- Not generating production trait PNGs.
- Not designing the logo.
- Not picking a mint price in XCH.
- Not deploying a Chia offer, royalty transfer program, or DID.
- Not claiming a public URL.

Review the geometry and the art direction. Then Phase 1 can begin.
