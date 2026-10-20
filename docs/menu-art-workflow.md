# Menu artwork production and approved skyline recipe

Start here for future menu work. Use the [prompt scaffold](../prompts/menu-widescreen-extension.txt)
and [seam review procedure](widescreen-backgrounds.md). These are manual authoring
instructions; no image API or new wide-texture importer is wired into the tools.

## Owner-approved reference

The retail title's isolated skyline version `seam-v3/full-height-right-repair`
was approved by Vlad on2026-10-17. Its5120×1536PNG SHA-256 is
`683e5481d3bef12a27be00a1eda0afbbcfcefdbc3583be862f00ee21b809f2f0`.
The private `skyline-approval.json` also pins all five aspect previews and the
owner's exact approval wording. Keep this version immutable. Approval covers
the isolated artwork, not other layers, separate restoration trials or runtime
validation. No workshop candidate is silently selected or approved by it.

The complete private experiment is retained under
`<data>/scratch/menu-ui-approved-skyline-v3-20261017/`. Its manifest covers the
source/faithful joins, exact prompts, raw outputs, guides/masks, processors,
receipts, master/crops and approval. It is self-contained, unlike the earlier
incremental v1/seam-v2/seam-v3 overlays. Game artwork stays outside Git.

## Reproduce the accepted skyline

1. Validate the two source IDs and image hashes against the retained corpus.
   Join prestart name2 (512×512) at x0 and name1 (128×512) at x512. Preserve all
   source pixels, alpha and padding. The faithful4×join is2560×2048.
2. The approved wide master uses a faithful3×center1920×1536 at master x1600.
   The full canvas is5120×1536. Center pixels stay exact. This is a scenery
   extension; the separate source-palette cleanup trial is not its center.
3. Retain the initial left/right raw panels and their exact generation prompts
   in `generations.json`. The initial raw panels required documented full-panel
   normalization. They were only side-art proposals; their regenerated source
   context was not accepted. Copying back the real center revealed cloud cuts.
4. Use the FINAL assembled composite as the next edit target. `seam-v2/` retains
   the left/right1536×1024context crops and annotation guides. Exact prompts
   require cloud ridge/channel height, tangent, curvature, thickness, softness
   and lighting to continue from the original into fixed outer scenery.
5. `seam-v2/assemble-bridges.py` applies the generated cloud proposals only in
   master rectangles[1216,380,384,324] and[3520,380,384,324]. A harmonic correction
   matches fixed four-edge boundaries and the source-side normal gradient. It
   keeps local proposal gradients rather than blurring across the original.
   Known harmonic-ramp, identity and numerical residual checks pass. This is a
   retained private processor, not a generally approved production algorithm.
6. The left join was accepted, but the right rectangle ended at y704 and missed
   the LOWER clouds/horizon. `seam-v3/right-full-height-prompt.txt` and its target,
   guide and raw output correct that omission. `seam-v3/assemble.py` applies the
   same method over[3520,380,512,580], down to y960. The accepted left and entire
   original center remain exact. The tool output was1536×1024; no repair-crop
   resizing was needed. Nine built-in ImageGen calls led to this accepted art;
   earlier rejected color/structure variants remain in the archive.
7. Settled skyline transform is stage_y=source_y−134, stage_x=source_x. At3×,
   take master rows402..1350 into a5120×1440stage at y0. Leave the uncovered
   lower stage for the other depth layers. Derive centered widths1920/2304/
   2560/3360/5120 for4:3/16:10/16:9/21:9/32:9. All five original centers match
   the faithful4:3preview exactly. Do not stretch the skyline to fill480rows.

## Gates for every next layer

- Prove tile order, UV-active bounds, half-pixel overlaps, alpha and timeline
  transform from metadata before art. Preserve full original sheets for export;
  clip active geometry for layer previews. Opaque filler is not transparent.
- Restrained restoration keeps original per-pixel Lab chroma and broad lighting.
  The current private color recipe permits only25% fine-L* difference, clipped
  to±1L*, using an8HD-pixel blur radius at4×. Protect lettering, graphics, alpha,
  silhouette bands, tile seams, padding and gamut-clipped pixels exactly. Save
  masks, processor and measured color/alpha checks; this is a technical derivative
  of raw ImageGen, not recovered authentic detail or a raw model output.
- Derive lit/dark states from the same structural detail, retaining EACH original
  illumination/chroma and its own geometric mapping. Never independently invent
  a second poster layout. Keep text, logos, spotlight and door controls live.
- Build extension targets around the actual final original/restored center,
  not a separate source reference. Reuse real offstage scenery before inventing
  additions. Make allowed regions, immutable sides and coordinates explicit.
- Trace material-specific structures through BOTH ends of the repair: clouds,
  roof lines, perspective, masonry courses, slat spacing, grain and lighting.
  Check the WHOLE visible height, including low clouds/haze and the horizon.
- Enforce protected pixels technically AFTER generation, then review THAT final
  assembly. Exact center equality or a near-zero seam metric alone does not prove
  continuity; matching a boundary numerically can leave a wrong cloud path.
