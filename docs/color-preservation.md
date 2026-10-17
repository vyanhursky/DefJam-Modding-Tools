# Preserve original skin color during restoration

Status: proposed workflow, not implemented color processing. Existing candidate
images and owner reviews are unchanged.

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

## Recommended next pilot

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

Start with Trejo's current v4 as a new child revision, then reuse the verified
process on Blaze and Nyne. Existing generations may be reusable without another
imagegen call. No automatic color pass or new art revision was applied here.

## Sources

- [OpenAI image prompting](https://developers.openai.com/api/docs/guides/image-prompting):
  state preservation constraints, inspect each edit, and composite protected
  regions when pixel identity is required.
- [Three.js color management](https://threejs.org/manual/pages/color-management.html):
  annotate color textures as sRGB, use a linear working space and sRGB display output.
