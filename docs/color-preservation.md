# Preserve original skin color during restoration

Status: Trejo v4 deterministic pilot implemented and imported as two new
unapproved drafts. All 11 prior candidate files/records and existing reviews
remain unchanged. Reuse on other fighters requires their own mask/seam review.

## Evidence, 2026-10-16

Vlad reports warmer/yellower generated bodies against untouched faces in the
model viewer. The latest Rich Original Detail draft for each pilot was compared
at matching UV coordinates with its faithful HD baseline. Original skin-material
triangles define a diagnostic mask, eroded one source texel; protected boxes are
excluded. Sample warm midtones (R > G > B, mean RGB 35..220) at source resolution.
This is an approximate unweighted body-color test, not exact neck-seam measurement
or a semantic skin segmentation. Shape and tattoo changes can affect the totals.

| Fighter | Sampled texels | Median change in Lab a* | Median change in Lab b* |
|---|---:|---:|---:|
| Trejo, Rich Original Detail v4 | 97,049 | +6.21 | +7.77 |
| Blaze, Rich Original Detail v1 | 19,212 | +4.35 | +4.93 |
| Nyne, Rich Original Detail v1 | 64,294 | +5.75 | +6.12 |

Positive a* is redder, positive b* yellower (CIELAB D65). Protected face boxes and
full alpha are byte-identical in all three comparisons. No PNG profile metadata
was present in these assembled images. The assembly currently resizes generated
RGB, restores alpha/protected pixels and applies parent-bound edit boxes; it does
not normalize body color. Raw PNGs and exact prompts are retained.

Both viewer lanes use the same sRGB texture/output handling and no tone mapping.
Use Texture RGB/unlit to judge color first; Studio is approximate colored lighting.
These observations support generated-pixel drift as a contributor, without
establishing exact parity with the game's own lighting/shaders.

## Workflow and controls

1. Keep original/faithful HD as the palette authority. Explicitly prompt to retain
   skin hue, saturation, brightness, painted shading and white balance, with no
   warm grade. This guides generation; it is not a pixel or color guarantee.
2. Create reviewed skin masks and UV seam bands. Keep the original face and alpha
   exact. Restore an original-colored band on the BODY side of the neck seam,
   tapering the correction inward with padding for filtering/mips. Atlas image
   borders are not necessarily UV seams; identify them from the mesh UVs.
3. Compare two controlled postprocess drafts: a gentle skin-only chroma correction
   toward corresponding original skin samples, and a spatial low-frequency color
   correction that retains generated high-frequency detail. Use masked/per-island
   sampling so blur does not mix clothing, tattoo ink, jewelry or empty atlas space.
   Keep original local gradients; do not flatten all skin to an averaged face tone.
4. Retain generated tattoo strokes, pores, fabric lettering and material detail.
   Exclude clothing/jewelry from skin calibration. Luminance and chroma/detail
   strength need separate controls; inspect for lost ink color, halos and clipping.
5. Keep raw, corrected and original views selectable in 2D/3D. Save masks, seam
   widths, color space, algorithm/version, strengths and source/parent hashes with
   every new immutable revision. Preserve notes and approvals on previous revisions;
   corrected drafts start unapproved.
6. Measure color drift in stable skin patches and seam discontinuity relative to
   the ORIGINAL seam under unlit rendering, at multiple zoom levels/mips. Then
   validate the approved pilot in game. A score alone cannot establish art fidelity.

## Trejo pilot, 2026-10-16

Vlad approved trialing the deterministic color pass on the retained v4 image.
Two child drafts of `r-a74be693951f4617` are in both gallery and model selectors:

- **Gentle** `r-8125b0d8196d4f61`: 75% per-connected-mask median chroma correction;
  generated luminance retained outside the seam guard.
- **Source palette** `r-342bd7dadb964b67`: full spatial chroma correction and 50%
  low-frequency luminance correction (bounded to +/-8 Lab L before strength).

