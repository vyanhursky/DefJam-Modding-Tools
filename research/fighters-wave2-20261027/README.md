# Five-fighter review batch, 2026-10-27

The owner reported HD Fighters0.1 looks great in native playtesting, selected
Redman and Henry Rollins next, and authorized body/face color matching,
face/headwear detail restoration, then final tattoo/clothing review for Blaze,
Nyne and Trejo. This supersedes the earlier three-fighter face hold for fine
detail only; likeness, proportions, expression and original game style remain.
Public0.1 stays unchanged. No new approval, game installation or publication.

## Delivered review drafts

- Blaze color-only Source palette `r-f64a96c0804b4f2f`, parent0.1 Rich detail.
- Blaze face/headwear `r-ce482323cf104130`, parent the color-only draft.
- Nyne color-only Source palette `r-fa477444a8a44bd5`, parent0.1 Rich detail.
- Nyne face/headwear `r-bb686c64f6464ea7`, parent the color-only draft.
- Trejo face/headwear `r-8cc03d584fa1400d`, parent0.1 Source palette trial.
- Redman Rich Original Detail/Source palette `r-31ad7a43fb6547ec`.

Redman and Rollins source mapping/identity and in-memory decode evidence are in
[mapping.md](mapping.md). Both private models exported successfully with the
unchanged decoder: Redman5206vertices/6015triangles/41parts; Rollins4536/5810/30.
Rollins has original/Faithful previews only. Two built-in imagegen attempts were
rejected by output moderation as sexual despite this nonsexual adult game-atlas
request; request IDs, exact prompts/errors are retained privately. No invented
fallback or provider change. Four successful built-in imagegen edits supplied
Redman's full atlas and the original three face/headwear patches.

## Technical assembly and limitations

`assemble.py` consumes an isolated staging-workshop and saved prompt/raw inputs.
New atlases are2048²RGBA; full material alpha is restored exactly. Redman's face
block is baseline-identical. Face patches were authorized for the original three;
the raw generated look was stronger than the source, so `face_detail.merge`
blends at.55 strength after three12px box-blur Lab drift estimates against the
Faithful source. A24px patch-edge taper and held mouth/teeth/eye/swatch rectangles
preserve tile boundaries and standalone facial tiles. Parent pixels outside the
1024² upper-right patch stay exact; geometry and all tattoo layout remain.

Body palette correction uses each fighter's geometry-derived skin/material masks.
Blaze has zero proven held-face/body skin edge pairs; its explicit palette-only
mode makes no seam-guard claim. Nyne has38paired edges, Trejo80face-side pairs,
and Redman6. These are all observed shared protected/body UV edge pairs, not a
claim all are neck edges. Guard core3sourcepx, taper12sourcepx. Existing Trejo
Source palette body remains unchanged; face patches retain source-side guard
cores. No Trejo-specific landmark mask was copied onto another model.

These checks establish pixel/material/geometry invariants, not authentic new
wrinkles, tattoo symbols, inscriptions or likeness. Faces, cap/bandana detail,
body joins, lettering, garment weave and tattoo strokes need owner visual review.
Redman atlas UV/image alignment also needs review on the actual model.

## Recovered gallery and persistence

The old corpus path had been removed. Every recorded baseline of the17existing
candidates matched the current corpus, and all7review-referenced source IDs were
present. `reconnect.py` performs explicit migration v1 with exact metadata backup,
old-state change detection and immutable-file overwrite refusal. Original reviews,
candidates, request records, cameras and resolved workspace path were preserved;
only corpus binding and new additive draft/request records changed. Owner
confirmed no unsaved browser notes before reconnecting at the same8768origin.

Current corpus ID80010c23d2d99dca0d0420d1111f83027821e292e97f298a8f97d01bdb0f61c5;
previousa512d2429f11f9ab03d2eaef65df53afd0a2a2536cfe67af638156ba69bb00ec.
Migration receipt under private workshop/backups/fighters-wave2-rebind-20261027/.
Private exact prompts, raw outputs, processors, masks, reports and review contact
sheet are retained in workshop/experiments/fighters-wave2-20261027/. The scratch
staging copy remains outside Git. The live workspace now has23candidates,
19request records and five models. Original17candidates/reviews remain exact.

74synthetic tests +12subtests,8Node tests and source hygiene pass. Live HTTP checks
cover all five original/Faithful model pairs plus six candidate GLBs (16total),
all six candidate PNG hashes, page routes and persisted review/camera identity.
Browser URL policy blocked inspecting the review tab; no alternate browser or
raw-automation workaround was attempted, so new browser visual validation is
pending. Server stays live at http://127.0.0.1:8768/model-viewer.

Select each fighter's latest Rich Original Detail candidate in the right dropdown;
existing saved cameras/right selections were preserved. Compare face crops, skin
joins and Back/Chest/Belt/Pants/Shoe details, leaving notes on the chosen right
revision. Keep all new review flags unapproved/unselected until owner review.
