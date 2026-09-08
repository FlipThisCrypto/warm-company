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
