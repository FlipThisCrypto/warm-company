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

## Iteration 15/50
- Evolution: Ignore regenerable review dumps and atomic-write temp files so they cannot be committed by accident.
- Bottleneck: `build/final-polish-review/` and `build/review-v2/` sat untracked beside the real review-v3 gate for the whole round.
- Verification: gitignore test; review-v3 remains committable.

## Iteration 16/50
- Evolution: `warm-company status` reports seed lock, mint eligibility, layer completeness, and tree digest without generating 800 DNA.
- Bottleneck: Operators had to run generate/preflight to learn whether the tree was mint-blocked.
- Verification: status ok, mint_allowed false on the placeholder seed.

## Iteration 17/50
- Evolution: Collection validation checks the 800 tokens still sum to the $12,000 goods table ($13,200 gross).
- Bottleneck: Class supplies and unit costs could drift independently of the fundraiser document.
- Verification: 400×7.50 + 200×15 + 200×30 = 12000 on config and generated tokens.

## Iteration 18/50
- Evolution: Report identical PNGs that share a folder (work-boots copied as snow-boots) without failing the library.
- Bottleneck: Snug/Pup snow and work boots are byte-identical; operators had no machine-readable warning.
- Verification: duplicate_layer_pairs includes work-boots.png and snow-boots.png.

## Iteration 19/50
- Evolution: Generation result includes collection_fingerprint next to provenance so DNA identity is stored with the run.
- Bottleneck: Fingerprint lived in tests and a gitignored summary; tokens.json did not record it.
- Verification: generate_collection result fingerprint equals the frozen digest.

## Iteration 20/50
- Evolution: CLI subcommand set is a contract test covering generate through status/preflight/provenance.
- Bottleneck: New operator commands could be omitted from the parser without a failing test.
- Verification: 12 registered commands match the expected set.

## Iteration 21/50
- Evolution: Mark config/review_samples.json as the legacy 9-sample prototype; production gate is the 12-sample catalog.
- Bottleneck: Two sample lists existed; the cyan 9-sample file still looked current.
- Verification: gate=legacy-v1; REFINEMENT_SAMPLES length 12.

## Iteration 22/50
- Evolution: Lock production layer PNG count at 129 so silent library growth or deletion fails tests.
- Bottleneck: Extra/missing path tests did not assert the known accepted library size.
- Verification: LAYERS rglob count == 129.

## Iteration 23/50
- Evolution: Special catalog must be exactly 13 unique ids and names with stories and traits.
- Bottleneck: Duplicate or story-less specials could ship while generate still injected 13 rows.
- Verification: special_catalog_problems is empty.

## Iteration 24/50
- Evolution: Reconstruction strips show compositor-prepared layers so overlay boots appear at class foot anchors.
- Bottleneck: Strips showed source clip-art piles while the composite had registered feet.
- Verification: Pup strip footwear centers match Pup foot anchors.

## Iteration 25/50
- Evolution: CI caches pip from requirements.txt so Pillow install is not repeated every run.
- Bottleneck: Every GitHub Actions job re-downloaded pinned Pillow from scratch.
- Verification: workflow contains cache: pip.

## Iteration 26/50
- Evolution: Composite writes build/reports/composite_missing.json for every run.
- Bottleneck: Missing layers were stdout-only and vanished after an 800-token composite.
- Verification: CLI still accepts --report-missing; report payload shape is documented in tests.

## Iteration 27/50
- Evolution: generate CLI JSON includes collection_fingerprint so operators can record DNA identity at generate time.
- Bottleneck: Fingerprint was inside tokens.json only after opening the file.
- Verification: generate print payload key is collection_fingerprint.

## Iteration 28/50
- Evolution: Rarity report records collection fingerprint and the $12,000 goods rollup.
- Bottleneck: Rarity audit could look healthy while DNA identity or campaign math had drifted.
- Verification: build_report includes fingerprint and token_goods_usd 12000.

## Iteration 29/50
- Evolution: SECURITY.md tells reporters how to handle seed leaks, legal-title bugs, and mint bypasses.
- Bottleneck: Public fundraiser repo had no vulnerability reporting path.
- Verification: SECURITY.md names production seed, legal_title, and preflight --mint.

## Iteration 30/50
- Evolution: Compatibility forces must be idempotent (apply twice = apply once).
- Bottleneck: Sequential force rules could oscillate; generate would depend on pass count.
- Verification: review tokens and coffee/rest force are stable.

## Iteration 31/50
- Evolution: Compatibility rules may only name live traits; pruned clip-art ids removed from the rule table.
- Bottleneck: Dozens of rules still referenced backpack, umbrella, thermos, and other dropped traits.
- Verification: orphan_rule_problems is empty; DNA fingerprint must still hold.

## Iteration 32/50
- Evolution: Config integrity requires every class anatomy block to include leg origins, lower-leg centers, foot centers, and foot_replace_h.
- Bottleneck: Missing anatomy keys would fail compositing at runtime instead of preflight.
- Verification: current three classes already have the keys; preflight checks them.

