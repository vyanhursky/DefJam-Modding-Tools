# Def Jam Modding Tools — progress and handoff

## Current status

**Wave three ready for review (2026-10-28):** owner expands head/face/hair/
headwear restoration to all five, requests slightly more realistic skin/hair,
original clothing palette, and permits cleanup. Five new built-in imagegen head
edits succeeded, including Rollins. v3 drafts combine .8-strength palette-held
head detail and source-guided cloth/shoe/headwear Lab correction, preserving
matched skin outside the head patch, alpha and held eye/mouth/tattoo tiles.
Median cloth chroma source/before/after: Blaze12.17/15.10/10.85,
Nyne10.02/11.70/10.12, Trejo8.37/17.02/9.03, Redman7.00/10.71/7.83;
Rollins0.59/0.59/0.59 (clothes were already original). All safe cloth coverage
uses source triangles minus other-material coverage plus1sourcepx guard;
Blaze/Nyne shared UVs remain held to preserve skin. No geometry/UV changes.
Live at8768, PID23344/exec99295,28candidates/24request records.12older fighter
revisions soft-archived via tags; all PNGs/notes/parents/hashes retained,0.1 and
saved/approved/selected choices kept visible. New Show archived revisions and
Latest restoration controls are served without a restart or forced tab reload.
81tests+12subtests/8Node checks and JS syntax pass; five new PNG hashes and model
GLB endpoints checked; saved cameras and old notes intact. Browser visual check
remains blocked by URL policy. New drafts unapproved/unselected;0.1 unchanged.
Exact prompts/raw/reports/recoverable archive receipt: private workshop
experiments/fighters-wave3-20261028/; source research/fighters-wave3-20261028/.
Next: owner saves any notes, refreshes viewer, presses Latest restoration for
all five, and checks skin/hair/headwear, less vivid clothes, seams and likeness.

- 2026-10-28: owner-requested viewer restart completed at127.0.0.1:8768.
  All five model exports, viewer scripts/style and23drafts respond; saved review
  and camera JSON hashes unchanged. Single writer PID23344 / exec99295.
  Same five-fighter source worktree/profile; no art, install or publication change.

**Wave two ready for review (2026-10-27):** owner selected Redman and Henry
Rollins, prioritizing body/face color matching, face/headwear improvement, then
final tattoo/clothing review on Blaze/Nyne/Trejo. Explicit face-detail exception
recorded in AGENTS/CLAUDE; preserve likeness, proportions and expression.
Gallery recovered at 127.0.0.1:8768 after owner confirmed no unsaved browser notes.
Versioned corpus rebind backed up metadata and preserved workspace path, all17
old candidates, old reviews/requests and cameras. Current workspace has23drafts,
19requests (including2new blocked Rollins calls), five main-outfit models.
New drafts: Blaze/Nyne Source palette + face/headwear children; Trejo Source
palette face/headwear child; Redman Rich Original Detail with held face/alpha
and source-palette assembly. Rollins original/Faithful model available; both
new imagegen attempts rejected by service output moderation, no substitution.
74tests +12subtests /8Node checks pass,16model GLB HTTP endpoints and6candidate
hashes verified. Browser visual checks blocked by URL security policy; no bypass.
Private inputs/prompts/raw/recipes/reports retained under workshop experiments/
`fighters-wave2-20261027/`; source report/recipes in research/fighters-wave2-20261027/.
No new draft approved/selected, no game install or new catalogue publication.
Public0.1 remains immutable. Next: owner reviews Face/Chest/Back/Belt/Pants/Shoe
views, likeness/headwear, skin joins and original tattoo/script/material fidelity.

**Fighter continuation (2026-10-27):** Vlad reports HD Fighters 0.1 looks great
in his playtest and authorizes continued work on Blaze, Nyne and Trejo plus more
fighters. The playtest gate is satisfied at pack level; the report did not name
which fighters/outfits were exercised, so no per-revision face/channel/authenticity
flags were changed. Preserve public 0.1 and its exact three selections as the
known-good comparison baseline. Prepare targeted child revisions and the next
small fighter batch; names/priorities were then supplied (see wave two above). See
`research/hd-fighters-beta-20261026/NEXT-BATCH.md`. The gallery was subsequently recovered with a backed-up corpus rebind after
the owner confirmed saved notes; see the latest wave-two report above.

