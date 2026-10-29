# Five-fighter head and clothing revision — 2026-10-28

Owner feedback expands face/hair/head/headwear restoration to all five fighters,
aims for slightly more realistic skin/hair and requests source-color matching
for all clothes. Owner also permits cleaning older revisions. We preserve the
original game's likeness/expression, atlas layout and existing body skin match.
No new approval, game installation or catalogue publication;0.1 stays immutable.

## New review revisions

| Fighter | v3 revision |
|---|---|
| Blaze | r-c82bf031a7cb4726 |
| Nyne | r-c781fcc1ff7e43e9 |
| Trejo | r-a41e97bb2dc3445f |
| Redman | r-dad44c6a3d9d4461 |
| Henry Rollins | r-230c857e841f4273 |

All five built-in imagegen edits succeeded. These are1024²head-region edits,
with current head target plus original Faithful source as reference. They are
not whole-body regeneration; Rollins' previous whole-atlas service rejections
remain recorded as history. Exact prompts/reference paths/raw outputs are private.
The full assembled atlases are2048²RGBA, unchanged material alpha.

Head assembly retains the original broad palette, pairs seam guards only from
that fighter's geometry, holds standalone eye/teeth/mouth/swatch tiles and
Redman's neck characters, and uses an.8detail strength with source low-frequency
color and24px patch-edge taper. Face proportions/expression/likeness still require
owner review; invariant checks do not establish facial authenticity. Other than
the head patch and safe cloth mask, parent RGB stays exact.

## Clothing palette

See [material-audit.md](material-audit.md). Actual emc4_cloth UV triangles contain
clothes, footwear and headwear; other material triangles plus1sourcepx guard are
held. Blaze/Nyne have genuine shared skin/cloth UVs; preserving skin requires
holding those shared pixels. Hair is not a separate shader group. nospec belongs
to head/mouth parts, so it is held by clothing correction.

New material_palette module estimates local Lab source-minus-draft fields within
each connected safe cloth island, with three6-source-pixel masked blur passes.
It includes neutral/dark fabrics; the skin-specific warm-midtone filter is not
reused. Normalized field upsampling avoids mask-edge attenuation, and exact hard
coverage prevents recoloring skin/jewelry. Broad source hue/lightness is restored
while fine weave/stitching detail remains; image alignment still needs review.

| Fighter | Median cloth chroma source | Before | After | Median Lab distance before→after |
|---|---:|---:|---:|---:|
| Blaze |12.17|15.10|10.85|7.18→4.16|
| Nyne |10.02|11.70|10.12|4.36→2.92|
| Trejo |8.37|17.02|9.03|10.84→4.89|
| Redman |7.00|10.71|7.83|8.39→3.20|
| Rollins |0.59|0.59|0.59|0.00→0.00|

These same-UV texture diagnostics measure palette proximity, not visual approval
or GPU/in-game parity. Rollins' clothes already used original/Faithful pixels.

## Review and reversible cleanup

Import uses the live token-authenticated API, honoring its single writer and
optimistic review versions. No direct live-workshop JSON edits or restart.
12older fighter candidates received the existing archived tag; no PNG, note,
prompt, hash, ID or parent link was removed. Published0.1 selections, approved/
selected candidates and saved view/session choices remain visible. Menus untouched.
Workspace now28candidates,24request records, five models. Archived revisions are
hidden from default2D/3Dselectors, available with Show archived revisions. Remove
the archived tag in2Dreview to restore one. Latest restoration saves pending
notes and selects the newest active Rich Original Detail candidate in3D.

Source preparation/import recipes are prepare.py and import_review.py. Private
experiment contains inputs, raw, prompts.json, assembled-v1/receipt.json,
pre-archive-workshop.json, review-import-receipt.json, palette-comparison.png,
verification.json and review-index.md. Frozen processor copies retained there.
New revisions remain unapproved and unselected. Owner should save browser notes,
refresh http://127.0.0.1:8768/model-viewer, select each fighter and press Latest
restoration. Compare Original/Faithful and0.1 at Face/Chest/Back/Pants/Shoe presets.

Validation:81tests+12subtests,8Node tests and JS syntax checks pass. New synthetic
coverage verifies red/blue/neutral fabric calibration, skin/shared-UV guards,
fine weave retention, exact alpha/exterior and unchanged source identity. Live
checks verify five candidate PNG hashes and GLB exports, archive controls, old
candidate/notes identity and saved camera/comparison bytes. Browser visual testing
remains blocked by the existing URL security policy; no workaround attempted.
User visual review remains required. Server stays live at same origin/PID23344.
