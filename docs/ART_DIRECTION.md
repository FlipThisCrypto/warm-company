# Art direction

One illustrator. One winter. Three objects that learned faces.

## 1. The look, locked

Hand-drawn 2D cartoon. Warm. Approachable. Slightly imperfect. Outdoorsy. Family-friendly. Mission-oriented. Tasteful humor. Bold at 128px. Enough grain and brush to escape clip art. Never photoreal, never 3D, never a second drawing style sneaking in through a "rare" trait.

Think: a picture-book camping manual illustrated by someone who likes people.

## 2. Line

| Role | Weight at 1024 | Color |
| --- | --- | --- |
| Outer silhouette | ~7px, slight taper at ends | `#3A2A22` warm umber |
| Structure (poles, zipper, door) | ~4px | `#3A2A22` |
| Interior detail (baffles, stitches, laces) | ~2.5–3px | `#3A2A22` at ~80% |

No pure black outlines. No round vector-even stroke. Line weight breathes. Corners of fabric can be a little soft. Poles stay straighter than fabric because they are poles.

## 3. Light

Locked for the entire collection:

- **Key:** warm, upper left, about 11 o'clock, ~30° elevation.
- **Shadow fall:** down-right.
- **Fill:** cool snow bounce from below, never strong enough to look like a second sun on the right.
- **Night scenes:** the key stays warm (lantern, campfire, cabin-window logic). Moonlight is fill only.

A Lodge on a starry night still has its left planes lit warmer than its right planes.

Shading language: one core shadow, one highlight, optional bounced cool on the belly/skirt. No PBR, no rim-light from nowhere, no ambient occlusion pass that looks 3D.

Highlight paint: cream `#FFF6E8`, laid as a brush dash, not a hard white specular.

## 4. Color

Snow is never `#FFFFFF`. Use warm paper snow `#F4F0E8` by day and `#D8E2EE` by night.

Fabric lives in a camping-catalog earth:

- olives, rust, navy, burgundy, mustard, cream, charcoal, sky, plum
- tent orange, forest, royal blue, tan, camp red, granite, teal, purple, yellow
- two-tone olive/tan and navy/orange as tent colorways
- legendary *Aurora Cloth* is painted iridescence (2–3 extra hues, still flat-to-gummy paint), not a hologram render
- legendary *North Star Navy* is navy with illustrated stars, not glitter photography

Saturation is medium-high so thumbnails pop. Avoid neon. Avoid pastel washouts.

## 5. Texture

Every fill has paper grain or fabric tooth. Quilting is stitched, not airbrushed. Tent fabric can show a faint ripstop grid *drawn*, not photographed. Edges of color sit slightly inside the outline, like colored-in ink.

If a layer looks like a flat SVG icon, it fails.

## 6. Faces

Faces are **integrated**:

- Snug: the hood opening *is* the face panel.
- Pup / Lodge: the door *is* the face panel.

Not googly stickers. Not a circular head attached to a tent with a neck.

Shared recipe (absolute pixels differ per class; see coordinate doc):

- Eye whites `#FFF8F0`
- Iris `#2A1810`
- Highlight: 8px cream, upper-left of iris
- Brows: simple umber strokes, 6px
- Mouth: 5px stroke, simple shapes
- Optional cold blush `#E8A090`

Expressions are modular (eyes + brows + mouth + optional facial). Illegal combos are encoded, not discovered in QA.

## 7. Hands, arms, feet

- Arms are cartoon tubes with a simple three-finger / mitten hand. Same construction on all classes.
- Default pose: arms slightly out, elbows soft, hands at hip-to-waist height.
- Feet sit *on* baseline Y=896. Soles are ellipses. No hover.
- Footwear is chunky and readable at thumbnail: boots, sneakers, slippers (Snugs only), mismatched as a joke about style not poverty.

## 8. Hats, on purpose

Tents are tents first. A beanie does not sit on the door-face. It perches on the **peak**, brim at `headwear_brim_y`, which is above the door.

Sleeping bags wear hats on the **hood crown**, brim above the eyes.

This is a collection signature. It is also an occlusion rule.

## 9. Backgrounds

Backgrounds are illustrated places in the same hand. Not gradients behind cutouts.

They support the character:

- Quiet in the occupancy union `(152, 112) 720×784`
- Quiet in the face ovals
- Quiet in the top-right logo safe
- Interest lives in sky, distant hills, tree edges, snow at the feet

Kentucky / Appalachian winter is welcome as ridge lines, hardwoods, low mountains, a distant town glow. An "underpass" scene, if used, is abstracted infrastructure — a quiet overpass, snow, sodium light — **without** trash gags, slogan graffiti, or sleeping figures used as scenery.

## 10. Dignity rules (art)

Forbidden as traits, gags, or "gritty rare" palettes:

- Cardboard signs with begging jokes
- Trash, bottles, needles, dirt-as-identity
- Torn clothes as a poverty flex
- Sad-sack "homeless mascot" styling
- Photoreal people in the background used as props

Allowed:

- Patchwork as *care*
- Well-loved tent fabric as *use*
- Cold blush, chattering mouth, worried brows as *weather*
- Volunteer sash, thermos, lantern, map, soup, spare blanket as *help*

## 11. Personality, not just parts

Loadouts should feel like a sentence.

- Sleepy eyes + coffee + sunrise = Early Riser
- Determined eyes + lantern + night = Night Watch
- Patchwork + snow boots + hand warmer = Survivor
- Heart sign + sash + dawn = Volunteer

Random generation will produce plenty of quieter sentences. Specials author the loudest thirteen.

## 12. What "one illustrator" means in production

After the three canonicals exist, **do not `image_gen` a hat from nothing.** `image_edit` the canonical Snug / Pup / Lodge, ask for the hat in the headwear zone, extract it, register it.

Recolors are edits of the master body, not new drawings of a different tent.

If a layer arrives looking like a different artist (slicker, darker, more 3D, more anime, more sticker), it is rejected even if the coordinates are perfect.
