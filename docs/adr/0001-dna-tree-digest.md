# ADR 0001 — Bind DNA to a tree digest, not a git commit

Status: accepted

## Context

Warm Company DNA is deterministic from seed + config + generator source.
Pixels are deterministic from DNA + layer PNGs. A mint that cannot detect
later edits to either would ship a different collection than the one reviewed.

Git revision is informational. Operators work with uncommitted layer edits.
A git SHA would go stale or look green while PNG bytes changed.

## Decision

1. `tree_digest` hashes seed, phase, generator_version, DNA config JSON,
   DNA-affecting Python modules, every layer PNG, and supply.
2. `collection_fingerprint` hashes the 800 `token_id:class_id:dna` lines.
3. Runtime (Python, Pillow, requirements hash, git revision) is recorded
   but does not enter `tree_digest`.
4. `status` compares the last `build/dna/provenance.json` to the live tree
   without rolling DNA.
5. `--mint` still refuses the development seed.

## Consequences

- Editing a hat PNG or `traits.json` after generate makes `generation_stale`.
- Changing Pillow does not retarget DNA; it shows on `status.runtime`.
- Restoring a DNA zip restores provenance; operators must still match the live tree before composite.
