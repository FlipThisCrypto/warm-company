# Operator runbook

This is the mint-adjacent path. It does not mint on Chia. It does not write 800 PNGs unless you run `composite`.

## Every day

```powershell
$env:PYTHONPATH = "src"
python -m warm_company status
python tests/test_pipeline.py
```

`status` does not generate DNA. It tells you whether the placeholder seed still blocks `--mint`, whether layers are missing, the current `tree_digest`, and whether the last generate (if any) still matches that tree (`generation_stale` / `ready_to_composite`). `ready_to_mint` is true only when mint is allowed, DNA matches the live tree, the build dir is writable, and a verified DNA backup exists. If you edited layers or config after generate, regenerate before compositing.

## Before calling a generate "the collection"

```powershell
python -m warm_company preflight --phase 9
```

That command must print `"ok": true`. It generates the development-seed 800, checks provenance, CHIP-0007 legal title, dignity labels, the $12,000 goods table, and the frozen DNA fingerprint.

`python -m warm_company generate --dry-run --phase 9` rolls the same DNA and prints `collection_fingerprint` without writing `build/dna`.

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

```powershell
python -m warm_company backup
python -m warm_company backup --verify build/backups/dna-....zip
python -m warm_company backup --restore build/backups/dna-....zip
```

That zip holds DNA + provenance only (no 800 images). Verify it before relying on a restore copy.

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

## Disaster recovery

DNA is the record. Images and metadata are regenerable from DNA + the live tree.

| Failure | What to do |
| --- | --- |
| `generate` killed mid-run | `tokens.json` is atomic; the previous complete generate remains. Re-run `generate`. |
| `composite` killed mid-run | `python -m warm_company composite --resume` after `status` shows `ready_to_composite`. |
| `build/dna` deleted | `python -m warm_company backup --restore path\to\dna-....zip` then `status` (must not be `generation_stale`). |
| Accidental second `generate` | `python -m warm_company backup --restore-bak` to put `tokens.json.bak` back, then `status`. |
| `generation_stale` true | Layers/config changed. Re-run `generate` (or `--dry-run` first). Do not `--force` composite for a mint. |
| `BuildLockHeld` | Another generate/composite is running, or a dead lock is less than 6 hours old. Wait, or delete `build/.generate.lock` / `build/.composite.lock` only if the pid is dead. |
| `build directory is not writable` | Free disk, fix permissions, re-run `status`. |

Never mint 800 images until the 12-sample gate and `preflight --mint` are green. Never rewrite git history at `6aa596f`.
