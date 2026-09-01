# Contributing

This collection is meant to be worked on by more than one person. The rule that keeps it from falling apart:

**Every asset is designed in the context of every other asset.** Hats are drawn to `headwear_preferred`, not the legal maximum zone. Eyes sit on published anchors, on the hood (Snug) or door (Pup/Lodge). The compositor never repositions pixels except for documented registration snaps.

## Start here

1. Read [docs/COLLECTION_BIBLE.md](docs/COLLECTION_BIBLE.md).
2. Open [docs/COORDINATE_SYSTEM.md](docs/COORDINATE_SYSTEM.md) and `config/anchors.json` — those numbers are the contract.
3. Look at `templates/` (occupancy + blueprints), the locked v3 canonicals in `references/approved/`, and `build/review-v3/` (12-sample refinement gate).

If a PNG and `anchors.json` disagree, regenerate the PNG. Do not edit the JSON to match a drifted drawing unless the group agrees to change the geometry.

## What belongs in git

Commit:

- docs, config, source, tests, prompts
- `templates/` blueprints and occupancy masks
- accepted `layers/**/*.png` (full 1024×1024, never cropped)
- review composites under `build/review-samples/` and `build/review-v3/`

Do not commit:

- `build/dna/`, `build/metadata/`, `build/images/` of a full 800-run (regenerable)
- editor junk, virtualenvs, `.env`

## Adding a layer

1. Add or confirm the trait id in `config/traits.json`.
2. Generate with the frozen prompt prefix (`python -m warm_company prompts`).
3. After Phase 1 canonicals exist, `image_edit` from that class's canonical — do not `image_gen` a new silhouette.
4. Save as `layers/{class}/{slot}/{id}.png` at 1024×1024 RGBA (backgrounds opaque).
5. Register to occupancy. Drift over 12px is a redraw, not a nudge.
6. Run `python -m warm_company validate-layers`.

## Generator

```powershell
$env:PYTHONPATH = "src"
python -m warm_company generate --phase 9
python tests/test_pipeline.py
```

The dev seed is `warm-company-dev-seed-v0`. Do not rotate a production seed once Phase 11 starts.

## Dignity

No poverty-as-costume traits, no begging-sign gags, no dirt-as-rarity. Patchwork means care. Worried eyes mean weather.
