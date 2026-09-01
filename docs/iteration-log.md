# Warm Company — 50-iteration quality log

Baseline: `d7d466a35c1281276cb900eba7fbf9075d728962`

Each entry is chosen from the then-current project. Not a predetermined roadmap.

## Iteration 1/50
- **Selected issue:** Production compositor ignored `layer_stack.json` v2 (no rear_leg/rear_atmosphere/light_effect; rear_arm only for wave).
- **Why highest leverage:** 800 tokens would composite the old sticker stack, not the locked attachment architecture.
- **Success criteria:** `resolved_stack` emits rear_arm before body for rest; lantern includes light_effect; snow splits rear/front; oversized hats clamp to preferred width.
- **Change:** Rewrote `composite.py` to drive from the stack + `split_assets`; synced `traits.json` arm/leg/lantern files; tests for stack, lantern, snow, hat clamp.
- **Comparison:** Before: rest pose never loaded rear_arm. After: rest loads rear_arm then body; a live Snug composite used that order (legacy art still noisy — next issue).
- **Technical:** `python tests/test_pipeline.py` 16 tests OK.
- **Visual:** Compositor order is correct; current layer PNGs still include sticker faces/extra shoes. System retained, art cleanup follows.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `config/traits.json`, `config/layer_stack.json`, `tests/test_pipeline.py`
- **Remaining concern:** Featureless cream face ovals and leftover v1 eyes/footwear still paint on top of v3 bodies.

## Iteration 2/50
- **Selected issue:** Featureless cream face ovals composite as stickers on v3 bodies that already own the hood/door.
- **Why highest leverage:** Destroys integrated-face rule on every token that has a `face` layer.
- **Success criteria:** Blank cream panels skipped; faces with ink still load; tests cover the detector.
- **Change:** `is_blank_face_panel` / `layer_has_ink`; compositor returns None for blank `face` slots.
- **Comparison:** iter01 had a second cream oval; iter02 uses the bag hood as the face.
- **Technical:** 17 tests OK.
- **Visual:** Hood-integrated face. Extra shoes and googly v1 eyes remain.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Duplicate feet (rear_leg + basic-shoes) and v1 eye stickers.

## Iteration 3/50
- **Selected issue:** Rear-leg cartoon feet plus default `basic-shoes` produced a second pair of shoes on the hem.
- **Why highest leverage:** Breaks sleeping-bag-first identity and the hidden-leg-root rule on every default token.
- **Success criteria:** Default rest pose shows one pair of feet emerging from the footbox/skirt.
- **Change:** `short-legs` occupies only `rear_leg`; compositor skips default footwear when rear_leg is active.
- **Comparison:** iter02 extra shoes; iter03 footbox feet only.
- **Technical:** 17 tests OK; rest-pose stack omits `legs` and `footwear`.
- **Visual:** Legs emerge from the open footbox. Arms still noisy.
- **Verdict:** RETAIN
- **Files:** `config/layer_stack.json`, `config/traits.json`, `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Cyan fringe on v1 eyes; rear-arm isolations still look like extra quilt pads.

## Iteration 4/50
- **Selected issue:** Cyan/magenta extraction fringe on v1 layers (visible on eyes).
- **Why highest leverage:** Every composite inherits contaminated edges.
- **Success criteria:** `strip_key_fringe` reduces cyan edge alpha; unit test covers a cyan pixel.
- **Change:** `matte.strip_key_fringe`; compositor runs it on every layer.
- **Comparison:** Test pixel alpha 120 → <50. Visual composite still uses v1 eyes (next).
- **Technical:** tests OK.
- **Visual:** Safety net retained; existing art still googly.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/matte.py`, `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Fringe not yet reported by validate-layers.

## Iteration 5/50
- **Selected issue:** `validate_layers` did not report extraction fringe.
- **Why highest leverage:** Bad mattes could ship undetected.
- **Success criteria:** Transparent layers get a fringe warning field; errors still only for hard failures.
- **Change:** `fringe_report` wired into `validate_library` as warnings.
- **Comparison:** n/a (QA instrumentation).
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/validate_layers.py`
- **Remaining concern:** Face features can paint outside the hood/door.

