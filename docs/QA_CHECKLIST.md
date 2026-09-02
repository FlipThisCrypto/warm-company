# QA checklist

Nothing ships because it "looks fine in the prompt preview."

## A. Every production layer

Canvas and file

- [ ] 1024×1024
- [ ] PNG
- [ ] Backgrounds: opaque (alpha ≥ 250 everywhere)
- [ ] All other layers: RGBA with real transparency
- [ ] Not cropped to the visible bounding box
- [ ] No white matte, checkerboard painted in, studio backdrop, or drop-shadow plate
- [ ] No text, letters, numbers, watermark, signature, or accidental logo
- [ ] Filename = trait id in the correct folder

Geometry

- [ ] Occupancy IoU ≥ 0.82 against `templates/{class}/occupancy.png`
- [ ] Face / eyes / mouth / feet within published tolerances
- [ ] Headwear drawn to `headwear_preferred`, not filling the legal zone
- [ ] Tent hats human-scale on the peak; they do not hide A-frame or cabin identity
- [ ] Lodge face is the D-door panel, never a circular sticker
- [ ] Handheld in the hand zone, actually gripped (correct occlusion), not hovering beside a closed fist
- [ ] Footwear soles on baseline Y=896; leg roots hidden by hem/footbox
- [ ] Two distinct feet at class foot anchors (not a central boot pile); overlay boots replace contained feet; max two legs and two feet
- [ ] Shoulder/arm roots begin behind the body
- [ ] Tent poles and bag width match the master, not a new silhouette
- [ ] No cyan/teal extraction fringe; magenta matte fully keyed
- [ ] Snap-translate used only for ≤12px; otherwise redrawn

Style

- [ ] Umber outlines, not black, not missing
- [ ] Line weight in family with the canonical
- [ ] Warm key from upper left, shadow down-right
- [ ] Same paper/fabric grain language
- [ ] Not 3D, not photoreal, not anime-cel, not clip-art flat
- [ ] Looks like the same illustrator as the canonical of that class

Occlusion

- [ ] Split assets have both halves
- [ ] Pattern does not erase structure
- [ ] Atmosphere leaves the face oval empty
- [ ] Rear pieces are actually rear-shaped (no features that should be in front)

Dignity

- [ ] No poverty gag, trash, begging-sign text, or degraded "rare" dirt

## B. Every composite (token)

- [ ] 1024×1024 PNG
- [ ] Character stands on Y=896
- [ ] No illegal combo (run the engine, do not eyeball)
- [ ] Face readable at 128px; object class (bag / 3-person tent / 6-person tent) reads first
- [ ] Logo absent until Phase 10; then inside the safe zone only
- [ ] Background does not compete with the face
- [ ] Snow supports depth; it is not the subject
- [ ] Accessories match the canonical's line weight and texture density

## C. Collection

- [ ] 400 Snugs, 200 Pups, 200 Lodges
- [ ] 800 unique DNA
- [ ] 13 specials present, one of each id
- [ ] CHIP-0007 JSON for every token
- [ ] `legal_title_to_physical_item` is false
- [ ] Rarity report written
- [ ] Contact sheets: all, by class, specials
- [ ] Same seed rebuilds the same DNA list

## D. Contact-sheet hunt (humans)

Look specifically for:

- scale drift (a Pup that is Lodge-wide)
- floating shoes / legs pasted on the hem
- hats that become architecture
- Lodge circular face stickers
- eyes sliding off the door
- a layer that got shiny/3D
- snow covering pupils
- two lanterns
- empty gripping hands / objects beside closed fists
- cyan/teal extraction halos
- accidental words in the sky

## E. Phase gates

A phase is not done when the files exist. It is done when this checklist has been ticked for that phase's assets and someone has looked at the sheets.
