# Def Jam Modding Tools — progress and handoff

## Current status

**2026-11-01 — CAF neck fits and retail clothing navigation.** Owner requested
closing the E/F neck gap and replacing resource-only clothing cards with the
actual game item names, colors and wearing styles. Cache decoder 2 applies the
retail default face build morph to the base face for all A–F builds. The nine
shared jaw/neck attachment positions now agree within 0.00002 source units on
E/F (previous maximum gap 0.19862); source UVs, textures and scalp are retained.
Decoder-1 caches and schema-1 outfits/inspection records remain readable.

The own-dump SODB/English locale reader maps **326 shop clothing items**, including
**123 Tops**, **1,454 colors**, **1,185 fittings** and all **4,634 combinations**.
The sidebar shows garment names plus texture IDs, then named Color → Style
buttons; the inspector mirrors those choices. Wearing styles change the actual
model, color changes retain the style where available, and raw source controls
remain accessible. Exact source names disambiguate distinct same-suffix textures;
only identical references are treated as legacy aliases. No catalogue text or
art is bundled. Left wristbands remain explicitly separate from right resources;
automatic outfit conflicts/pairing and broader grooming/jewelry names are pending.

Validation: **209 tests / 51 subtests**, synthetic malformed metadata/schema and
alias checks, all 4,634 own-dump selection/resource joins, preserved old catalogue
IDs and six mixed-outfit build compositions. Browser checks cover E/F seam close-ups,
retail search, geometry/style and color persistence, reload and A/B. The native
Story shop confirms the garment → color → fitting flow and representative labels
on a disposable guarded save, restored byte-identically. This is representative
menu verification, not exhaustive native outfit/render parity. Source/wheel
checks and the backed-up local viewer cutover preserve existing reviews, outfits,
queue records and artwork. No runtime/setup change, art approval or source push.
Machine paths, receipts, restart/rollback commands belong in ignored
`.local-handoff.md`. Next: owner review of the updated local CAF viewer; retain
milestone **v0.13.0** for any PR.

**2026-10-31 — Create-a-Fighter fitting room, local beta.** Owner requested a
customization assembly/secondary-inspection tool. The separate `caf build/serve`
commands index the own-dump parts XML and compose four source atlases from proven
FSH placement/blend metadata. Source geometry, UVs and material groups are retained;
A–F body deltas, full neck fits, accessory remaps and default facial-hair fits are
implemented without changing the existing fighter decoder/cache contracts.

The UI has a category hierarchy/search, independent equipped slots, design/color
resources, per-source immutable revisions, synchronized split or single-view A/B,
hold-to-compare, close-up/UV-derived decal framing, palettes, isolation/wireframe,
saved outfits and a hash-pinned secondary-inspection queue with conflict-safe notes.
The 2D gallery source adds an exact source/revision handoff to the separate CAF
origin; the existing live writer is preserved. The standalone CAF service reads
that workshop and its corpus; only its separate schema-1 inspection state is written.

Validation: final own-dump cache **38 groups / 879 XML entries / 5,319 texture
resources / 483 static model resources**, zero rejected mesh/build conversions;
**842/842** first-variant equip/build composition cases. Synthetic suite **198
passed / 51 subtests**; JS syntax, source policy and clean wheel resource checks
pass. Browser checks cover actual mixed clothing/shoes/hair/jewelry, named hair
palette, source C/F builds, revision selection, queue notes and outfit reload.
Existing workshop/model metadata remains byte-identical. No art generation,
approval, pack installation, game/runtime/setup change or source push.

Use [the CAF guide](docs/create-a-fighter-viewer.md) and
[assembly evidence](docs/research/caf-static-assembly.md). Machine paths/startup
and private receipts belong in ignored `.local-handoff.md`. Native outfit parity
is still pending: source A–F retail size labels, full hat/hair compatibility,
face blend-shape editing, animation and game shader effects are not claimed.
Next: owner inspection of the local fitting room, then representative native
outfit/color/decal acceptance. Any PR uses the current **v0.13.0** milestone;
keep the live review service and published art untouched.

