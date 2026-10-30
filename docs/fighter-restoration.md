# Fighter restoration — calibrated workflow

The owner approved the complete five-fighter reference set on2026-10-29:
Blaze v4, Nyne/Trejo v3, Redman v4 and Henry Rollins v6. Exact revision/output
hashes are pinned in research/hd-fighters-0-2-beta-20261029/selection.json;
actual artwork, prompts, references and processor evidence remain private.
HD Fighters0.2(beta) packages only this approved set. Native0.2 playtesting
remains pending. The next ten main-outfit drafts are excluded from that release. The owner has
now accepted nine complete models, including the repaired Ludacris and Flava
Flav children. Warren G's latest complete back-crest repair requires review.
The second ten-fighter batch also remains unapproved and outside0.2.

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

## Named chest details are separate review targets

The first ten-fighter batch exposed a specific failure: source holds kept the
Ludacris shirt print, Flava Flav clock dial and Warren G script low-resolution,
even though their garments/props had generated detail. This was an assembly
omission, not proof that imagegen missed all chest details. The owner accepted
everything else and requested these three repairs on2026-10-29.

Inventory each visible chest logo, wordmark, pendant, clock and important tattoo
by name and source bounds. Record restored, pending or explicitly owner-accepted
held. An uncertain small inscription can be held; a broad whole-logo/prop hold
leaves that feature pending. A high global/material-component changed count does
not prove that a named feature was restored. Compare its own final crop against
source and parent after all holds and palette correction, at100/200%.

Use a dedicated focused crop for a missed feature. Spell known words and line
breaks explicitly, preserve original handwriting paths, bounds and split UV
islands, and request reconstruction rather than retaining pixel blur. For clock
props name hand angles, marker layout and case/dial geometry. Unknown microtext
must not become a guessed brand. Keep the rest of the accepted atlas exact.
`feature_detail.restore` applies source-palette control inside a material/feature
mask without an extra rectangular edge hold; alpha and parent pixels elsewhere
stay exact. See research/chest-details-20261029/ for measured source-specific
masks and the three focused repairs. Those coordinates are examples only.

Warren's back crest also spans two distant atlas fragments. One repaired half
does not close the feature. Inventory every fragment/copy, including back,
rotated and mirrored islands; inspect final assembled Front AND Back views.
Clip source triangles to UV and model-space bounds when identifying fragments.
The RGB UV diagnostic helps inspect their junction but ignores alpha and game
shaders. Keep actual source geometry unchanged. See the
[split back-crest repair](../research/warren-back-logo-20261029/README.md).

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

Compare the source's semantic features as well as sharpness: Freeway's cap digits
were erased despite new cloth detail, and Elephant Man's figurine became jeweled
letters. Inventory legible headwear inscriptions and the actual type of each prop.
Keep every existing readable mark, including text split by a seam. Changed pixels
do not prove that the original content survived. Do not let shorthand for another
jewelry tile become the figurine's design instruction. For a reference-assisted
repair, use the original tile as layout authority and photographs only for the
specified sculptural/material detail; preserve the rest of the parent exactly.

Unresolved tattoo wording requires evidence. Preserve the source's strokes, spacing
and placement; a contour-preserving cleanup can make ink cleaner but cannot verify
the intended words. Avoid adopting generated or OCR transcriptions as reference.
Record the uncertainty and seek a matching period photo/video or higher-resolution
version of the same art. Owner approval is needed for a proposed interpretation.

Keep playtest reminders distinct from visual acceptance. On2026-10-29 the owner
found Bonecrusher visually OK and requested a reminder when preparing the next
HD Fighters test pack. The private revision review carries `playtest-next-pack`;
include that reminder in the next pack's test instructions. Native verification
stays false until the owner actually tests it.

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
The owner requested twenty more in the latest batch. Individual approval, uncertain marks
and native playtesting remain review gates for every future release.

For bulk assembly see research/fighters-batch10-20261029/assemble.py. It derives
actual opaque-material coverage, holds eyes/alpha/unknown groups plus one source
texel, records both sides of distinct paired skin UV edges, and subtracts local
source Lab drift. It then matches clothing separately, including cloth1, and
restores declared source holds and seam cores after that last pass. Per-material
connected-component coverage flags omissions. The private per-fighter plan
records inspected mouth/inscription/emblem holds. No head quadrant, anatomical
plane, Rollins seam count or watch/glyph rectangle is a generic default.

