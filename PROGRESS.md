# Def Jam Modding Tools — progress and handoff

## Current status

**Latest chest-only correction,2026-10-29:** owner prefers v5A and requests chest
skin/tattoo restoration. New unapproved v6 r-5304b94c634a4fa9 is a child of
r-a6ca883293734644; output SHA256
b0992fd40cf4c73bc430002c4e509992712f93ce57be7f57b2d61e7453d06760.
New built-in CREEPY CRAWL tattoo edit succeeded. Direct chest-skin output was
moderation-blocked (48ea5469-0b56-4d61-a6f3-0a84c7da63e6); no such image imported.
Skin instead uses the successful prior material study at finer512HDtile scale,
bounded L residual RMS1.2/cap3, and gentle original luminance sharpening. Keeps
source diffuse color/anatomy/shading. Initial coarse-pore QA stage not adopted.

Actual model/UV triangle clipping isolates93,104HDmain chest pixels plus50,256
separate chest-tattoo pixels; all143,360allowed pixels stay skin-only.16paired
seam cores and inner-boundary feather hold current parent. Changed74,068skin/
44,853tattoo pixels; all v5A outside chest, head/hair/arms/back/clothes/boots and
alpha verified exact. User preference recorded on v5A with chest work pending;
new child remains UNAPPROVED/unselected. Live PNG hash/GLB RGBA and all33previous
candidate metadata/files verified; unaffected reviews/cameras/preferences held.
34candidates/30requests, same8768writer PID23344/exec99295, no restart/reload or
game/pack/publication change.92tests+15subtests pass. Source report/recipes:
research/rollins-chest-v6-20261029/. Private final stage: experiments/
rollins-chest-v6-20261029/assembled-v3/; earlier stages are QA history only.
Next: owner saves notes, refreshes, chooses Latest restoration/Chest detail,
checks chest skin/oval/lettering/joins against v5A. Bulk recipe stays provisional.


**Prior regional studies,2026-10-28:** owner asks to start and try different
localized approaches. Five built-in edits succeeded: sun/caption, arm art,
plain skin-material sample, transparent decal and small emblem. Two new2048RGBA
Rollins children are imported and UNAPPROVED: v5A r-a6ca883293734644 (localized
sun/arm detail + skin grain, SHA256 a5d773e7da306230d4b1627630fdadb517e8aa484fe998964f372f23c1d33695)
and v5B r-48b6674ae55e409c (source contours + generated skin/ink grain, SHA256
261513e9273f4e8dd2f6a206f4b057c77262c6908a203d7e38d5c0daa165fe86).
A changes1,499,830bodypixels; B1,274,009. Source body Lab distance1.138/.703.
Exact approved v4 head/hair/clothes/boots, non-skin, alpha and16paired seam cores
held. Tiny uncertain arm/emblem lettering stays source; B also holds the sun
caption. A's known SEARCH & DESTROY caption/design interpretation needs review.
Raw arm output guessed words; those were not adopted. Transparent decal/direct
emblem changed art too much, retained as studies only. Emblem uses source
contours in both; earlier QA's hard-cut redraw is not in either imported atlas.

Live writer unchanged PID23344/exec99295 at8768.33candidates/29live request/
assembly records,17archived; all31previous candidate metadata/PNGs and existing
revision reviews/approvals retained. Current Rollins shared notes now describe
successful regional drafts; old blocked requests remain history. Saved right
is A; other view fields/fighters stay exact.88tests+15subtests pass; two PNG
hashes/alpha/nonbody and GLB pixels verified. No browser visual test (prior URL
policy), restart, forced reload, new game install, publication or0.1change.
Private experiment: rollins-region-studies-20261028/, final assembled-v2/.
Source report: research/rollins-region-studies-20261028/. Freeze bulk method only
after owner accepts a body result. All four other fighters stay approved/unchanged.