## Iteration 6/50
- **Selected issue:** Eyes/mouth could paint outside the hood/door.
- **Why highest leverage:** Sticker features destroy object identity at the face.
- **Success criteria:** Pixels outside the door/hood are dropped.
- **Change:** `clip_to_face_region` on eyes/eyebrows/mouth/facial.
- **Comparison:** Unit test: corner pixel alpha 0, hood pixel kept.
- **Technical:** tests OK.
- **Visual:** Features constrained to the opening.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Extra PNGs not in traits.json would still be treated as legal.

## Iteration 7/50
- **Selected issue:** No check that every layer PNG is a declared trait id.
- **Why highest leverage:** CONTRIBUTING says extra files are errors, not extra traits.
- **Success criteria:** Unknown stems fail layer validation; current library has 0 extras.
- **Change:** `FOLDER_TO_SLOT` + trait-id membership in `validate_library`.
- **Comparison:** Scan found 0 extras.
- **Technical:** tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `src/warm_company/validate_layers.py`
- **Remaining concern:** Lodge vs Pup width was documented but not asserted.

## Iteration 8/50
- **Selected issue:** Lodge>Pup size and split_assets/trait `files` agreement were untested contracts.
- **Why highest leverage:** Drift here would silently rescale the fundraiser identity.
- **Success criteria:** Tests fail if Lodge is not wider than Pup, or if trait files disagree with split_assets.
- **Change:** Two tests in `test_pipeline.py`.
- **Comparison:** n/a (contract tests).
- **Technical:** 21 tests OK.
- **Visual:** n/a
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Rear-arm isolations still don't match the locked canonicals.

## Iteration 9/50
- **Selected issue:** Snug rear-arm isolation had extra quilt pads that stuck out beside the bag.
- **Why highest leverage:** Rest pose is the majority of 400 Snugs.
- **Success criteria:** Mittens emerge from behind the bag without extra stars/pads.
- **Change:** New isolation from canonical v3 keyed to `layers/sleeping-bag/arms-rear/rest.png`.
- **Comparison:** iter03 extra pads vs iter09 hidden-shoulder mittens.
- **Technical:** chroma_key; 1024 RGBA.
- **Visual:** Better attachment. Hugging pose reduced to side mittens.
- **Verdict:** RETAIN
- **Files:** `layers/sleeping-bag/arms-rear/rest.png`
- **Remaining concern:** Pup/Lodge arm isolations still drift.

## Iteration 10/50
- **Selected issue:** Fresh Pup/Lodge arm isolations (111, 113) added belts/disconnected tubes.
- **Why highest leverage:** Needed to know if Imagine could match canonicals.
- **Success criteria:** Isolations must match canonical attachment; worse files must not replace production layers.
- **Change:** Generated 111/113; compared; did not replace production files.
- **Comparison:** 111 belts/rectangles and 113 disconnected tubes vs current rest arms.
- **Technical:** Did not write over `arms-rear/rest.png`. Tests still green.
- **Visual:** New isolations worse; kept prior files.
- **Verdict:** REJECT
- **Files:** none kept
- **Remaining concern:** Default eyes still v1 googly stickers.

## Iteration 11/50
- **Selected issue:** Snug had no `eyes/normal.png`; happy eyes were googly stickers.
- **Why highest leverage:** Default expression is on most tokens.
- **Success criteria:** Closed-eye arcs sit on the hood like the canonical.
- **Change:** Extracted canonical closed eyes → `layers/sleeping-bag/eyes/normal.png`.
- **Comparison:** Googly sticker vs hood-integrated arcs.
- **Technical:** bbox y≈340–400 near eye baseline 360.
- **Visual:** Matches canonical language.
- **Verdict:** RETAIN
- **Files:** `layers/sleeping-bag/eyes/normal.png`
- **Remaining concern:** Pup/Lodge default eyes.

