# Fighter restoration — calibrated workflow

The owner approved the complete five-fighter reference set on2026-10-29:
Blaze v4, Nyne/Trejo v3, Redman v4 and Henry Rollins v6. Exact revision/output
hashes are pinned in research/hd-fighters-0-2-beta-20261029/selection.json;
actual artwork, prompts, references and processor evidence remain private.
HD Fighters0.2(beta) packages only this approved set. Native0.2 playtesting
remains pending. The owner now authorizes ten new main-outfit review drafts;
those remain unapproved/unselected and excluded from the release.

## Prepare each fighter

Identify the exact main outfit, source texture ID, source/parent PNG hashes and
decoded geometry hash. Reference images must come from that same source atlas;
different outfits or promotional photos do not control its UV composition.
Record the latest accepted parent separately from published0.1 and exploratory
drafts. Keep the original atlas and Faithful HD available beside the target.

Inventory head/face, hair, headwear, torso, arms/tattoos, upper clothes, trousers,
shoes, jewelry and standalone eyes/mouth. Mark each as restored, intentionally
held, missing, blocked or awaiting review. A2048px output is not evidence of
restoration: Rollins' unprocessed body was already Faithful HD at that size.

Build edit/hold masks from actual material UV triangles and inspect disconnected
components. Crop rectangles bound a request; they do not establish safe pixels.
Broad eye/mouth holds excluded Redman's headwear strips/panel and Blaze's cap
corner. Check those small islands explicitly before importing a full atlas.
Subtract shared material coverage and its guard; ambiguous overlaps require
inspection. Keep source alpha separate throughout the process.

## Generate and assemble

Use the built-in imagegen skill, Rich Original Detail only, one fighter or
localized repair per call. Label every input's role. Use the templates in
[fighter-restoration-prompts.txt](fighter-restoration-prompts.txt), filled with
the actual edit region, source references, exact known inscriptions and held
areas. Save the exact submitted prompt, input hashes, raw output and errors in
the private experiment before importing a new child revision.

Preserve original likeness, proportions, expression and illustrated sculpting;
slightly more realistic skin/hair and fine material detail are authorized.
Unknown tattoo marks and logos are not an invitation to invent. Check reliable
references where available; uncertain interpretation needs Vlad's approval.
Keep silhouettes, animal/tree positions and handwriting paths from the original
even when the inscription is known. Text clarity does not justify redesign.

After generation, source RGB controls broad hue, saturation and baked shading.
Use geometry-scoped skin/seam calibration and separate cloth calibration, which
also handles neutral pants, shoes and headwear. Do not apply the skin filter to
black clothing or increase contrast globally. Preserve restored fine detail.
Parameters are fighter-specific; the pilot's rectangles are not a reusable
coordinate template. Freeze the processor source and receipt for every output.

For an isolated omission, first inspect the saved raw output. Reuse its detail
under a safe material mask instead of regenerating accepted areas. The
`clothing_detail.repair` assembler copies all parent pixels outside that mask
and its full alpha exactly. Match palette before copying the repaired region.
It does not establish likeness or tattoo authenticity.

If generation is blocked or fails, record the request/error and leave that
coverage incomplete. Do not substitute an original enlargement and call it
restored, nor automatically repeat a blocked request through other providers.

## Regional study method

For separate artwork/material tasks, inspect matching original crops first.
Rollins' successful studies independently restored a sun/known caption, arm
illustrations, a small emblem, a plain non-anatomical skin swatch and a transparent
decal. The decal and direct emblem redraw did not meet fidelity needs and remain
studies only. Generation success is not an adoption criterion.

Transfer a plain material sample's fine luminance residual only; retain the
atlas's original coarse color, baked shading and anatomy. Derive skin-only UV
coverage and actual head/body seam guards from the current fighter's geometry.
Hold current-parent seams, approved head/clothes and full alpha exactly.
Use direct crop detail only where interpretation is acceptable; otherwise
restrict generated residuals to original ink interiors and keep contours.
Protect uncertain source words technically even when the raw looks more legible:
the arm study guessed text despite a preservation prompt. Check source letters
and isolated curve continuity after applying holds, before importing.

See research/rollins-region-studies-20261028/ for source recipes and measured
parameters. Compare richer and contour-preserving children; do not present subtle
ink grain as reconstructed lettering or authenticate a tattoo from sharpness.
For chest-local work, clip source triangles against anatomical model-space and
UV bounds rather than choosing entire triangles by their centroids. Explicitly
union separate tattoo islands. The atlas may be rotated or nearby islands may
belong to hands/neck rather than chest. Calibrate generated grain's spatial
frequency as well as amplitude; whole-swatch enlargement can produce oversized
pores. See research/rollins-chest-v6-20261029/ for the measured Rollins example.

## Review and freeze

Import through the live writer API. Keep one writer and the same browser origin.
Back up workshop reviews and model views first; use review versions to reject
concurrent overwrites. New children remain unapproved and unselected. Retain all
old images, notes and provenance; archive superseded choices reversibly.

Check the actual displayed revision ID in the model viewer. Saved choices may
point at a published baseline even when newer drafts exist. Use Latest
restoration; inspect any Older texture notice. Record the exact right revision
and output hash with the feedback. Never infer approval of an unseen child from
a comment about its parent.

Compare Original/current/parent at25/50/100/200% in2D, then unlit model Front,
Back, Face, Chest, Belt, Pants and Shoes; orbit both sides of the head and neck.
Check skin continuity, restrained original cloth color, visible small islands,
tattoo/lettering placement, alpha, source UV boundaries and material joins.
Studio lighting is supplementary; the original geometry and game effects have
not been upgraded. Technical pixel checks do not replace owner visual review.

Before calling a fighter complete, retain evidence for:

- Every intended visible material/island restored or explicitly accepted as held.
- Exact alpha; approved parent pixels outside localized repairs unchanged.
- Coarse source palette retained for both skin and clothing, with paired UV seams
  guarded where established. No invented seam guarantees when no pairs exist.
- Source geometry/UVs unchanged; PNG and exported GLB embed the intended revision.
- Owner approval attached to the exact revision, with resolved notes summarized
  and old notes recoverable. Face/channel checks and pack selection remain explicit.
- Native playtest recorded for the resulting pack;0.1's prior playtest does not
  verify later face/headwear revisions.

The approved five now form the frozen private calibration reference. Their
methods are examples, not reusable atlas coordinates. Whole-atlas generation
suits mostly clothed fighters; Rollins required localized tattoo/material work.
The owner's current new batch size is ten. Individual approval, uncertain marks
and native playtesting remain review gates for every future release.

For bulk assembly see research/fighters-batch10-20261029/assemble.py. It derives
actual opaque-material coverage, holds eyes/alpha/unknown groups plus one source
texel, records both sides of distinct paired skin UV edges, and subtracts local
source Lab drift. It then matches clothing separately, including cloth1, and
restores declared source holds and seam cores after that last pass. Per-material
connected-component coverage flags omissions. The private per-fighter plan
records inspected mouth/inscription/emblem holds. No head quadrant, anatomical
plane, Rollins seam count or watch/glyph rectangle is a generic default.

Do not apply color_trial.correct with a newly restored protected head: that
function requires protected parent pixels equal Faithful. Use reference-matched
regional assembly instead. Grain transfer is an optional localized method;
calibrate spatial frequency and amplitude, not merely the overall output size.