**HD Fighters beta publication (2026-10-26):** owner requested a public first
fighter pilot before further revisions. Separate source branch
`codex/hd-fighters-beta` preserves the ongoing menu branch. Recipe/pins and
publication evidence: `research/hd-fighters-beta-20261026/README.md`.
Three existing 2048px atlases: Blaze/Nyne Rich Original Detail v1 and Trejo v4
Source palette trial; faces/material alpha exact, no new generation or review
approval. Cloudflare immutable ZIP is 19,432,340 bytes, six files, SHA-256
`bcba0164c1821f4121bba1089e806db4bf7111961a68cbef647d1c2991dfc62a`.
Catalogue PR #6 merged; protected scan/sign/deploy succeeded, live signed
catalogue revision 6 verified by the exact released v0.12.1 helper, public
download/managed install passed with all six file hashes exact. Stable channel
correctly excludes this beta. No active game/settings/save or review changes.
Publication: https://github.com/vyanhursky/DefJamFFNY-mods/pull/6; successful
workflow run 40453784754. No publishing blockers.
Local checks: released v0.12.1 + catalogue unpackers agree, source identities
verified against dump, public full download/hash/range verified; 14 catalogue
and 67 authoring tests +12 subtests /8 Node checks pass. The owner subsequently
reported a successful pack playtest on 2026-10-27 and authorized continuation;
individual detail-review flags remain unchanged.

**Source publication restored:** GitHub sign-in recovered. Existing source-only
branches are published, including the previously blocked commits; current gallery,
navigation and census source is on the same branches/draftPRs. Artwork, index
JSON/CSV, captures and owner shortlist data stay local.

- 2026-10-20 D182–D185/UI — Separate menu-only RC2 tested on this Mac after
  optional Faithful (library unbundled).157native/164slabs/62wideentries,
  421.6MBZIP/423.4MBinstalled; all670artpins intact/zeroimggen. Actualloader4paper
  variants/8technicalIDs registered from approved exterior, originalcores exact.
  Native1v1loadingall5ratios,FFA4/menu-only/Options/Jukebox/HighScores/charDec32:9
  pass; save guardsrestore, no runtime fault checks. Nested disposableAAAfixture
  resolvesintro namecollision. Transitionblackfirsttile alsoinFaithful/original
  controls; Crib/GF/partner/Tips/3-player/team coverage andowner signoffremain.
  Diskfull recoveredbyteidentically inisolatedsave; nativeharnessAPFSclone/fallback
  tested534unitpasses(2sandboxblockedchecks rerunwithhostaccess),32skip/1slowheld.
  20run nativegallery, framebuttons/keys/zoom/fullwidth/nooverflow/load verified.
  Source research/menu-ui-native-release-20261020/, privatefullarchive11716files/
  5552616413B, manifestf93b80f023bee2b5d1e43348aa4a67327244017ad0e96f9e08d38e01054da3e6.
  Ordinarygame/save/8768workshop unchanged; no public asset upload.

- 2026-10-20 D181/UI — All7widebackgroundscenes APPROVED.70newpins/670total,
  149reviewedsourceIDs(131unconditional+18conditional), registered121/core145.
  No more new-art batch requiredforv1; held19detailIDs/shopdrafts deferred.
  Review/inventorymarksartapproved, isolatedpackintegration/nativechecks pending.
  Existing600pins unchanged; no generation/pixel/activepack/gamechange. Native
  loadingroutes/live layers, fullpan/Mode/brandingderivatives/fiveaspects remain.
  Approvaloverlay <data>/scratch/menu-ui-wide-backgrounds-approved-20261020/;
  source approvalrecipe andcurrentreview preservedinwidebackgroundbundle.

- 2026-10-20 D179/UI–D180/UI — Owner scopes first menu-mod release to mainmenus,
  approved artwork and widescreen scenery/loading; leave other review candidates
  held. Seven background drafts13newIDs through32:9,15builtin calls/162historical.
  Exact35Faithful4:3cores;Cribdoorparent469.4/reusesapprovedrightscenery; tipsv3
  both128pxjoins+Lgrainmatched. Loaderplate/tips mapped separatelyfrom portraits/
  livetext/vignette; oldMLoad dynamicvenue remainsunprovenactive. Newreview
  wide-backgrounds.html withOriginal/Faithful,5ratios,joincloseups,linkednavigation,
  Prev/Next/keys/browsernotes, linkedfrominventory/artreviews. All600priorpins/
  136approvedIDs unchanged; newartUNAPPROVED/uninstalled. Existingdetail19IDs/
  shopraws held; currentgame/packs/saves/8768/workshop/Trejo untouched. Source
  research/menu-ui-wide-backgrounds-20261020/, private additivearchive
  <data>/scratch/menu-ui-wide-backgrounds-v1-20261020/. Nativeactive loading routes,
  masks/fades/fiveaspects/fullmovingpan and priorModecondition remainreleasegates.

