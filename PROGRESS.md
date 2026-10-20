# Def Jam Modding Tools — progress and handoff

## Current status

- 2026-10-20 D166/UI–D167/UI — Transition v4 CONDITIONAL; Story phone v1 IN REVIEW.
  Owner likes ladder art; full approval pending native moving-pan playtest.
  Freeze56files/10IDs; catalogue333pins/90reviewed IDs(72approved+8Modeconditional
  +10transitionconditional). No transition registrations/pack changes; bitmap9
  stays Faithful-only. Leave launcher-redesign game running; no launch/stop.
  Phone two native tiles, one built-in call/118historical; fine casing L only,
  exact LCD/branding/keycaps/alpha136..255/UVguards/padding. Wide studies extend
  identical native outer RGBA row profile, keep native device scale through32:9.
  Phone UNAPPROVED, notcatalogued/exported/installed. Offstagepart2/live text
  and actual clipping require game checks. Review51738 phone first with native/
  Faithful/RGBA/alpha,4backgrounds,3modes,5layouts. Browser controls pass,nooverflow
  at662px/zeroerrors; screenshot in private batch.333pins/1,725priorPNGs exact,
  22focused game-side tests pass. Extras stays approved, separate9tile export
  ready/uninstalled. Existingpacks/defaults/8768writer/17candidates/Trejo unchanged.
  Source bundle research/menu-ui-story-phone-20261020/; private additive archive
  <data>/scratch/menu-ui-story-phone-v1-transition-conditional-20261020/.
  Next: phone feedback, then venueframes/Start/support art after mapping;
  native transition and phone checks when serial game testing available.
  Historical blocks below.

- 2026-10-20 D163/UI–D165/UI — Extras APPROVED; fire-escape v4 IN REVIEW.
  Six Extras studies/nine source IDs/51newpins; game catalogue277pins,80IDs
  (72approved+8conditionalMode). Separate9-tile4xexport pixel-identical,notinstalled.
  Owner says leave launcher-redesign game running; no further game launch/stop.
  Transition ten-tile texel reconstruction,11new builtin calls/117historical;
  rejected coarse material/framing retained. Source-guided bridges plus v4
  L-only contrast matching; original/restored center,tilealpha/guards/padding
  exact. Bitmap9 placement differs from texel reconstruction; keepFaithful-only
  and defer actualpan/geometry/wideregistration. Alltransitionart UNAPPROVED.
  Review51738 first:5aspects/play/scrub/wipe/bounds/bothjoins; browser30states/
  3joinpairs pass,nooverflow/zeroerrors. 1,445oldPNGs/277pins exact,22focused
  game-side tests pass. Existingpacks/defaults/8768writer/17candidates/Trejo
  unchanged. Private archive menu-ui-transition-v4-extras-approved-20261020;
  source recipes/prompts/review in research/menu-ui-transition-20261020/.
  Next: transition art feedback/refinement, then guarded livepan/bitmap9 checks
  when serial game testing is available. Old23-source shortlist now19; Story
  phone/venueframes/Startgraphics remain. Historical blocks below.

- 2026-10-20 D161/UI–D162/UI — RESTORATION RESUMED explicitly by Vlad.
  PR62 already implements HD/wide menus and contains PR73's settings fix;
  combined toolkit dd63e17. Owner playtest: menus/ultrawide look good.
  New Extras batch: six unapproved studies over nine tiles (five generated
  papers plus Faithful-only ribbon); 106 historical imagegen calls. Native
  alpha/graphics/folds/UV padding/tile guards protected; at most four RGB levels
  of fine detail. All 1,314 prior PNGs/226 approved pins unchanged. Browser24
  reference/channel cases and30 five-aspect placement pairs pass. Review51738.
  Game-side22 focused tests/226 artpins pass; new private overlay185files,
  199,746,134bytes. No runtime changes in this iteration.
  Existing tested packs, 8768 writer and17workshop/Trejo candidates unchanged.
  Fire-escape transition: ten trans/t1 tiles, continuous master needed; no fix
  delivered. First guarded32:9 probe missed actual pan, saves restored. Other
  checkout's game active; owner asked before closing it for serial checks.
  Source recipes/prompts/review: research/menu-ui-extras-20261020/. Private
  overlay <data>/scratch/menu-ui-extras-v1-20261020/; old paused full snapshot
  immutable. Next: Extras feedback and pan measurement/restoration; Story
  phone/frames/Start graphics queue remains. Historical blocks below.

- 2026-10-19 D157/UI — RESTORATION PAUSED at owner request until credits return.
  Published source-only draftPR1(initialcommit3b0a0a2);gamehandover draftPR62(a130cfe). Remoteheads verified;14game focusedtests/226artpins and451game/319tools sourcechecks passed.
  Do not generate/repaint or advance Extras/phone queue. Engineering handover:
  game repo docs/menu-ui-modpack-handover.md;71sourceIDs(63approved+8conditional),
  226pinnedartfiles/12scopes,101historicalcalls. Native-shaped sparse testpack first,
  widescreengeometry/UV/scissor separately. Brandingv2approvedrawcanvases need
  native-shape registration;do not use unapproved old source-safe alternate.
  Fullprivate snapshot <data>/scratch/menu-ui-restoration-paused-20261019/
  session/pilot-v1,manifest-bound. Existing8768writer/17candidates/Trejo untouched.
  Source-only recipes/prompts/reviewcode preservedin research/menu-ui-pilot-20261017;
  publicbranch codex/menu-ui-art-source;gamerepobranch codex/menu-ui-modpack-handoff.
  Art/arrays/reviewJSON/captures staylocal. No newgeneration/import/install/game/
  build/runtime change. Nextagent implementsplaytestpack;restoration resumes only
  onVlad's explicitrequest. Previousstatusblocks beloware historical.