- Inspect both bounds and outer band edges at native/coarse scales with bounds
  hidden. Use full-height close-ups and separate upper/middle/lower diagnostics.
  Check every aspect; do not let black/transparent padding dominate statistics.
- Keep previous/raw versions, exact input/output hashes, prompts, alpha/region
  masks, transforms, normalization, technical recipes, quality findings and
  explicit owner approval scope together. Do not modify the approved skyline.
- Game validation remains separate: animated transitions, parallax, spotlight,
  alphablending, UV/scissor/mips and native-aspect captures on each renderer.

For the second batch, a rigid roof silhouette required technical alpha/geometry
registration to the source edge's measured slope; color blending alone left a
step. Keep AI texture proposals but verify straight architectural planes and
their source coordinates. Generated-side alpha remains subject to art review.
A1024square bridge target returned1254square; assembly uniformly restored the
original1440square crop. The50%join and24%poster-top landmark stayed registered. Uniform full-canvas resolution normalization is
allowed only when aspect and landmark registration agree, with actual sizes and
transforms recorded. Reject crop, zoom, perspective or registration drift; never
silently stretch a repair in one axis. Restore protected pixels afterward.


## Source-faithful title logo and door emblems (2026-10-17, D133-D135)

Owner approved the city, completing all three title scenery layers. Mode Select
remains conditional on right original4:3-border lighting in game. Authorized
order is title logo/emblems, Options/Jukebox, then Battle setup/selection.

Use [the logo/emblem scaffold](../prompts/menu-logo-emblem-restoration.txt).
Actual door artwork is8mode states/21source fragments, not the6support icons.
Retail title name19 samples508×88inside512×128. It has colored RGB, real graded
alpha and transparent colored filler; it is not a white alpha-only stencil.
Join full source fragments according to proven material/UV mapping, clip active
bounds and retain every original stored tile canvas for later split.

Nine built-in calls produced the wordmark/eight-emblem audition. Exact private
prompts/inputs/raws are in pilot-v1/branding-v1/generations.json. Raw output can
change aspect/framing, add a backdrop/glow, invent holes or broaden contours.
Do not promote it as a source-mapped replacement based on bbox similarity.
Current final audition instead holds Faithful4×alpha/strong RGB edges/seams/
padding exact and takes only source-chroma/broad-light-preserving fine L detail:
35% residual,±2L, radius6HD pixels. Exact transform/helper/runtime snapshots and
masks are retained. Credits is essentially baseline(160changed pixels); say so.
No new core preset or automatic adoption of the experimental processor.

The read-only page offers original/FaithfulHD versus final/raw, RGBA/alpha,
three background colors/patterns and PNG/provenance links. All72combinations
load;9protected/alpha pairs and21source-shaped split/reassembly/padding checks
pass. New logo/emblem art stays unapproved; no workshop writer/import changed.
Stable private overlay <data>/scratch/menu-ui-logo-emblems-20261017/ preserves
this batch and city pins separately from earlier immutable archives.

Next background mapping already distinguishes XboxOptions71|70 from PS2/GC8|7,
independent scrolling wall4, Jukebox20|19 plus live bottom/mask/light layers, and
four640×480Battle backgrounds with8distinct IDs. Do not stretch2fighter art to
3/4fighter layouts or flatten console-dependent live layers. Exact metadata is
in coordinating recomp reports menu-options-jukebox-shape-audit-2026-10-17.md
and menu-battle-background-shape-audit-2026-10-17.md.


## Transparency feedback and repair (2026-10-18, D136)

Owner likes sharper raw logo/emblems but found see-through areas filled black.
Existing restrained candidates already have exact source alpha; do not silently
substitute their almost-baseline art for the raw artwork he likes. The original
title's FIGHT strokes have alpha129/255; dark distress can be opaque. Transparent
RGB filler can be green, pink or black. Read coverage independently.

Nine built-in edit retries used transparent output plus magenta/alpha guides.
They improved some openings but retained speaker fill/trophy halo and changed
RGB. Preserve retries as history; a prompt alone is not an alpha lock. Direct
affine mask copying also left ghosts. The final nine raw-canvas auditions keep
the liked RGB byte-identical, using locally registered original coverage capped
by previous alpha. Displacement maps, recipes, exact prompts/refs/results and
checks are retained in coordinating recomp pilot-v1/transparency-v2/.
These use the generated canvas, not game-ready UVs. Source-shaped runtime alpha
must still stay exact. No automatic preset/import or workshop writer change.

Review51738 defaults Transparency repair v2/checkerboard; original, Faithful HD
and previous raw references; old candidates retained.54image/reference/channel
pairs load, three backgrounds work, zero console warnings/errors. Nine RGB and
alpha recipe pairs exact;27reference hashes and41scenery pins unchanged.
28semantic probes pass; an explicit prior-clear cap retains the disc feather0
instead of registered original8. No unexplained failures.36pilot calls total.
Private new overlay <data>/scratch/menu-ui-transparency-20261018/ preserves the
old archives. New branding drafts remain unapproved; game validation is later.


