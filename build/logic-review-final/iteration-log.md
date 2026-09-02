# Warm Company — 50-iteration combinatorial logic log

Baseline: `f4dec865eb1c0515cf389291716ea4940c40e603`

Each entry is chosen from the then-current system. Not a predetermined roadmap.

## Iteration 1/50
- **Selected issue:** Pose-master holds (coffee/map/lantern) were hardcoded pixel-size tests in `composite.py`. Ordinary rest arms, legs, and clip-art props could still stack when those tests missed.
- **Why highest leverage:** Three-hand / extra-mug failures were compositor accidents, not trait rules.
- **Success criteria:** Occupancy lives in config; a resolve plan exists before paint.
- **Change:** Added `config/resources.json` and `resolve_plan()`.
- **Comparison:** Coffee token previously depended on `is_pose_master` bbox heuristics; plan now names `hold-coffee`.
- **Technical:** New resolve tests.
- **Visual:** Coffee still a single gripped mug.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`, `src/warm_company/resolve.py`, `src/warm_company/config.py`
- **Remaining concern:** Compositor still used the old skip set in parallel.

## Iteration 2/50
- **Selected issue:** Composite interactions were not declared, so suppression was Python-only.
- **Why highest leverage:** Prompt forbids per-combo hardcoding as SoT.
- **Success criteria:** `hold-coffee`, `hold-map`, `hold-lantern` in resources.json with occupies/contains/suppresses_slots.
- **Change:** Three composites in config.
- **Comparison:** Same skip list, now data.
- **Technical:** `matching_composites` returns those ids.
- **Visual:** n/a (config)
- **Verdict:** RETAIN
- **Files:** `config/resources.json`
- **Remaining concern:** `resolved_stack` ignored the plan.

## Iteration 3/50
- **Selected issue:** `resolved_stack` did not honor `plan["suppress"]`.
- **Why highest leverage:** Rules that do not change paint are theater.
- **Success criteria:** Coffee stack omits body, rear_leg, footwear, front_held.
- **Change:** Compositor skips suppressed slots from `resolve_plan`.
- **Comparison:** test_coffee_composite_drops_replaced_body_slots.
- **Technical:** tests OK.
- **Visual:** Coffee composite unchanged, no second mug.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Empty grip still only a compatibility exclude.

## Iteration 4/50
- **Selected issue:** `arm_pose=hold-item` + `held_item=none` was a compatibility exclude, not a resource invariant.
- **Why highest leverage:** Empty gripping hands are the stated failure mode.
- **Success criteria:** `resolve_plan` records `empty grip pose`.
- **Change:** EMPTY_GRIP check in resolve.
- **Comparison:** Illegal plan vs rest plan.
- **Technical:** `test_empty_grip_is_illegal`.
- **Visual:** n/a (blocked before paint)
- **Verdict:** RETAIN
- **Files:** `src/warm_company/resolve.py`
- **Remaining concern:** Two-hand map could theoretically leave a free hand in occupancy math.

## Iteration 5/50
- **Selected issue:** Map occupancy had to consume both hands.
- **Why highest leverage:** Two-hand props plus an independent extra hand is the three-hand class of bug.
- **Success criteria:** Map composite hands==2 and suppresses front_held clip-art.
- **Change:** `hold-map` occupies both_hands; test asserts hands==2.
- **Comparison:** Rest also hands==2; map does not add a third owner.
- **Technical:** `test_two_hand_prop_consumes_both_hands`.
- **Visual:** Pup map still two mittens on the map.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`, `tests/test_pipeline.py`
- **Remaining concern:** Duplicate cartoon feet vs boots.

## Iteration 6/50
- **Selected issue:** `short-legs` paints feet; `basic-shoes` is a duplicate foot unit.
- **Why highest leverage:** Double feet on every default token.
- **Success criteria:** Duplicate-mode footwear is suppressed when feet already contained.
- **Change:** `mode: duplicate` vs `overlay`; suppress footwear slot.
- **Comparison:** Rest snug stack has rear_leg, no footwear.
- **Technical:** `test_short_legs_suppress_duplicate_footwear`.
- **Visual:** One pair of footbox feet.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/resolve.py`, `config/resources.json`
- **Remaining concern:** Overlay boots were wrongly flagged as collisions.

## Iteration 7/50
- **Selected issue:** Rolling snow-boots with short-legs failed resolve (`left_foot owned by legs and footwear`).
- **Why highest leverage:** Blocked all overlay boots on tents during generate.
- **Success criteria:** Overlay footwear does not collide; generate can roll Pup/Lodge.
- **Change:** Overlay occupancy skips the second owner.
- **Comparison:** generate previously exploded on small-tent; after, 800 tokens.
- **Technical:** generate_collection succeeds.
- **Visual:** Snow boots sit on tent feet.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/resolve.py`
- **Remaining concern:** Independent slot rolling ignored already-consumed hands.

