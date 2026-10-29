# Def Jam Modding Tools — progress and handoff

## Current status

**2026-10-29: seven new models approved; three focused chest repairs ready.**
Owner accepted everything except Ludacris shirt print, Flava Flav clock and
Warren G script. Diagnosis: broad source holds reverted generated chest features
to low resolution. Three new focused built-in edits now reconstruct those details;
source placement/letter paths, muted colors and approved surrounding art retained.
New children are UNAPPROVED/unselected: Ludacris r-9b80bbe05e6a4b59,
Flava r-9d997f2360fe4bd5, Warren r-70bb2a3cdb234d93. Exact pins/method in
research/chest-details-20261029/. New module feature_detail.py controls scoped
source-palette matching without an atlas-edge omission. Changes146515/102801/
134866pixels,94.7–99.0% per named region. Alpha and every parent pixel outside
masks exact; tiny unreadable clock signatures remain held. Final contact sheets
inspected, three live PNG/GLB pixels verified, all56previous candidates retained.

Seven complete first-batch models approved through API; these three v1 parents
have component acceptance and chest defects pending. New feature children await
review. Exact before-notes/versions retained. Cameras/left/lighting/groups and
active fighter preserved; right choices updated for these three.59candidates,
30requests,15models; same PID19687/exec52690, no restart/forced reload.
98tests+15subtests pass, including3new feature scope/palette/atlas-edge tests.
Prompts/guides now name chest logos/props explicitly and require per-feature final
crop review. Whole-feature holds are pending, not restored; global coverage does
not close them. No new release/install or0.2 change.

**Prior release/batch baseline:** approved five published as HD Fighters0.2(beta).
Owner explicitly approved all five complete models, requested0.2 publication and
then ten new fighters using the same guidelines. He also confirmed all browser
notes saved and authorized the viewer restart. Five approved PNGs stay exact.

### Published0.2

- `hd-fighters` version0.2.0-beta.1, testing/prerelease; min game0.12.1.
- Blaze/Redman v4, Nyne/Trejo v3, Henry Rollins v6. Exact revisions/hashes in
  research/hd-fighters-0-2-beta-20261029/selection.json.
- Five2048RGBA atlases; full Faithful material alpha; png_mips=channels.
  Faces/hair/headwear are now restored and explicitly owner-approved.
- ZIP34,424,972B; unpacked34,417,307B;8files; SHA256
  1a10e9a714c0c2df00e6c68203213381b1cc628622ce14ae3eb20187c78a8561.
- Immutable Cloudflare objects uploaded; full public size/hash/206range verified.
- Catalogue PR8 merged as d552860160f3ba72e30358f39ca45ad8346d9344.
  Protected publish40914786807 succeeded, signed catalogue revision8. Existing
  owner approval gate retained; bootstrap=false; no key/protection changes.
- Released0.12.1 helper and catalogue package checker produce identical eight
  files/fiveIDs. Released pinned key verifies signed public index; fresh disposable
  managed install exact; stable channel excludes beta; settings/save sentinels and
  then-current workshop unchanged. Native0.2 playtest still pending.
- Public0.1 remains immutable; owner reported its successful playtest2026-10-27.
  Ten new drafts are excluded from0.2. See release README for download/install.

### New ten-fighter review batch

D-Mob, Sticky Fingaz, Ludacris, Ice-T, Crow, Sean Paul, Crack, Flava Flav, WC,
Warren G. All ten XML main-outfit identities, image0 source IDs and accepted
original512/Faithful2048 hashes measured. Models decode unchanged; Xzibit and
Ghostface were excluded after unsupported index-header probes. Method Man is
already Blaze. Corpus stays read-only; no binding/schema migration needed.

Ten built-in whole-atlas edits succeeded, Rich Original Detail only. Head/face/
hair/headwear, skin, clothing/footwear and safe opaque jewelry included. Slightly
more realistic hair/skin keeps original likeness/layout. Assembly derives actual
material masks and both sides of unambiguous paired skin UV seam edges; no copied
pilot quadrant/eye boxes/Rollins anatomical constants. Local Lab correction plus
separate cloth correction handles skin AND all garments, including Ice-T cloth1.

Eyes/alpha/unknown materials, narrow mouth tiles and uncertain source glyphs/
watchfaces/emblems stay held. Distinctive raw interpretations were not adopted.
Exact alpha/outside holds/seam cores verified. Final stages `assembled/*-v2/`
change2.62–3.21M pixels. Every editable component16+native pixels changes≥25%;
median source skin Lab distance1.20–1.55, cloth groups0.94–2.31. These are technical
checks, not evidence of likeness/design authenticity. Atlas contact sheets inspected.

All ten initially imported via single live API, unapproved/unselected, tagged
batch-10-20261029. Exact new PNG hashes and selected revision/GLB RGBA verified.
All46prior candidate metadata/PNGs, old reviews, request/session state held through
import. Current/shared approved-five notes then reconciled separately with exact
backups and optimistic versions; old revisions/notes remain recoverable.

