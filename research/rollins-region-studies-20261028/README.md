# Rollins regional restoration studies —2026-10-28

The owner requests trying different localized restoration approaches after the
whole-atlas skin/tattoo output failures. Five new built-in imagegen studies
succeeded: sun+SEARCH & DESTROY crop, arm-artwork crop, non-anatomical plain
skin-material swatch, transparent sun decal, and small-emblem crop. Exact prompts,
inputs, original raw outputs and SHA256 pins stay private; no alternate provider.

## Adopted review variants

Both are children of accepted-components v4 r-0ca085cea9db4beb. Neither is approved.

| Method | Revision | PNG SHA256 |
|---|---|---|
|v5A · Localized tattoos + skin detail|r-a6ca883293734644|a5d773e7da306230d4b1627630fdadb517e8aa484fe998964f372f23c1d33695|
|v5B · Source contours + skin/ink grain|r-48b6674ae55e409c|261513e9273f4e8dd2f6a206f4b057c77262c6908a203d7e38d5c0daa165fe86|

A uses source-palette-matched sun/arm edits at.8strength. It restores clear ink
detail and the known SEARCH & DESTROY inscription, but its interpretation of rays,
facial lines and tattoo designs still needs owner review. Raw arm output guessed
tiny words; those exact source letter regions are technically held, not adopted.
The direct small-emblem output redraws curves; holding its text bands caused
visible discontinuities. That component instead uses source contours in A too.

B retains original tattoo contours/lettering, adds generated fine skin grain,
and transfers small generated luminance residuals only inside original dark ink.
It is deliberately restrained and does not make tiny source text more legible.
The transparent decal is retained only as a graphic study: it cleans/changes the
art too much and has residual fill. It was not composited into either model.

## Technical assembly and evidence

`region_detail.py` transfers material luminance residuals with no generated base
hue/shading transfer. Direct crops use existing source-guided Lab detail assembly.
Generated edge rounding may be normalized only within0.5%aspect error; differently
framed crops fail. Final edits are bounded by actual emc2_skin UV coverage minus
all other materials and the accepted head quadrant. Source mask repeats exactly
4x; no interpolated holds. A read-only audit found16actual head/body paired edges;
the old.49wide protection also included body borders and reported74pairs.

All nonbody pixels, approved head/hair/clothes/boots and material alpha remain
exact v4. Sixteen current-parent seam cores are held, fading12–48HDpx. Source
tiny lettering holds are explicit and exact. A changes1,499,830pixels; B1,274,009.
Median downsampled body Lab distance from source is1.138(A)/.703(B); diagnostics
measure palette proximity, not visual approval. The skin swatch fills plain body
coverage and the narrow upper-arm bands outside the tattoo crop. Native skin
coverage104,187pixels, HD1,666,992. The small emblem remains conservative.

`prepare.py` writes a new immutable stage; final stage is assembled-v2. Initial
assembled/ files and comparisons are retained as unimported QA history; the
direct emblem artifact there is NOT the current atlas. `import_review.py` uses
the authenticated live writer, imports B then A, and preserves optimistic review
versions. Shared Rollins notes now describe the successful studies rather than
the obsolete active service blocker. All other existing revision notes/approvals
and PNGs remain intact. Saved Rollins right is A; left/camera/preferences and
other fighters stay unchanged. No restart or forced browser reload.

88tests+15subtests pass; new synthetic tests verify material/alpha/held-text/seam
invariants, source-ink restriction, invalid inputs and bounded aspect rounding.
Live checks verify both candidate PNG hashes and exported GLB decoded RGBA,
all31prior candidate metadata/files and existing revision reviews. Workspace now
33candidates/29live assembly/request records;5actual new generation calls are
recorded separately in the private prompt manifest. Browser visual check remains
blocked by prior URL policy; no workaround. No game install/publication or0.1change.

Private workshop experiment rollins-region-studies-20261028/ contains inputs,
prompts.json, raw, mask-audit.md, assembled-v2/receipt.json and comparison PNGs,
before-import backups, import-receipt.json, verification.json and review-index.md.
Owner saves browser drafts, refreshes the existing model viewer and chooses
Henry Rollins v5A or v5B. Compare original/v4/new from both sides and at tattoo,
neck and skin closeups. Native playtest and final Rollins approval still pending;
bulk calibration remains provisional until the owner chooses an acceptable result.
