# Generation plan

## Software

Python 3.11+, Pillow.

Deterministic stream: `sha256(f"{seed}:{counter}")` as a 256-bit integer, rejection sampling for ranges. Python `random` is not used. A seed plus the config files must rebuild the collection on any machine.

CLI:

```
python -m warm_company generate --seed <seed> --phase 9
python -m warm_company metadata
python -m warm_company rarity
python -m warm_company contact-sheet
python -m warm_company validate-layers
python -m warm_company validate-collection
python -m warm_company composite --allow-missing   # skeleton only, until art exists
python -m warm_company blueprints
python -m warm_company prompts
```

Package: `src/warm_company/`. Wrappers: `scripts/`.

## What the generator actually does

1. For each class, fork a child RNG and roll legal trait dicts until the quota is filled.
2. Apply compatibility forces/excludes/requires; reroll failures and duplicate DNA.
3. Inject 13 specials by replacing a token of the required class.
4. Seeded Fisher–Yates shuffle assigns public `token_id` 1..800.
5. Write `build/dna/tokens.json` and `collection.jsonl`.
6. Assert 400 / 200 / 200, unique DNA, contiguous ids.

Compositing is a later step and is skipped until layers exist. Dry-run generation does not need any PNGs.

## Image-model reality

Prompts may mention coordinates. Models will still drift.

Production path for every layer:

1. Build the prompt from the frozen prefix (`python -m warm_company prompts`).
2. For canonicals: `image_gen` at 1:1, then `image_edit` against `templates/{class}/guides.png`.
3. For every later layer: `image_edit` the **approved canonical** of that class. Never a blank `image_gen`.
4. Knock out remaining matte.
5. `register.measure` against occupancy / bbox / anchors.
6. Snap-translate at most 12px. More drift = redraw.
7. `validate-layers` must pass before the file is legal input to the compositor.

The compositor only alpha-overs 1024×1024 PNGs and draws the contact shadow. It does not "find" the hat.

## Phases

| Phase | Name | Exit gate |
| ---: | --- | --- |
| 0 | Design bible (this repo) | Geometry and direction approved. **You are here.** |
| 1 | Three canonical characters | Registered Snug, Pup, Lodge. Same light, same line, shared baseline. |
| 2 | Basic backgrounds | 4 scenes that respect occupancy and logo safe. |
| 3 | Minimal trait set | Phase-3 rows in `traits.json` exist as PNGs. |
| 4 | Test composites | 10 + 10 + 10. Visual review of all 30. |
| 5 | Stress tests | Sunglasses+hats, two-hand map, backpack, heavy snow, vestibule, wave. |
| 6 | Expand library | Phase-6 traits. |
| 7 | 100-NFT pilot | Seeded subset or first 100 shuffled ids. |
| 8 | QA pilot | Contact sheets, occupancy, style drift hunt. |
| 9 | Complete library | Phase-9 traits. |
| 10 | Logo | Designed against real composites, z=23, signature-sized. |
| 11 | Final 800 | Production seed locked. |
| 12 | Full collection QA | Sheets for each class, specials, entire set. |
| 13 | Metadata + rarity reports | CHIP-0007 JSON, histogram, duplicate check. |

Do not jump to Phase 11.

## Test composite plan (Phase 4)

Generate 10 of each class using `--phase 3`, composite, and inspect:

- scale vs. the occupancy mask
- face sitting in door vs. hood
- feet on Y=896
- hat on peak vs. hood
- light direction
- no white boxes
- no text artifacts

Then generate the 13 specials as soon as their traits exist, even if the rest of Phase 9 is incomplete.

## Reproducibility

Store, when Phase 11 begins:

- production seed (config + offline paper)
- git hash of the repo
- `build/dna/tokens.json`
- SHA-256 of every accepted layer PNG

The dev seed in config now is `warm-company-dev-seed-v0` and is **not** the mint seed.

## Chia minting

Out of scope for Phase 0. Metadata is CHIP-0007-ready with:

- `format`, `name`, `description`, `minting_tool`
- `series_number` / `series_total`
- `attributes[]` with human labels
- `collection.id` UUID (off-chain grouping, **not** a launcher id)
- `data.legal_title_to_physical_item = false`

Image URIs, metadata URIs, license URI, DID, royalty transfer program: later, when they exist.