## Options and Jukebox draft workflow (2026-10-18, D137-D138)

Owner approved the exact nine transparency-v2 repaired PNGs. Pin their hashes;
source-shaped game mapping remains separate. Earlier unapproved text above is
historical. The next batch now has Options and Jukebox drafts at review51738,
all five ratios, native-original side/wipe/center comparisons and alpha views.
13 new built-in calls,49 pilot total; no workshop import/writer change.

Use Xbox Options71|70 and separately moving wall4; keep PS2/GC8|7 as alternate
reference. Reuse wall4's extra85 stored columns before synthesizing scenery.
Keep full stored sampling support when filtering the original stage edge.
Jukebox20|19 backdrop stays separate from88|87 bottom strip,mask,live text and
console-dependent lighting. Options studies currently cover top scroll state;
the independently moving layers still need full-extrema/native geometry work.

Three restrained layers retain original Lab chroma/broad lighting, alpha,
protected paper/posters/graphics,seams and padding. Only25% fine-L residual,
radius8HD,±1L is allowed; medianLab0 for all three. When splitting, copy each
individual faithful stored tile's unused bottom32rows exactly: enlarging the
assembled parent has different seam filtering in unused texels. Check active
reassembly independently from original individual padding.

Avoid padded edit targets: two3072×1024 proposals filled the inactive bottom
160rows and stretched scenery, so both were rejected. Use fully active,
full-height side canvases with real original/known context already in place.
Record actual output aspect and landmarks before uniform resolution
normalization. Narrow512HD bridge edits then connect fixed inner and outer
contexts in1536×1440 targets. Protect actual source/outer pixels after generation.
Residual technical matching applies only to generated bands. Grain/blur matching
and numerical boundary equality do not establish natural material continuity.
Reflected-material and clamped-support trials repeated/streaked; reject them.

Current refined drafts still show sharpness/material changes at some joins,
especially Options door. Do not call them seamless,approved or game-ready.
The review exposes both full-height joins; original palette applies exactly to
the source-derived center,not a proof of every invented side pixel's color.
Exact13prompts,raws,targets,guides,recipes,history,dimensions/hashes/checks are in
coordinating recomp pilot-v1/menus-v1/.13built-in calls:3restoration,2rejected
wide,4full-height sides,4focused bridges. Current paths use *-refined.png.
9refs,3alpha/protected pairs,4active splits+individual padding,10centers,
2known contexts,50prior art pins and27branding refs pass. Browser10scene×4images,
24texture×2images,controls,9approved branding and prior title pair pass;zero
console errors. These checks cannot replace art review or gameplay acceptance.

Private overlay <data>/scratch/menu-ui-options-jukebox-20261018/ contains the
new batch,review page,approved nine and helper/toolchain snapshots. Apply to a
COPY of earlier pilot archives to resolve older review sections. No change to
writer8768/17candidates,Trejo,installation or runtime. Battle is next authorized
group after this batch. Follow coordinating results report for remaining work.


## Options door and Jukebox joins v2 (2026-10-18, D139)

Owner accepts Options left and likes restored texture art, asks complete right
architecture from Mode Select lit-wall reference and both Jukebox brick joins.
Freeze Options entire left+4:3center and Jukebox4:3center. Only three scenery
sides change. Options right allowed region now begins at original4:3 edge,
including the previously reused85stored columns if needed to finish architecture.
The source-safe wall tile remains unchanged;preview reuse is not an immutable
boundary when owner requests replacement of incomplete beyond4:3 scenery.

Five built-in imagegen calls,54pilot total. One complete-door proposal adopted;
its right jamb,threshold and masonry reference existing Mode art without copying
its lamp,emblem poster or lighting. Two first Jukebox filled-target retries
retained the wrong smaller brick grid. Reject after actual-source assembly.
Second attempts blank the erroneous side field and use real source context plus
seven approximate mortar-bed trajectories. Explicit source-course height/count
works better than asking to continue an already wrong dense field. Guide
coordinates are approximate trajectories,not acceptance metrics. Trace actual
mortar at both original borders after source pixels are restored. Never render
guide marks,mirror/clamp material or change source to fit a generated grid.

Same-aspect full-canvas resolution normalization is recorded (1591×988/989 to
2320×1440). Generated-side384px harmonic residual/grain matching follows the
structure repair (radius3 Options,1.5Jukebox);original pixels never filtered.
Both generated band ends,full-height joins,complete door and10aspect crops
visually inspected. New material/architecture remains owner-review art,not
runtime acceptance.319prior PNGs,2sourcecenters,Options entire left+center,
10aspect crops exact. Browser20menu/revision/aspect×4images and4join×2images
load;wipe25%/center lock pass,zero console errors. Source restoration/alpha
and approved branding untouched. Review51738 defaults v2,retains v1 selector,
full-height before/after plus complete-door/reference links. No workshop change.

