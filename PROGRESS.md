# Def Jam Modding Tools — progress and handoff

## Current status

**2026-10-29: Starks badge fixed; 20 more drafts imported (16 new fighters + 4 costumes).**
Source 65 outfit catalogue validated; live writer still 45 pending saved-notes confirmation.
Owner approved the other 19 prior drafts, exact displayed IDs checked and reviews
updated with optimistic versions/private backups. Starks's accepted components
stay exact outside lettering. New child r-aeba1996ca364784, SHA256
82dc1699d7e0c0c715572307ba3cd2902e48262db09a66e245c4a7e7e8a7ecc5,
5016 changed pixels, exact full alpha/outside mask. CITY/POLICE final text checked;
child unapproved/unselected/not game verified. Earlier request/notes preserved.

New 16: Cruz, Meca, Kimora, Shawnna, Cindy J, Carmen Electra, Lauren, Teck, Dan-G,
Baby Chris, Ghostface Killah, Joe Budden, Jervis, Lil Kim, Manny, Prodigy. Owner
explicitly authorized filling missing slots with alternate outfits: D-Mob B/C,
Blaze B, Sticky Fingaz B.65 supported outfits cover 61 distinct fighters. New 20
remain unapproved/unselected/not native verified/outside public 0.2. Three agents
assisted mapping/decoder investigation, disjoint builtin generation and final QA;
root owned code, tests, assembly and all live API writes/cutover.

All 20 raw outputs are 1254 square built-in edits; final 2048 RGBA, calibrated Rich Original Detail.
Face/hair/headwear/skin/clothes/shoes/jewelry restored, both skin and cloth source
palette matched.215 named final crops checked:211 detail-present requiring review,
4 pending-held. Prodigy uncertain tattoo paths stay source-contour locked, generated
fine ink residual only; no guessed words adopted. Four low-change components are
exact flat black source material (Meca/Cindy/Carmen/LilKim), not missing detail.
Cruz/Meca chains/cross, Kimora cross, Joe crest/Jervis button zero-UV padding
finished; never override mapped holds or infer runtime non-use. Neighboring
editable feather edges can change<= 1 RGB level, not byte-identical claims.

Jervis initial mirrored final E fixed using already-generated correct POLICE
lower-band lettering:2255 pixels changed, every other draft pixel/full alpha exact,
own palette/ornament retained. Final v3 PNG equals inspected v2 with complete
processing provenance. Cindy actual four buttons, Teck three crosses, Manny actual
laces and BLAZE/31 all copies checked after palette/masks. Original prompt wording
immutable when later feature labels/bounds corrected. Tiny watch/ID/tattoo details
remain interpretations/source-held, owner review needed. No new approval inferred.

Decoder 2 adds verified direct index layout, validating first VB count/pointer and
all bounds/strip winding. Existing decoder 1 caches remain readable.45 adopted model
arrays and files untouched; source vertex/UV/normal/color/index arrays compared
exact. New 20 have 1000 retained primary-atlas mesh parts. External tape near-mouth
meshes omitted for Kimora/Cindy/Carmen/LilKim; Shawnna primary A406 mouth auxiliary
also explicitly omitted due unresolved UV/shader semantics. Not disposable/non-use
claims. Shared art untouched. No normal synthesis: Shaniqua still unsupported.
Suspect is playable but not adopted. Injury alternatives remain original; native
damage transitions unverified. Studio/hair transparency remain approximations.

Exact audited hair, Cruz alpha-skin and narrow mixed-alpha RGB regions enabled;
full source alpha, all mapped holds and seam cores exact. Small<=2 native-texel
UV overshoots rasterize with canvas clipping only; original UVs untouched. Local
ABM_BLEND source state enables blend despite missing_ALPHA label. Parent shader
inheritance remains approximate.113 pytest tests + 21 subtests pass. No JS/UI changes.

All 282 pre-import candidates/files retained;
302 total at import verification (includes unrelated customization).
All prior reviews/session/requests/cameras/choices exact;30 requests. One writer,
same http://127.0.0.1:8768/model-viewer. No browser policy bypass/fresh browser visual
test; source/final crops and CPU UV projections inspected, API images/offline GLB
embedding checked separately. Do not claim live65GLB checks until cutover verified.
Private final plan-v6/stages-v6, exactprompts/raw/frozenprocessors/receipts/backups
and independent reports live under experiments/fighters-batch60-20261029/.

Bonecrusher NEXT test-pack playtest reminder unchanged, native verified false.
Mack10/Scarface lettering remains reference-needed. Warren complete-back-P child
still pending. Original five/public 0.2 immutable; no pack/manifest/install/runtime/
settings/save/frozen snapshot changes. Source commits local until push requested.

## Published baseline

- HD Fighters0.2.0-beta.1: testing/prerelease, min game0.12.1. Only approved five:
  Blaze/Redman v4, Nyne/Trejo v3, Henry Rollins v6.2048 RGBA, png_mips=channels.
  Exact revisions/hashes: research/hd-fighters-0-2-beta-20261029/selection.json.
