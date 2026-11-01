# CAF static assembly evidence

This describes the bounded source investigation used by the offline CAF viewer.
Addresses refer to the owner's Xbox executable. They are not a game-code payload.
The tooling keeps every derived model, palette and inspection image private.

## Texture registration

CAF builder `0x0009A050` loads four base resources `V2CP_[A-D]_[build]`, bound to
`cp_a` through `cp_d`. The measured source canvases are 256×256. Each source bitmap
can carry a linked FSH attachment chain; its header's upper 24 bits advance to
the next attachment. `0x001DF714` finds attachment `0x6F`, whose string at +8
contains comma-separated atlas letter, copy mode and optional integer fields.
`0x000A4510` initializes omitted fields to zero. `0x001DF775` finds attachment
`0x7C`; its signed x/y coordinates at +8/+12 are read by `0x000A4740`.

Mode `c` uses `0x000A46C0` / `0x001DDDDD` for direct bitmap copies. Mode `b`
uses `0x00092C00` / `0x001DDCCA` for blending. The decoded RGBA row at `0x001DDAAE`
keeps the destination at source alpha 0 and copies the source at alpha 255.
Otherwise each RGB channel is `(src*alpha + dst*(255-alpha) + 128) >> 8`;
the output alpha is the maximum of source and destination alpha. This evidence
resolves the shared-atlas origins that were unknown in the customization pilot.

The table at `0x002A4278` has 38 records of mount stage, texture stage and atlas
index. The compositor loops texture stages 0..3, then slots in their original XML
order. Face components and jewelry precede tattoo decals; grooming/hand maps
follow; clothing is last. Primary metadata integer 0 counts `al01..alNN` companion
maps. They retain their own placement and copy/blend instructions.

`0x000A4620` applies indexed alternate palettes. Positive stored skin values
select `plNN` directly; a selected part color uses its zero-based value plus one.
Thus part color 0 selects `pl01`. Source identity remains the original accepted
corpus identity, even when previewing an explicitly named alternate palette.

## Geometry and source builds

Raw CP mesh parts share coherent source-body coordinates. Existing mesh decode
preserves position/UV splits, source normals, triangle strips and material groups.
No guessed local crop normalization or generated body is used.

`0x00098EE0` derives a shape resource name from the selected model and the build
table A–F at `0x002E1B18`. The switch at `0x000997C0` applies generic shape deltas
only to upper body12, lower body13, shoes14, wristbands16/17, hands18, necklaces22,
bracelets23, watches24 and rings28. Build C is the baseline. Shoes/hands/rings use
the table at `0x002A4B84`: A/B share A, C/D retain C, E/F share F. Necklaces retain
their independent A–F shapes.

Neck3 selects complete `V2CP_530_0001_[A-F]` models (`0x00098820` through
`0x000989BC`). Facial hair21 uses a full-model A/A/C/C/F/F remap at `0x00098D40`,
with a suffix from face type modulo four. The initial viewer fixes face type 0
and uses the corresponding suffix 1. Head C/C1 and Norm/Long template changes
depend on face type rather than body build; other face types are not exposed.

`0x00026140` sets the morph weight, clamps 1 to approximately 0.9999, and calls
`0x001128D0`. The morph resource contains named semantic groups and channels;
each chunk has a 16-byte header: packed payload size/format, vertex count,
destination byte offset and render-mesh ID. The low 28 bits give payload bytes;
the upper bits specify component count and scalar width. Float3 Coordinates
chunks are added to matching original position arrays using the stored weight
(`0x00112210`), with source topology and UVs unchanged. Bounds, counts and finite
values are checked. Unknown layouts are rejected. A decoded byte-color morph on
one shoe is omitted from RGB rendering while its valid coordinate deltas apply;
this omission is surfaced in the preview.

The exact retail labels for the six source builds remain unproven. Static
coordinates and decoded deltas do not prove full skeleton animation, cloth fit
through poses, or hat/hair attachment compatibility. Native outfit comparison is
still a separate acceptance step.
