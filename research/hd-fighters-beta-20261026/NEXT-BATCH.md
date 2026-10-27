# Fighter continuation — 2026-10-27

The owner reports: “I tested the HD Fighters 0.1 mod and it looks great. I think
we can continue our work on these three fighters, and incorporate more into the
mix.” This satisfies the requested pack playtest gate and authorizes resuming
fighter work. It does not identify which fighters/outfits were exercised or
individually authenticate generated tattoos, lettering, faces or material alpha.
Record the report without changing historical per-revision review flags.

## Baseline and next work

Keep the published `0.1.0-beta.1` artifact, receipts and three pinned candidates
immutable. Compare new child revisions against both that baseline and the
original/Faithful source. No broad regeneration of accepted art is required.
New work uses Rich Original Detail only; faces/likeness, UV layout, original
composition, palette and complete material alpha remain protected. Use references
for uncertain inscriptions/logos; ask the owner to approve uncertain details.

For Blaze, Nyne and Trejo, select localized improvements from owner feedback:
garment/denim lettering, jewelry, tattoos and any visible color seams. The main
atlases already contain clothing, skin and accessory areas; camera presets do
not imply separate shoe/pants textures. Trejo's tattoo stroke/script paths and
animal/tree placement retain their original-composition constraints. Do not
reapply Trejo's neck mask to another fighter without inspecting its geometry.

The existing source mapping documents 15 unique texture IDs across five model/
state variants: the three main atlases already shipped, two additional Blaze
states, and ten smaller secondary images. Blaze `113C` is annotated as a bloody
state; do not silently present it as a cosmetic outfit. `br01`/`br02` labels and
alpha extrema do not prove damage-map semantics. Inspect their materials/runtime
use before any image generation. Existing static model support is limited to
the three main outfits; new fighters need identity/geometry/UV verification.

Ask for two or three next fighter names and the preferred existing-fighter
priority. Then map their dump archive/model/texture IDs, inspect atlases and
references, establish protected faces/material masks, and add verified models
and one Rich Original Detail draft per selected main atlas to review. Preserve
all prior revisions and notes. Compare in 2D (25/50/100/200%) and synchronized 3D;
revise locally, then prepare a new beta only after review. Publication is a
separate explicit step, with a new version and immutable hash for changed bytes.

## Review-session prerequisite

Read-only checks on 2026-10-27 found no port-8768 listener. Original tools
`local.json` points to a removed DefJamPR19-20 corpus. The private workshop,
17 candidates and cached Blaze/Nyne/Trejo models are intact. The current setup
corpus has a different recipe identity, so merely changing local.json must not
silently reset or rebind the existing workspace. First inspect compatibility
and preserve browser drafts, metadata and exact candidate/model hashes; restore
the old corpus or use an explicit backed-up migration if needed. Keep origin
127.0.0.1:8768 and single-writer ownership. No server restart, migration, model
conversion, review mutation, new generation or new publication was performed
while recording this continuation plan.

Technical evidence is in the existing restoration-pilot-fighter-mapping report,
model conversion receipts and color-preservation guide. The published recipe
remains pinned to its exact original builder/selection hashes. This documentation
change needs no new synthetic or native runtime tests.