Viewer has15models at same8768/workspace, writer PID19687/exec52690. Exact JSON,
old cameras/choices/groups and session survived cutover. Initially56candidates,
30request records,17archived choices (includes existing menu candidates).
New fighters default Original/new draft; existing saved views retained.
Browser visual QA was not repeated because prior browser URL policy remains;
backend model/pixel verification and local atlas inspection performed. No bypass.
No active game installation/settings/save, runtime or frozen snapshot change.

## Decisions

- 2026-10-29: owner approves seven complete new models and all other components
  of Ludacris/Flava/Warren, asking to restore their chest print/clock/script.
  Keep accepted parent pixels outside scoped repairs exact; three new children
  remain unapproved. Broad holds caused the omission. Dedicated feature prompts
  and named-feature final crop checks replace whole-logo/prop source holds;
  two genuinely uncertain tiny clock signatures remain held. No new publication.

- 2026-10-29: owner approves all five complete models and authorizes HD Fighters
  0.2(beta) publication. Pin exact accepted revisions; full restored faces are
  intentional, replacing the old face-exact-to-Faithful condition. Alpha remains
  exact. Owner visual approval supports face review; technical checks support
  channels/selection. Do not infer native0.2 playtest from old0.1 acceptance.
- 2026-10-29: owner chooses batch size10 and delegates fighter selection. Choose
  ten distinct main outfits with compatible current model decoding. New drafts
  remain unapproved and outside the approved release. Preserve unknown source
  marks rather than adopt generated words/emblems. Keep raw studies privately.
- 2026-10-29: freeze calibrated workflow from accepted five, with private exact
  prompt/parent/output evidence. Geometry/material masks and per-fighter source
  holds are mandatory. `color_trial.correct` is unsuitable for newly restored
  protected heads; reference-matched regional assembly plus cloth correction is
  used. Pilot quadrants, Rollins16seams and anatomical/RM IDs are not bulk defaults.
- 2026-10-29: owner confirms all browser notes saved; explicit backed-up single
  writer cutover on the same origin. No corpus/schema migration or forced reload.
- Prior art choices retained: Rich Original Detail only; include face/hair/head/
  headwear, slightly more realistic surfaces with unchanged sculpt/likeness;
  source palette for skin/clothes/shoes/headwear. Unknown interpretations need
  owner review. Original UV/tattoo silhouettes/handwriting paths outrank semantics.
- Trejo caption Debbie Danielle; buckle bear left, deer right, smaller deer middle.
  Approved v3 bytes retained. Rollins v6 retains v5A outside clipped chest and
  combines successful tattoo edit with finer prior material detail after direct
  anatomical skin generation failed. Historical failures/studies retained.
- Cleanup remains reversible archived-review tags; never delete PNGs/IDs/prompts/
  parents/hashes. Current resolved notes may be reconciled with backup/version
  checks. Preserve published baselines and saved comparison choices.
- Authoring belongs in this repo; runtime/loader/setup stay in the recomp with
  frozen compatibility snapshot. Source-only Git; private artwork/models/reviews.

## Evidence and validation

Source release recipe: research/hd-fighters-0-2-beta-20261029/.
Source batch recipe/report: research/fighters-batch10-20261029/.
Focused chest repairs: research/chest-details-20261029/; private same-named experiment.
Calibrated docs: docs/fighter-restoration.md + fighter-restoration-prompts.txt.
Private paths/commands/import IDs live in ignored .local-handoff.md and workshop
experiment review-index.md. Exact prior status archived unchanged under ignored
`docs/worklog/fighter-progress-before-release02-20261029.md`.

Checks:98pytest tests+15subtests pass (three new synthetic feature tests after
the prior three material/seam tests).
Initial sandbox run denied the two existing HTTP bind tests; rerun with loopback
permission passes all. Catalogue14tests, metadata validation and protected remote
content verification pass. Eight Node tests and JS syntax pass; source checker520files/0policy failures. All ten output masks, per-component coverage, alpha/palette,
PNG/GLB exactness and existing-candidate retention verified privately.

## Handoff

1. Keep same single writer live. Owner can refresh8768/model-viewer after saving
   notes; choose each new fighter and Latest restoration. Inspect unlit Front/
   Back/Face/Chest/Pants/Shoes, both head/neck sides, clothing color and small
   islands. Notes/flags stay revision-bound. Browser drafts/409 preserve conflicts.
2. Seven new-batch models are approved; preserve bytes. Review only the latest
   Ludacris/Flava/Warren chest-feature children, using Chest detail and2D100/200%.
   Current exact IDs/hashes: private chest-details-20261029/imports.json. Keep
   all accepted head/skin/clothing outside masks exact. No new-child approval
   inferred from the accepted surrounding parts.
3. Owner can install/update0.2 through Mods → Show testing versions → Refresh
   catalogue → HD Fighters, then enable after optional Faithful HD and restart.
   Native0.2 acceptance is still needed. No active game install was changed here.
4. Preserve all accepted art and old private data. Next release requires owner
   approval of exact new children and a new immutable version; do not change0.2.
5. Current source branch codex/hd-fighters-beta in isolated tools checkout;
   continuation commit local until owner requests push. Catalogue publication is
   already pushed/merged/live. Original menu checkout source stays unchanged.