Exact5prompts/raws,guides,failed retry history,processors/receipts/hashes:
coordinating recomp pilot-v1/menus-seams-v2/. Stable private overlay
<data>/scratch/menu-ui-options-jukebox-seams-v2-20261018/ includes helper and
old-input snapshots;apply only to COPY of previous pilot tree. Previous archives
immutable. Next owner review,then native scroll/UV/lighting/transition checks;
Battle remains next authorized background group. No import/install/game run.


## Jukebox approval and narrow Options door v3 (2026-10-18,D140-D141)

Owner approves exact Jukeboxv2:11files pinned in coordinating
pilot-v1/jukebox-approval-20261018.json;art unchanged. Optionsv2 still too wide
andplain. Owner supplies screenshot for WIDTH andPANEL TEXTURE. New layout
seeds the actual reference doorway730×1110 at NATURAL SCALE (no squeeze),right
jamb targetlocal~1280,left~570,height~1110;~0.65width/height. Preserve real
original left oflocal720. Blank faulty far-side field,retain narrow reference
door as EDITABLE context;ask imagegen for its closely ribbed,stained/painted
surface andwall continuation. Do not copy other menu lamp,poster,composition or
unrequested illumination. Original small orange/silver hardware finishes locally,
not as long bars across the new panel. Correct geometry before narrow bridge.

Two built-in edits,56pilot total:fullside1591×989→2320×1440,then256px material
bridge1295×1215→1536×1440. Real source andcorrect outer door fixed after editing;
only generated-side residual/grain matching. The accepted entire Optionsleft+
4:3center exact;371prior PNGs/11Jukeboxpins/5aspectcrops exact. Material/width/
actualjoin remain ownerreview;do not infer invisible joins from numericalchecks.
Review51738 currentOptionsv3/approvedJukeboxv2;priorOptionsv2/v1,Jukeboxv1 retained,
fullheightbefore/after,original/wipe/center/all5ratios. Browser25scene×4images+
4joinpairs×2load,wipe50%/centerlock pass,zeroerrors. Existing generic individual
restoration draft labels are historical;mainstatus andapprovalmanifest control.

Exactowner screenshot,source crop,2prompts/raws,guidecoordinates,processors,
prebridge history,receipts/hashes:coordinating pilot-v1/options-door-v3/.
Private overlay <data>/scratch/menu-ui-options-door-v3-20261018/ includes approved
Jukebox snapshot,helper/toolchain andpriorinput;apply only toCOPY ofearlierpilot.
Oldarchives immutable. Noautomaticcorepreset,writer8768/17candidate/Trejowrites,
import/install/game/build/runtime/commit/push. NextOptionsownerreview,then native
UV/scroll extrema/transitions/lighting/gamechecks;Battle authorizednext.


## Options optical softness only (2026-10-18,D142)

Owner likes v3 otherwise and requests slight right blur/DOF. One built-in edit
supplies softness reference,57pilot calls total;raw pixels are NOT pasted over
the liked art. Final projects equivalent Gaussian2px at1440high onto existing
v3 RGB only,masterx3520..5120,64pxsmoothstep onset. Preserve source4:3center,
accepted entire left,door proportions/wear/brick layout. No repaint/geometry
warp/global grade. MeanRGBdelta<0.009 on0..255. This is bakedtexture defocus,
not new runtime lens/depth-of-field support. HighfrequencyRMS supports strength
selection,but final fullheight/5aspect visual review remains authoritative.

Review51738 currentOptionsv4/approvedJukeboxv2;v3/v2/v1 history.30browser scene×
4images+4joinpairs×2load,wipe50%/centerlock pass,zeroerrors. PriorPNGs and11Jukebox
pins exact;5aspectcenters exact. Prompt/reference/raw/filter recipe,histories/
hashes in coordinating pilot-v1/options-softness-v4/. New private overlay
<data>/scratch/menu-ui-options-softness-v4-20261018/ includes v3input/toolchain;
apply toCOPY ofearlierpilot,archives immutable. Owner finalOptionsreview and
native scroll/UV/lighting/transitions/gamechecks pending;Battle next authorized.
No8768/17candidate/Trejowrites,import/install/game/build/runtime/core/commit/push.


## Options v4 approval — 2026-10-18 D143

Vlad approved the current right softness and complete Options scene. The exact
13 master/crop/proof/source-restoration pins are retained in coordinating
`logs/ui-restoration-20261017/pilot-v1/options-approval-20261018.json`.
No pixels or prompts changed for approval; v4 filter/reference provenance and
v3/v2/v1 histories remain intact. Next authorized art scope is Battle match setup
and separate two-, three- and four-fighter selection backgrounds (eight source
image IDs), each in five ratios. Preserve original frame geometry, alpha/padding,
colors and separately rendered portraits/UI; check both extension joins and
matching softness. Native mapping/scrolling/lighting/game acceptance is pending.


## Battle first-pass recipes and border feedback — 2026-10-18 D144

Four distinct scenes: Battle setup and2/3/4fighter selection;8original IDs,
stored640x512/active640x480,split512/128. Preserve32unused source rows, each
tile’s independent alpha, all paper/portrait-frame layouts, poster lettering and
live portrait/name/lighting layers. Do not copy/stretch the2fighter layout to3/4.
Restrained source-palette assembly preserves broad spatial colors and chroma;
bounded fine lightness only. Original blue-green walls/cream paper must not be
warmer,yellower,brighter or more saturated. Raw AI drift is history, not final.

