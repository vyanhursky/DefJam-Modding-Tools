# Def Jam Modding Tools — progress and handoff

## Current status

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
| Redman |r-615ab80f98c34738|v4 headwear repair; needs review|
| Blaze |r-75cda6b939fc4c88|v4 restored head/source palette + cap repair; needs review|
| Henry Rollins |r-0ca085cea9db4beb|v4 head + clothes; body skin/tattoos blocked/incomplete|

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
DRAFT until remaining three and all intended material coverage are accepted.

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
3. Review repaired cap/panel/strips, Blaze likeness/skin/clothes/neck and Rollins
   trouser/boot detail. Nyne/Trejo are held accepted. Rollins skin/tattoos remain
   a service blocker. Do not claim all five complete or freeze the bulk recipe.
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
