# Register approved menu masters for native export

`defjam_tools.menu_native` supplies mechanical registration helpers. It does not
generate artwork, change approvals, install packs or infer UVs from filenames.
The caller must freeze original source identities, approved raw hashes and
verified native material rectangles in a private recipe before using these helpers.

Use the original texture dimensions and a 4× native replacement canvas. Some
review references are already 4× exports: retain their existing replacement size
and use reference scale 1. Confirm that against the source inventory; do not infer
native dimensions from a review PNG alone.

For a whole word, `fit_canvas(raw, native_size, source_bounds, scale=4)` registers
its approved alpha-128 bounds to the measured original bounds. It performs one
Lanczos resize and rounded final placement, with a clipping receipt. This preserves
the approved raster; no font substitution, artistic sharpening or recolouring is
performed. Review the clipping receipt and preserve any real original clipping.

For words split across materials, render the complete master once, then call
`material_patch` with each verified source-UV rectangle and corresponding logical
joined rectangle. Every inserted region is checked byte-for-byte against the same
render. Never independently fit the two halves of one word. Preserve unrelated
native atlas pixels and original transparent gaps. `repeated_guard` updates a
one-texel gutter only where the original pixels prove exact edge repetition.

If a complete accepted master includes previously approved neighbouring materials,
record that context adoption and its precedence explicitly. Audit reconstructed
joins after all assignments, since a later master can supersede an earlier partial
context. Preserve independent constant/material cells, such as a detached white
atlas corner, unless it is actually part of the accepted artwork.

For a bitmap font page, `register_glyph_page` pairs occupied glyphs by row and
column order, then fits each approved glyph into its original cell/baseline. It
requires identical row counts and glyph counts and returns every source/raw/cell
rectangle. Detached accents within a row remain with their glyph. It performs no
OCR or retyping. This method requires a page with separable rows/columns; reject
ambiguous or touching glyphs and provide explicit mapping instead. Inspect the
registered page and test actual runtime text; a whole-page bounds fit is insufficient.

For proven runtime effect layers, `preserve_gray_marks` protects genuine opaque
RGB127 source markings at their original coordinates. These are data/ink, not holes.
Use only when source pixels and the layer role establish that contract.

Where static UV evidence proves a venue badge samples only an atlas prefix, fit
within that sampled region, add a clamped guard and clear genuinely unsampled
contaminated padding. Keep the complete source-sized canvas; a cropped badge is
not an installable replacement by itself. Retain the UV audit in the private recipe.

After assembly, use the existing RGB-bleed exporter with source alpha preserved;
verify alpha and visible RGB separately. Generate new file hashes, run the
[lossless PNG staging step](lossless-png.md), rebuild the complete pack manifest,
validate it with the released installer, and run serial save-guarded native checks.
Keep raw masters, source PNGs and recipes immutable. Artwork and runtime captures
remain private; only reusable code, synthetic tests and documentation enter Git.