- 2026-10-20 D175/UI–D178/UI — Scope changes to widescreen backgrounds and
  owner-selected exceptions; stop routinepanel/button imagegen. Gym15/22
  approved127newpins/600total/136IDs,22tile4xexport exact/uninstalled. Prior16/19
  pending. Prepared30studies57sources deferred;3inflight rawshopproposals held,
  noassembly/adoption,147historicalcalls. Sevenotherplannedcalls notstarted.
  Fullimagebrowser51738/inventory.html:1323registered(115reviewed/1208outside),
  optional1834core(132reviewed/1702outside). Original/Faithful/status/customwhere
  available, search/screen/size/backgroundfilter, zoom/pan, Prev/Next/keys,
  localshortlistnotes/download. Fiveknownwidegroups10tiles; nativeuse/clipunknown.
  All1323IDs paginatedonce/28pages; comparison/mouse/arrow/shortlistreload pass,
  zerooverflow/errors.8Node+22gamefocusedtests/600pins pass. Game/packs/saves/
  8768writer/17workshop/Trejo untouched. Source research/menu-ui-inventory-20261020/,
  privateoverlay <data>/scratch/menu-ui-inventory-widescreen-focus-20261020/.
  Preserve browser selections, previousimmutablearchives and conditionalpan/Mode
  checks. No moregenerationbeforeownerchoices. GitHub sign-in recovered; source-only branch/draftPR published.

- 2026-10-20 D172/UI–D174/UI — Popup/profile15studies/22sources APPROVED.
  Frozen130newpins/473total,114reviewedIDs(96unconditional+18conditional).
  Separate22tile4xexport exact/uninstalled. Prior16/19remains pending.
  New15Gym/controlstudies/22sources pending:2restrainedpapers+13Faithful;
  complete Gymshapes50/60/64 with3narrowcompanions.2calls/144historical.
  Originalalpha/marks/UVguards/padding exact,maxRGBdelta4;473pins/2439oldPNGs
  unchanged;75isolatedaspectpairs. Review51738 nowlinkedmousewheel/drag/fit
  on105images46groups, including legacy/wipe/tallpan.60refcases/75aspects
  loaded,zerooverflow/errors,4Node+22gamefocusedtests pass. Authoring67tests
  and12subtests pass (HTTP tests retried outside restricted loopback sandbox).
  Game untouched.
  Source resources under src/defjam_tools/resources/review_navigation.*;
  recipe/prompt bundle research/menu-ui-controls-20261020/. Private additive
  archive <data>/scratch/menu-ui-controls-v1-popup-approved-20261020/.
  Native placement/clip/pan/platform validation remains pending; preserve8768,
  17workshop/Trejo and existingpacks. GitHubauthstillinvalid; commitlocal and
  publish existing branches after sign-in, then update PR62description.

- 2026-10-20 D170/UI–D171/UI — Two batches pending; popup/profile first.
  Vlad explicitly leaves the previous16-item/19-source batch for review. No
  approval/pin/export inferred; all prior pixels unchanged. Catalogue343pins/
  92reviewed IDs remains74unconditional+8Mode+10transition conditional.
  New15-item/22-source popup/profile/autosave batch: ten paper restorations,
  original-core widened profile wall, four Faithful stamps/effects.15new
  built-in calls/142historical. Native wall admitted zero generated pixels;
  source core, baked paper/emblem exact. Wide wall v3 repairs both128nativepx
  joins, then fineLcontrast match(.625left/.885right median); v1/v2 retained.
  Native UVs, header stretch, negative offsets, platform/language/live text
  remain separate. PS2 French is under PS2bkg50, GC uses A/B, Xbox independent.
  All343pins/2,044previousPNGs,22tilealpha/graphics/guards/padding,75centers exact.
  Browser60reference/channelcases+75aspectpairs loadedafterrevisit,3BG/modes,
  75%bounds,3wallversions/bothjoins,nooverflow/errors;22focused tests pass.
  All15new studies UNAPPROVED, notinstalled/exported. Phone/Extras approved
  source4xexports ready/uninstalled; ladder conditional pendingnativepan.
  Running game untouched. Preserve8768writer/17candidates/Trejo.
  Review51738: newbatch above previous16, original/Faithful/alpha/overview/
  five ratios/bothjoins/history. Source-only bundle
  research/menu-ui-popup-profile-20261020/; private additive archive
  <data>/scratch/menu-ui-popup-profile-v1-pending-20261020/.
  Next: explicit feedback on bothbatches, then bounded remaining Story/widget/
  map classification. Native validation when serial game testing available.
  Historical records below.