**2026-10-31 — PR4 approved for merge.** Vlad approved the published-pack viewer
and mouse/page-size refinements and requested merging PR4 into main. It retains
milestone **v0.13.0**. Validation is 181 tests / 51 subtests plus passing macOS,
Windows and Linux CI. The existing 8768 deployment already runs the reviewed
implementation; preserve its private configuration, textures, reviews and model
history. Next: continue the owner-led revision pass through `/packs`.

**2026-10-31 — Viewer mouse controls and page sizes.** Owner requested Gallery
sizes 10/25/50/100/200 and synchronized mouse zoom/pan in Inspect. Page size is
remembered and used by the API, page counts and cross-page inspection navigation;
the API bound is now 200. A shared original-canvas camera provides cursor-anchored
wheel zoom, captured left-drag, scrollbar/keyboard synchronization and double-click
Fit across all available panes, including late-added fourth comparisons. No
review/approval schemas or image bytes changed. Owner moved current/future PRs
to **v0.13.0**; viewer PR4 is retargeted accordingly. Existing historical release
milestones below describe their original work.

Validation: focused synthetic paging/camera tests and browser checks cover all
five page sizes, actual wheel/drag input, all-four-pane synchronization and reset.
Full suite: 181 tests / 51 subtests pass with Node; a clean wheel install includes
the camera module and UI resources. Saved notes were checked before cutover;
review/model JSON remains byte-identical and old API snapshots match afterward.
Browser tests also verify two-axis fighter panning; narrow Inspect controls wrap
within their panel. Deployment retains the existing origin/private workspace.



**2026-10-31 — Published-pack texture library.** Owner requested a review pass over
current menu/fighter releases rather than the old fighter pilot. `/packs` reads
pinned immutable ZIPs, covers native/wide/supporting PNGs, and compares original,
Faithful, published and optional candidate/older-release images. Search/category/
component/status filters, gallery, shared scale/pan, source crops, RGB/alpha and
contrast backdrops support review. A separate schema-1 review store uses artifact
and PNG hashes, optimistic versions, atomic saves and browser draft recovery;
old workshop approvals, candidates and model views are unchanged.

Private setup indexes 1,522 menu native mappings (1,251 corpus references plus
271 recovered originals), 222 widescreen PNGs, and 218 current fighter mappings.
Recovered originals also have explicitly labelled Lanczos 4× preview baselines.
An older menu release is available for optional comparison. No artwork or private
index is tracked. Live cutover preserves the fighter branch's newer features;
source-only feature branch integrates current main to avoid importing dated
production history.

Validation: after integrating current main (fighter PR3), 179 Python tests /
46 subtests pass with bundled Node, including loopback auth, archive
coverage/hash/path guards, stale saves, failed-write rollback and release-scoped
reviews. Browser preview verifies real published comparisons and isolated note
persistence, synchronized pan and optional old-release/candidate loading. The live
fighter-source suite passes 133 tests / 39 subtests; old workshop/model JSON and
API snapshots match exactly after cutover. Wheel packaging/source policy pass.
Procedure: [published library](docs/published-texture-library.md).
Machine-specific source, startup command, metadata and rollback pins belong to
ignored `.local-handoff.md`. Next: use the new pass to flag revisions; no art is
automatically re-approved, generated, installed or republished.



2026-10-31: owner authorized the recommended reusable-tooling cleanup. Curated
fighter integration is delivered through PR3 (`codex/fighter-tools-cleanup`), based on `b36f78b`
(menu PR1 and authoring-boundary PR2 merged). Full fighter source history was
pushed at `d1c3de4` before cleanup. The maintained tree imports reusable source
and synthetic tests, not dated production ledgers or batch runners.

- Decoder 2, nested Story sources and decoder-1 cache reads retained. Source
  geometry/UVs/normals stay exact; tape omissions are explicit catalogue rules.
- One packaged validated inventory drives 76 preview entries, 81 atlas aliases
  and gallery filters. Compatibility FIGHTERS/PILOT imports and every existing
  source ID, alias, label, route and preview order are checked against pinned
  pre-refactor source contracts. Atlas-only aliases remain available in 2D.