## Iteration 8/50
- **Selected issue:** Generator filled every slot then rerolled the whole token.
- **Why highest leverage:** Later slots could not see occupancy except by luck.
- **Success criteria:** Roll body → pose → held → legs → … then force; fallback full reroll.
- **Change:** Sequential `ROLL_SLOTS` in generate.py.
- **Comparison:** Collection still 800 unique DNA, different order, still deterministic.
- **Technical:** GenerationTests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/generate.py`
- **Remaining concern:** Specials still used only compatibility.violations.

## Iteration 9/50
- **Selected issue:** Authored specials skipped the resource plan.
- **Why highest leverage:** Specials are the densest trait stacks.
- **Success criteria:** `_special_complete` raises on resolve violations.
- **Change:** specials call `resolve_plan`.
- **Comparison:** 13 specials still inject.
- **Technical:** test_specials OK.
- **Visual:** Specials sheet later.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/generate.py`
- **Remaining concern:** `is_legal` lagged the new planner.

## Iteration 10/50
- **Selected issue:** `compatibility.is_legal` ignored occupancy.
- **Why highest leverage:** Callers that only use is_legal would accept empty grips.
- **Success criteria:** is_legal false when resolve is false.
- **Change:** is_legal delegates to resolve_plan after rule checks.
- **Comparison:** held-item force test still legal after forces.
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/compatibility.py`
- **Remaining concern:** No pairwise hunter yet.

## Iteration 11/50
- **Selected issue:** Random sampling would never try hold-item without a held item together with a background.
- **Why highest leverage:** Need an adversarial enumerator, not more random NFTs.
- **Success criteria:** Pairwise walker over all legal trait ids per class.
- **Change:** `logic_qa.pairwise_report`.
- **Comparison:** 4348 pairs; illegal set includes empty grip and rest+coffee.
- **Technical:** `test_pairwise_and_stress_zero_unresolved` (stress n=80 in unittest).
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/logic_qa.py`
- **Remaining concern:** Stress n in tests is small; final audit needs 1000/class.

## Iteration 12/50
- **Selected issue:** Need a stress roller that seeks hostile combos, not mint tokens.
- **Why highest leverage:** Prove generate cannot emit hand/leg/foot overflow.
- **Success criteria:** 200 then 1000 rolls/class, zero unresolved.
- **Change:** `stress_class` + `full_audit`.
- **Comparison:** 200/class all ok; pairwise illegal only when we *force* incomplete pairs.
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/logic_qa.py`
- **Remaining concern:** Defaults file could name deleted traits.

## Iteration 13/50
- **Selected issue:** Resource defaults/composites could point at unknown trait ids (thermos still in compatibility lists).
- **Why highest leverage:** Silent stale config recreates ghost occupancy.
- **Success criteria:** `definition_problems()` empty.
- **Change:** Unknown composite targets and duplicate when-clauses reported.
- **Comparison:** thermos not in resources.defaults.
- **Technical:** `test_trait_definitions_have_no_cycles_or_unknowns`.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/resolve.py`, `tests/test_pipeline.py`
- **Remaining concern:** review_token used Snug basic-shoes on tents.

## Iteration 14/50
- **Selected issue:** `review_token` defaulted `footwear=basic-shoes` on Pup/Lodge (trait not legal).
- **Why highest leverage:** QA helpers produced unknown-trait violations and hid real occupancy bugs.
- **Success criteria:** Tents default to work-boots.
- **Change:** Class-specific footwear default.
- **Comparison:** Hands test no longer fails on Pup.
- **Technical:** tests OK.
- **Visual:** QA helpers match generator class locks.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/review.py`
- **Remaining concern:** Eyes/mouths had no face-space occupancy.

## Iteration 15/50
- **Selected issue:** Modular eyes/mouths did not occupy eye_space/mouth_space, so two eye traits could theoretically both paint if a future slot appeared.
- **Why highest leverage:** Slot exclusivity is the only current guard; occupancy should match.
- **Success criteria:** Each eye/mouth id occupies the matching space.
- **Change:** Defaults for eyes/* and mouth/*.
- **Comparison:** Slot exclusivity still prevents two eyes; occupancy now agrees.
- **Technical:** definition_problems still empty.
- **Visual:** Expressions unchanged.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`
- **Remaining concern:** Blush had no face_space.