## Iteration 12/50
- **Selected issue:** Pup default eyes could be extracted from the canonical door-face.
- **Why highest leverage:** Door-as-face must stay consistent.
- **Success criteria:** Eyes sit inside the cream door, not as a separate circular panel.
- **Change:** `layers/small-tent/eyes/normal.png` from canonical.
- **Comparison:** Eyes sit on the cream door in the Pup composite.
- **Technical:** bbox inside door y-range; 1024 RGBA.
- **Visual:** Acceptable; slightly large.
- **Verdict:** RETAIN
- **Files:** `layers/small-tent/eyes/normal.png`
- **Remaining concern:** Lodge eyes.

## Iteration 13/50
- **Selected issue:** Lodge eye isolation 116 sat on the fly above the D-door.
- **Why highest leverage:** Violates door-is-face.
- **Success criteria:** Lodge eyes must live on the D-door, not the fly.
- **Change:** Generated 116; restored previous `layers/large-tent/eyes/normal.png` from git.
- **Comparison:** Eyes on fly vs eyes on door (restored).
- **Technical:** `git checkout HEAD -- layers/large-tent/eyes/normal.png`.
- **Visual:** New file worse; restored.
- **Verdict:** REJECT
- **Files:** lodge eyes restored to prior version
- **Remaining concern:** Black feature strokes vs umber.

## Iteration 14/50
- **Selected issue:** Canonical-extracted Snug eyes were pure black, not umber.
- **Why highest leverage:** Breaks one-illustrator outline color.
- **Success criteria:** Pure-black feature pixels recolor to collection umber.
- **Change:** `umber_ink()` on eyes/mouth/facial at composite time.
- **Comparison:** Unit test 10,10,10 → UMBER (58,42,34).
- **Technical:** tests OK.
- **Visual:** Features restyle toward collection outline.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Hats filling legal zone.

## Iteration 15/50
- **Selected issue:** Headwear PNGs wider than preferred size were only clamped at composite, not flagged in QA.
- **Why highest leverage:** Oversized hats would ship undetected in 800 outputs.
- **Success criteria:** validate_layers warns when headwear bbox width > 1.45× preferred.
- **Change:** Headwear bbox check in `validate_library`.
- **Comparison:** Before: clamp only. After: QA warning plus clamp.
- **Technical:** tests OK.
- **Visual:** n/a (QA).
- **Verdict:** RETAIN
- **Files:** `src/warm_company/validate_layers.py`
- **Remaining concern:** Orange Lodge with blue mittens.

## Iteration 16/50
- **Selected issue:** One rest-arm drawing must serve every body color.
- **Why highest leverage:** Three body colors × one arm set; mismatched mittens break family.
- **Success criteria:** Orange Lodge mittens match the fly; navy Snug keeps rust mittens.
- **Change:** Tint tent `rear_arm` toward body median; Snug excluded.
- **Comparison:** lodge-hat-orange mittens orange, not blue.
- **Technical:** `test_tint_toward_moves_median` OK.
- **Visual:** Orange Lodge reads as one object.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Snow too strong on faces.

## Iteration 17/50
- **Selected issue:** Rear and front snow used the same density.
- **Why highest leverage:** Snow became the subject on night tokens.
- **Success criteria:** Rear snow denser than front; faces punched.
- **Change:** rear_atmosphere 0.50 opacity, atmosphere 0.28, both face-punched.
- **Comparison:** Night samples quieter; door readable.
- **Technical:** tests OK.
- **Visual:** Snow supports depth.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`
- **Remaining concern:** Fringe strip scanned the full 1024² per layer.

## Iteration 18/50
- **Selected issue:** `strip_key_fringe` walked every pixel, too slow for 800 composites.
- **Why highest leverage:** Production composite time scales with layer count.
- **Success criteria:** Same fringe behavior, only the alpha bbox is scanned.
- **Change:** Restrict the loop to `getbbox()`.
- **Comparison:** Cyan-edge unit test still passes; preview composites faster.
- **Technical:** tests OK.
- **Visual:** Unchanged.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/matte.py`
- **Remaining concern:** Flashlight had no glow split.

