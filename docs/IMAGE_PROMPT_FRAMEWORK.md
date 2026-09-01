# Grok Image prompt framework

Do not write layer prompts from scratch. Assemble them.

```
MASTER STYLE PREFIX
+ CHARACTER TEMPLATE (if the layer belongs to a class)
+ LAYER-SPECIFIC INSTRUCTION
+ TRAIT EXTRA
+ COORDINATE / ANCHOR BLOCK
+ TRANSPARENCY or BACKGROUND INSTRUCTION
+ NEGATIVE CONSTRAINTS
```

Canonical implementations:

- Prefix and negatives: `config/prompts.json`
- Assembler: `src/warm_company/prompts.py`
- Export: `python -m warm_company prompts` → `prompts/library.json`

After Phase 1, **stop using blank `image_gen` for class layers.** Use `image_edit` on that class's approved canonical, with `templates/{class}/guides.png` as a second reference when possible.

---

## 1. Master style prefix (frozen)

Copy verbatim. Do not paraphrase per layer. Drift in this paragraph is how a collection starts looking like ten artists.

> Hand-drawn 2D cartoon illustration for a cohesive NFT collection, as if one human illustrator inked and painted every asset. Warm, approachable, slightly imperfect outdoor winter character art. Bold enough to read at thumbnail size. Visible brush and pencil texture in fills, not clip-art flatness and not 3D rendering. Warm dark umber outlines with gentle line-weight variation, thicker on the outer silhouette (~7px at 1024) and thinner on interior seams (~3-4px). Lighting is a warm key from the upper left (11 o'clock) with a cool snow bounce fill from below; shadows fall down-right. Family-friendly, tasteful humor, mission-oriented winter-shelter mascot energy. Color is saturated but earthy: camp oranges, forest greens, navy, burgundy, cream, snow-blue. Paper-like grain. No photorealism, no CGI, no anime-cel shine, no vector-flat corporate mascot look, no watermarks, no signatures, no captions, no letters, no numbers.

## 2. Character templates

**Snug**

> A tall, narrow anthropomorphic winter sleeping bag character named a Snug. Mummy-bag silhouette with a rounded hood, visible quilting baffles, a zipper suggestion on the viewer's right, a face integrated into the upper-middle hood opening, short goofy legs and cartoon arms. It should feel friendly and slightly goofy, and remain the narrowest, tallest member of the family.

**Pup**

> A compact anthropomorphic 3-person tent character named a Pup. It must read as a tent FIRST and a character second: soft A-frame with a hint of dome, front D-shaped door holding the face, two visible poles, a low snow skirt, arms from the side walls, feet under the hem. Clearly smaller than the six-person Lodge.

**Lodge**

> A substantial anthropomorphic 6-person tent character named a Lodge. Wider and taller than the Pup, with side walls, a ridge pole, a larger D-door that holds the face, more paneling, a wider footprint, arms from the side walls, feet under the hem. Immediately reads as the larger tent when standing beside a Pup.

## 3. Layer instructions (slot recipes)

| Slot | Instruction |
| --- | --- |
| canonical | Draw the complete canonical character in default rest pose, no headwear, no handheld, standard face, normal eyes, neutral brows, smile, basic shoes. This becomes the master reference. |
| body | Body/fabric silhouette only. No face features, no arms, no legs, no accessories. |
| pattern | Fabric pattern only, already clipped to the body. |
| structural | Poles / zipper / baffles / door trim only, on the master silhouette. |
| face | Face panel only (hood opening or door), no features. |
| eyes / eyebrows / mouth / facial | That feature only, on the published anchors. |
| front_arm / rear_arm | Arms for this pose, attached at arm anchors. |
| legs / footwear | Legs or shoes only. Soles on Y=896. |
| headwear | Headwear only. Tents: on the peak, brim above the door. Bags: on the hood, brim above the eyes. |
| front_held / rear_held | Held object (or its rear half) at the hand point. |
| background | Complete opaque 1024×1024 environment. Quiet occupancy zone. No figures. |
| atmosphere | Weather only. Face oval fully empty. |

## 4. Coordinate block (always appended)

World, then class, from `config/anchors.json`. Example for a Snug layer:

> Canvas exactly 1024x1024 pixels, 1:1, origin top-left. Shared world: center X=512, baseline Y=896, horizon Y=640, ground plane Y=768. Safe margin 48px. Hard margin 24px. Logo safe zone top-right x=832 y=40 w=168 h=128 stays visually quiet. Warm key light from upper left, shadows fall down-right. Class Sleeping Bag (Snug): bounding box x=296 y=112 w=432 h=784. Character center X=512, baseline Y=896. Peak=(512,112). Face center=(512,376). Eye baseline Y=360; left eye=(456,360); right eye=(568,360). Mouth baseline Y=424 at (512,424). Left arm anchor=(304,472); right arm anchor=(720,472). Left foot=(448,896); right foot=(576,896). Headwear zone x=360 y=64 w=304 h=168, brim Y=216. Rounded hood, visible horizontal baffles, zipper suggestion on viewer's right, short cartoon legs. Face sits in the upper-middle of the bag, not as a sticker.

The assembler writes this from JSON so it cannot silently rot.

## 5. Transparency / background closer

**Traits:**

> The character or trait sits on a true transparent background. No matte, no white box, no checkerboard painted in, no cast studio backdrop. Full 1024x1024 canvas with the subject already placed at the specified pixel coordinates. Empty pixels are alpha zero.

**Backgrounds:**

> This is the only opaque layer. Fill the entire 1024x1024 canvas with a complete illustrated winter environment in the same hand-drawn style as the characters. Keep the central character occupancy zone visually quiet so a later character can stand there. Do not place important landmarks, high-contrast props, or any figures in the middle. Tasteful. No homelessness spectacle.

## 6. Negatives (always last)

> Avoid: photorealistic, 3D render, CGI, Unreal Engine, plastic toy, clip art, vector flat infographic, chibi with giant head on a tiny tent, googly sticker eyes, horror, grimdark, poverty caricature, trash pile, cardboard joke sign, alcohol, drugs, weapons, text, letters, numbers, watermark, signature, logo, UI, frame, border, drop shadow studio backdrop, pure white background box, collage, multiple characters, off-center crop, widescreen cinematic letterbox.

## 7. Exact Phase-1 prompts (canonical characters)

These are the first three prompts to submit, and the last three that are allowed to be blank `image_gen`. Submit at 1:1. Then `image_edit` with `templates/{class}/guides.png`.

The exported, concatenated strings live in `prompts/library.json` after `python -m warm_company prompts`. The three canonical ids are:

- `sleeping-bag/canonical/master`
- `small-tent/canonical/master`
- `large-tent/canonical/master`

Every other row in that JSON is the exact prompt for that asset.

### 7a. Canonical Snug (sleeping bag)

Assemble: prefix + Snug template + canonical instruction + "Default body color is ember-rust." + Snug geometry + transparency + negatives.

### 7b. Canonical Pup (small tent)

Assemble: prefix + Pup template + canonical instruction + "Default body color is trail-olive." + Pup geometry + transparency + negatives.

### 7c. Canonical Lodge (large tent)

Assemble: prefix + Lodge template + canonical instruction + "Default body color is trail-olive." + Lodge geometry + transparency + negatives.

Do not type a fourth original style paragraph "to make it better." If the result is wrong, change the **layer instruction** or the **reference image**, not the prefix.

## 8. Example layer prompt (not a new style)

**`sleeping-bag / headwear / beanie`**

Prefix + Snug template + "Paint only the headwear in the headwear zone. On tents it perches on the peak, brim above the door/face. On sleeping bags it sits on the hood crown, brim above the eyes." + "Trait: Winter Beanie." + Snug geometry + transparency + negatives.

Then: `image_edit` the approved Snug canonical, extract the hat, register.

**`shared / background / winter-sunrise`**

Prefix + background instruction + "Trait: Winter Sunrise." + world geometry (no class) + opaque-canvas instruction + negatives.

No character in the background file.

## 9. Why coordinates in the prompt are not enough

They are a hint for the model and a contract for us. The production pipeline (`register.py`, occupancy masks, bbox checks) is the enforcement. A beautiful hat 40px too low is a failed layer.

## 10. Reference order (Phase 1 onward)

1. Approved canonical PNG of the class
2. `templates/{class}/guides.png` (magenta occupancy, cyan eyes, yellow mouth, green arms, orange feet)
3. Optional: a previously accepted layer of the same slot

Never: a random image from another collection, a photo of a real tent as the style driver, or a new prefix.