- 2026-10-16: owner-approved Trejo v4 color pilot completed. Two new unapproved
  child drafts: Gentle r-8125b0d8196d4f61 and Source palette r-342bd7dadb964b67.
  Original v4 and all 11 prior candidate files/records/reviews preserved;
  13 total candidates, 13 imagegen requests unchanged, zero queued.
  67 tests +12 subtests pass. Browser Face/Chest, rear/arms, source comparison
  and studio checks pass; zero console errors. Source palette visibly reduces
  the neck color break; requires owner review, no game installation/acceptance.
  Recipe/masks/input/processor hashes and pre-import review backup retained in
  private experiments/trejo-color-v4-20261016-202427/. No new imagegen call.

- 2026-10-16: verified model viewer source is on origin/main at e938889; all
  three CI platforms passed. Added Face/Pants/Shoe detail camera presets; all
  nine fighter/preset combinations visually checked in the live browser, with
  synchronized framing and saved Nyne shoe view verified after reload.
  56 tests + 12 subtests, JavaScript syntax and source/whitespace checks pass.
  Investigated owner-reported warm body/face seam; see docs/color-preservation.md.
  This investigation led to the subsequent Trejo pilot above.

- Standalone version 0.1.0 established from DefJamFFNY-recomp `f71ab64`.
- Repository: https://github.com/vyanhursky/DefJam-Modding-Tools (private).
- Local Python package/CLI/resources, prompts, documentation, focused agent
  instructions, source hygiene and three-platform synthetic CI configured.
- Live gallery/model viewer now runs from this checkout at 127.0.0.1:8768.
  Existing private corpus, reviews, candidates and model caches stay in place.
- 56 tests + 12 subtests pass in the final checkout and an independent fresh
  clone. Installed wheel imports/resources/browser preview also pass.
- Real-workspace compatibility: catalog/details equal, seven GLBs byte-identical
  (three original/faithful pairs plus Trejo v4), selected pack keys/images/channel
  policies identical. Review/camera files byte-identical immediately after
  cutover; all 11 candidate hashes match. Browser confirms v4 and saved notes.
- Recomp retains frozen offline HD setup helpers and runtime/mod-manager work;
  authoring copies are retired there. Its focused HD/setup/pin/agent checks34/34.

## Decisions

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

## Art review

The fighter pilot (Blaze, Nyne, Trejo) retains13drafts plus4menu trials,17workshop candidates total. The13fighter drafts comprise11imagegen and two deterministic
color trials;13imagegen request records, zero queued. Wide-art drafts are separate private experiments. Trejo A source-guided v4 `r-a74be693951f4617` awaits
owner review of tattoo script/stroke paths, animal/tree/buckle placement and
skin seams. Original script guidance: "Debbie Danielle". Exact exterior/face/alpha
checks do not establish interior authenticity. No art is automatically approved.

## Technical limits

Three static main-outfit fighter meshes; original geometry, UVs, source normals
and material partitions. Game lighting/reflections and sparkle effects are not
reproduced. No rig/animation, venue decoder or game mesh replacement yet. GLBs
validate in Khronos; Blender itself was unavailable for a native import test.
Optional legacy auditions retain Windows font / isolated CUDA requirements.

## Validation and handoff

Read AGENTS.md, docs/WORKFLOW.md, docs/texture-workshop.md and docs/model-viewer.md.
Resume the existing session with `.venv/bin/defjam-tools serve` from this checkout;
local.json (ignored) contains exact machine paths. If the server is already live,
use its browser or `workshop import --server http://127.0.0.1:8768`.
Live owned PID10791 / exec54009; verify current ownership before stopping it.
Machine-specific paths/backup location are in .local-handoff.md (ignored).

A metadata backup was written under the private workspace's backups/ before
cutover. Migration probes only approved/exported a disposable copied workspace;
owner review data and all production approval flags were preserved. No art was
generated, installed or published. No game runtime/save/installer behavior changed.
The port's frozen core hashes are recorded in provenance.json and in its
config/hd-tools-core-snapshot.json; deliberately review future synchronization.

Next: compare Trejo color-trial Source palette (r-342bd7dadb964b67) with parent
v4 (r-a74be693951f4617), Gentle (r-8125b0d8196d4f61) and Faithful HD, using Face/
Chest presets and unlit RGB. Review/notes still bind to the selected right draft.
Model tab9 is left v4/right Source palette; the owner's other model tab is intact.
Private experiment experiments/trejo-color-v4-20261016-202427/ has receipt.json,
verification.json, import-receipt.json, recipe text, masks and review-backup/.
No art is approved/selected or installed. Tune after owner feedback, then in-game
acceptance; extend to Blaze/Nyne only after their mask/seam checks. See
 docs/color-preservation.md for exact parameters and CLI. Keep source changes in
this repo; the recomp's frozen HD setup helpers are unchanged.
Run focused tests for changes; keep source and private artwork backups separate.

Windows CI initially exposed default-codepage decoding of UTF-8 review JSON.
All implicit module text reads now specify UTF-8; a simulated cp1252 roundtrip
checks non-ASCII notes and queued prompts. Linux/macOS initial CI passed; the fix is covered by the three-platform CI
regression suite. Source checkouts use LF to keep vendored hashes stable.