The processor is `defjam_tools.color_trial`, available as `defjam-tools color-trial`.
It reads equal-resolution square RGB/RGBA PNGs, original decoded geometry, explicit
protected rectangles and required SHA-256 pins. It refuses changed inputs, an
existing output directory, insufficient skin samples or absent proven UV seams.
No workshop metadata is changed by this command. Import output PNGs separately
through `workshop import --server`, with the v4 parent and retained recipe text.
No server restart or review schema migration is needed.

Masks rasterize source skin-material UV triangles, conservatively excluding all
other material coverage and protected rectangles. One source texel of padding is
allowed only in unused atlas space. Separate connected mask regions calibrate from
stable warm midtones; clothing, jewelry and neutral/dark ink do not supply skin
calibration. Spatial correction uses a normalized, masked three-pass box blur at
six source texels per pass and an interpolated smooth Lab offset field. Dark or
neutral generated ink attenuates correction to avoid a compensating blue cast.
Parent pixels are never spatially resampled or warped.

The neck guard uses **ten welded 3D edges with different body/protected UVs**.
The measured Trejo region is normalized height 0.65..0.87 and center X +/-0.18
of model height. Every included edge is shared; the region filter excludes other
skin boundaries. RGB within three source texels is restored exactly from faithful
HD; the blend tapers to twelve. It has no inferred seam correspondence for other
models. Alpha and protected faces remain exact. Clothing/jewelry, other-material
UV coverage and all pixels outside the editable mask stay byte-identical to v4.

Private outputs retain processor/input hashes, parameters, masks and hashes,
paired seam UVs, invariant checks, PNG hashes and recipe text. Imported candidate
prompts retain the recipe and parent provenance. The exact processor source is
also retained with the experiment for reproducibility. Masks are diagnostic
geometry-derived starting points; they still need owner art review.

| Same-UV body diagnostic | Raw v4 | Gentle | Source palette |
|---|---:|---:|---:|
| Median red shift, Lab a* | +6.21 | +1.55 | 0.00 |
| Median yellow shift, Lab b* | +7.77 | +1.68 | -0.01 |
| Median lightness shift, Lab L | +1.11 | +1.00 | +0.50 |

99,509 warm body texels sampled; shape/ink differences still influence these
approximate unweighted measurements. At 90 samples one source texel inward from
the neck edges, additional Lab distance from the original is median 11.16 for
raw v4 and zero for both guarded drafts at full resolution. Simulated RGB Lanczos
1024/512 previews retain zero median added seam difference (maximum 0.59 at512).
This measures texture-pixel differences; it is not GPU mip or in-game parity.

Browser checks cover both drafts at Face/Chest detail, Source palette against
Faithful HD, rear/arm view and approximate studio lighting. The Source palette
trial is the recommended starting point for owner review: visibly reduced neck
step, tattoo stroke positions retained. There was no new imagegen call, tattoo
redraw, approval, game installation or in-game acceptance. The complete suite is
**67 tests +12 subtests passing**, including eleven new synthetic color/UV/provenance
checks. All existing reviews and imagegen request records were preserved.

Example (paths and pins come from the retained corpus, candidate and model receipts):

```sh
defjam-tools color-trial \
  --reference /private/faithful.png --reference-sha256 BASELINE_SHA256 \
  --parent-image /private/v4.png --parent-sha256 V4_SHA256 \
  --geometry /private/geometry.json --geometry-sha256 GEOMETRY_SHA256 \
  --asset-id SOURCE_ID --parent-id r-a74be693951f4617 \
  --protect-region 0.49,0,0.51,0.51 \
  --seam-height-range 0.65,0.87 --seam-half-width 0.18 \
  --output /private/new-color-trial
```

Next: owner compares the two drafts, especially tattoo ink/skin contrast, subtle
halos and side seams. Tune strengths/masks as new immutable outputs if needed,
then validate an approved selection in game before extending the pilot.

## Sources

- [OpenAI image prompting](https://developers.openai.com/api/docs/guides/image-prompting):
  state preservation constraints, inspect each edit, and composite protected
  regions when pixel identity is required.
- [Three.js color management](https://threejs.org/manual/pages/color-management.html):
  annotate color textures as sRGB, use a linear working space and sRGB display output.