Review51738 now has the4drafts×5ratios,matching native originals,wipe,center lock,
original bounds,both full-height joins,stored RGBA/alpha/checker and raw history.
No newly generated artwork is approved by this work. All previous art remains
unchanged. Coordinating battle-v1/generations.json holds22exact built-in prompts
and all input/raw hashes (79pilot calls total); targets/guides/raws/processors and
receipts are retained beside it. Private overlay menu-ui-battle-backgrounds-v1-
20261018 is immutable;apply toCOPY ofpreviouspilot. Final processing sequence is
in coordinating docs/research/menu-battle-background-results-2026-10-18.md.

Carry-forward lessons: blank full-height targets, explicit role-labeled references,
fixed-center restoration, structural line/course alignment at EVERYheight on
BOTHbounds, smooth broad lighting and native optical softness. No duplicated
frame/panel/roomcorner on the added sides. A source-material reflection/edge-hold
support strip produced vertical bands here and was REJECTED; eight blank-gap
AIbridges replace it. Setup-left needed brick-only context (plasterroom reuse
introduced an extra corner) and26source-height mortar guides plus generated-only
row registration. Keep all rejected passes for diagnosis. Source center is never
blurred/graded/warped; modest Gaussian2px outergenerated softness and harmonic
boundary matching apply to generated pixels only. RMS is a supporting metric;
inspect grain SCALE, courses, shadows and full-height transitions visually too.
Owner review remains authoritative; invariants do not prove seamless artwork.

Verified756previous PNGs unchanged,8sourceIDs/alpha/padding/splits,4protected
mosaics,20cropcenters;browser20scene×4images+8joins/32texture×2load,zeroerrors,
wipe25%/center1920/bounds pass,no398px horizontal overflow. Nextownerfeedback,
then nativeUV/scissor,portrait/name alignment2/3/4,lighting/transitions/all5ratio
gamechecks;Options scroll and Mode conditional rightborder remain integration
work. Existing writer8768/17candidates/Trejo untouched;no import/install/game,
build/runtime/core/commit/push.


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


## Setup left material still rejected; full-left v3 — 2026-10-19 D147

Owner still clearly sees the leftbrickmaterial difference in v2. Preserve the
originalcenter,ENTIREv2right/ceiling,top78rows and39approved2/3/4fighter files.
Replace the whole generatedleft x0..1600,y78..1440 rather than another narrowgap
beside older mismatched art. New prompt references nativebrick ONLY,not previous
AIbrickmaterial;blank1600plus208nativecontext andcourseguides. Explicitly avoid
bright/chalky/raisedmortar,coarse porous masonry,3Dbevels,warming/yellowing,
objects/corners and extra floor horizon.

Two built-in calls/84pilot total. First source-only proposal adopted through
material normalization. Native-game-style retry stillrough and addedfloor;
rejected. Retained technical studies:wide quantile/harmonic assembly caused
bright band;globalcontext andspectral-only normalization insufficient. Do not
promote exact center checks to visual approval. Promptalone has not guaranteed
same material;check nativegrain/contrast/lighting atfullheight and crop scales.

Final `battle-left-v3/assemble.py` invokes `edge-material-study.py`:normalize
addedtexture through534×480native-density sampling then1600×1440. Match Labmean/
contrast/shading to actual originaladjacent96px,measuring512generatedpixels and
smoothing heightprofiles Gaussianσ64,gain0.3..1.6. Apply overwholeleft,not source.
8pxadditive seamconditioning and16generated-row beamblend. No copied source
materialstrip,reflection/edgehold support or vertical coursewarp. Allraws,
refs,prompts,stats,rejectedstudies and scripts preserved,pinned by receipts.
Currentmaster cmtype-wide-v3.png,5ratios,fullleftproof andv2/v3leftbefore/after.
All991prior PNGs/39approvedpins/5centers/entireright/top78 exact;browser30cases×6
+2leftproofs pass,wipe50%/center1920/labels/nooverflow/zeroerrors. Review51738
currentv3,v2/v1history andapprovedfighterpaths unchanged. V3isUNAPPROVED.
Private menu-ui-battle-left-v3-20261019 overlay includes fullbatch,inputs/helpers,
updatedpage/sourceworkflow;apply toCOPYofpriorpilot,earlierarchives immutable.
Nextownervisualreview. NativeUV/scissor/portrait/lighting/transitions/all5ratio
gamechecks,Options scroll and Modeconditionalborder remainlater. No8768writer/
17candidate/Trejochanges,imports/install/game/build/runtime/core/commit/push.


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


## Corrected side: upper-left lighting v5 — 2026-10-19 D149

