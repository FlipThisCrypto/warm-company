# Operator runbook

This is the mint-adjacent path. It does not mint on Chia. It does not write 800 PNGs unless you run `composite`.

## Every day

```powershell
$env:PYTHONPATH = "src"
python -m warm_company status
python tests/test_pipeline.py
```

`status` does not generate DNA. It tells you whether the placeholder seed still blocks `--mint`, whether layers are missing, the current `tree_digest`, and whether the last generate (if any) still matches that tree (`generation_stale` / `ready_to_composite`). If you edited layers or config after generate, regenerate before compositing.

## Before calling a generate "the collection"

```powershell
python -m warm_company preflight --phase 9
```

That command must print `"ok": true`. It generates the development-seed 800, checks provenance, CHIP-0007 legal title, dignity labels, the $12,000 goods table, and the frozen DNA fingerprint.

## Production seed lock (Phase 11)

1. Replace `config/collection.json` `production_seed.value` with a new secret.
2. Set `production_seed.status` to something other than `placeholder-not-for-mint`.
3. Store the seed offline. Do not put it in an issue or chat.
4. Update `DEV_COLLECTION_FINGERPRINT` only if you intentionally retarget DNA (you should not, for a production seed).
5. Run:

```powershell
python -m warm_company preflight --mint --phase 9
python -m warm_company generate --mint --phase 9
```

Record `collection_fingerprint` and `tree_digest` from the JSON output. If either changes later, do not mint.

## Metadata

```powershell
python -m warm_company metadata
python -m warm_company rarity
```

CHIP-0007 files must keep `legal_title_to_physical_item: false` and must not invent IPFS/HTTP image URLs.

## Images

Do not composite all 800 until a human has approved the 12-sample gate in `build/review-v3/` against baseline `6aa596f`.

```powershell
python -m warm_company composite --allow-missing --limit 12
python -m warm_company composite --resume
```

`--resume` skips tokens that already have a complete 1024 PNG so an interrupted 800-image run can continue. Composite refuses a stale last-generate (`generation_stale`) unless you pass `--force`.

Missing layers are written to `build/reports/composite_missing.json`.