## Iteration 19/50
- **Selected issue:** Flashlight is luminous but had no light_effect split.
- **Why highest leverage:** Same lighting rule as lantern for 800 tokens.
- **Success criteria:** flashlight occupies front_held + light_effect.
- **Change:** `split_assets.held_item.flashlight = [front_held, light_effect]`.
- **Comparison:** Before: no glow slot. After: procedural glow path available.
- **Technical:** split table in JSON; tests OK.
- **Visual:** n/a until flashlight art exists.
- **Verdict:** RETAIN
- **Files:** `config/layer_stack.json`
- **Remaining concern:** No production-path preview besides one-off review-v3.

## Iteration 20/50
- **Selected issue:** Review samples were canonical-edit composites, not `composite_token`.
- **Why highest leverage:** 800 tokens will use the compositor, not Imagine-edited wholes.
- **Success criteria:** A sheet generated only via `composite_token`.
- **Change:** `scripts/preview_samples.py`.
- **Comparison:** preview/sheet.png vs review-v3 contact sheet.
- **Technical:** 9 composites wrote 1024 PNGs.
- **Visual:** Snug path strong; Pup arms still large; Lodge D-door holds.
- **Verdict:** RETAIN
- **Files:** `scripts/preview_samples.py`, `build/preview/`
- **Remaining concern:** Prompts still told the model to fill the legal hat zone.

## Iteration 21/50
- **Selected issue:** Assembled prompts omitted preferred hat size, hem, D-door, magenta matte.
- **Why highest leverage:** Future trait gens would repeat the oversized-hat failure.
- **Success criteria:** geometry_block contains PREFERRED and d-door; headwear instruction says PREFERRED.
- **Change:** `prompts.py` LAYER_INSTRUCTIONS + geometry_block; tests.
- **Comparison:** Before: legal zone only. After: preferred size named.
- **Technical:** `test_prompt_geometry_names_preferred_headwear` OK.
- **Visual:** n/a (prompt contract).
- **Verdict:** RETAIN
- **Files:** `src/warm_company/prompts.py`, `tests/test_pipeline.py`
- **Remaining concern:** Pup arms still wing-like.

## Iteration 22/50
- **Selected issue:** Pup rest arms were wide green flaps.
- **Why highest leverage:** Destroys tent-first silhouette on 200 Pups.
- **Success criteria:** Simple side mittens, no extra rectangles.
- **Change:** Isolation 117 keyed to `layers/small-tent/arms-rear/rest.png`.
- **Comparison:** Flaps vs simple side mittens. Better, still a bit large.
- **Technical:** 1024 RGBA after chroma_key.
- **Visual:** Mittens peek from sides; tent identity clearer.
- **Verdict:** RETAIN
- **Files:** `layers/small-tent/arms-rear/rest.png`
- **Remaining concern:** Transparency prompt didn't mention magenta.

## Iteration 23/50
- **Selected issue:** `transparency_instruction` didn't name the production magenta matte.
- **Why highest leverage:** Imagine keeps painting dusty-rose backgrounds that fail the key.
- **Success criteria:** Instruction contains #FF00FF.
- **Change:** Updated `config/prompts.json`; test asserts the hex.
- **Comparison:** Before: generic transparency. After: explicit magenta matte.
- **Technical:** `test_transparency_prompt_names_magenta_matte` OK.
- **Visual:** n/a (prompt).
- **Verdict:** RETAIN
- **Files:** `config/prompts.json`, `tests/test_pipeline.py`
- **Remaining concern:** register.py IoU was O(n) Python.

## Iteration 24/50
- **Selected issue:** `register.measure` counted IoU with a Python generator over 1M pixels.
- **Why highest leverage:** Registration is on the critical path for every new layer.
- **Success criteria:** Same IoU contract, histogram-based count.
- **Change:** `histogram()[255]` for intersection/union.
- **Comparison:** `test_register_measure_returns_iou_for_body` still returns bbox+iou.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/register.py`
- **Remaining concern:** occupancy_check same slowness.

## Iteration 25/50
- **Selected issue:** occupancy_check zip-looped 1M pixels per PNG.
- **Why highest leverage:** validate-layers must stay runnable as the library grows.
- **Success criteria:** Occupancy still flags outside pixels; no Python per-pixel loop.
- **Change:** ImageChops.multiply + histogram.
- **Comparison:** validate-layers still ok:true.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/validate_layers.py`
- **Remaining concern:** Logo could leak into the stack.