Owner clarifies LEFT border lighting;right looks fine. Use v3base and restore
entire pre-v4right,not v4right lighting. Retain v4asrevertedhistory,all older
revisions/39approvedfighterfiles. One built-in lighting edit/86pilot total:
1440×720target includes960addedleft +480originalright;prompt explicitly states
LEFT,x960join,fixedRIGHTcontext,no warmth/yellow,unchangedgeometry/material.
No generated RGB/detail pasted. Uniform1440×720normalization;Gaussian32luminance
guide gain.55..1.15 onexistingv3RGB. Native64pxadjacent brickband profiles,
Gaussian16,gain.55..1.4,320pxleftwarddecay,onset640..800,bottomfade480..720.
Same scalarRGBgain preserveschannelratios. Domainx640..1600,y0..720 only.
1035priorPNGs/39pins/5centers/nativecenter/entire pre-v4right/outside domain
exact. Browser5ratios×6images+4history+3fighterpaths+2proofs load,wipe50%,center
1920/aspectlock/nooverflow/zeroerrors. Review51738currentv5,upper-left b/a;
v4clearlyrevertedhistory. Prompts/raw/recipe in coordinating pilot-v1/
battle-left-light-v5/;report menu-battle-left-lighting-v5-2026-10-19.md.
Private menu-ui-battle-left-light-v5-20261019 overlay;earlierarchives immutable.
Nextowner visualreview;nativegamevalidation later. No8768/17candidate/Trejo
writes/import/install/game/build/runtime/core/commit/push.


## Battle setup approved; Rewards/Unlock shared wall — 2026-10-19 D150-D151

Owner approves setupv5;13exactpins in coordinating battle-setup-approval-20261019.json,
plus39fighterpins unchanged. AllBattle background art accepted;gamechecks separate.
Next sharedRewards/Unlockwall:identical2IDs inbuyrewards2/1,unlockchar11/10,
unlockven11/10.699×480active,699×512stored;512+188parts overlap1px at511.
Rewardswallleft−29,unlock−50.4;nativecrop29 vs50.4. Foregroundframes separate.
NativeRGBANDalpha contain edgevignette(alpha52..255). Source-shapedrestorations
andnative4:3retain alpha/padding/fade. Widecoverage deliberately replacesperipheral
oldedgefade andmoves96pxvignette toouterviewedge. Trustedinterior40..659native
isRGBexact;fullwide4:3centerRGBAequality is explicitlyNOTclaimed. Do not generalize
this backgroundcoverage decision toemblem/portraitalpha orloaderconstraints.
Sixbuilt-in calls/92pilot total:1restoration,1rejectedfull-referenceleftrepeat,
source-onlyleft/right plus2fullheight256pxsidebridges. Do notsupplyfullwall as
secondary compositionref when blanktargetmustextend;use narrowfixednativecontext.
Prompts forbid warmth/yellowing/newobjects/rowchanges,requiremortar/material/
lighting/graincontinuity. RestorationonlytinyLhighpass(Gaussian4,±1.5L×.35),
sourcealpha/padding/seam/edges exact. Sides native-density,LabGaussian64rowmean/
contrast(gain.6..1.4),bridge sourcehalfdiscarded/16pxedgecondition/64pxouterblend.
World5256×1440,origin−512native,core1656..3513;3labels×5ratios,original/wipe/
native4:3/joins/checkerboardalpha onreview51738. All1051priorPNGs/52Battlepins
unchanged. Browser15×6+2alpha loads,wipe50%,center1920/aspectlock,bounds75%,
draft+side/nooverflow/zeroerrors. Exactjobs/raws/rejections/recipes coordinating
pilot-v1/rewards-v1/. Newprivate menu-ui-rewards-v1-battle-approved-20261019 overlay;
earlierarchivesimmutable. NewwallDRAFT;ownerreviewnext,gamevalidationlater.
No8768writer/17candidate/Trejo changes/import/install/game/build/runtime/commit/push.


## Rewards wall approved; High Scores draft — 2026-10-19 D152-D153

Owner approves sharedwall;27current files pinned rewards-approval-20261019.json,
including reviewedwidevignette policy. All27+52Battlefiles frozen. NewHighScores
isindependent:640×480,names2/1,opaque512×512+128×512,root0,0,32paddingrows.
SimilarRewardswall failedlimitedRGBregistration;do not reusepanorama byappearance.
3built-in calls/95total. Wholeboard native[48,86,588,440] protected,sourcealpha/
padding/seam exact. TinyLabL highpass outsideboard only(Gaussian4,±1.5L×.35),
no rawmodelboard pixels adopted. Side targets1744×1440 haveblank1600 +native
brick144,boardexcluded. Requirecourse/material/lighting/softness continuity,
forbid addedwarm/yellow,newboard/text/objects/rowchanges. New sidesnative-density
534×480->1600×1440,LabGaussian64profiles/gain.6..1.4,16pxedgeconditioning.
No sourceblur/grade/warp. Master5120×1440 center1600..3520 exact,all5crops.
1126priorPNGs/79approvedpins/wholeboard/alpha/padding/seam/5centers exact.
Review51738 firstpanel withoriginal/wipe/center/bounds/joins andnative/Faithful
texturecomparison;5ratios×6+2refs×2imagesload,wipe50%,center1920/aspectlock,
bounds75%/draft+side/nooverflow/zeroerrors. Exactprompts/raws/recipes coordinate
pilot-v1/hiscores-v1/;source report menu-hiscores-background-results-2026-10-19.md.
Private menu-ui-hiscores-v1-rewards-approved-20261019 overlay,earlierarchives
immutable. HighScoresDRAFT;ownerreviewnext. Remaining21refshortlist includes
result/rematch/reward-earned papers,Extrasnotes,Storyphone,not21backgrounds.
Mapatlas/alpha first;preserve handwriting/keycaps/rules. Softlightmaps staysoft.
Nativegameintegration/checks remainlater. No8768/17candidate/Trejo writes/
import/install/game/build/runtime/core/commit/push.

