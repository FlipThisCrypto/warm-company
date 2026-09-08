# Warm Company — Round 3 resilience, scale, and recovery log

## ROUND 3 BASELINE

- Current branch: `main`
- Starting commit: `c7fea7c921f0a1a8914c48057aa123e4903ffffa`
- Round 1 evidence: quality loop commits through `cd7a2ff`; ancestor `6aa596f` intact
- Round 2 evidence: `docs/round2-log.md`; commits `cd6a8ae` … `1e3c984` (`round 2 iteration 1` … `round 2 iteration 50`)
- Round 2 commit range: `b5be77d..1e3c984`
- Current tests: 114 OK
- Current lint/type-check: none configured (unittest only)
- Current CI: `.github/workflows/ci.yml` status → tests → preflight --phase 9, Python 3.11, pip cache
- Current security: mint seed lock, dignity scanner, CHIP-0007 legal_title false; no live marketplace
- Current observability: `status` + provenance digest; no last-generate vs live-tree comparison
- Current backup/recovery: atomic writes only; no resume, no DNA bundle, no generation lock
- Current scale: 800 DNA is fast; 800-image composite is the slow path and is all-or-nothing
- Working tree at baseline: clean on `c7fea7c`
- Major capabilities: deterministic generate, compositor, occupancy, CHIP-0007, 12-sample gate, preflight, CI
- Major Round 3 gaps: stale generation invisible on `status`; composite not resumable; no exclusive lock; no DNA backup/restore; tokens.json vs jsonl not cross-checked on the cheap path

This baseline is not an iteration.

---

## Iteration 1/50
- Evolution: `status` reports whether the last generate still matches the live tree (`generation_stale` / `ready_to_composite`) without rolling 800 DNA.
- Constraint: Layer/config edits after generate left operators able to composite against a silent provenance mismatch.
- Why Round 3: recovery and decision quality; Round 2 stored hashes, this makes drift visible on the cheap operator path.
- Verification: missing stored manifest is not stale; forged digest is stale; status still `ok` when no generate exists (CI).
- Commit: `round 3 iteration 1: flag stale last-generation vs live tree on status`

## Iteration 2/50
- Evolution: Cross-check `tokens.json` against `collection.jsonl` (count, token_id, class_id, dna). Status and validate-collection both run it.
- Constraint: An interrupted or hand-edited half of a generate could leave one file looking complete.
- Why Round 3: corruption detection and recovery; Round 2 atomic writes protect a single file, not the pair.
- Verification: matching pair is clean; length/dna mismatch is reported; one file without the other is reported.
- Commit: `round 3 iteration 2: cross-check tokens.json against collection.jsonl`

## Iteration 3/50
- Evolution: `composite --resume` skips complete 1024 PNGs so an interrupted 800-image run can continue.
- Constraint: Composite was all-or-nothing; a crash meant redoing every token.
- Why Round 3: scale and recovery of the slow path. Round 2 wrote missing-layer reports; this resumes pixels.
- Verification: 1024 PNG is skippable; tiny/missing files are not; CLI exposes --resume; report includes skipped.
- Commit: `round 3 iteration 3: resume interrupted composite by skipping complete PNGs`

## Iteration 4/50
- Evolution: Exclusive `build/.generate.lock` and `build/.composite.lock`; steal dead/stale pids.
- Constraint: Two overlapping generate/composite runs could interleave tokens.json and PNGs.
- Why Round 3: failure isolation. Round 2 atomic writes protect one file, not two processes.
- Verification: live lock raises BuildLockHeld; dead pid + old mtime is stolen; lock files gitignored.
- Commit: `round 3 iteration 4: exclusive generate and composite build locks`

## Iteration 5/50
- Evolution: Composite refuses a stale last-generate unless `--force`.
- Constraint: `--resume` could keep painting new art onto DNA bound to an old tree.
- Why Round 3: prevents silent pixel/DNA mismatch after layer edits.
- Verification: `--force` skips the gate; CLI exposes the flag; OPERATOR.md documents it.
- Commit: `round 3 iteration 5: refuse composite when last generate is stale`

## Iteration 6/50
- Evolution: `generate --dry-run` rolls and validates DNA without writing `build/dna`.
- Constraint: Operators had to overwrite the last generate to learn the fingerprint of a trial seed.
- Why Round 3: safe rehearsal before mutating durable DNA files.
- Verification: CLI exposes `--dry-run`; payload includes `wrote: false`.
- Commit: `round 3 iteration 6: dry-run generate without writing DNA files`

## Iteration 7/50
- Evolution: Pin GitHub Actions `checkout` and `setup-python` to immutable commit SHAs.
- Constraint: Floating `@v4`/`@v5` tags can be retargeted; CI supply chain was mutable.
- Why Round 3: dependency compromise mitigation. Round 2 added CI; this hardens it.
- Verification: workflow contains 40-char SHAs; test forbids `checkout@v4`.
- Commit: `round 3 iteration 7: pin GitHub Actions to immutable commit SHAs`

## Iteration 8/50
- Evolution: Preflight rejects trait/special ids that are not kebab/snake-case (path traversal, spaces).
- Constraint: A `../` trait id would be joined into a layer path.
- Why Round 3: abuse-case / path safety. Round 2 checked unknown ids, not character set.
- Verification: baseball-cap and arm_pose pass; `../layers` fails; live catalog is clean.
- Commit: `round 3 iteration 8: reject unsafe trait and special identifiers`