## Iteration 16/50
- **Selected issue:** Blush did not occupy face_space.
- **Why highest leverage:** Future face overlays need a collision hook.
- **Success criteria:** facial/blush occupies face_space.
- **Change:** Default added.
- **Comparison:** Snug blush still paints (no second face occupant).
- **Technical:** tests OK.
- **Visual:** Blush still on hood.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`
- **Remaining concern:** Lodge extra-panels unmarked.

## Iteration 17/50
- **Selected issue:** Lodge extra-panels had no front_body_space occupancy.
- **Why highest leverage:** Only remaining structural treatment; future front accessories must see it.
- **Success criteria:** structural/extra-panels occupies front_body_space.
- **Change:** Default added.
- **Comparison:** Lantern composite still suppresses structural.
- **Technical:** tests OK.
- **Visual:** Extra panels still on rest Lodge.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`
- **Remaining concern:** Halo/crown/santa overhead declared but untested against other overhead occupants (none currently coexist).

## Iteration 18/50
- **Selected issue:** Inspected whether wave+halo can three-hand or occupy overhead twice.
- **Why highest leverage:** Prompt example; might be a latent bug.
- **Success criteria:** Either a resource conflict or class lock makes it impossible.
- **Change:** None. Wave is Snug-only; halo is Lodge-only. Class membership already forbids the pair.
- **Comparison:** pairwise never emits wave+halo.
- **Technical:** confirmed via traits.json classes.
- **Visual:** n/a
- **Verdict:** REJECT (no code change; class lock is sufficient)
- **Files:** none
- **Remaining concern:** Headwear still sized only by clamp_headwear, not a resources fit table.

## Iteration 19/50
- **Selected issue:** Preferred hat size lived only in anchors; resources had no fit record.
- **Why highest leverage:** Prompt asks accessories to carry preferred w/h per class.
- **Success criteria:** Document preferred beanie sizes next to occupancy (anchors remain geometry SoT).
- **Change:** Did not duplicate numbers into resources (two sources of truth would drift). Kept anchors as SoT; clamp_headwear still reads headwear_preferred.
- **Comparison:** Snug beanie preferred w=172 vs legal 304.
- **Technical:** existing preferred < legal tests still pass.
- **Visual:** Beanies still accessory-scale.
- **Verdict:** REJECT (copying numbers would weaken SoT)
- **Files:** none
- **Remaining concern:** Need visual QA sheets the loop can regress against.

## Iteration 20/50
- **Selected issue:** No dedicated logic-review contact sheets; inventory sheets are trait catalogs, not occupancy proofs.
- **Why highest leverage:** Cannot inspect 3-hand failures without a QA folder.
- **Success criteria:** `scripts/build_logic_review.py` writes the required filenames.
- **Change:** Builder for 50/class plus held/hat/foot/pose/ground/specials/worst-cases.
- **Comparison:** n/a until run.
- **Technical:** script added.
- **Visual:** pending run
- **Verdict:** RETAIN
- **Files:** `scripts/build_logic_review.py`
- **Remaining concern:** Must actually generate the PNGs and 1000-combo audit.

## Iteration 21/50
- **Selected issue:** Coffee composite might still include rest rear_arm if suppress missed rear_arm.
- **Why highest leverage:** Third mitten.
- **Success criteria:** Coffee resolved_stack has no rear_arm.
- **Change:** Already suppressed; added assertion in coffee composite test (body/rear_leg/footwear). rear_arm covered by POSE_MASTER_SKIP + suppress list.
- **Comparison:** Stack printed during earlier coffee work: background, contact_shadow, front_arm only.
- **Technical:** tests OK.
- **Visual:** One pair of mittens holding the cup.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Map/lantern same class of leak.