**Prior whole-atlas approval/retry,2026-10-28:** owner says everything else is good and
approved, and explicitly requests retrying Rollins skin/tattoos. Redman/Blaze
exact v4 are now visually approved; Rollins v4 head/hair/clothes/boots accepted
as components, with the whole fighter still incomplete. Nyne/Trejo accepted
bytes retained. Built-in retry used the v4 atlas with a nonsexual technical
restoration prompt, preserving existing tattoo shapes and SEARCH & DESTROY
lettering. Service again rejected the generated output (sexual); request ID
9623d88c-f2a4-44aa-ac83-dea47e1aefe8. No image returned or imported. Exact prompt,
error, prior notes and approval receipts are private under experiments/
rollins-skin-retry-20261028/. Six current/shared reviews reconciled through live
API; all31candidate metadata/PNGs, requests and model-view state verified exact.
No restart, new provider, game install, publication or approval of unseen skin.
Only remaining pilot art gate: generate and owner-review Rollins skin/tattoos.
Bulk method remains provisional. Source report: research/rollins-skin-retry-20261028/.

**Wave four,2026-10-28:** owner accepts Nyne/Trejo, requests Redman headwear gap,
Rollins missing body detail, and Blaze head/palette rework, then a bulk method
once all five are accepted. Nyne/Trejo exact v3 bytes retained and visually
approved from that feedback; no face/channel/game/selection flags inferred.

Redman v3 broad eye/mouth/nipple holds accidentally excluded two complete
headwear strips and part of a white panel; Blaze had a small held cap corner.
Actual cloth UV masks minus guarded other-material coverage recover saved raw
v3 detail locally: Redman39,119changed/39,200safe px, Blaze4,707/4,720.
All nonmask pixels and alpha are exact v3. No new generation needed for these.
Blaze's saved viewer right was published v1, explaining its unrestored head and
vibrant old body despite v3 existing. New right captions show revision ID/status
and warn when a newer active restoration exists; manual baselines stay supported.

One built-in Rollins body attempt was output-moderation blocked; exact prompt,
error and request ID retained privately. A distinct clothing-only request
succeeded with all head/skin/tattoos excluded from its input/edit scope. New v4
restores trousers/boots under actual cloth UVs and source-palette matching:
943,831changed/951,008safe pixels, all other v3 pixels and alpha exact. His head
is retained restored; body skin/tattoos are STILL Faithful HD, incomplete.
No blocked body output imported and no alternate generation service used.

| Fighter | Current right revision | State |
|---|---|---|
| Nyne |r-c781fcc1ff7e43e9|Owner visually accepted; unchanged|
| Trejo |r-a41e97bb2dc3445f|Owner visually accepted; unchanged|
| Redman |r-615ab80f98c34738|v4 visually approved; unchanged|
| Blaze |r-75cda6b939fc4c88|v4 visually approved; unchanged|
| Henry Rollins |v6 r-5304b94c634a4fa9|Preferred v5A with chest-only correction; awaiting review|

Live8768 single writer PID23344/exec99295, same isolated source/profile.
31candidates/27live request records,5models,17archived old choices. Twelve
current/shared reviews reconciled before the Rollins clothing addition; exact
old notes in before-workshop.json and before-clothing-workshop.json. Five more
old revisions archived reversibly; every prior PNG/ID/prompt/parent retained.
Shared stale face-protection guidance updated to the newer likeness-preserving
head authorization. Cameras, left choices, lighting/groups and active fighter
preserved; only Redman/Blaze/Rollins right choices changed. No server restart,
forced tab reload, game install or publication. Public0.1 stays immutable.

83tests+15subtests,8Node tests and JS syntax pass. Five live PNG hashes, exact
alpha and embedded GLB RGBA verified; old28candidate files/metadata and requests
retained. Browser visual check remains blocked by URL policy; no bypass.
Private prompts/raw/recipes/masks/receipts/backup and review index:
workshop/experiments/fighters-wave4-20261028/. Source report/recipes:
research/fighters-wave4-20261028/. Bulk guide/template in docs/ is explicitly
DRAFT until the owner accepts a Rollins regional body result.

