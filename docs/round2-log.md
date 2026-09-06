# Warm Company — Round 2 higher-order evolution log

## ROUND 2 BASELINE

- Current branch: `main`
- Starting commit: `b5be77ddf2e854c630dd712bb751ea9d090f49f6`
- Previous iteration history: Round 1 quality loop `cd7a2ff`; combinatorial resource planner `ac41641`; footwear anatomy refinement `b5be77d`. Baseline `6aa596f` preserved.
- Current build status: local Python package, no CI
- Current test status: 69 tests OK at Round 2 start
- Current deployment status: not minted; no live marketplace
- Major capabilities already present: deterministic generator, compositor, resource occupancy, CHIP-0007 metadata, 12-sample gate
- Major maturity gaps: generation not bound to config/layer hashes; no CI; no operator preflight
- Working tree status: clean except untracked regenerable review folders

---

## Iteration 1/50
- Evolution: Bind each generation to SHA-256 hashes of DNA-affecting config and every layer PNG.
- Bottleneck: DNA could not detect later config or art edits; mint would silently use a different tree.
- Verification: 73 tests OK; `python -m warm_company provenance` prints `tree_digest`.
- Commit: `round 2 iteration 1: bind generation DNA to config and layer hashes`

## Iteration 2/50
- Evolution: GitHub Actions CI runs tests, layer validation, provenance, generate, and collection validation on main.
- Bottleneck: Nothing verified generation or layers on push; drift could land untested.
- Verification: 74 tests include workflow contract; local operator commands already pass.

## Iteration 3/50
- Evolution: Provenance digest also hashes DNA-affecting Python modules.
- Bottleneck: Editing generate.py/rng/resolve could retarget the mint while config and layer hashes stayed green.
- Verification: source drift is a validate-collection failure; 5 source files in the manifest.

## Iteration 4/50
- Evolution: `warm-company preflight` fail-closed operator path (config, layers, generate, provenance).
- Bottleneck: Mint checks were four separate commands; a missed step could ship illegal DNA.
- Verification: preflight passes on the current tree; CLI wired.
