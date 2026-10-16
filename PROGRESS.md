# Def Jam Modding Tools — progress and handoff

## Current status

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
- New art is Rich Original Detail only; older stylized drafts remain history.
  Faces/protected pixels/alpha stay unchanged unless specifically approved.

## Art review

Blaze, Nyne, Trejo are the pilot; 11 retained drafts, 13 request records,
0 queued at migration. Trejo A source-guided v4 `r-a74be693951f4617` awaits
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

Next work is owner art/model review, then targeted Rich Original Detail revisions.
Run focused tests for changes; keep source and private artwork backups separate.

Windows CI initially exposed default-codepage decoding of UTF-8 review JSON.
All implicit module text reads now specify UTF-8; a simulated cp1252 roundtrip
checks non-ASCII notes and queued prompts. Linux/Mac initial CI passed; rerun
Windows after this fix.