- Model/gallery history filtering retains archived approved/selected and saved/
  current left/right/lane/review/parent choices. Hiding unrelated history no
  longer silently substitutes and persists another comparison revision.
- Scoped face/cloth/feature/region/palette/skin/injury operations and UV diagnostics
  are maintained libraries. Local-neural code stays experimental; default app
  adds neither Torch nor weights. Existing metadata schemas are unchanged.
- Current guides/manual prompts replace stale pilot and approval chronology.
  Frozen source history/release recipes remain pinned on the historical branch;
  see docs/tooling-history.md. Agent mirrors now contain durable rules.
- Main's menu exporter, registration, lossless PNG and private-input/source-policy
  work is retained. Menu 1.4 and fighter 1.0 release metadata are unchanged.

Validation: combined Python suite 169 passed +30 subtests (one Node-dependent
pytest test skipped locally because node is not on shell PATH); the exact
standalone JS regression passed separately in bundled Node. CI explicitly sets
up Node 22 on macOS/Windows/Linux. Synthetic browser at port 8779 confirms saved
archived gallery lanes/review and model left/right survive history on/off and
reload, approved history remains available and unrelated history is hidden.
Built wheel installed into an independent temp target imports all fighter/menu
modules and includes the catalogue and browser resources from an unrelated cwd.
Source policy: 505 files, zero failures; whitespace checks pass. Code commit
47ffdbb passed all three hosted platforms (run 41270542085), including package
build and source-policy checks. PR3 retains milestone v0.12.2.

## Private workspace and releases

The live port 8768 writer now includes the published-pack library alongside the
fighter tools, using the existing private profile/workspace. The viewer cutover
checked saved browser notes, backed up metadata and verified exact old review/model
JSON. The separate fighter source cleanup itself did not restart that server.
No art, review versions, corpus, model caches, saves, active game install or frozen
setup snapshot changed. Exact local ownership
and paths are in .local-handoff.md, not public source. Synthetic test workspace
uses a separate port/root and is disposable.

HD Fighters 1.0.0 is published stable: 218 IDs (200 restored, 12 Lanczos, 6 native),
ZIP SHA256 `1bea1239abb8e6b86fff85ecb9fbd0d805df2b1567183e6e8a16b6f131725e0f`.
Catalogue PR10 and protected publication succeeded; fresh released-client install
was verified. No immutable release rebuild/reupload. Bonecrusher, native injury/
Story switching, alpha and distant mip playtests remain separate; no automatic
native flags. Private approvals/selection receipts remain the art authority.
Menu 1.4.0 and its signed catalogue publication remain unchanged as well.

## Decisions and next steps

- Integrate reusable code and timeless guides, preserve dated fighter evidence on
  its pinned remote branch. Do not add production selections/prompts to main.
- No workspace migration, approval reset, new generations or live server cutover
  is required for cleanup. Keep source development isolated from active reviews.
- Portable job/pack APIs are a separate focused follow-up. Existing local sparse
  schema-1 export remains supported; style/labels do not prove generation method.
  A metadata change needs versioned migration/backup/rollback. Do not claim a
  generic release runner exists or silently alter published recipes.
- R2/public verification and catalogue automation belong in DefJamFFNY-mods;
  runtime installation/native acceptance belong in DefJamFFNY-recomp.

1. Read AGENTS.md, docs/WORKFLOW.md and docs/tooling-history.md. Verify current
   branch/remote and private writer ownership before editing or restarting.
2. Pull main for future source work after PR3 integration. Keep other authoring
   worktrees and the live 8768 server unchanged; no automatic source cutover.
3. Continue art review through the existing workspace. Future live cutover needs
   saved browser notes, metadata backup and compatibility checks first.
4. Implement portable assembly jobs/offline release building separately, with
   pinned inputs, collision/concurrency checks, exact-byte staging and synthetic
   tests. Then extract configurable catalogue upload/smoke automation in its repo.
