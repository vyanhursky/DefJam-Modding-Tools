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
