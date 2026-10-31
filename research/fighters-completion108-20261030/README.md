# Remaining fixed fighter texture restoration — 2026-10-30

Owner scope: the 108 source IDs without restoration children in the audited fixed
core: 15 main/state atlases and 93 secondary maps. New outputs require final owner
review before HD Fighters 1.0 packaging. No new package, upload, manifest update,
selection, native verification or push is authorized in this pass.

## Result

94 review drafts were imported:12 main/state atlases and82 secondary maps
(81 injury states plus the uninjured Carmen B head). Four partial studies remain
private;10 ImageGen refusals remain gaps. All108 IDs are accounted for, but the
fixed core is not fully restored:199/213 have full draft coverage,14 remain
incomplete. New drafts are not owner-approved. Exact hash/status metadata:
[selection.json](selection.json).

103 fresh built-in calls produced93 raw studies and10 refusals;5 earlier
successful raw studies were reused with exact provenance. New main refusals:
Xzibit, David Banner, Carmen B. Injury refusals:Sticky A02, Sticky B02, D-Mob C02,
Blaze C01/C02, Memphis Bleek01/02. Xzibit/Banner01/02 have only partial studies.
Fresh refusals stopped without provider substitution or disguised input.

Root independently audited94 final PNGs and verified all94 live PNG hashes plus
11 new GLB embedded textures.121 tests+23 subtests pass. All719 baseline candidate
files/metadata, previous reviews and the65 adopted model caches were preserved.
Four unused decoder1 caches were archived intact before strict decoder2 staging;
one identical decoder2 cache reused and six additional cache directories added.
The live viewer has76 models. UI smoke checked Bo, Magic Story B and Shaniqua2D;
94 tagged results are searchable. Prior model view entries stayed exact; only
new Bo/Magic views and intentional gallery filter choices were saved.

Independent QA inspected every full atlas feature and injury comparison/detail.
Source mark boundaries and chroma speckle remain; Baxter02/Meca02/Teck02 deserve
close100% review (baseline clipping5266/5438/7432 events respectively). Clipping
sets may overlap; counts are not proof of harmlessness or unique damaged pixels.

## Execution and provenance

Three disjoint private workers plus the root process used the built-in ImageGen
edit tool, one call per distinct source. Root alone imported into the existing
writer. Exact prompts, input pins, raw outputs or error receipts, frozen
assemblers, comparisons, independent audits and before/after review snapshots
live in the private workspace under
`experiments/fighters-completion108-20261030/`. No artwork belongs in this repo.
See its `review-index.md`, `delivery-ledger.json`, `imports.json`,
`root-technical-audit.json` and `live-verification.json` for exact IDs/paths.

Main atlases use original layout, likeness, actual UV masks where supported,
source skin/clothing/headwear/footwear palette, own alpha and inspected auxiliary
holds. Unknown tattoo words/medallion designs retain original contours; successful
image generation does not authenticate ambiguous writing. Registered Story states
reuse restored clean materials plus the own source RGB difference, with bounded
new luminance only in declared state regions. Raw stronger marks and new designs
are excluded. Source boundaries/compression patterns and clipping remain disclosed.

Supplemental injury states use the independently registered clean head plus own
original RGB delta and bounded generated fine luminance described in
[the injury workflow](../../docs/damage-restoration.md). Each own alpha is exact;
actual holds and clean exterior are checked. Carmen B's shared br01/br02/br03
source visibly contains an uninjured head: it is a secondary head state with
unverified usage, restored independently, never labeled invented damage.

Rejected ImageGen outputs retain exact receipts and remain gaps. Independent
Xzibit/David Banner injury-local studies retain an unenhanced clean reference:
these are partial studies, not whole-head restorations, and never reconstruct a
rejected main atlas. Zero-new-generation continuity studies likewise do not
satisfy missing injury detail. No fresh rejection is retried through a different
provider or disguised input.

## Source model previews

Eleven additional source models pass existing strict decoder validation. Two
nested cinematic members route through bounded exact archive traversal. Original
positions, UVs, normals and partitions remain authoritative; no synthetic normal
repair is adopted. Shaniqua, Cindy B and Crow B/D remain 2D-only because strict
source-normal validation fails. Blocked main atlases can still have original
geometry previews; model availability does not mean their texture was restored.

The static viewer does not establish native injury switching, UV transforms,
material alpha or Story binding. Native fight/state-transition and Story checks
are required before a damage-enabled release; prerecorded movies are unaffected.
Core213 excludes unresolved shared effects and the separate created-player stream.
See [the coverage audit](../fighter-coverage-20261030/README.md).

## Review and release gate

Use the same local origin at port8768. Full texture library, clear other filters,
search `fighters-completion108-20261030`; compare at25/50/100/200% and save notes.
New main atlases can also be checked in the model viewer where strict geometry
is supported. All new children stay unreviewed/unselected/not game verified.
Preserve earlier approvals, candidate bytes, notes, requests and camera choices.

Resolve or explicitly accept every remaining gap during final review before
calling the fixed core complete. Remind Vlad to playtest Bonecrusher when the
next HD Fighters test pack is prepared. Public0.2 remains unchanged.

## Immutable receipt metadata erratum

Seven main creation receipts (LilFlip,Santos,DmobD,BlazeC,CindyB,CrowB,CrowD)
have an `editable_hair_groups` field containing an override dictionary, caused
by a variable-name reuse in the private helper. It does not change their actual
allowed masks, pixels, source geometry or frozen processing. Plans, allowed.png,
geometry/override/processor pins and independent pixel/seam checks define scope
and pass. Preserve original receipts with this erratum; do not parse that field
as a list of material groups. No schema migration or live review change made.