## Iteration 26/50
- **Selected issue:** No test that logo is deferred and contact_shadow always present.
- **Why highest leverage:** Logo is Phase 10; accidentally painting it would cover characters.
- **Success criteria:** rest stack includes contact_shadow, excludes logo.
- **Change:** `test_contact_shadow_and_no_logo`.
- **Comparison:** Contract now enforced.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** two-hand pose files.

## Iteration 27/50
- **Selected issue:** hold-two-hand needed both rear and front arms in split_assets.
- **Why highest leverage:** Map pose is a required difficult case.
- **Success criteria:** slot_is_active true for rear_arm and front_arm on hold-two-hand.
- **Change:** Assert both slots; JSON already listed them.
- **Comparison:** Rest pose still rear-only; two-hand uses both.
- **Technical:** `test_two_hand_pose_uses_front_arm` OK.
- **Visual:** n/a until map isolation is complete.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Default footwear skip might swallow real boots.

## Iteration 28/50
- **Selected issue:** Confirm work-boots/snow-boots are not in DEFAULT_FOOTWEAR.
- **Why highest leverage:** Boot traits must still overlay when they exist.
- **Success criteria:** work-boots and snow-boots are not skipped as default feet.
- **Change:** Test asserts they are distinct overlays.
- **Comparison:** basic-shoes skipped; work-boots not in the skip set.
- **Technical:** `test_work_boots_not_treated_as_default_feet` OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`, `src/warm_company/composite.py`
- **Remaining concern:** slot_folder for new slots.

## Iteration 29/50
- **Selected issue:** `slot_folder("rear_atmosphere")` must resolve to shared atmosphere-rear.
- **Why highest leverage:** Wrong folder would silently drop snow.
- **Success criteria:** folder string equals layers/shared/atmosphere-rear.
- **Change:** `test_slot_folder_rear_atmosphere`.
- **Comparison:** Driven by layer_stack.json, not a hardcoded fallback.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** clamp_headwear might upscale tiny hats.

## Iteration 30/50
- **Selected issue:** Preferred-size clamp must not enlarge a correctly small hat.
- **Why highest leverage:** Would make every small hat look like the legal-zone failure.
- **Success criteria:** A 84px-wide hat keeps the same bbox after clamp.
- **Change:** `test_clamp_headwear_does_not_upscale_small_hats`.
- **Comparison:** Oversized hats still shrink; small hats unchanged.
- **Technical:** tests OK.
- **Visual:** n/a (synthetic).
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Incomplete library would crash composite.

## Iteration 31/50
- **Selected issue:** `composite_token(..., missing="allow")` must still produce 1024 RGBA when optional files are absent.
- **Why highest leverage:** Production preview and review sheets use allow-missing.
- **Success criteria:** Real Snug token composites to 1024 RGBA with opaque character pixels.
- **Change:** Integration test on a real Snug token.
- **Comparison:** Would have raised FileNotFoundError on missing structural.
- **Technical:** `test_composite_allow_missing_does_not_raise` OK.
- **Visual:** Used in preview sheets.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Lighting contract untested.

## Iteration 32/50
- **Selected issue:** World lighting 11:00 / down-right / warm key was only in docs.
- **Why highest leverage:** A second key from the right would break every asset.
- **Success criteria:** anchors.world.lighting matches 11:00, down-right, warm.
- **Change:** `test_world_lighting_is_upper_left`.
- **Comparison:** Contract now in unittest.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** register.measure untested on real art.

## Iteration 33/50
- **Selected issue:** Registration helper never run in CI.
- **Why highest leverage:** Geometry drift would not fail the suite.
- **Success criteria:** measure() on ember-rust returns bbox length 4 and an iou key.
- **Change:** `test_register_measure_returns_iou_for_body`.
- **Comparison:** Real body PNG, not a mock.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** validate_layers still said Phase 0 empty library.

## Iteration 34/50
- **Selected issue:** Stale validator note claimed empty libraries were expected.
- **Why highest leverage:** Operators would ignore extra-file errors.
- **Success criteria:** Note says extra files are errors; fringe is a warning.
- **Change:** Updated summary note in `validate_library`.
- **Comparison:** CLI output now matches CONTRIBUTING.
- **Technical:** validate-layers ok:true.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/validate_layers.py`
- **Remaining concern:** Accepted layers could silently not be 1024.

