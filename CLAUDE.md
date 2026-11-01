# Agent instructions for Def Jam Modding Tools

Read this file then PROGRESS.md at session start. Keep AGENTS.md and CLAUDE.md
byte-identical. Vlad owns this authoring project. Implement authorized work fully;
ask only for real missing decisions and preserve active review sessions.

## State and private data

- Update PROGRESS.md in the same turn with status, tests, decisions and exact
  next steps. Keep dated history private under ignored docs/worklog/. local.json
  and .local-handoff.md hold machine-specific paths and current writer ownership.
- Never commit game dumps/art, generated references, models/Blender files, review
  JSON, submitted production prompts/ledgers, captures, checkpoints, secrets or
  release archives. Use synthetic fixtures. Run the source checker and
  `git add -A --dry-run` before source-only commits; push when authorized.
- Preserve corpus/source/revision IDs, hashes, relative image paths, provenance,
  workspace paths, schemas and optimistic review versions. Schema changes need
  explicit versioned migration and backup/rollback. Never silently reset reviews,
  re-approve art or rebuild accepted corpora. Git is not the private data backup.
- One writer per workspace. The live review origin is http://127.0.0.1:8768;
  changing origin changes browser drafts. Check unsaved browser notes before any
  live reload/restart. Back up metadata and verify compatibility before cutover.
  Use separate synthetic workspaces for tooling tests; keep the live writer up.

## Art and review

- New work uses Rich Original Detail. Preserve likeness, expression, UV geometry,
  source palette/shading and the game's illustrated character. Faces, hair and
  headwear may be restored when declared in scope; protect accepted pixels outside
  that scope. Match clothing, footwear and headwear color as carefully as skin.
- Original atlases control tattoo silhouettes, animal/tree positions, inscriptions
  and handwriting paths. References can clarify details; uncertainty needs owner
  approval. Do not invent words. Check named logos/props and every split, repeated
  or mirrored UV fragment, including assembled Front/Back views.
- Derive masks/seams from actual source geometry; never reuse another fighter's
  coordinates. Alpha, material holds and exterior parent pixels need exact
  technical enforcement after assembly. Prompts alone are not pixel locks.
- New imports are immutable children, initially unapproved/unselected/not native
  verified. Preserve exact submissions, raw outputs, errors, parents and hashes
  privately. Keep failures honest; a baseline is not a generated restoration.
- Archive unrelated history with the existing tag; keep all PNGs and notes.
  Approved/selected and saved/current revisions remain available. Reconcile stale
  notes only against explicit feedback with prior-note backups and review-version
  checks. Never infer child approval from a parent's acceptance.
- Art review, technical/channel review, selection, release authorization,
  publication and actual game verification are distinct. Preserve published
  bytes. [Tooling history](docs/tooling-history.md) links frozen fighter recipes;
  do not replay dated import/review scripts into a current workspace. Current
  private records, not old batch chronology, control ongoing art work.

## Engineering and ownership

- Maintain code in src/defjam_tools with packaged resources, source-only validated
  catalogue data and pinned licensed browser dependencies. No runtime CDN.
  Optional Torch/CUDA/weights stay separate; local-neural assembly is experimental.
- Use rg first. Test meaningful persistence/decoder/mask changes with synthetic
  inputs and verify UI changes in the browser. Test installed package resources,
  not just a checkout's editable import. Preserve decoder-1 cache compatibility,
  original geometry/UVs/normals and explicit documented preview omissions.
- Static GLB previews do not reproduce rigs, animation, game shaders or injury
  switching. No venue decoding or game mesh reimport claim. Offline injury
  correspondence is not runtime acceptance; native tests belong in the recomp.
- Runtime loader/mod-manager/setup work belongs in DefJamFFNY-recomp. Its shared
  HD core is a frozen snapshot: synchronize only via a reviewed pin and setup
  tests. Do not maintain independent evolving authoring copies in that repo.
- Modding Tools owns offline authoring/export; DefJamFFNY-mods owns catalogue,
  R2 distribution and protected signing. Do not add publication/game installation
  to the local gallery Export button. Menu exporters require explicit private
  inputs; preserve current menu commands and source-boundary guards.
- Read-only bounded independent investigations may be delegated. The main agent
  owns serial edits/tests/cutovers and validates findings that change outputs.