## High Scores approval / result-paper batch — 2026-10-19 D154-D155

High Scores v1 APPROVED by owner: "High Scores is approved lets move on".
`hiscores-approval-20261019.json` freezes13current artwork files; earlier raws,
rejected proposals and native game acceptance excluded. Battle/Rewards/HighScores
approval manifests total92pins,all exact. Other earlier approvals remain in their
own manifests. No approved PNG changed.

Next batch `pilot-v1/results-v1/`: six source-shaped paper panels,18source tiles:
rematch1;matchSm1 11/10/9/8;matchSm2 18/17/16/19;matchSm3 21/19/18/20;
matchSm4 15/14/13/16;rewardun1. All6 drafts unapproved. Source UVs/material/root
matrices/ancestors/frames audited in `next-scope/result-panels-metadata.json`.
`references.json` preserves source IDs/full hashes and stage placements.

Six built-in image_gen edit calls,101pilot total; no CLI. `jobs.json` is the exact
request set. `generations.json` adds input/raw hashes and adoption decisions.
All inputs were viewed before generation. All raws requested true transparency
and remain unmodified, along with normalized proposals. Generated silhouettes,
alpha, printed ink, crease placement and broad lighting are excluded from
assembly: source alignment/alpha stay authoritative after prior black-fill
feedback. No newly invented text, scores, stars, boxes or rows are adopted.

`prepare.py`: immutable source copies, native APT mosaic and4x reference.
`assemble.py`: tile-aware4xLanczos faithful RGBA basis (same resampling as individual
tile exports). Active mosaic is assembled from those exact tile candidates.
Use only fine RGB luminance residual from Gaussian4 raw at*.14 capped±1.25L,
remove mask-weighted mean, retain source Lab a/b before8bit rounding. Safe paper
must be fully opaque after25pxMinFilter, L>61,RGB spread<85; source gradients
>20 across8px are expanded25px and protected. Paper-detail masks feather4px
inside safe area. Entire printed bands/header/score cells are excluded; rematch
safe y64..143,results safe y112..232 or337..355. Reward card protects full
native[12,15,443,312],including every red/star/black graphic. Source tile/UV edges
have4nativepx guards; all tile outer16output pixels and unusedUV are exact.
Max actual RGB delta4/255 (reward3),adopted changes only0.22%reward and6.06..9.47%
other active pixels; hue means limited by8bit roundoff (abs mean a/b<.0021).
Full masks/statistics/checksums are in `assembly-receipt.json`.

Special geometry: matchSm4 bottom-right starts y255,not256; source1row overlap
and mapping preserved. Narrow edge tiles/padding retained,not stretched.
Stage placements at640×480:rematch184,233;Sm1 194,66;Sm2 50,60;Sm3 43,65;
Sm4 44,66;reward110.5,68. Exact APT matrices retained in audit. Preview rounds
Sm2 .05native materialshift and reward110.5×3 to332 (-1/6nativepx); these are
review studies,not runtime geometry changes. Five1440-high stage sizes1920,
2304,2560,3360,5120:transparent larger margins,original scale/placement and4:3
viewport centered. No panel outpaint or widescreen stretching; backdrop/live
text/lighting/animation remain separate.30original/draft pairs have exactcenters.

Verification:1161priorPNGs unchanged,92Battle/Rewards/HighScorespins exact,
18tile alphas/unusedUV/edgeguards and6mosaic alpha/protected pixels exact.
Browser6panels×5ratios×2stage images +6×2refs×2channels×5texture/raw images load;
checker/dark/light backgrounds expose true transparency,img CSS transparent;
wipe50%,draft-only/side,bounds75%/12.5%at16:9,HighScoresapprovedstatus pass,
no horizontaloverflow/consoleerrors. `browser-verification.json`,`review-proof.png`.
Review defaults4player/original/RGBA/checker/side;stage16:9collapsed.

Source report `docs/research/menu-result-rematch-panels-2026-10-19.md` and both
projects' handoffs updated. Private immutable archive
`<data>/scratch/menu-ui-results-v1-hiscores-approved-20261019`;apply overlay to
COPY of earlier pilot;do not overwrite earlier archives. Authoring writer8768,
17workshop candidates andTrejo untouched. No import/install/game/build/runtime/
core edits/commit/push. Nextownerpaperreview;then Extrasnotes,Storyphone and
remaining frames after mapping. Nativegame acceptance stillpending.