- ZIP34,424,972B; unpacked34,417,307B;8files; SHA256
  1a10e9a714c0c2df00e6c68203213381b1cc628622ce14ae3eb20187c78a8561.
  Immutable Cloudflare size/hash/206range verified. Catalogue PR8 merged as
  d552860160f3ba72e30358f39ca45ad8346d9344; protected publish40914786807 succeeded,
  signed catalogue revision8; existing approval/signing protections retained.
- Released0.12.1 helper/package checker agree; released key verifies public index;
  fresh disposable install exact; stable channel excludes beta; sentinels intact.
  Owner playtested0.1 successfully. Native0.2 acceptance still pending. Neither
  subsequent ten-fighter batch is included. No approved five bytes changed.

## Decisions

-2026-10-29: owner approves19of previous 20; Starks CITY POLICE lettering only
  needs repair, keep other accepted parent pixels exact. New child needs review.
-2026-10-29: next 20requested; Santos/Xzibit/Banner output moderation rejections
  saved, no retries/provider switch. Owner explicitly chooses alternate outfits
  for shortfalls.16 new fighters+4 real costumes, never disguised damage/alias copies.
  Prior House/Bo/LilFlip failures remain held. Blaze C injury copy excluded;
  Crow B invalid normals excluded. No unsupported output counted as restored.
-2026-10-29: direct-index decoder 2 and exact material/UV permissions are narrowly
  source-audited. Preserve old caches/schema/source arrays. Explicit mouth-tape
  omissions remain limitations; not proof unused. No synthetic normals adopted.
-2026-10-29: source-contour ink for uncertain Prodigy art, strict zero-UV feature
  padding where justified, exact alpha/holds/seams. Final semantic crops beat
  global change counts; tiny metadata/word claims remain qualified.
- Owner wants Bonecrusher reminder at NEXT pack preparation, not a timed alarm.
  Native verification remains false. Keep public 0.2 exact and no new release here.

## Validation and evidence

-113 pytest tests + 21 subtests pass; new index bounds/tape/blend/compatibility,
  overscan/hair/mixed-alpha guard tests. No runtime/frozen snapshot changes.
-20 finalPNG hashes, source alpha/declared holds/paired seam cores, geometry and
  frozen processing hashes exact.215 namedcrops,40 RGBUVFront/Back,20 comparisons
  reviewed by independent agents. No new browser visual test under prior policy.
- Four low-change components are exact black source, guards not weakened. All
  1000 retained newparts bind own main/costume atlas; omissions explicitly recorded.
- All pre-import images/metadata/reviews/session/requests/views retained. Prior
  archive:docs/worklog/2026-10-29-before-batch60.md (ignored), exact private backups.
- Source hygiene: 540 tracked text files, zero policy failures; mirror/diff checks pass. No art,
  models, reviews, raw/frozen private processors or generated game code in Git.
- Latest pre-cutover verification: 331 candidates (additional unrelated art after
  our import), all earlier reviews/session/requests/cameras exact. All 20 live PNG
  hashes and offline GLB embedded RGBA/revision IDs exact; live Starks PNG/GLB exact.
  New 20 remain unapproved/unselected/not game verified. Live model selector still
  45 until saved-notes confirmation and same-origin cutover. No second writer.

## Handoff

1. Source checkout /private/tmp/defjam-tools-hd-fighters-20261026, branch
   codex/hd-fighters-beta. Current writer originallyPID59111/exec8401, origin8768.
   Check .local-handoff.md for latest PID/status before action. Never two writers.
2. Final 20imported, IDs/hashes/paths in experiments/fighters-batch60-20261029/imports.json.
   Canonical selection plan-final-v6.json/final-stages-v6.json. Review links:
   /Users/vlad/Code/defjam-data/hd-work/texture-workshop/experiments/fighters-batch60-20261029/review-index.md
3. Saved-notes confirmation requested before restart, still pending unless later
   cutover receipt says complete. Preserve exact current workshop/model-view bytes,
   validate schema/corpus/candidate/model pins, stop only dedicated writer, restart
   same8768/profile and verify65live PNG/GLB IDs/RGBA plus old reviews/views exact.
   New source catalogue validated offline. Never bypass browser URL policy.
4. Starks exact CITY/POLICE child r-aeba1996ca364784 is already imported. Review
   Latest after saving notes; other 19approved. New 20allpending owner review.
   Shared/unresolved mouth tape/damage/hair shader appearance needs native checks.
5. At NEXT HD Fighters pack preparation remind Vlad to playtest Bonecrusher and
   read fighter-feedback-20261029/next-test-pack-checklist.json. Keep nativefalse
   until tested. Mack10/Scarface words need references, Warren latestP pending.
6. No publication/install requested. Public0.2 immutable, source push only on
   request. Private plans/images/notes and unrelated customization work retained.