The [second batch recipe](../research/fighters-batch20-20261029/README.md) uses
`fighter_scopes` and measures each named feature after ALL assembly holds and
palette correction. A missing required feature fails even when overall coverage
is high. A declared held feature is pending. This detects omission, not design
authenticity; inspect the final crops as well. Repeated fragments need separate
checks and assembled views. Alpha material names alone do not mean RGB must be
held: an audited cloth or jewelry group can opt in while alpha remains exact. An explicitly
identified source RGB tile absent from ALL static UV coverage can be restored
separately; this must never override a mapped held material or imply non-use in
the game. Record the reason and limitations. Keep prompt history immutable when
later inspection corrects a feature's shorthand description.

The [twenty-fighter recipe](../research/fighters-batch40-20261029/README.md)
adds explicit audited jewelry RGB opt-ins and Comp's opaque `others` head/hair
group. Other unknown and eye materials remain held. Source alpha stays exact.
Verify the source role through actual UV coverage; the group name alone is not
evidence. Named-feature padding can be restored via strictly zero-UV-covered
runs, never by overriding mapped holds. Skull's lettering, Havoc's lace tile and
Solo's tiny pendant exposed source-held unmapped remainders. Their padding was
finished using existing raw detail. Static absence still does not prove game
non-use. Preserve genuine skin seam guards even when small crown components
show low change; unchanged plain black or collapsed UV pixels need interpretation.

For parallel batches, assign disjoint private plans/raw files and keep one import/
review/cutover owner. Persist each exact submitted prompt before generation and
capture every result independently with `Promise.allSettled`, so one rejection
does not lose another result. Keep failures and uncertain attribution honest.
When fighter choice is delegated, a rejected input may be replaced by a distinct
compatible fighter; do not claim a rejected enlargement is restored or silently
switch providers. Preserve input/output hashes and original prompt wording when
later inspection corrects a feature label or anatomical location.

Inventory supplementary texture slots too. In this batch every retained static
mesh binds its primary A### atlas; br01/br02 resemble injury alternatives and are
outside clean-atlas restoration. Runtime triggers are unproven. Check damage
transitions in the game for detail/palette breaks before considering them complete.

Do not apply color_trial.correct with a newly restored protected head: that
function requires protected parent pixels equal Faithful. Use reference-matched
regional assembly instead. Grain transfer is an optional localized method;
calibrate spatial frequency and amplitude, not merely the overall output size.


## Direct-index resources and female hair

The [next twenty restorations](../research/fighters-batch60-20261029/README.md)
contain16new fighters and4explicitly authorized alternate costumes. Do not call
alternate or damage copies new characters. Retain blocked requests honestly;
ask before substituting outfit work when the remaining unique roster is exhausted.
No provider switch or disguised retry. Source identity and complete final feature
checks apply to every costume independently.

Inspect actual texture bindings before deriving main-atlas masks. Some female
mouth-tape meshes use shared external art; Shawnna uses unresolved primary-atlas
mouth-tape semantics. The static decoder omits these exact audited cases with
visible limitations. Do not let their broad UVs hold most of the body atlas or
pretend their appearance was restored. All retained meshes bind their own atlas.

Hair needs exact audited group permissions, including spelling variants ASym_Hair
and L_Hair. Some alpha groups mix eyelashes and rear hair: use a declared narrow
material/box intersection, leaving other components and overlapping holds intact.
Source alpha remains exact. Alpha-looking pixels alone do not prove source blend
mode. Preserve actual UV overshoots; bounded canvas clipping reflects the current
clamp preview, not universal game sampler parity.

Named feature checks must sample the actual mark: Cindy buttons, Manny laces,
Teck three bandages and every BLAZE/31 fragment exposed mistaken inventory bounds.
Correct metadata without rewriting submitted prompts. Strict zero-UV padding may
finish source-looking outer cross/chain/crest copies, never mapped holds. Tiny
already-editable feather boundaries can change by1RGB level between stages;
do not claim all mapped pixels byte-identical. Genuine flat black components do
not need invented texture to satisfy a change percentage.

If raw tattoo contours or words drift, retain source paths and add only generated
fine ink residual, as in Prodigy. This is not decoded text or full reconstructed
tattoo imagery. Keep uncertain areas pending and record their actual scope.
Known CITY/POLICE lettering was verified after final masking; Jervis's mirrored
last E was corrected with already-generated correct lettering under a narrow
lower-band mask, retaining his own palette and all other parent pixels exactly.