- 2026-10-20 D168/UI–D169/UI — Phone APPROVED; sixteen-item Menu/UI batch IN REVIEW.
  Phone frozen10files/2IDs; game catalogue343pins/92reviewed IDs(74approved+
  8Modeconditional+10transitionconditional). Separate2tile4xexport exact,
  uninstalled. Ladder v4 conditional pending native moving-pan playtest.
  Larger batch16items/19sources:3venuecards+4Startstickers restrained papers;
  6supporticons+2shadows+radialeffect Faithful-only. Two raw icon proposals
  invented dots/halftone and rejected; no pixels adopted.9new built-in calls,
  127historical. Sourcealpha/ink/geometry/UVguards/padding exact;343pins and
  1,751priorPNGs unchanged.80isolated aspectpairs retain graphic size; not
  game placements. Browser64ref/channelcases+80aspectpairs loaded,3BG/3modes,
  75%bounds,nooverflow/zeroerrors.22focused game-side tests pass. All16batch
  candidates UNAPPROVED, notcatalogued/exported/installed. Phone remains frozen.
  Leave launcher-redesign game running; no game/build/runtime/default/pack edit.
  Review51738 batch first, overview/selector/native/Faithful/alpha/wipe/5ratios.
  Artwork/history local; source bundle research/menu-ui-details-20261020/.
  Private additive archive <data>/scratch/menu-ui-details-v1-phone-approved-20261020/;
  earlier complete/Extras/transition/phone archives immutable. Preserve8768/
  17candidates/Trejo. Next: explicit batch feedback, then remaining UI
  classification beyond17-ID prioritylist; native validation when serial game
  testing available. Historical blocks below.

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

Latest wave-three handoff: source research/fighters-wave3-20261028/README.md;
private experiments/fighters-wave3-20261028/review-index.md. Same writer
PID23344/exec99295 on8768, no restart. Refresh only after saving browser notes.
Use Latest restoration and Show archived revisions; archives can be restored
by removing the archived tag in the2Dreview. All five latest v3 drafts need
owner visual/likeness/material review before any new pack. No0.1change.

Latest wave-two handoff: see research/fighters-wave2-20261027/README.md. Single
writer PID23344 / exec99295, running from this isolated source worktree on8768.
The original tools checkout/menu branch is untouched; local.json now points to
the validated current corpus. Use the isolated worktree source when restarting
so all five model IDs are supported. Machine paths are in ignored .local-handoff.md.
Backups: workshop/backups/fighters-wave2-rebind-20261027/. Do not undo the rebind
or overwrite owner notes. Review all six new drafts; Rollins generation remains
service-blocked. No automatic art approvals, installation or publication.

Latest fighter handoff (2026-10-27): owner pack playtest passed; continuation
authorized, next fighter names/priorities pending. Use NEXT-BATCH.md.
Publication handoff (2026-10-26): follow the beta publication report above
before the older session notes below. The exact private release/receipts are in
`<data>/scratch/hd-fighters-v0.1-beta1-published-20261026/`. The release recipe
needs no running gallery. At publication time port 8768 had no listener and the
old DefJamPR19-20 corpus path in local.json no longer existed; the workshop and
candidate files were intact, and baseline PNG hashes matched the currently
installed Faithful channels pack. Do not restart a server against stale paths
or overwrite browser drafts. Repair/reconnect the authoring session separately
after the owner's Trejo playtest, preserving all review JSON and candidate IDs.
The original tools checkout/menu source branch is unchanged by this isolated
publication worktree. Active game settings and save were not modified.

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