**Known-good publication:** HD Fighters0.1(beta),0.1.0-beta.1, published2026-10-26
via Cloudflare immutable object and DefJamFFNY-mods PR6; signed catalogue rev6,
workflow40453784754. Three2048RGBA atlases: Blaze/Nyne Rich Original Detail v1,
Trejo Source palette. ZIP19,432,340B,6files, SHA256
bcba0164c1821f4121bba1089e806db4bf7111961a68cbef647d1c2991dfc62a.
Owner reported successful pack playtest2026-10-27, permitting continuation;
that does not verify later head/restoration revisions. Publication recipe:
research/hd-fighters-beta-20261026/README.md. No new release requested now.

**Other work:** menu authoring remains on its separate original-checkout branch;
its prior review/registration work and private experiment archives are unchanged.
Detailed earlier status is archived unchanged under ignored docs/worklog/
fighter-progress-before-wave4-20261028.md. Source publication previously recovered;
current fighter continuation commits remain local until Vlad requests a push.
The authoring repository is vyanhursky/DefJam-Modding-Tools; runtime/loader/setup
remain in DefJamFFNY-recomp with the frozen compatibility snapshot.

## Decisions

- 2026-10-29: owner prefers v5A and asks for chest skin/tattoo correction. Limit
  child to model-space chest plus its separate UV emblem; retain v5A elsewhere.
  Use successful tattoo edit and frequency-calibrated prior material detail
  after direct chest-skin rejection. Preference is not new-child approval.

- 2026-10-28: owner authorizes regional studies and different approaches. Compare
  localized tattoo interpretation against source-contour ink/skin detail. Adopt
  only source-letter-held drafts; keep unfaithful decal/emblem interpretations as
  studies. Regional generations succeeded; previous whole-atlas block is history.

- 2026-10-28: owner explicitly approves everything except the unfinished Rollins
  skin/tattoos and requests a new built-in attempt. Record whole-draft approval
  for Redman/Blaze, component acceptance for Rollins; preserve all approved art.
  The retry failed at service output moderation. No returned image means no new
  revision, generation-complete claim or bulk-calibration signoff.
- 2026-10-28: exact Nyne/Trejo v3 visually accepted by owner; keep bytes. Rework
 remaining three locally. Bulk calibration is conditional on all five passing.
- 2026-10-28: repair overly broad protection holds by material geometry, reusing
 existing raw detail. Preserve accepted areas exactly; never copy pilot UV
 rectangles as universal fighter masks. Distinguish enlargement from restoration.
- 2026-10-28: reconcile stale current/shared notes through the live API with exact
 private backups and review versions. Archive history, never remove art. Show
 actual displayed revision IDs and warn on older saved comparisons.

- 2026-10-28: Vlad requests face/hair/head/headwear restoration on all five,
  slightly more realistic skin/hair, source-matched clothing color and cleanup.
  Use original diffuse palette/low-frequency shading as authority, retain fine
  generated texture and existing skin match, and apply cloth correction after
  head assembly. All new art stays as unapproved child revisions.
- 2026-10-28: Cleanup is reversible review-tag archiving, with default pickers
  hiding archived choices and an explicit Show archived revisions control.
  Keep published0.1, approved/selected and saved comparisons; preserve all PNGs,
  notes, prompts, IDs and lineage. No new schema or destructive asset migration.
- 2026-10-27: Next fighters are Redman and Henry Rollins. Owner prioritizes
  body/face color matching, face/headwear restoration and tattoo/clothing final
  review for the original three. This explicitly permits targeted face detail
  changes while locking likeness/proportions/expression. Keep new drafts and
  0.1 separate. Rollins service rejections are retained as blocked attempts;
  do not substitute artwork or change generation service without authorization.
- 2026-10-27: Owner confirmed no unsaved browser notes and requested reconnect.
  All recorded baseline hashes match the current corpus. Use an explicit backed-up
  schema1 binding migration receipt v1; preserve original reviews/candidates/requests,
  cameras and workspace path. No paired skin UV seam exists for Blaze in this
  decoded model, so his color pass reports palette-only matching. Derive other
  masks/paired guards from each fighter's own geometry, without a guessed seam.
- 2026-10-27: Vlad reports the published HD Fighters 0.1 beta looks great in
  playtesting and lifts the hold on fighter work. Continue the same three and
  expand to a small next batch. Keep 0.1 immutable and distinguish this reported
  pack playtest from itemized authenticity/face/channel review. Requested next
  fighter names and existing-fighter priorities before generating new artwork.
