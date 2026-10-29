# Five-fighter clothing/headwear UV ownership audit — 2026-10-28

Read-only analysis of `models/{blaze,nyne,trejo,redman,rollins}/{geometry,index}.json` in `/Users/vlad/Code/defjam-data/hd-work/texture-workshop`, and source `/private/tmp/defjam-tools-hd-fighters-20261026/src/defjam_tools/color_trial.py`. No source/live/review changes, builds, exports, generation or game runs. Computational scratch and metadata-only tables are under `/private/tmp/`.

## Findings that affect implementation

1. Every fighter's pants and footwear are in `emc4_cloth~DJIrradTextureEnvmap_Skin4`. No hidden `nospec` pants/boots were found. All ordinary `nospec` geometry is at face/mouth height (Y approximately 19.1–20.6, narrow X); Trejo's `nospec_ALPHA_MatAlph` is also head-height (Y19.40–19.89). These should be held by the clothing correction. This is anatomical-position evidence; group naming alone does not identify a specific lip/tooth/hair image region.
2. Blaze, Nyne and Redman have headwear triangles in the cloth group; Trejo and Rollins have zero cloth triangles wholly above Y19 and within |X|<2. Therefore “correct all clothes” includes headwear on the former three. Do not blindly hold the entire upper-right quadrant as the old face protection did.
3. Hair is **not a separately named material** in these meshes. Any skin-group hair/scalp/brows/beard remains inseparable by shader name. Head restoration needs an anatomical triangle mask and explicit image-region review; do not label the whole skin group as bare skin for calibration.
4. Blaze and Nyne have true skin/cloth UV intersections, not only raster edge contact. One atlas pixel cannot receive independent skin and clothing color corrections. Subtract skin (and preferably a one-source-texel guard) from cloth, retaining the already matched skin in the overlap.
5. Old `color_trial.geometry_masks()` intentionally edits skin only and holds every other group; it does not correct clothes. Its `color_field()` also rejects dark/neutral colors (`L>32`, chroma>8), so reusing that skin calibration unchanged misses black trousers, gray/white shirts and neutral shoes. Build garment-specific calibration rather than one global desaturation or a renamed skin mask.
6. Preserve full source alpha exactly. It contains material/shader data, not merely opacity. Color calibration and masked assembly should operate RGB only. Keep eyes/eyelid alpha/jewelry and mouth groups out of the clothing field.

## Conservative cloth coverage at 512 source texels

Raster matches `geometry_masks`: PIL triangle fill at `(u*512,v*512)`, excluding exactly zero-area UV triangles. Extents below are metadata bounds **not fill rectangles**. Raster overlap counts include triangle-edge pixels and differ from exact polygon intersection area.

| Fighter | Cloth source pixels | Skin/other overlap held | Cloth minus every other material | Cloth triangles | Wholly head cloth triangles* | Wholly low shoe triangles** |
|---|---:|---:|---:|---:|---:|---:|
| Blaze | 141,477 | 32 | 141,445 | 3,859 | 247 | 877 |
| Nyne | 99,200 | 314 | 98,886 | 1,963 | 248 | 536 |
| Trejo | 53,126 | 0 | 53,126 | 1,608 | 0 | 622 |
| Redman | 141,963 | 0 | 141,963 | 3,451 | 286 | 747 |
| Rollins | 59,438 | 0 | 59,438 | 1,722 | 0 | 789 |

\* All three triangle vertices Y>=19 and |X|<2; a bounded location probe, not final hair/hat segmentation.\
\** All three vertices Y<3.5; proves footwear is covered by cloth but excludes upper boots/pant joins.

These triangle counts include degenerate source topology, although rasterization excludes zero UV-area triangles. Data live in `/private/tmp/fighter-mask-metadata-20261028.json`.

### Actual shared UV cases

A separate convex-triangle clipping pass confirms genuine positive-area overlaps:

- **Blaze:** cloth RM29 triangles208/209 intersect skin RM0 triangle141 at source bounds `(489,114)–(493,122)`. Two intersections sum to16 source square texels. Both are head-height ownership; guard skin here to avoid headwear/skin bleeding. The 512 raster finds32 pixels, four survive both masks'1px erosion.
- **Nyne:**136 positive-area triangle-pair intersections; skin/cloth duplicate/shared triangles make the summed416.416 square-texel pair area **not a union measurement**. Intersections occur in cloth/skin RM pairs `(3,14),(3,15),(5,14),(6,14),(6,15),(6,16),(10,14)`. Combined bounds `(257,39)–(387,509)` span multiple disjoint locations, so holding that whole box would be excessive. Example head overlap is `(374,39.75)–(387,43)` (clothRM6 triangle194, skinRM16 triangles33/36). Raster finds314 pixels,59 remain after1px erosion of both masks. Use raster union subtraction, not a guessed box.
- **Nyne jewelry:** opaque jewelry vs alpha jewelry shares78 raster pixels (36 after both1px erosions). Both remain held during clothing calibration.
- **Trejo/Redman/Rollins:** no cross-group raster intersections at512 with this method. This is not proof of zero filtering bleed at runtime; use an unused-atlas-only gutter and per-material guards.

Exact-clipping scratch: `/private/tmp/fighter_exact_overlap.py`. Raster scratch: `/private/tmp/map_fighter_masks.py`. These produce no artwork exports.

## Group UV bounds

Each bound is `[xmin,ymin,xmax,ymax]` in a512×512 source atlas, top-left origin as the existing code. Multiply by4 for2048 draft coordinates. Group bounds often cover disconnected islands and must not become edit rectangles.

### Blaze

