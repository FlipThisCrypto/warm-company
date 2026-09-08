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