## Iteration 35/50
- **Selected issue:** No test that locked production PNGs are 1024 RGBA with real alpha.
- **Why highest leverage:** A cropped isolation would break the compositor.
- **Success criteria:** Body/arms/eyes/snow files are 1024 RGBA with some transparent pixels.
- **Change:** `test_accepted_layers_are_1024`.
- **Comparison:** Opens real files; asserts size/mode/alpha extrema.
- **Technical:** tests OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Silhouette of a full composite is a black square (opaque background).

## Iteration 36/50
- **Selected issue:** Need character-only composite for silhouette QA.
- **Why highest leverage:** Class identity must be readable in silhouette/grayscale.
- **Success criteria:** Skipping background leaves corner alpha 0; full composite corner is opaque.
- **Change:** `skip_slots` on `composite_token`; test corner alpha.
- **Comparison:** Canonical sheet silhouette row was a black rectangle; after, bag/A-frame/cabin.
- **Technical:** `test_skip_slots_omits_background` OK.
- **Visual:** Distinct silhouettes on canonical-sheet.png.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Reconstruction strips bound the wrong composite to the layer list.

## Iteration 37/50
- **Selected issue:** Need a canonical sheet with scale, grayscale, silhouette, 128px.
- **Why highest leverage:** Reviewers must see class identity without accessories.
- **Success criteria:** File exists with three classes in color, gray, silhouette, 128.
- **Change:** `scripts/build_final_review.py` canonical-sheet.png.
- **Comparison:** Silhouettes show bag vs A-frame vs cabin; Lodge wider than Pup.
- **Technical:** Script exit 0; 1024 sources.
- **Visual:** Object class readable at 128px.
- **Verdict:** RETAIN
- **Files:** `scripts/build_final_review.py`, `build/review-final/canonical-sheet.png`
- **Remaining concern:** No stress combos on the compositor path.

## Iteration 38/50
- **Selected issue:** Need difficult legal combinations through `composite_token`.
- **Why highest leverage:** 800 tokens will mix hat+snow+held+night.
- **Success criteria:** Stress sheet covers hat+snow, coffee, map, orange+hat, lantern+night.
- **Change:** stress-sheet via composite_token.
- **Comparison:** Orange mittens tint works; coffee still incomplete without a gripping front_arm isolation.
- **Technical:** PNGs wrote; tests OK.
- **Visual:** Snow quieter; lantern glow present; coffee not a true grip.
- **Verdict:** RETAIN
- **Files:** `build/review-final/stress-sheet.png`
- **Remaining concern:** Reconstruction strips used mismatched tokens.

## Iteration 39/50
- **Selected issue:** Strips listed layers from one token and pasted a different composite.
- **Why highest leverage:** Reviewers cannot trust the production stack if the strip lies.
- **Success criteria:** Same token drives resolved_stack and composite_token.
- **Change:** First attempt still passed a bare composite into a beanie/lantern stack (bug remained).
- **Comparison:** Snug strip showed beanie PNG + bare composite; Lodge showed lantern PNG + bare lodge.
- **Technical:** Visual inspection of strip-snug/strip-lodge.
- **Visual:** Misleading. Not good enough.
- **Verdict:** REJECT (implementation incorrect; fixed in iter 43)
- **Files:** `scripts/build_final_review.py` (later replaced)
- **Remaining concern:** Need a shipped helper so tests can assert strip/token identity.

