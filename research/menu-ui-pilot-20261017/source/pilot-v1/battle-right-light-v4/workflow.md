

## Setup upper-right lighting v4 — 2026-10-19 D148

Owner likes improved v3 brick texture and requests only upper-right illumination.
Preserve whole v3left, originalcenter, rightbelow640 and39approved fighter files.
One built-in lighting-only edit (85pilot total),1600×720target containing480px
nativeleft context. Preserve source colors; no warming/yellowing, no geometry or
texture redesign. Raw guidance alone still leaves a broad ceiling highlight.
Use ONLY low-frequency luminance guidance from normalized raw (Gaussian32,
gain.85..1.15) on existingv3RGB. Match native24pxadjacent-band row illumination
with Gaussian12 profiles, gain.55..1.5,horizontal480pxdecay,fade1120..1600 and
vertical256..640. Carry native160pxceiling-row illumination across thebeam using
Gaussian48field,gain.6..1.4,onset0..96,verticalfade128..224. Apply the same scalar
toRGB; retain texture/geometry and cool channelratios. No model RGB/detail copied.
Only x3520..5120,y0..640 maychange. Exactrecipe/prompt/raw/reference in coordinating
pilot-v1/battle-right-light-v4/. Currentmaster cmtype-wide-v4.png and5ratios;
review51738 v4,v3/v2/v1history andnewlightingbefore/after; approvedfighterpaths
retained. 1019priorPNGs/39pins/5centers/left/center/rightbelow640 exact. Browser
5ratios×6images+3history+3fighterpaths+2proofs load,wipe50%,center1920/aspectlock,
nooverflow/zeroerrors. Setup art is DRAFT,not approval; nativegame checks later.
Private menu-ui-battle-right-light-v4-20261019 overlay,earlierarchives immutable.
No8768writer/17candidate/Trejo changes,import/install/game/build/runtime/commit/push.