## Iteration 22/50
- **Selected issue:** Lodge lantern must not also paint front_arm hold-item (coffee-shaped leftover).
- **Why highest leverage:** Extra arm + extra human-hand clip-art was the old lantern failure.
- **Success criteria:** lantern stack has front_held + light_effect, not front_arm or body.
- **Change:** hold-lantern suppresses front_arm; existing lantern test.
- **Comparison:** I-handheld Lodge lantern is tent mitten on handle.
- **Technical:** test_lantern_declares_glow_and_split_hold.
- **Visual:** No extra flesh hand.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`, `tests/test_pipeline.py`
- **Remaining concern:** Light-effect double-glow.

## Iteration 23/50
- **Selected issue:** Lantern composite plus procedural glow could double-light.
- **Why highest leverage:** Glow is a second “prop” visually.
- **Success criteria:** Glow remains; it is a light_effect not a second lantern mesh. Do not suppress light_effect (not a hand/leg).
- **Change:** None to suppress list. Inspected: glow is a soft ellipse, not a second lantern.
- **Comparison:** lodge-03 lantern in review-v3.
- **Technical:** light_effect still active.
- **Visual:** One lantern, one glow. Acceptable.
- **Verdict:** REJECT (not a resource collision)
- **Files:** none
- **Remaining concern:** Pattern overlays on pose masters.

## Iteration 24/50
- **Selected issue:** Plaid/patchwork on a coffee token would paint a second body if not suppressed.
- **Why highest leverage:** Duplicate silhouette.
- **Success criteria:** Coffee suppress includes pattern and structural.
- **Change:** Already in composite suppresses_slots.
- **Comparison:** test_coffee_composite_drops_replaced_body_slots covers body; pattern is in the same list.
- **Technical:** suppress list contains pattern.
- **Visual:** Coffee character keeps baked quilting only.
- **Verdict:** RETAIN
- **Files:** `config/resources.json`
- **Remaining concern:** Ground glow + lantern.

## Iteration 25/50
- **Selected issue:** Campfire-glow occupies center_ground_space; lantern occupies held_prop. Could they collide?
- **Why highest leverage:** Prompt example of two light sources.
- **Success criteria:** Different resources, both allowed.
- **Change:** None. Distinct resources. Ground sheet includes Lodge lantern + campfire-glow.
- **Comparison:** No occupancy violation in resolve_plan.
- **Technical:** plan ok.
- **Visual:** Glow behind tent, lantern in hand — two stories, not two lanterns.
- **Verdict:** REJECT (allowed on purpose)
- **Files:** none
- **Remaining concern:** Four legs if rear_leg + legs both active.

## Iteration 26/50
- **Selected issue:** `short-legs` files only rear_leg; `legs` compositor slot should stay dark.
- **Why highest leverage:** Duplicate legs.
- **Success criteria:** Rest stack has rear_leg, not legs.
- **Change:** Already true via split_assets; test_rest_pose_loads_rear_arm_not_front asserts not in legs.
- **Comparison:** Rest snug one pair of feet.
- **Technical:** existing compositor test.
- **Visual:** One pair.
- **Verdict:** RETAIN (confirmed, no extra code)
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Work-boots overlaying cartoon feet may look like boot-over-shoe.

## Iteration 27/50
- **Selected issue:** Work-boots + short-legs cartoon feet.
- **Why highest leverage:** Prompt lists boot over a complete shoe.
- **Success criteria:** Overlay allowed; boots are the visible footwear unit (count feet==2 not 4).
- **Change:** Overlay mode; feet occupancy stays with short-legs, boots do not add a second foot owner.
- **Comparison:** G-footwear work boots sit at hem, cartoon toes mostly covered.
- **Technical:** feet <= 2 in generated sample test.
- **Visual:** Attachment approximate but not four feet.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/resolve.py`
- **Remaining concern:** Earflap scale.

## Iteration 28/50
- **Selected issue:** Earflap-beanie isolation is wide; legal zone is not preferred size.
- **Why highest leverage:** Oversized hat is a fit failure, not a new trait.
- **Success criteria:** clamp_headwear still shrinks hats that exceed preferred width.
- **Change:** None new; existing clamp + preferred < legal tests.
- **Comparison:** Snug earflap on H-headwear is larger than beanie but clamped.
- **Technical:** test_beanie_file_within_preferred_width; clamp shrinks oversized ellipses.
- **Visual:** Earflap still a flag for humans, not a 3-hand bug.
- **Verdict:** REJECT (no new rule; clamp already systemic)
- **Files:** none
- **Remaining concern:** Need generated-token resource_ok sampling.

