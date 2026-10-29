# Agent instructions for Def Jam Modding Tools

Read this file then PROGRESS.md at the start of a session. AGENTS.md and CLAUDE.md
must remain byte-identical. This repository owns authoring tools, not the game
runtime. The owner is Vlad. Implement authorized work fully; ask only for real
missing decisions and preserve an active review session during changes.

## State and data

- Update PROGRESS.md in the same turn: current status, decisions, tests, remaining
  work and exact next steps. Keep it concise. Archive long history under ignored
  docs/worklog/. local.json and .local-handoff.md carry machine-specific paths.
- Game dumps, textures, generated artwork, references, models, Blender files,
  review JSON and exports remain in the configured PRIVATE workspace outside Git.
  Never commit them, captures, checkpoints, API keys or built game code. Use only
  synthetic test fixtures. Run the source checker and git add -A --dry-run before
  a source-only commit; push only when the owner requests it.
- Preserve corpus/source/revision IDs, hashes, schemas, review versions, relative
  image paths, parent provenance and the resolved workspace path. Schema changes
  require explicit versioned migration and backup/rollback. Never reset an old
  workspace, silently re-approve art or regenerate its accepted corpus.
- There is one writer lock per workspace. The live review uses exactly
  http://127.0.0.1:8768; changing host/port changes browser draft storage. Check
  for unsaved browser notes before reload/restart. Never run two writers on the
  same workspace. Preserve data, snapshot review JSON and verify compatibility
  before a server cutover; leave the working server available afterward.

## Art direction

- New generations are Rich Original Detail only. Keep earlier stylized drafts
  as history. Preserve likeness/proportions/expression. On 2026-10-28 Vlad
  explicitly included face, hair, head and headwear restoration for all five
  fighters, aiming for slightly more realistic skin/hair. Keep child drafts
  unapproved until reviewed. Match clothing, footwear and headwear color to the
  original after generation, preserving restored fine detail and matched skin.
- Original atlases and faithful enlargements control composition, UVs, animal
  silhouettes, tree positions and handwriting paths. Semantic descriptions do
  not authorize redesign. Use references; have Vlad approve uncertain detail.
- Owner-authorized cleanup uses the existing archived review tag and Show
  archived revisions controls. Keep all PNGs, notes, prompts, parent links and
  hashes. Published0.1, approved/selected and saved comparison choices stay
  visible; never silently delete art or change approval flags.
  Current/shared stale notes may be reconciled to explicit owner feedback only
  with an exact private prior-notes backup and optimistic review-version checks.
- On2026-10-29 owner approved all five complete models, including Rollins v6,
  and authorized HD Fighters0.2(beta) publication plus ten new fighters using
  the calibrated method. Preserve exact approved bytes: Blaze/Redman v4,
  Nyne/Trejo v3, Rollins v6. New ten stay outside0.2. On the next feedback the
  owner approved seven complete new models and all other components of Ludacris,
  Flava Flav and Warren G, requesting only their shirt logo/clock/jacket script
  repairs. The three new feature children require review; keep accepted pixels
  outside their masks exact. Name and check focal chest details individually.
  Broad source holds leave a logo/prop pending, not restored; tiny uncertain
  marks alone may stay held. See the focused prompt and source-specific recipe.
  The earlier Rollins whole-atlas moderation failures and v5A/v5B studies are
  retained as history; final v6 used successful regional art/material inputs.
  Never infer new-child approval from a parent's acceptance. Check displayed
  revision IDs; use actual material UV masks and inspected narrow tile holds,
  not copied pilot head quadrants/eye/mouth rectangles or Rollins seam counts.
  Source-palette matching must include clothing/headwear/footwear as well as skin.
  See docs/fighter-restoration.md and its calibrated prompt template.
- Exact prompts/reference notes/raw outputs belong to immutable candidate
  history. Every import is a new revision. Keep alpha separate and technically
  restore protected pixels; a prompt alone is not a pixel lock.
- Trejo caption: owner says "Debbie Danielle". Buckle: bear left, deer right,
  smaller deer middle. Current v3 child retains the earlier tattoo work and is
  visually accepted. Do not infer new-child approval, pack selection, game
  verification or installation from that acceptance.

## Engineering

- Package code in src/defjam_tools; ship UI, aliases and pinned licensed browser
  dependencies as resources. No CDN is needed at runtime. Keep optional Torch,
  CUDA and neural-upscaler environments separate from the main app.
- Use rg first. Make focused tests for logic and persistence changes. Existing
  synthetic tests cover decoder bounds, source identity, protected assembly,
  revisions, stale-review conflicts, hashes, HTTP auth and view persistence.
  Use the browser to verify visible behavior after UI changes. Do not write
  tests merely mirroring a trivial reversible edit.
- Keep runtime loader/mod-manager/installer changes in DefJamFFNY-recomp.
  Its HD setup modules are frozen at the hashes in provenance.json. This repo
  owns future tool development. Synchronize a pinned compatibility snapshot
  deliberately with setup tests; do not maintain independent evolving copies.
- New corpus builds fingerprint code and may produce a new recipe identity.
  Reading an existing corpus/workspace must not change it.
- Model viewer decodes fifteen static main-outfit fighter meshes: the accepted
  five plus D-Mob, Sticky Fingaz, Ludacris, Ice-T, Crow, Sean Paul, Crack,
  Flava Flav, WC and Warren G.
  Preserve source geometry/UVs/normals/material partitions; label lighting
  approximations and omitted effects. No rig, venue or game reimport claim.
- Read-only independent investigations can be delegated while the main agent
  owns edit/test/cutover operations. Report evidence and validate claims that
  would change outputs. Do not delegate the serial migration or live writer.
