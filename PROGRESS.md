# Def Jam Modding Tools — progress and handoff

## Current status

- Version 0.1.0 extraction underway from DefJamFFNY-recomp `f71ab64`.
- Standalone Python package/CLI/resources, prompt policy, focused agent
  instructions and synthetic tests prepared. 55 tests + 12 subtests pass. Wheel installation, real-workspace
  read compatibility, seven byte-identical GLBs and selected pack equivalence pass.
  Browser verifies the installed wheel against a copied workspace with no errors.
- Current production viewer still runs the original source at 127.0.0.1:8768.
  Keep it available until the new checkout is installed and verified.

## Decisions

- 2026-10-16: Vlad approved setting up this dedicated repository and will resume
  texture/model review afterward. Initial remote is private; code-only Git.
- Authoring lives here; runtime/mod-manager/setup stay in the recomp. Its shared
  HD core remains a frozen byte-identical snapshot. One owner for new core work.
- Existing private data stays in place. Preserve IDs, hashes, review versions,
  schemas, relative image paths, browser origin and single-writer lock.
- New art is Rich Original Detail only; older stylized drafts remain history.
  Faces/protected pixels/alpha stay unchanged unless specifically approved.

## Art review

Blaze, Nyne, Trejo are the pilot; 11 retained drafts, 13 request records,
0 queued at extraction. Trejo A source-guided v4 `r-a74be693951f4617` awaits
owner review of tattoo script/stroke paths, animal/tree/buckle placement and
skin seams. Original script guidance: "Debbie Danielle". Exact exterior/face/alpha
checks do not establish interior authenticity. No art is automatically approved.

## Technical limits

Three static main-outfit fighter meshes; original geometry, UVs, source normals
and material partitions. Game lighting/reflections and sparkle effects are not
reproduced. No rig/animation, venue decoder or game mesh replacement yet. GLBs
validate in Khronos; Blender itself was unavailable for a native import test.

## Next steps

Finish compatibility tests, install final checkout, switch live server at the
same origin with saved workspace intact, then retire recomp authoring copies.
After cutover, resume owner review using local.json and `defjam-tools serve`.
Run focused tests for changes; keep source and private artwork backups separate.
