

## Battle fighter approval and setup refinement — 2026-10-19 D145-D146

Vlad approves the2-,3-,4fighter backdrops.39exact approved files are pinned in
coordinating `battle-fighter-approval-20261019.json`;do not alter those variants.
Setup remains a draft. Owner says left brick courses align but surface texture
differs;right wall is good except a slight ceilingline mismatch. Keep the original
center,colors,goodwall and all unrequested content exact.

Three built-in imagegen calls (82pilot total):first left filled-target surface
edit copied the existing vertical smear and is rejected. A512pxclean-gap retry
with original234×1440brick-material reference and26mortar-height guides replaces
the smeared strip. Adopt only generated x1088..1600,y78..1440,Gaussian1px,
boundary color reconciliation;NO vertical course remapping. The earlier rowwarp
was a cause of stretched face texture:use courseguides in generation and inspect
surfaces afterward. Filled-target editing can preserve an unwanted texture;
retain rejected attempts and switch to a clean gap when that occurs.

The right edit uses2080×720context andchanges only generated x3520..5120,y0..256.
Source/proposal gradientfit overy70..170 measures1px;shift generated beam up1px,
easing off below160,then blend into unchangedwall192..256. Sourcecenter andright
below256 remain byteexact. No source blur/grade/warp,reflective/edgehold strip or
palettewarming. Geometry/source references remain authoritative over modeloutput.
Allprompts/refs/raws/adoptionnotes/finalrecipe saved in coordinating
`pilot-v1/battle-setup-v2/`;recipe `assemble.py`,review updater uses before snapshot.
Currentreviewdefaultssetupv2,retainsv1history,shows approvedfighters onexactv1paths,
and adds focusedceilingbefore/after. Dropdownmaxwidth avoids narrowpaneoverflow.

39approvedpins/963priorPNGs/5centers/rightwall/unrequestedpixels checked;browser
25scene/revision/aspect cases×6images+2ceilingproofs load,wipe50%,center1920,
labels/versionlock pass,zeroerrors/nooverflow. Private overlay
`menu-ui-battle-setup-v2-20261019` includes approvedfiles,input/helper andnewbatch;
apply toCOPYofpriorpilot. Nextowner setupreview;nativeUV/scissor/portraits/
lighting/transitions/all5ratio gamechecks later. Existing8768writer/17candidates/
Trejo untouched;noimport/install/game/build/runtime/core/commit/push.
