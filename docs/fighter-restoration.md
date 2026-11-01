# Fighter restoration

Use Rich Original Detail with the original atlas as the authority for layout,
likeness, lettering paths, muted palette and painted shading. Face, hair, head
and headwear may be restored within the declared scope, with slightly more
realistic skin/hair detail and the original proportions and expression.

## Prepare and generate

Pin the source ID, original/faithful/parent image hashes, geometry hash and exact
outfit/state. Inventory head, hair, cap, torso, arms/tattoos, garments, shoes,
jewelry and auxiliary eye/mouth tiles. Record each as restored, held, missing,
blocked or pending. Output dimensions alone do not establish restoration.

Build edit masks from actual material UV triangles and inspect every disconnected
component. Rectangles bound a request; they do not establish safe pixels. Subtract
other-material coverage and guards. Alpha/unknown groups need an explicit audited
opt-in and reason. `fighter_scopes.scopes` derives these scopes and paired skin
UV seams; `skin_scope.rasterize` clips triangles by anatomical planes. Never copy
another fighter's head quadrants, eye/mouth rectangles or seam counts.

Use the [manual prompt templates](fighter-restoration-prompts.txt). Record every
input's role/hash, exact submission, raw output or error privately. References
can clarify real details; uncertain lettering needs owner approval. Preserve
original tattoo silhouettes, animals/trees, handwriting paths and placement.
Keep failures honest; do not call a faithful enlargement an ImageGen restoration.

## Assemble and match color

Choose the smallest operation that addresses the observed defect:

| Library operation | Purpose |
|---|---|
| `face_detail.merge` | Bounded face patch with source broad color and parent exterior |
| `region_detail.patch` | Source-locked or direct regional detail under explicit masks |
| `clothing_detail.repair` | Recover generated garment detail excluded by broad holds |
| `feature_detail.restore` | Focused logo/prop repair, including features touching crop edges |
| `material_palette.match` | Restore source clothing, headwear and footwear palette |
| `color_trial` | Geometry-scoped skin/seam calibration |
| `damage_detail.restore` | Registered clean detail plus own state difference; see separate guide |

These are parameterized Python library operations. They do not import or approve
results. Keep processor source/version, parameters, masks and receipts with each
private immutable stage. Broad source hue/saturation and shading must match on
both skin and clothes; preserve generated fine detail. Separate skin and cloth
strategies avoid brightened black clothing or warmer neck/body seams.

After the final palette step, enforce exact source alpha, declared holds and
accepted parent pixels outside the edit mask again. Measure each component and
inspect the final assembly. A prompt is not a pixel lock. Local-neural assembly
(`local_restoration`) remains experimental: pixel invariants do not establish
quality, and those trials were excluded from HD Fighters 1.0.

## Check named details and split UV islands

Inventory each chest logo, wordmark, pendant, clock, important tattoo and cap
inscription separately. Spell source-confirmed text exactly and include every
copy, rotation, mirrored section and distant front/back fragment. A broad logo
hold leaves that feature pending even when its garment has new fabric detail.
`fighter_scopes.feature_coverage` detects unchanged fragments; changed pixels
do not prove legibility, authentic wording or correct design.

Check final feature crops at 100/200%, plus assembled Front and Back views. A
half-restored crest is incomplete. `uv_preview` can expose split fragments but
ignores game shaders and is a diagnostic, not a native render. Hold only specific
uncertain marks; request references for a whole uncertain logo rather than
inventing words. Reuse good raw detail inside safe masks before regenerating
accepted surrounding areas.

## Import, review and package

Import each output as a new immutable revision through the single live writer.
Retain parent links, prompts, raw outputs, errors and hashes. New children start
unapproved/unselected/not game verified. Compare exact left/right revision IDs in
the 2D and model viewers. Archive unrelated history with the existing tag; keep
all files and notes. Saved/current/approved/selected archived revisions remain
visible so a history toggle cannot silently replace the comparison.

Art approval, technical/channel review, pack selection, release authorization,
publication and native verification are separate decisions. The existing workshop
export writes a local sparse schema-1 test pack; it neither installs nor publishes
it. Preserve published release bytes. Further fixes require a new child and new
versioned release, followed by actual fight/Story/alpha/mip tests in the recomp.

The source-only [catalogue](../src/defjam_tools/resources/profiles/fighters.json)
controls preview support and atlas aliases, not approval or release selection.
Dated recipes and immutable release evidence are indexed in
[tooling history](tooling-history.md); their source-specific coordinates are not
reusable defaults. Portable batch jobs and a generic release builder are separate
follow-ups, not supported CLI commands today.