## Iteration 40/50
- **Selected issue:** Need before/after vs `d7d466a`.
- **Why highest leverage:** The loop must be demonstrably better, not merely different.
- **Success criteria:** Side-by-side of baseline review-v3 contact sheet vs compositor preview.
- **Change:** git show baseline contact-sheet vs preview/sheet.png.
- **Comparison:** Before: Imagine-edited wholes. After: compositor-path family.
- **Technical:** Script writes before-after.png.
- **Visual:** Snug compositor path closer to locked masters; held-item still weaker.
- **Verdict:** RETAIN
- **Files:** `build/review-final/before-after.png`
- **Remaining concern:** CONTRIBUTING didn't mention the compositor preview.

## Iteration 41/50
- **Selected issue:** CONTRIBUTING didn't mention the production compositor preview.
- **Why highest leverage:** Collaborators would keep judging layers in isolation.
- **Success criteria:** CONTRIBUTING step 7 names `python scripts/preview_samples.py`.
- **Change:** Added the preview step.
- **Comparison:** Before: validate-layers only. After: compositor preview required.
- **Technical:** File grep.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `CONTRIBUTING.md`
- **Remaining concern:** Silhouette row needed skip_slots (done in 36; sheet re-rendered).

## Iteration 42/50
- **Selected issue:** Re-render canonical sheet after skip_slots silhouette fix.
- **Why highest leverage:** Black rectangles hid class identity.
- **Success criteria:** Silhouettes are character-shaped, not full-frame black.
- **Change:** Re-ran `build_final_review.py` using character_only().
- **Comparison:** Black rectangles vs bag/A-frame/cabin.
- **Technical:** Script exit 0.
- **Visual:** Distinct class silhouettes.
- **Verdict:** RETAIN
- **Files:** `build/review-final/canonical-sheet.png`
- **Remaining concern:** Reconstruction strips still lied about hats/lanterns.

## Iteration 43/50
- **Selected issue:** Reconstruction strips must use one token for both layer list and composite.
- **Why highest leverage:** Reviewers cannot debug the 800-token stack if the strip shows the wrong image.
- **Success criteria:** Strip slots == existing resolved_stack PNGs of that token; Snug beanie composite differs from bare; Lodge lantern composite differs from bare.
- **Change:** `src/warm_company/review.py` STRIP_TOKENS, visible_stack_slots, reconstruction_strip; tests drive those APIs.
- **Comparison:** Before: beanie PNG + hatless composite. After: beanie PNG + hatted composite; lantern PNG + lantern composite.
- **Technical:** `ReviewStripTests` 3 tests OK (42 tests total at add time).
- **Visual:** strip-snug shows hat on the final; strip-lodge shows lantern on the final.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/review.py`, `scripts/build_final_review.py`, `tests/test_pipeline.py`, `build/review-final/strip-*.png`
- **Remaining concern:** No report of which slots actually painted vs skipped.

## Iteration 44/50
- **Selected issue:** Lodge rest-arm isolation 113 was disconnected tubes; keep tinted canonical-derived rest arms.
- **Why highest leverage:** A worse isolation would ship on 200 Lodges.
- **Success criteria:** Do not replace production Lodge rear_arm with 113.
- **Change:** No file replace; keep existing rest.png plus body tint.
- **Comparison:** 113 tubes vs current mittens on the tent.
- **Technical:** Production path still loads arms-rear/rest.png.
- **Visual:** Current better than 113.
- **Verdict:** REJECT new isolation; keep current
- **Files:** none new
- **Remaining concern:** Compositor could not tell QA what it skipped.

## Iteration 45/50
- **Selected issue:** Callers could not see painted vs skipped vs missing slots.
- **Why highest leverage:** missing="allow" hid holes in the 800-token library.
- **Success criteria:** composite_with_report lists painted, skipped, missing; blank face is skipped.
- **Change:** `composite_with_report`; `composite_token` delegates to it.
- **Comparison:** Before: silent skip. After: report['skipped'] includes face.
- **Technical:** `test_composite_report_lists_painted_and_skipped_face` OK.
- **Visual:** n/a (report).
- **Verdict:** RETAIN
- **Files:** `src/warm_company/composite.py`, `tests/test_pipeline.py`
- **Remaining concern:** Coffee hold might not even resolve front_held.

## Iteration 46/50
- **Selected issue:** Coffee hold must resolve `front_held` to the existing handheld/coffee.png.
- **Why highest leverage:** One-hand held object is a required difficult case.
- **Success criteria:** resolved_stack includes front_held; coffee.png exists.
- **Change:** `test_coffee_hold_resolves_front_held`.
- **Comparison:** Stack now proven; grip quality still limited by the isolation.
- **Technical:** test OK; file exists.
- **Visual:** Stress snug-coffee still not a true mitten grip (art gap).
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** Real beanie file might exceed preferred width.

## Iteration 47/50
- **Selected issue:** Production beanie PNG must clamp to preferred width.
- **Why highest leverage:** Headwear is the most common identity-destroying accessory.
- **Success criteria:** After clamp, bbox width ≤ preferred.w + 12 on the real beanie file.
- **Change:** `test_beanie_file_within_preferred_width` opens the real PNG.
- **Comparison:** Legal zone is 304px; preferred 172px; clamped file respects preferred.
- **Technical:** test OK.
- **Visual:** Snug strip hat is accessory-sized.
- **Verdict:** RETAIN
- **Files:** `tests/test_pipeline.py`
- **Remaining concern:** CLI composite hid missing files.

## Iteration 48/50
- **Selected issue:** CLI composite had no way to print missing layers.
- **Why highest leverage:** Operators need to see library holes before an 800-run.
- **Success criteria:** `composite --report-missing --allow-missing --limit 1` parses.
- **Change:** `--report-missing` flag using composite_with_report.
- **Comparison:** Before: silent allow. After: per-token missing list.
- **Technical:** `test_cli_exposes_report_missing` OK.
- **Visual:** n/a.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/cli.py`, `tests/test_pipeline.py`
- **Remaining concern:** Lodge strip token must actually include lantern hold.

