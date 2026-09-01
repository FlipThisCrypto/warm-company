# Warm Company

Repo: [github.com/FlipThisCrypto/warm-company](https://github.com/FlipThisCrypto/warm-company)

Working title for the **Not By Chance Outreach** winter fundraiser collection on Chia.

Exactly **800** illustrated winter-shelter companions.

| Class | Family name | Supply | Symbolically represents |
| --- | --- | ---: | --- |
| Sleeping Bag | Snug | 400 | 1 sleeping bag |
| Small Tent | Pup | 200 | 1 three-person tent |
| Large Tent | Lodge | 200 | 1 six-person tent |

**Phase 0 (design bible + generator) is in this repository.** Nine layered review composites are in `build/review-samples/`. Production trait libraries are not locked yet — geometry lives in `config/anchors.json` so art can be revised without guessing coordinates.

## Do not start with random layers

Read, in this order:

1. [docs/COLLECTION_BIBLE.md](docs/COLLECTION_BIBLE.md)
2. [docs/ART_DIRECTION.md](docs/ART_DIRECTION.md)
3. [docs/COORDINATE_SYSTEM.md](docs/COORDINATE_SYSTEM.md)
4. [docs/VISUAL_BLUEPRINT.md](docs/VISUAL_BLUEPRINT.md)
5. [docs/blueprints/index.html](docs/blueprints/index.html) (open after rendering blueprints)
6. The rest of `docs/`

## Architecture notes vs. the production brief

The brief's `collection/` tree is preserved in spirit. These changes are deliberate:

- **Repo root is the collection.** There is no extra nested `collection/` folder.
- **Python package under `src/warm_company/`** with thin wrappers in `scripts/`. Importable, testable, one CLI.
- **`config/*.json` is the source of truth.** Extra PNGs on disk are errors, not extra traits.
- **Contact shadows are procedural** so they cannot drift.
- **Blueprints are rendered from `config/anchors.json`.** If a picture and a number disagree, the JSON wins and the picture is regenerated.
- **Grok Image prompts are assembled, not hand-typed per layer.** Master style prefix + class template + layer instruction + exact coordinates.
- **CHIP-0007 metadata** with no invented URLs, IPFS CIDs, or on-chain identifiers.

## Clone and work

```bash
git clone https://github.com/FlipThisCrypto/warm-company.git
cd warm-company
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python tests/test_pipeline.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding layers. Do not invent per-asset coordinates.

## Commands

```bash
python -m pip install -r requirements.txt
set PYTHONPATH=src

python -m warm_company blueprints
python -m warm_company generate --phase 9
python -m warm_company metadata
python -m warm_company rarity
python -m warm_company contact-sheet
python -m warm_company validate-layers
python -m warm_company prompts

python tests/test_pipeline.py
```

Equivalent scripts live in `scripts/`.

The development seed is `warm-company-dev-seed-v0`. Replace it before Phase 11 and never rotate it after final generation.

## Current status

| Item | Status |
| --- | --- |
| Design bible | Written |
| Coordinate system | Locked in `config/anchors.json` |
| Master silhouettes / blueprints | Generated from config (not illustrated art) |
| Trait matrix | Specified, phased 3 / 6 / 9 |
| Compatibility engine | Implemented |
| Generator / compositor skeleton | Implemented |
| Layer validation / contact sheets | Implemented |
| Grok Image prompt framework | Implemented |
| 9 layered review composites | In `build/review-samples/` |
| Production trait library | **Not locked — review first** |
| Logo | **Deferred to Phase 10** |