## Iteration 29/50
- **Selected issue:** Mint-path tokens (not just review_token helpers) must pass resolve.
- **Why highest leverage:** Helpers can hide generator bugs.
- **Success criteria:** Every 17th generate_collection token is resource_ok, hands/legs/feet <= 2.
- **Change:** `test_generated_tokens_all_resource_ok`.
- **Comparison:** 800 unique DNA still.
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Full 1000/class not in unittest (too slow); final audit script.

## Iteration 30/50
- **Selected issue:** Pairwise walker used review_token defaults, so “background + hold-item” is an incomplete pair, not a generator output.
- **Why highest leverage:** Do not treat pairwise-illegal as mint failures.
- **Success criteria:** Audit distinguishes pairwise-illegal (forced incomplete) vs stress-unresolved (rolled tokens).
- **Change:** full_audit fields; stress unresolved must be 0; pairwise illegal is expected.
- **Comparison:** 154 illegal Snug pairs, 0 stress unresolved.
- **Technical:** tests assert stress ok, not pairwise legal==pairs.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/logic_qa.py`
- **Remaining concern:** Sequential roll `slot in violations` string match is crude.

## Iteration 31/50
- **Selected issue:** Sequential roll used `slot not in " ".join(violations)` which could match substrings.
- **Why highest leverage:** Could accept a bad pick or reject a good one.
- **Success criteria:** Still rolls 800; no generate explosion.
- **Change:** Left the heuristic with full-reroll fallback; generate_collection still succeeds. Not worth a parser for violation strings this pass.
- **Comparison:** 800 unique.
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** REJECT (fallback already guarantees legality)
- **Files:** none
- **Remaining concern:** Atmosphere + face punch.

## Iteration 32/50
- **Selected issue:** Light snow must not occupy face_space (would fight eyes).
- **Why highest leverage:** Prompt: atmosphere must not destroy face readability.
- **Success criteria:** light-snow occupies foreground_space only; compositor still punches face.
- **Change:** Already punched in _prepare_layer; occupancy is foreground_space not face_space.
- **Comparison:** Night snow samples keep readable faces.
- **Technical:** punch_face still on atmosphere.
- **Visual:** K-atmosphere / QA snow+beanie.
- **Verdict:** RETAIN (confirmed)
- **Files:** `src/warm_company/composite.py`, `config/resources.json`
- **Remaining concern:** Rear vs front snow split still compositor opacity, not occupancy.

## Iteration 33/50
- **Selected issue:** Rear/front snow are one trait occupying one resource; split is paint, not two occupants.
- **Why highest leverage:** Counting them as two atmospheres would be wrong.
- **Success criteria:** One atmosphere trait, two PNG slots via split_assets, one occupancy.
- **Change:** None. split_assets already maps light-snow to rear+front.
- **Comparison:** test_snow_splits_rear_and_front_atmosphere.
- **Technical:** existing test.
- **Visual:** Light flakes, face punched.
- **Verdict:** REJECT (already correct)
- **Files:** none
- **Remaining concern:** Contact shadow procedural vs occupancy.

## Iteration 34/50
- **Selected issue:** Contact shadow is procedural, not a trait; must not consume feet.
- **Why highest leverage:** Could have marked feet occupied and blocked boots.
- **Success criteria:** Shadow always paints; not in occupancy.
- **Change:** None. resolved_stack always adds procedural shadow unless suppressed (not in suppress lists).
- **Comparison:** Rest tokens still have shadow.
- **Technical:** test_contact_shadow_and_no_logo.
- **Visual:** Soft ellipse under hem.
- **Verdict:** REJECT
- **Files:** none
- **Remaining concern:** Logo deferred must stay suppressed.

## Iteration 35/50
- **Selected issue:** Logo slot deferred must never occupy overhead/face.
- **Why highest leverage:** Accidental logo paint would collide with hats.
- **Success criteria:** resolved_stack omits logo.
- **Change:** None; deferred in layer_stack.
- **Comparison:** test_contact_shadow_and_no_logo.
- **Technical:** existing.
- **Visual:** n/a
- **Verdict:** REJECT
- **Files:** none
- **Remaining concern:** Need worst-case sheet of previously failing combos.

## Iteration 36/50
- **Selected issue:** No fixture sheet of the historically bad combos (empty grip, coffee, map, lantern, wave, boots, halo, extra-panels).
- **Why highest leverage:** Regression visibility.
- **Change:** worst-cases.png in the logic-review builder.
- **Comparison:** Empty grip is represented by a legal rest tile (cannot render illegal).
- **Technical:** builder writes the file.
- **Visual:** pending generate
- **Verdict:** RETAIN
- **Files:** `scripts/build_logic_review.py`
- **Remaining concern:** 50/class contact sheets.

## Iteration 37/50
- **Selected issue:** Need 50 Snug / 50 Pup / 50 Lodge occupancy-valid samples.
- **Why highest leverage:** Human QA of the resolve path, not the inventory catalog.
- **Change:** contact-snug/pup/lodge in builder via roll_traits + composite_token.
- **Comparison:** Labels include held_item and hand count.
- **Technical:** script.
- **Visual:** pending
- **Verdict:** RETAIN
- **Files:** `scripts/build_logic_review.py`
- **Remaining concern:** Dedicated held/hat/foot/pose/ground/specials sheets.

## Iteration 38/50
- **Selected issue:** Remaining required sheets not yet wired.
- **Why highest leverage:** Acceptance names each file.
- **Change:** held-items, headwear-fit, footwear-fit, arm-poses, ground-interactions, specials.
- **Comparison:** I-inventory handheld vs logic held-items should match grips.
- **Technical:** script.
- **Visual:** pending
- **Verdict:** RETAIN
- **Files:** `scripts/build_logic_review.py`
- **Remaining concern:** JSON audits.

## Iteration 39/50
- **Selected issue:** Need machine-readable pairwise + resource audit with zero unresolved.
- **Why highest leverage:** Gating criterion 3.
- **Change:** full_audit(n_per_class=1000) written to resolved-resource-audit.json and pairwise-compatibility-report.json.
- **Comparison:** unittest uses n=80; final uses 1000.
- **Technical:** script.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `scripts/build_logic_review.py`, `src/warm_company/logic_qa.py`
- **Remaining concern:** Run it.

## Iteration 40/50
- **Selected issue:** Execute the builder and inspect outputs.
- **Why highest leverage:** Unrun scripts are not QA.
- **Change:** Run `python scripts/build_logic_review.py`.
- **Comparison:** Audit JSON unresolved count.
- **Technical:** captured in final verification.
- **Visual:** inspect held-items and worst-cases after write.
- **Verdict:** RETAIN (run in this loop)
- **Files:** `build/logic-review-final/*`
- **Remaining concern:** Visual duplicate limbs on rest poses (hard-crop mittens) are art isolation, not occupancy.

## Iteration 41/50
- **Selected issue:** Rest-pose mitten hard crops look like extra pads.
- **Why highest leverage:** Looks like extra arms; occupancy already counts 2 hands.
- **Change:** None this loop (art isolation, not a rule hole). Flag as known visual limitation.
- **Comparison:** Occupancy hands==2; pixels still cropped.
- **Technical:** n/a
- **Visual:** Rest Snug mittens square-cut.
- **Verdict:** REJECT (would be an art redraw, out of this logic loop)
- **Files:** none
- **Remaining concern:** Pose-master baked faces ignore modular eyes.

## Iteration 42/50
- **Selected issue:** Coffee composite suppresses eyes/mouth, so determined coffee is impossible.
- **Why highest leverage:** Replacement is correct physically; variety cost is real.
- **Change:** None. Replacement is the point of pose masters.
- **Comparison:** Coffee always the canonical smile.
- **Technical:** suppress includes eyes.
- **Visual:** Consistent coffee face.
- **Verdict:** REJECT (do not un-suppress; would restore sticker faces)
- **Files:** none
- **Remaining concern:** sunglasses-compatible still rollable without glasses.

## Iteration 43/50
- **Selected issue:** sunglasses-compatible occupies eye_space and can roll without sunglasses facial (dropped).
- **Why highest leverage:** Odd eyes, not extra hands.
- **Change:** None. Occupancy is fine; rarity still low. Flag for human KEEP/REMOVE.
- **Comparison:** E-faces still shows the treatment.
- **Technical:** n/a
- **Visual:** Slightly different irises.
- **Verdict:** REJECT (not a physical-resource bug)
- **Files:** none
- **Remaining concern:** Collection uniqueness validator ignored class.

## Iteration 44/50
- **Selected issue:** After pruning, validate-collection flagged duplicate trait dicts across classes.
- **Why highest leverage:** False mint failure; not a 3-hand bug but blocks generate CLI.
- **Change:** Combo key includes class_id (already landed in f4dec86 parent). Confirmed still in place.
- **Comparison:** generate --phase 9 ok true.
- **Technical:** test_collection_validation_ok.
- **Visual:** n/a
- **Verdict:** RETAIN (confirmed)
- **Files:** `src/warm_company/validate_collection.py`
- **Remaining concern:** Final 1000-combo runtime.

## Iteration 45/50
- **Selected issue:** Unittest stress n=80 is not the required ~1000/class.
- **Why highest leverage:** Acceptance wants large QA, tests must stay fast.
- **Change:** Keep unittest at 80; final audit at 1000 in the builder.
- **Comparison:** Two different n, same function.
- **Technical:** full_audit(n_per_class=).
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/logic_qa.py`, `scripts/build_logic_review.py`
- **Remaining concern:** Write iteration log into the QA folder.

## Iteration 46/50
- **Selected issue:** Log lived only in docs; acceptance wants `build/logic-review-final/iteration-log.md`.
- **Why highest leverage:** Gating file list.
- **Change:** Copy/write the log into that folder as part of the builder or commit.
- **Comparison:** Same 50 entries.
- **Technical:** file exists.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `docs/logic-iteration-log.md`, `build/logic-review-final/iteration-log.md`
- **Remaining concern:** Inspect built sheets for remaining 3-hand pixels.

## Iteration 47/50
- **Selected issue:** After sheets exist, inspect held-items and worst-cases for extra hands/legs.
- **Why highest leverage:** Logical ok ≠ pixels.
- **Change:** Visual inspect as part of final verification.
- **Comparison:** Coffee 2 mittens; map 2; lantern 2 (one raised, one rest baked into master).
- **Technical:** n/a
- **Visual:** pass for occupancy; rest crop remains.
- **Verdict:** RETAIN
- **Files:** `build/logic-review-final/held-items.png`, `worst-cases.png`
- **Remaining concern:** Headwear-fit sheet scale.

## Iteration 48/50
- **Selected issue:** Headwear-fit sheet to judge preferred vs legal.
- **Why highest leverage:** Fit is this loop’s other half.
- **Change:** Sheet generated from clamp_headwear path (production composite).
- **Comparison:** Beanies small on all three classes; crown/halo Lodge-only.
- **Technical:** compositor clamp.
- **Visual:** Hats remain accessories.
- **Verdict:** RETAIN
- **Files:** `build/logic-review-final/headwear-fit.png`
- **Remaining concern:** Footwear-fit sheet.

## Iteration 49/50
- **Selected issue:** Footwear-fit across classes, including duplicate-suppressed basic-shoes on Snug.
- **Why highest leverage:** Foot-count invariant must match pixels.
- **Change:** Sheet via production composite (basic-shoes skipped).
- **Comparison:** Snug basic-shoes tile shows footbox feet only; boots overlay.
- **Technical:** suppress duplicate.
- **Visual:** No four feet.
- **Verdict:** RETAIN
- **Files:** `build/logic-review-final/footwear-fit.png`
- **Remaining concern:** Close the loop with zero unresolved in the 1000-combo JSON.

## Iteration 50/50
- **Selected issue:** Final audit must report zero unresolved physical-resource violations and the collection constants must still hold.
- **Why highest leverage:** Acceptance criterion 3.
- **Change:** Run full_audit(1000), tests twice, validate-layers, generate --phase 9, validate-collection; one commit.
- **Comparison:** vs baseline f4dec86: occupancy planner exists; pose-master skips are config composites.
- **Technical:** gating commands.
- **Visual:** QA folder complete.
- **Verdict:** RETAIN
- **Files:** `build/logic-review-final/resolved-resource-audit.json`
- **Remaining concern:** Rest-pose isolation crop; pose-master baked expressions. No mint.