## Six menu papers approved / remaining census — 2026-10-19 D156

- 2026-10-19 D156: owner APPROVESall6results/rematch/reward-earned panels;
  results-approval-20261019.json freezes60files/18tiles/6mosaics+alphas/30stage
  studies. NoapprovedPNGchanged;101pilotcalls unchanged,nogeneration. Review
  51738firstsectionapproved;nativegameacceptance separate. Remainingunique
  source-IDcensus:71covered(63approved+8conditionalMode),1,252/1,323registered
  flows notcustomrestored;core1,763/1,834,broad11,190/11,261. Scopesoverlap,
  existingFaithfulHDcoverslibrary;notbackground/jobcounts.23confirmednextart:
  Extras4/phone2/venueframes3/title shield+localizedStart8/supportemblems6;
  additionalframes/popups/Story/header/Extrasfragments stillneedclassification.
  Exactcoverageledger/remainingCSV inpilot-v1/results-approved-v1/;source report
  menu-ui-remaining-inventory-2026-10-19.md. Newimmutable privateoverlay
  menu-ui-results-approved-inventory-20261019,applytoCOPYofearlierpilot.
  NextExtrasnotes thenStoryphone/venue/popup/title/support;noautomaticmassbatch.
  Modeconditionalrightlighting,Optionsscroll andallnativeintegration/testing
  later. No8768/17candidate/Trejo writes/import/install/game/build/runtime/core/
  commit/push. Earlierblocks historical.

## Pause and modpack handover — D157/UI

- 2026-10-19 D157/UI — RESTORATION PAUSED at owner request until credits return.
  Do not generate/repaint or advance Extras/phone queue. Engineering handover:
  game repo docs/menu-ui-modpack-handover.md;71sourceIDs(63approved+8conditional),
  226pinnedartfiles/12scopes,101historicalcalls. Native-shaped sparse testpack first,
  widescreengeometry/UV/scissor separately. Brandingv2approvedrawcanvases need
  native-shape registration;do not use unapproved old source-safe alternate.
  Fullprivate snapshot <data>/scratch/menu-ui-restoration-paused-20261019/
  session/pilot-v1,manifest-bound. Existing8768writer/17candidates/Trejo untouched.
  Source-only recipes/prompts/reviewcode preservedin research/menu-ui-pilot-20261017;
  publicbranch codex/menu-ui-art-source;gamerepobranch codex/menu-ui-modpack-handoff.
  Art/arrays/reviewJSON/captures staylocal. No newgeneration/import/install/game/
  build/runtime change. Nextagent implementsplaytestpack;restoration resumes only
  onVlad's explicitrequest. Previousstatusblocks beloware historical.

## Resumed Extras paper pass — 2026-10-20 (D161/UI–D162/UI)

Vlad explicitly resumed restoration after the HD/widescreen playtest. The old
pause is historical. Existing approved bytes, the 8768 workshop and its 17
candidates remain unchanged. PR62 carries the implemented menu pipeline and
PR73's settings fix; current combined toolkit is dd63e17 on defjam/menu-wide.

Extras has four separate notes, a four-tile list sheet, and a small ribbon:
nine native source tiles, six logical studies. Generate the five larger papers
with genuine transparency, original colors and no new text, retaining the raw
attempts. Keep the tiny ribbon Faithful HD. Alpha is authoritative; green stored
RGB is not a color key. Do not outpaint these small foreground panels or enlarge
them to fill widescreen. APT geometry and live text remain separate.

Use tile-aware 4x Lanczos as the final geometry/alpha authority. Adopt only 14%
of the raw proposal's fine brightness residual (Gaussian radius 4 output pixels,
clamp ±1.25 Lab L, weighted mean removed). Source a/b and broad folds remain the
authority. Exclude partial alpha, silhouettes, strong source edges, the whole
arrow/red-line bands, list border/header/rules, unused UV areas and four-native-
pixel tile guards. This pass is intentionally subtle: final RGB changes are
at most four levels; the ribbon is exactly Faithful HD. The square arrow raw
has 3.43% canvas-aspect drift: it supplies only masked fine material detail;
its geometry, alpha, arrow and fold layout are rejected. Do not reuse that
normalization as permission to warp a structural or widescreen seam repair.

Review native/Faithful references, RGBA/alpha, checker/dark/light, wipe, and
five isolated placement studies. The latter show the centered 640x480 viewport
and original paper size; they omit live text, state visibility and animation.
Preserve exact material matrices for runtime export; preview rounding is not a
runtime coordinate. All six new studies are UNAPPROVED and review-only.

The Press Start pan is a separate ten-tile trans/t1 scene. Assemble and restore
it as one continuous tall scene, then extend both sides from the FINAL center.
Check every vertical tile join and BOTH original side bounds over the whole pan:
brick courses/material, stair rails, lighting, grain and focus must continue.
Measure the moving runtime geometry before wide registration. Existing wide
menu anchors do not cover this scene. No pan fix is claimed by this art pass.