- 2026-10-26: Vlad authorized packaging the existing three-fighter pilot as
  HD Fighters 0.1 (beta), uploading to Cloudflare and registering with the mods
  catalogue using the HD-Menu workflow. Use SemVer `0.1.0-beta.1` on the testing
  channel; ship Trejo Source palette and Blaze/Nyne Rich Original Detail v1,
  preserve reviews, and defer new revisions until his Trejo playtest. Beta
  publication is separate from stable art approval. No extra aliases are added
  without observed runtime evidence; the three canonical IDs match the dump.
- 2026-10-16: Vlad approved setting up this dedicated repository and will resume
  texture/model review afterward. Initial remote is private and code-only.
- Authoring lives here; runtime/mod-manager/setup stay in the recomp. Its shared
  HD core remains a frozen byte-identical snapshot. One owner for new core work.
- Existing private data stays in place. Preserve IDs, hashes, review versions,
  schemas, relative image paths, browser origin and single-writer lock.
- 2026-10-16: Vlad requested Face, Pants and Shoe detail presets and confirmed
  publishing the viewer source. Added body-scaled, aspect-aware synchronized
  crops. Source-side skin/seam correction is proposed for owner review; current
  pixels and art approvals stayed unchanged at that stage.
- 2026-10-16: Vlad approved the deterministic Trejo color trial using existing
  v4 pixels. Retain two strengths as child drafts, keep face/alpha/other materials
  exact, guard only proven neck UV edges, and preserve all old reviews. Suggest
  Source palette for visual review; no automatic approval or rollout to others.
- New art is Rich Original Detail only; older stylized drafts remain history.
  Faces/protected pixels/alpha stay unchanged unless specifically approved.

## Art review and technical limits

Only Rich Original Detail for new art. Original/Faithful controls layout/palette;
likeness/proportions/expression stay fixed. Slightly more realistic face/hair is
now authorized. Uncertain tattoo/logo/script interpretations need owner review.
Trejo caption: Debbie Danielle; buckle bear left, deer right, smaller deer middle.

Five static main-outfit meshes retain original geometry/UVs/normals/materials.
No rig, animation, venue decoder, mesh reimport or game effects parity claim.
Historical three-fighter GLBs passed Khronos with0errors/0warnings; recent
five-fighter checks verify pixel embedding/identity, not native Blender import.

## Validation and handoff

1. Keep current writer live at http://127.0.0.1:8768/model-viewer. Source is the
   isolated codex/hd-fighters-beta worktree; exact paths/command in ignored
   .local-handoff.md. Original menu checkout source remains unchanged.
2. Owner saves browser notes, refreshes and presses Latest restoration for
   Redman/Blaze/Rollins. A page already open can flush its old saved choice on
   reload; use the revision ID/Older texture notice to verify the actual draft.
   Do not force reload or discard drafts. Concurrent notes cause409, not data loss.
3. Review Rollins v6 (Latest restoration) at Chest detail versus preferred v5A.
   Tattoo is newly restored; skin uses finer prior generated material detail
   after direct anatomical crop failed. Check oval/strokes/lettering, grain scale
   and joins. All v5A outside chest and four other fighters stay exact. Freeze
   bulk calibration only after the owner accepts the new chest/body result.
4. Private experiment has before-workshop/models, before-clothing backups,
   assembly/import/verification receipts, immutable prompts/raw and frozen
   processor versions. Show archived revisions recovers earlier comparisons;
   removing archived in2D restores a draft. No old art was deleted.
5. Continue targeted revisions from exact current parent hashes; after all five
   pass, freeze private calibration/reference manifest and finalize docs/
   fighter-restoration.md + prompts for a small new batch. Publish only on a
   separately requested versioned release;0.1 remains the playtested baseline.

Checks: PYTHONPATH=src <tools-venv>/bin/python -m pytest -q;
<bundled-node> --test tests/*.test.mjs; --check model_viewer.js;
python scripts/check-source-tree.py. Source-only staging/dry-run before commit;
never track private images/models/review JSON. AGENTS/CLAUDE must match.