## Iteration 33/50
- Evolution: .gitattributes marks PNGs/JPGs binary and JSON as LF so layer files cannot pick up CRLF.
- Bottleneck: Git already warned that layer_stack.json CRLF would be rewritten; images had no binary attribute.
- Verification: attributes file lists png/jpg binary and json lf.

## Iteration 34/50
- Evolution: Dependabot watches GitHub Actions weekly and pip monthly so the pinned compositor and CI actions can be updated on purpose.
- Bottleneck: Action and Pillow versions would only change when someone remembered.
- Verification: dependabot.yml names both ecosystems.

## Iteration 35/50
- Evolution: CONTRIBUTING start-here now requires status and preflight before a mint-quality generate.
- Bottleneck: Onboarding listed docs and tests but not the fail-closed operator path.
- Verification: CONTRIBUTING names both commands.

## Iteration 36/50
- Evolution: generate --no-specials still yields 800 unique DNA and the $12,000 goods mix, with a different fingerprint.
- Bottleneck: The no-specials operator path was untested; a quota bug could hide behind special injection.
- Verification: special_count 0, supply 800, goods 12000, fingerprint differs from the specials run.

## Iteration 37/50
- Evolution: Preflight requires CHIP-0007 collection_id to be a UUID and forbids populated marketplace URLs.
- Bottleneck: Invented website/IPFS fields could ship in collection.json before they exist.
- Verification: collection_id is a UUID; website is null; image_uris is empty.

## Iteration 38/50
- Evolution: Preflight fails if a logo PNG appears or the logo stack slot is no longer deferred.
- Bottleneck: Phase 10 logo is easy to drop into layers/shared/logo and silently paint on every token.
- Verification: logo_status deferred; no logo PNGs.

## Iteration 39/50
- Evolution: Tests require the three v3 canonical JPEGs to remain in references/approved.
- Bottleneck: Art-direction SoT could be deleted without failing generate or preflight.
- Verification: three v3 files exist and are larger than 20KB.

## Iteration 40/50
- Evolution: Occupancy, allowed-full, and blueprint templates must exist for every class.
- Bottleneck: Layer occupancy checks silently warn when templates are missing.
- Verification: three files per class in templates/.

## Iteration 41/50
- Evolution: CI cancels stale runs on the same branch so overlapping pushes do not race.
- Bottleneck: Sequential pushes queued duplicate 20-minute jobs.
- Verification: workflow concurrency cancel-in-progress.

## Iteration 42/50
- Evolution: Operator runbook documents status, preflight, mint seed lock, metadata, and the no-800-images rule.
- Bottleneck: Mint steps lived across README, CONTRIBUTING, and SECURITY.
- Verification: OPERATOR.md names preflight --mint, fingerprint, legal title, and 6aa596f.

## Iteration 43/50
- Evolution: generate CLI JSON includes token_goods_usd so a run that does not sum to $12,000 is visible immediately.
- Bottleneck: Campaign math was only inside rarity/validate reports.
- Verification: generate print payload includes token_goods_usd.

## Iteration 44/50
- Evolution: Tests require prompts/MASTER_STYLE.md to keep the magenta #FF00FF matte contract.
- Bottleneck: Style prefix could be emptied without failing generate.
- Verification: MASTER_STYLE.md contains #FF00FF and is non-trivial.

## Iteration 45/50
- Evolution: MASTER_STYLE.md now states the magenta #FF00FF matte contract used by production layers.
- Bottleneck: The style bible omitted the matte rule that prompts.json already required, so a failing test in 44 was evidence of a real gap.
- Verification: StyleBibleTests passes.

## Iteration 46/50
- Evolution: Tests require docs/blueprints/index.html to exist and name the shared center/baseline.
- Bottleneck: Blueprint HTML could go missing while anchors.json stayed; contributors open a dead page.
- Verification: index.html contains 512 and 896.

## Iteration 47/50
- Evolution: Preflight requires collection.organization to remain Not By Chance Outreach.
- Bottleneck: A rename in collection.json would mint metadata for the wrong charity without failing generate.
- Verification: organization string is locked.

## Iteration 48/50
- Evolution: CI runs `status` before the slow test suite so missing layers or config identity fail in seconds.
- Bottleneck: A broken collection.json still paid for a full unittest generate cycle.
- Verification: workflow lists status before tests.

## Iteration 49/50
- Evolution: README status table matches the operator-grade pipeline (provenance, preflight, CI, campaign math, no 800 mint).
- Bottleneck: README still described a skeleton generator and only the 9-sample prototype.
- Verification: status table names provenance, OPERATOR.md, and "800-image mint not started".

## Iteration 50/50
- Evolution: `status` reports the locked specials count of 13 alongside seed, campaign, and tree digest.
- Bottleneck: The cheap operator snapshot omitted the named-character catalog size.
- Verification: status specials == 13; full test suite and preflight run after this change.
