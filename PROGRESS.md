# Def Jam Modding Tools — progress and handoff

## Current status

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

The live port 8768 writer stays on the persistent `DefJam-Modding-Tools-hd-fighters`
checkout and its existing private profile/workspace. This source integration did
not restart it or alter art, notes, review versions, corpus, model caches, saves,
active game install or the recomp's frozen setup snapshot. Exact local ownership
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