## Iteration 9/50
- Evolution: Load `tokens.json` with a 32 MiB cap and a named invalid-JSON error.
- Constraint: A truncated or hostile tokens.json raised a raw JSONDecodeError or could be a JSON bomb.
- Why Round 3: failure containment on the operator load path.
- Verification: valid payload loads; `{not-json` names invalid JSON; oversized file names max.
- Commit: `round 3 iteration 9: cap and name errors when loading tokens.json`

## Iteration 10/50
- Evolution: Composite writes token PNGs atomically (temp + replace).
- Constraint: A crash mid-save could leave a truncated PNG that `--resume` might treat as done.
- Why Round 3: interrupted-operation recovery for the slow image path. Round 2 atomic-wrote JSON only.
- Verification: second write replaces pixels; no leftover `.tmp`.
- Commit: `round 3 iteration 10: write token PNGs atomically`

## Iteration 11/50
- Evolution: Composite refuses to start when free disk is below 1.5 MB × token count + 50 MB headroom.
- Constraint: An 800-PNG run could fill the disk mid-write and leave a partial set.
- Why Round 3: storage ceiling / failure prevention before the slow path.
- Verification: 800-token budget is 1.25e9 bytes; 10^18-byte request fails on a temp dir; 0 tokens is clean.
- Commit: `round 3 iteration 11: refuse composite when free disk is below PNG budget`

## Iteration 12/50
- Evolution: Provenance runtime records Python version; status compares it to CI 3.11 without failing `ok`.
- Constraint: Local 3.14 vs CI 3.11 was invisible; compositing could disagree later.
- Why Round 3: environment parity. Round 2 pinned Pillow, not the interpreter.
- Verification: status.ci_python is 3.11; python_mismatch is a bool; tree_digest still ignores runtime.
- Commit: `round 3 iteration 12: report local Python vs CI 3.11 on status`

## Iteration 13/50
- Evolution: `backup` zips last DNA+provenance; `--verify` checks members, jsonl pair, and fingerprint.
- Constraint: No portable copy of the mint DNA existed; a disk wipe of `build/dna` was unrecoverable.
- Why Round 3: disaster recovery. Images stay regenerable; DNA is the record.
- Verification: round-trip zip verifies clean; empty zip and missing path fail; CLI command registered.
- Commit: `round 3 iteration 13: zip and verify portable DNA backups`

## Iteration 14/50
- Evolution: `backup --restore` verifies then atomically replaces `build/dna` under the generate lock.
- Constraint: Operators had a zip but no tested restore path.
- Why Round 3: recovery must be exercised, not assumed. Restore is idempotent and refuses a bad zip.
- Verification: corrupting tokens.json then restoring yields 800 matching json/jsonl rows.
- Commit: `round 3 iteration 14: restore DNA from a verified backup zip`

## Iteration 15/50
- Evolution: Generation files carry `schema_version: 1`; loaders reject a future version.
- Constraint: A later format change could be misread as a valid 800.
- Why Round 3: data evolution / compatibility. Missing version defaults to 1 so current files still load.
- Verification: schema 99 raises; current generate includes schema_version 1.
- Commit: `round 3 iteration 15: version generation JSON and reject unknown schemas`

## Iteration 16/50
- Evolution: Layer inspector refuses PNGs larger than 8 MiB before opening them.
- Constraint: A huge file in `layers/` would exhaust RAM during validate/composite.
- Why Round 3: resource ceiling. Round 2 locked PNG count, not byte size.
- Verification: 8MiB+1 fake file is rejected; a real layer is under the cap.
- Commit: `round 3 iteration 16: reject oversized layer PNGs before decode`

## Iteration 17/50
- Evolution: Provenance runtime records SHA-256 of `requirements.txt`; status surfaces it.
- Constraint: A silent Pillow/requirements edit was invisible on the cheap operator path.
- Why Round 3: supply-chain visibility without retargeting DNA tree_digest.
- Verification: status.requirements_sha256 is 64 hex chars; tree_digest ignores it.
- Commit: `round 3 iteration 17: record requirements.txt hash on status`

## Iteration 18/50
- Evolution: `metadata --resume` skips tokens that already have valid CHIP-0007 JSON.
- Constraint: Re-running metadata after an interrupt rewrote all 800 files.
- Why Round 3: resumable workflow for metadata, matching composite --resume.
- Verification: first write counts wrote=1; second resume skipped=1.
- Commit: `round 3 iteration 18: resume CHIP-0007 metadata writes`

## Iteration 19/50
- Evolution: `status` probes that `build/` is writable and fails `ok` when it is not.
- Constraint: A read-only build dir would fail generate/composite with a raw OSError mid-run.
- Why Round 3: startup recovery / operator diagnosis before the slow path.
- Verification: probe succeeds on this machine; status.build_writable is true.
- Commit: `round 3 iteration 19: fail status when build dir is not writable`

## Iteration 20/50
- Evolution: Each generation records `generated_utc` (UTC, second precision).
- Constraint: tokens.json had no clock for incident reconstruction or backup freshness.
- Why Round 3: observability / incident timelines.
- Verification: generated_utc matches ISO-8601 Zulu regex.
- Commit: `round 3 iteration 20: stamp generation JSON with UTC time`
