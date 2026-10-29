# Rollins v6 chest correction —2026-10-29

Owner prefers v5A and requests chest skin/tattoo restoration. Use v5A
r-a6ca883293734644 as the immutable parent; do not infer whole-fighter approval
or change other accepted fighters. The new child remains unapproved/unselected.

The actual chest tattoo is the small CREEPY CRAWL patch at HD[768,512,1024,832).
Its previous v5A contour-preserving treatment was intentionally soft. Main chest
skin lives in the rotated upper-left UV island, separate from back sun/arms.
The narrow upper islands are hands/wrists. Four bars below the head map to rear
neck, not chest; those stay exact. A bounded independent UV audit is retained
privately and its relevant claims were checked by actual mask counts.

## Changes

One new built-in tattoo edit succeeded, clarifying the oval, nested curves,
internal strokes and CREEPY/CRAWL lettering against the original reference.
A direct chest-skin edit was output-moderation blocked, request
48ea5469-0b56-4d61-a6f3-0a84c7da63e6, category sexual. No skin image returned or
imported. Skin instead uses the earlier successful non-anatomical material study:
512HDpx detail tile, two radius2 high-pass filters, L residual RMS1.2 capped±3,
and gentle original-luminance sharpening. Original diffuse hue, anatomy and
broad baked shading remain the base. This is material-detail transfer, not a
new anatomical skin generation. Initial coarse-grain assembly failed visual
QA; intermediate stages are private history, not the imported result.

Source triangle polygons are clipped in model/UV space, not selected by centroid.
For this Rollins chest only, Y>=16,Z>=.3,|X|<=3,U<=.375,V<=.25 defines the main
chest; union RM11 triangles549–550 and RM16 triangles79–90 for the tattoo island.
Intersect actual skin-only coverage and the existing accepted head hold.
Main chest5,819native/93,104HDpx; tattoo3,141native/50,256HDpx; total143,360HDpx.
Four-source-texel inner feather and16verified current-parent head/body seam
guards avoid leaking detail into v5A. Anatomical limits are model-specific.

Final review child is r-5304b94c634a4fa9. Stage is **assembled-v3**. Output SHA256
b0992fd40cf4c73bc430002c4e509992712f93ce57be7f57b2d61e7453d06760.
Changed74,068front skin pixels and44,853tattoo pixels. All pixels outside chest,
including face/hair, back sun/caption, arms, clothes and boots, plus full material
alpha and verified seam cores stay exact v5A. New tattoo detail still needs
owner likeness/shape/lettering review; technical checks do not authenticate art.

## Review and validation

`prepare.py` pins inputs and writes an immutable private stage. `import_verify.py`
uses the existing authenticated single writer, preserves old notes with backups,
records v5A as preferred with chest revision pending, and imports a new child.
Only saved Rollins right selection changes; camera, left, lighting/groups and
active fighter stay intact. Shared notes describe the actual material method.
No server restart, forced reload, game install, pack release or0.1change.

92tests+15subtests pass. New synthetic cases verify clipping across model/UV
planes, explicit island unions and invalid inputs. Live verification checks
candidate PNG hash, exact outside-chest/alpha, exported GLB RGBA, every previous
candidate file/metadata and unaffected review records. Browser visual testing
remains blocked by prior URL policy; no workaround. Owner review is next.

Private experiment rollins-chest-v6-20261029/ holds inputs/prompts/raw, failed-skin
record, anatomical audit, all QA stages, final masks/receipt/comparisons,
before-import state and import-verification.json. Save browser notes, refresh
the existing model viewer and choose Latest restoration/Chest detail. Compare
new v6 with v5A and Original; all other fighters remain accepted and unchanged.
Bulk calibration stays provisional until the chest/body result is accepted.