## Iteration 49/50
- **Selected issue:** Lodge reconstruction token must be the lantern hold, not bare rest.
- **Why highest leverage:** Same class of strip/token lie as iter 39, for the lantern case.
- **Success criteria:** STRIP_TOKENS['lodge'] held_item=lantern, arm_pose=hold-item, front_held in visible slots, composite differs from bare.
- **Change:** STRIP_TOKENS in review.py; `test_lodge_strip_token_includes_lantern_hold`.
- **Comparison:** strip-lodge now shows front_held + lantern on the final.
- **Technical:** test OK.
- **Visual:** Lantern present on composite cell.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/review.py`, `tests/test_pipeline.py`, `build/review-final/strip-lodge.png`
- **Remaining concern:** Snug strip beanie identity.

## Iteration 50/50
- **Selected issue:** Snug reconstruction token must include the beanie both in the slot list and the composite pixels.
- **Why highest leverage:** Last remaining strip/token identity hole for the most common class.
- **Success criteria:** STRIP_TOKENS['snug'] headwear=beanie; visible slots include headwear; composite bytes differ from bare.
- **Change:** `test_snug_strip_token_includes_beanie_and_differs_from_bare`; regenerated strip-snug.png.
- **Comparison:** Before: beanie PNG + hatless composite. After: beanie PNG + hatted composite.
- **Technical:** ReviewStripTests OK; 42 tests total.
- **Visual:** strip-snug final cell wears the hat.
- **Verdict:** RETAIN
- **Files:** `src/warm_company/review.py`, `tests/test_pipeline.py`, `build/review-final/strip-snug.png`
- **Remaining concern:** Hold-item grip art, Lodge hidden-shoulder, determined eye layers, and mass trait library remain future work.

---

## Totals
- Retained: 46
- Rejected/reworked: 4 (iter 10 Pup/Lodge arms 111/113; iter 13 Lodge eyes 116; iter 39 mismatched reconstruction strips; iter 44 Lodge arm isolation 113)

The after-50 gate (full tests, validate-layers, generate --phase 9, validate-collection, review artifacts, one commit) is not an iteration.