| Group | UV bound | Ownership/hold |
|---|---|---|
| emc2_skin | [256.94,1,510,510] | Face/scalp/body; previously matched skin. Hair not separately identified. |
| emc4_cloth | [2,1,511,511] | Shirt/pants/footwear and headwear. Head-only triangle bound [257,31,511,255]. |
| emc1_eye | [371.49,174.43,411.52,214.46] | Hold for clothing; eye material separate. |
| nospec | [309.51,194,411.51,255.5] | Head/mouth-height; hold for clothing. |
| eyelid_ALPHA | [440,1,454,8] | Hold RGB and alpha during clothing correction. |
| emc3_jewelry | [116,15,379,338] | Hold; no head-only triangles in Y19 probe. |
| emc3_jewelry_ALPHA | [8,215,214,246] | Hold; a few earring/head-height triangles exist. |

### Nyne

| Group | UV bound | Ownership/hold |
|---|---|---|
| emc2_skin | [2.06,2,511,510] | Body and head span most atlas; no single quadrant skin mask is adequate. |
| emc4_cloth | [2,1,511,509] | Pants/footwear and headwear; head-only bound [257,1,511,56]. |
| emc1_eye | [471.31,215.31,511.69,255.69] | Hold. |
| nospec | [368,172,470.5,255] | Head/mouth-height; hold for clothing. |
| eyelid_ALPHA | [430,184,438,188] | Hold. |
| emc3_jewelry | [453.29,306.2,508.76,318] | Hold, shared with alpha jewelry. |
| emc3_jewelry_ALPHA | [375,260,507,317] | Hold; some head-height triangles. |

### Trejo

| Group | UV bound | Ownership/hold |
|---|---|---|
| emc2_skin | [1,1,511.14,511] | Body/face/scalp; large tattoo coverage. Keep prior matched skin and tattoo contours intact in clothing pass. |
| emc4_cloth | [1,1,285.21,511] | Pants/footwear; no head-height cloth. |
| emc1_eye | [373.5,215.48,413.53,255.52] | Hold. |
| nospec | [260,176,372,255] | Head/mouth-height; hold. |
| nospec_ALPHA | [257,324,381,347] | Face-height separate alpha part; not clothes. Could contain facial detail; semantic identity needs image review. |
| eyelid_ALPHA | [260,216,264,218] | Hold. |
| emc3_jewelry | [258,257,511,328] | Hold; buckle/jewelry semantic boundaries are not established by shader name alone. |
| emc3_jewelry_ALPHA | [211,258,486,311] | Hold; some head-height triangles. |

### Redman

| Group | UV bound | Ownership/hold |
|---|---|---|
| emc2_skin | [257,33,511,511] | Head/body; head-only bound [257,33,511,366] reaches body-island coordinates through shared head UVs. |
| emc4_cloth | [1,1,511,511] | Shirt/pants/shoes and headwear; head-only bound [257,1,511,240]. |
| emc1_eye | [471.51,215.48,511.54,255.52] | Hold. |
| nospec | [369,197,470,255] | Head/mouth-height; hold. |
| eyelid_ALPHA | [354,245,367,252] | Hold. |

### Henry Rollins

| Group | UV bound | Ownership/hold |
|---|---|---|
| emc2_skin | [2,1,511,510] | Tattooed body and head/hair; head-only bound [257,1,511,255]. |
| emc4_cloth | [1,211,509,510] | Pants/footwear; no head-height cloth. |
| emc1_eye | [359.5,215.48,399.53,255.52] | Hold. |
| nospec | [257,198,401,255] | Head/mouth-height; hold. Its bounding box overlaps eye bounding box, actual raster polygons do not. |
| eyelid_ALPHA | [368,210,376,212] | Hold. |

## Suggested conservative assembly

1. Build each fighter's union of actual nonzero UV-area cloth triangles. Build the union of **all other** material triangles separately. Use `cloth & ~dilate(other,1 source texel)` for calibration/edit safety, holding prior skin exactly. An optional cloth gutter may extend only to unused atlas space, never into another material. Repeat masks at the exact integer2048/512 scale; do not interpolate mask boundaries.
2. Fit the cloth color correction against the **same fighter's own original/Faithful atlas**, within each connected garment island or a smooth local field. Sample dark and near-neutral fabrics too; do not apply skin chroma thresholds. Correct low-frequency a/b drift and broad L drift while retaining generated high-frequency weave/seams/lettering. Inspect white/gray/black patches separately so reduced overall saturation does not introduce a color cast.
3. Perform head-detail generation/assembly separately from cloth color correction. Headwear should receive the original garment palette on Blaze/Nyne/Redman after detail generation. Treat hair/scalp/face as distinct visually reviewed image regions within the head triangle coverage; geometry materials do not supply this semantic distinction.
4. Preserve existing matched body skin RGB byte-for-byte in the clothes-only stage. When joining a newly restored face, use only proven paired position-welded UV seam edges and original-palette neck guards. All protected seams in prior images stay held. A skin union cannot distinguish beard/tattoo/black hair, so exclude those ink-like areas from skin-palette fitting.
5. Verify per-output full alpha exact, outside-intended-mask exact, prior matched body skin exact, eyes/eyelids/jewelry/mouth held in the cloth stage, no shared-UV skin drift, and measured original-vs-draft low-frequency color error improved separately for cloth/headwear/skin. Review unlit RGB alongside studio lighting; studio differences can hide a residual tint.

Unresolved by this bounded audit: exact semantic hair/hat/skin islands, chain/buckle subregions, originality of newly generated tattoo/head details, and game-shader fidelity. These require main-agent image review and owner A/B review. No source edit or live review mutation was made.
