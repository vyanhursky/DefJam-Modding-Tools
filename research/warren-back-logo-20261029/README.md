# Warren G complete split back crest —2026-10-29

Owner screenshot showed half the back P crest still low-resolution. Original
mesh/UV clipping established two separate native512 fragments [0,296,42,375]
and [261,296,300,375]. The previous lettering repair covered one fragment only.
A single built-in focused edit requested BOTH fragments using current crop as
edit target and matching original as layout/palette authority. Exact submitted
prompt, crops, raw output and masks remain in the private same-named experiment.

`assemble.py` intersects those two ROIs with actual cloth UVs and a back-facing
model-space mask, applies source-palette matching and preserves all other parent
pixels plus full alpha exactly. Both fragments were checked individually and in
an assembled back RGB UV projection. The CPU projection ignores alpha/game
lighting; geometry/UVs are unchanged and it is not a game-shader test.

Parent r-70bb2a3cdb234d93; new child r-a2b301c58a8c4680 (unapproved/unselected).
Output SHA256 0b9f9c2edf035aef803f8c619ebb84044c437bfd94c40cc875fb2da0eac8e4a8.
89,078changed pixels out of91,008safe pixels. Fragment changes98.04%/97.67%.
All accepted script/head/skin/clothing outside the back crest remain exact.
`assembled-v2` rebuild matches the already imported v1 PNG byte-for-byte; there
was no duplicate import. Final recipe/dependencies and receipt are frozen privately.

Live PNG and model GLB embedded RGBA/revision verified. Existing right view was
updated to this child, preserving other camera/left/lighting/groups and session.
Ludacris and Flava Flav latest feature children were separately approved per owner
feedback, with exact prior review backups and optimistic versions. Warren still
requires visual approval. No new pack version/publication/install was requested.

The calibration now requires each disconnected/repeated/rotated feature fragment
and an assembled Front/Back check. High global coverage or one sharp crop cannot
establish complete restoration. New synthetic scope and UV diagnostic tests
support the checks;104pytest tests+15subtests pass in the full tools suite.
