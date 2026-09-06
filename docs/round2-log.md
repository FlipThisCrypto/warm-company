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

## Iteration 5/50
- Evolution: CI mint gate is `preflight`, not four duplicated commands.
- Bottleneck: GitHub Actions could stay green while the operator preflight path drifted.
- Verification: workflow contract test requires preflight.

## Iteration 6/50
- Evolution: `--mint` refuses the well-known development seed and placeholder production_seed status.
- Bottleneck: generate/preflight would happily emit 800 DNA that looks production-ready with the public dev seed.
- Verification: mint_seed_problems and preflight --mint fail on the placeholder.

## Iteration 7/50
- Evolution: CHIP-0007 validator requires symbolic title, forbids invented IPFS/HTTP media URLs, and runs in preflight.
- Bottleneck: Legal-title and URL rules lived only in comments; a metadata change could mint the opposite.
- Verification: chip0007_problems flags legal_title=true and ipfs URIs; clean payloads pass.

## Iteration 8/50
- Evolution: Atomic writes for generation, provenance, validation, and metadata JSON.
- Bottleneck: An interrupted generate could leave truncated tokens.json that validate-collection would misread as a mint.
- Verification: atomic_write_text replaces a complete file and leaves no .tmp sibling.

## Iteration 9/50
- Evolution: Dignity scanner rejects forbidden poverty-as-costume labels on traits and specials; preflight runs it.
- Bottleneck: Dignity rules were comments. A new trait id could mint a banned name.
- Verification: current library is clean; homeless-chic is rejected.

## Iteration 10/50
- Evolution: Frozen SHA-256 fingerprint of the 800 token_id:class:dna lines for the development seed.
- Bottleneck: Uniqueness tests still passed if roll weights or specials silently retargeted every token.
- Verification: fingerprint 81da0c01… and token 1 DNA locked.

## Iteration 11/50
- Evolution: Config JSON loader names the file and rejects non-objects.
- Bottleneck: A broken traits.json raised a raw JSONDecodeError with no path, stalling generate.
- Verification: invalid JSON in traits.json raises ValueError naming the file.

## Iteration 12/50
- Evolution: 12-sample catalog lives in review.py; every gate token must be resource-legal. Dropped illegal Pup determined mouth and nonexistent eyebrows.
- Bottleneck: The review gate composited unknown traits (eyebrows/determined; Pup mouth/determined).
- Verification: 12 samples + 3 strip tokens resolve_plan ok.

## Iteration 13/50
- Evolution: validate-collection requires the frozen development-seed DNA fingerprint.
- Bottleneck: Only a unit test locked DNA identity; preflight could still pass a retargeted 800.
- Verification: fingerprint constant shared by generate, validate, and tests.

## Iteration 14/50
- Evolution: Pin Pillow 12.1.0 so local and CI compositing use the same library; record version in provenance runtime.
- Bottleneck: `Pillow>=10` let CI install a different compositor than the machine that reviewed samples.
- Verification: requirements pin matches installed PIL.__version__.
