# Supplemental injury texture restoration

The owner chose damage/injury work on 2026-10-30 after the compatible ordinary
roster and four genuine costumes had been restored. These are additional maps
for existing fighters, not new characters or costumes. The first adopted batch
contains both br01 and br02 for twenty fighters, forty source IDs.

## Establish correspondence before editing

Inventory each source alias, image index/name, dimensions, own alpha and accepted
corpus hashes independently. Names such as br01 are insufficient to establish
material channels, damage thresholds, runtime blending or UV remapping.

For each selected map, source inspection and exact RGB comparison independently
established an unwarped256-square correspondence to the top-right head quarter
of its own512-square main atlas. More than75% of native RGB pixels match exactly;
visual inspection establishes the same facial features, hair and auxiliary tiles.
The changed areas visibly depict facial injuries. These findings establish an
offline art correspondence, not the game's runtime binding. Never reuse the
crop coordinates or75% threshold as proof for an unrelated texture family.

Pin the clean restoration revision and its whole-file hash. A clean head crop
is a cross-source reference, not a candidate parent of the supplemental source.
Final1024-square maps match the4x texel density of2048-square main restorations.
Preserve every original main texture and its approval state.

## Generate and assemble

Use the built-in imagegen skill, Rich Original Detail only, one source state per
call. Supply the original damaged RGB tile as edit target and the registered
clean restored head as material/style reference only. Save the exact prompt,
input hashes, raw result or exact failure before import. Do not retry a rejected
state through another provider or present its enlargement as restored. In this
batch five incomplete pairs were retained privately; five different restored
fighters supplied complete pairs instead.

Prompt constraints: preserve original likeness, closed-eye expression, baked
lighting, every UV island and existing mark's position/extent. Keep that state's
own restrained palette and severity. No added/healed wounds, swelling, red flecks,
invented words or borrowed marks from another state. Unknown scripts, separate
dental/eyeball and small material tiles need inspected holds. Alpha/material data
is excluded from the RGB study and restored from the own faithful map afterward.

Raw generations repeatedly intensified blood and invented small marks despite
these constraints. A prompt is not a lock. The adopted method deliberately uses
only bounded fine luminance from the new generation:

1. Derive exact native RGB difference support between the own injury source and
   the registered clean source. Inspect and retain it without thresholding away
   small source marks.
2. Start with the exact clean restored head. Within a declared two-native-texel
   transition around source changes, add own faithful injury RGB minus the own
   clean faithful crop. Record clipping; do not claim exact original injury color.
3. Extract generated high-frequency luminance, bound it to plus/minus3 Lab L,
   and use strength0.8 only inside the original change support, feathered inward.
   No generated chroma, broad red marks or shifted wound paths are copied.
4. Restore each state's own faithful alpha and inspected held RGBA tiles exactly.
   Trejo's states have different alpha values; borrowing sibling or main alpha
   is incorrect. Keep clean restored RGB exact outside transition and holds.

See `damage_detail.restore` and
`research/damage-batch20-20261030/assemble.py`. Freeze the exact processor files
and receipt hashes for each immutable stage. The clean references already supply
generated skin/hair/headwear detail; this pass adds restrained injury detail,
not a newly interpreted face or authenticated high-resolution wound geometry.

Do not overprotect an entire garment/logo merely because auxiliary tiles share
the head quarter. Scarface's initial broad lower hold reverted his restored P
jacket to the original. The final version reuses the registered clean HD jacket,
retaining only actual auxiliary and uncertain neck-script holds. Original stages
remain in private history.

## Review and delivery

Compare both states with their own originals, faithful maps and pinned clean head.
Inspect every named mark, eyelid/mouth/hair boundary and held tile after assembly.
Preserve source injury placement; fine original boundary/compression patterns may
remain visible. Record both baseline RGB clipping and generated gamut clipping;
these event counts may overlap. Pixel checks do not establish visual authenticity.

Import under each true supplemental source ID through the single live writer,
with new unapproved/unselected/not-game-verified revisions. Existing notes, files,
requests, camera choices and schemas remain intact. The ordinary2D gallery supports
saved notes/flags and25/50/100/200% comparison. Browse Full texture library, clear
other filters and search `damage-batch20-20261030` for this batch.

An optional head-quarter substitution on existing geometry is only a labeled
synthetic RGB diagnostic. It does not emulate alpha, injury switching or shaders;
never import that composite as a new main-atlas replacement or pack entry.

The static model resources inspected bind their main atlas, not br01/br02. Engine
blood/sweat states exist, but no inspected source path proves how these secondary
maps reach draw resources. Content-addressed replacement may behave differently
if the engine copies them into mutable main-atlas data. Before a release, verify
native texture identity, state switching, UV treatment, alpha/material response,
mips and continuity during actual fights. No runtime changes or release are part
of this art batch. Remind the owner to playtest Bonecrusher when preparing the
next HD Fighters test pack; visual approval is distinct from native verification.

## Audited palette quantization exception (completion108)

Lil Flip's own maps match the clean head layout but only52.67–55.07% of native
RGB pixels exactly. Direct face/ear/braid/watch/neck-script inspection and
81.70–85.56% correspondence within three channel values establish a small palette
quantization difference, not a warped correspondence. An explicit optional
`registration_rgb_tolerance=3` permits this case only with at least50% exact and
80% close RGB pixels. The default remains the strict75% exact gate. Tolerance
is bounded to integer0..3; it is not proof of correspondence by itself.

The source change mask still uses literal RGB inequality; tolerance never erases
small original marks. Alpha, holds, clean exterior and detail limits are unchanged.
The immutable Lil Flip stages pin the private version2 processor and record both
exact/close fractions. Broadly requantized Story main atlases use separately
audited full-state correspondence and own RGB deltas; they do not silently relax
this head-map gate.

Carmen B's shared br01/br02/br03 source visibly has no injuries. Its independent
head/hair restoration uses original layout and local source palette with actual
eye/dental/gutter holds, rather than fabricating damage from a misleading name.
Runtime purpose is unverified. Partial Xzibit/Banner injury-local studies retain
unenhanced clean material, remain incomplete and are excluded from full-restoration
counts. See `research/fighters-completion108-20261030/README.md`.
