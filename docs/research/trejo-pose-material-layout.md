> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Trejo static preview: pose and material layout

2026-10-16. Bounded, read-only inspection of the owner's
`assets/v2ip.viv::V2IP_112A.o` and `V2IP_112A_F.o`, using the existing BIG and
RefPack readers. No game run, build, asset export or game-byte file write.
This report contains metadata/layout findings rather than asset arrays.
Offsets below are relative to the decompressed ELF **`.data` section** unless
explicitly identified otherwise. They are not guest virtual addresses.

## Result for the initial viewer

**Verified:** Trejo's stored position streams already assemble a recognizable
whole-model rest configuration in model space. Their aggregate bounds exactly
match the named model bounding box. A static texture preview should retain
these positions directly; it does not need to apply skeleton translations or
load `_F.o` merely to assemble the body. Animation, a particular in-game pose,
facial control, accurate environment shading and sparkle rendering remain
separate work.

**Verified:** the main model includes eleven named material groups covering
43 render-method resources. Main atlas bindings, optional environment inputs,
alpha passes and additive point-sprite passes can be identified through actual
ELF relocations and group tables, rather than inferred solely from filenames.
The primary atlas is named `A112` in the material bindings; the existing
workshop maps it to source ID
`1900051b32443a33a745c088a08231d039d80c9eb96483f4b43456a2a3f68f24`.
The source-ID correlation is established by the existing workshop census;
the ELF itself contains the shape name, not the source hash.

## Container facts and relocation handling

| Member | Decompressed bytes | `.data` bytes | Symbols | `.rel.data` entries | SHA-256 of decompressed member |
|---|---:|---:|---:|---:|---|
| `V2IP_112A.o` | 281,520 | 246,480 | 403 | 1,759 | `404617a26daced5c5d79147c04cd9aed6c8a5f45a8660cbf6d75bf3d4d7f03e3` |
| `V2IP_112A_F.o` | 2,704 | 2,144 | 4 | 6 | `550df3cc752fe6b79551bbe8eff846c80f71328427bd57fa494c1d74c064fbce` |

Both are ELF32, little-endian, relocatable data containers. `.data` starts at
file offset64. All inspected `.rel.data` entries have relocation type2, with
the addend stored at the relocation's target word. A local `.data` relocation
can therefore be resolved to its section-relative addend; an undefined-symbol
relocation must retain its symbol identity. An unresolved external binding's
stored word is often zero: reading that word alone loses its meaning.

The companion `_F.o` has only local `.data` relocations and exports
`__PosePaletteBank:::PosePaletteBank`. It supplies no undefined external
references and the main model has no undefined reference naming that bank.
This establishes **no direct ELF link dependency**, not that the engine never
loads or uses the bank by name.

## Exact model and material tables

The `__Model:::V2IP_112A_alpha` export is at `0x3c1f0`. Relevant fields:

| Model-relative field | Value/target | Verified content |
|---|---|---|
| `+0x00` | `0x3be00` | 22 named resource descriptors, each16 bytes |
| `+0x04` | 22 | Named descriptor count |
| `+0x0c` | identity4×4 matrix | Model root transform |
| `+0x9c` | 11 | Material-name/group count |
| `+0xa0` | `0x3baf8` | Eleven pointers to material-name strings |
| `+0xb4` | `0x3b990` | Model name string |
| `+0xbc` | `0x3bf7c` | Three16-byte texture-name/binding records |
| `+0xcc` | `0x3b8b4` | Group table: initial zero word, then eleven count/pointer lists |

The group-table pointers target wrapper records exactly `0x38` bytes after
the corresponding `__RM:::__GP_RM_V2IP_112A_alpha_N` export. Each wrapper's
first word relocates back to that RM record. Thus material-to-render-resource
association is explicit and checked for all43 resources.

| Group | Material string, shortened only after its semantic name | RM numbers | Bound atlas/input | Explicit state evidence |
|---:|---|---|---|---|
| 0 | `nospec` | 0 | `A112` | Triangle strip; depthLEQUAL |
| 1 | `emc1_eye~DJIrradTextureEnvmap_Skin1` | 1 | `A112`, `spectexture1` | Triangle strip; depthLEQUAL |
| 2 | `emc3_jewelry~DJIrradTextureEnvmap_Skin3` | 2 | `A112`, `spectexture3` | Triangle strip; depthLEQUAL |
| 3 | `emc4_cloth~DJIrradTextureEnvmap_Skin4` | 3–9 | `A112`; initial block also binds `spectexture4` | Triangle strip; specular state |
| 4 | `emc2_skin~DJIrradTextureEnvmap_Skin2` | 10–36 | `A112`; initial block also binds `spectexture2` | Triangle strip; specular state |
| 5 | `Direction` | 37 | No texture binding | Triangle strip; texture disabled; LitGouraud |
| 6 | `eyelid_ALPHA_MatAlph` | 38 | `A112` | Triangle strip; alpha compare0; alpha blend |
| 7 | `nospec_ALPHA_MatAlph` | 39 | `A112` | Triangle strip; alpha compare0; alpha blend |
| 8 | `emc3_jewelry_ALPHA_MatAlph~DJIrradTextureEnvmap_Skin3` | 40 | `A112`, `spectexture3` | Triangle strip; alpha compare0; alpha blend |
| 9 | `bling1_silver_MatAlph~DJFXSparkle_Skin` | 41 | `blg1` | Point list; sprite/scale enabled; additive; no depth writes |
| 10 | `bling4_diamond_MatAlph~DJFXSparkle_Skin` | 42 | `blg4` | Point list; sprite/scale enabled; additive; no depth writes |

The literal unresolved shape-binding symbols contain
`SHAPENAME=A112,1`, `SHAPENAME=blg1,1` or `SHAPENAME=blg4,1`, with clampU
and clampV. The model's three texture-name records also associate `A112`,
`blg1` and `blg4` with those bindings. ParentRM and shader relocations identify
IrradTexture/Envmap/LitGouraud/Sparkle families; this is stronger evidence than
the string labels alone. Continuation blocks may omit repeated state or
environment bindings, so a decoder should preserve group context rather than
require every submesh to repeat a complete material declaration.

The 22 named descriptors include `Coordinate4::EnvmapColour1` through4,
`IrradLight::IrradBlock`, `Light::LightBlock`, five `GeoPrimState::State`
instances, and sparkle coordinate/intensity/size/type resources. The two
`TAR_stage3::VId_0::Texture` descriptors reference `blg1`/`blg4`.
This describes explicit resource naming; it does **not** establish a complete
NV2A combiner emulation or a mapping from `spectextureN` to the corpus's
`br01`/`br02` images. Do not label those images normal/specular maps without
further evidence.

For the first unlit/RGB viewer, use `A112` for the regular textured geometry,
keep the three alpha-pass material partitions, and clearly identify simplified
material response. Point sprites are effects and should not be decoded as
triangles. Omitting their glints is a disclosed preview limitation; it is not
the removal of the underlying jewelry geometry in RM2/RM40.

## Static position-space validation

A bounded position-stream statistics pass read the first position stream of
each RM group. Their stream headers report12-byte stride, bounded byte counts
and local data pointers; the first records are finite XYZ coordinates. This
pass examined bounds/counts only and did not export the arrays.

There are5,081 stored position entries over43 groups, including duplicate
seam/partition vertices and the helper/effects. Their aggregate AABB is:

| Axis | Minimum | Maximum |
|---|---:|---:|
| X | -11.4056892395 | 11.4056892395 |
| Y | 0 | 21.8813667297 |
| Z | -4 | 5 |

These values match the six float fields at
`__BBOX:::V2IP_112A_alpha` (`0x38980`) exactly at float32 precision.
The head/eyelid streams sit aroundY19–21, the clothing streams spanY0–12,
and arms/hands extend toX±11.4 aroundY17. This agrees with the independently
decoded skeleton's model-space joint positions below. The main model's root
matrix is identity. Together these establish a common assembled model-space
rest configuration suitable for the static viewer. Applying local bone TRS
again to the stored position streams would move them out of that configuration.

`Direction` RM37 has10 vertices boundedX±3.5/Y0–3/Z[-4,5], no atlas and no
animation-buffer binding. **Inference:** it is a direction/ground helper,
consistent with its explicit name and ground-level geometry. Expose it as an
optional component rather than silently presenting it as textured fighter
surface. It accounts for the model's extremeZ bounding-box values. The
47 sparkle points in RM41/RM42 lie around the actual jewelry, as expected from
their material bindings.

## Main skeleton layout and limits

The94 `__Bone:::root.*` exports occupy16-byte scalar records from`0x389a0`
through`0x38f70`; each record's first uint32 is its name-to-bone index. Those
indices form exactly0–93. The symbols themselves are **not** bone matrices.

`__Skeleton:::root` at`0x38f80` begins with a16-byte header. Its count at`+8`
is94. The records start`0x38f90`, have112-byte stride, and end exactly at
`0x3b8b0` before the following resource tag/table.

| Record offset | Layout | Evidence |
|---|---|---|
| `+0` | float3 scale | Near-unit scales; finite |
| `+12` | int32 parent record | Root=-1; every other parent precedes child |
| `+16` | float4 local quaternion XYZW | Near-unit rotations; hierarchy/matrix agreement |
| `+32` | float3 local translation | Finite positions; hierarchy/matrix agreement |
| `+44` | uint32 second index/permutation | Exactly0–93, different from record order |
| `+48` | 16float stored matrix | Row-vector storage; transpose for ordinary column-vector math |

The field at`+44` appears to pair/swap left/right subtrees: for example,
record2's field is84 and record84's is2. **Its precise runtime purpose remains
unknown.** Do not automatically use it as the skin-joint index or as another
parent field. Export-name indices identify the record order separately.

Using ordinary local `T*R*S`, parent-before-child composition, and transposing
the stored matrices, hierarchyWorld × storedMatrixTranspose is approximately
identity for90/94 records (errors below`1e-5`). Representative world joint
locations are rootY10.56, chestY14.82, headY19.22 and handsX±8.56/Y17.53.
This confirms Y-up and the local-TRS interpretation for the common skeleton.

Four records do **not** satisfy that inverse relation: PonyTail2(61),
placellip(73), placerlip(75), Pendant2(83). The largest identity-test error is
about4.33. These stored matrices are therefore bind/correction candidates,
not a promise of exact inverses of the adjacent current local TRS for every
joint. The cause could include authored correction/deformation data; it was
not resolved here. A future rig/animation exporter must preserve and explain
them rather than regenerate all inverse matrices from current local TRS.

No local relocation targets the skeleton header or its transform records.
It is a separately named resource; the render methods instead reference the
external `EAGLAnimationBuffer` and local palette-like data. The static preview
can avoid inventing that skinning relation by retaining the assembled source
positions.

## `_F.o`: established boundaries, unresolved semantics

`PosePaletteBank` at`0x848` contains a bank header and two local pointers at
`+8/+12` to`0x278` and`0x83c`. Their internal pointers lead to two data spans:
`0x000..0x26f` (624bytes) and`0x290..0x82f` (1,440bytes), plus small tables at
`0x270` and`0x830`. Descriptor words at`0x280` and`0x844` are`0x30d` and
`0x2040f`. Their exact count/flag interpretation is unverified. The spans
contain quaternion/translation-like float vectors, but no bone-name strings
or relocation back to the main model skeleton. Calling these final bind
matrices, or applying them wholesale to the mesh, would be guessing.

This companion is useful future pose/facial-control research. It is not a
demonstrated prerequisite for the unchanged static Trejo preview. The viewer
should explicitly claim a recovered static rest configuration, not a specific
in-game fight pose, verified animation rig or complete renderer replacement.

## Independent strip topology and winding check

At the main implementer's request, a second bounded pass independently checked
all41 triangle resources RM0–RM40, without exporting their arrays. RM41/RM42
remain explicitly point-sprite resources. Sort each RM's `__VB` symbols by
their numeric stream suffix: regular resources have strides12,8,4,4,2 for
positions, UVs, color-like data, packed normals and blend-like data. The
`Direction` helper instead has three streams with strides12,4,4. This check
does not establish the meaning of the blend bytes or color-channel policy.

The index parameter is not at one fixed RM offset. For the regular resources,
locate the relocation to external `EAGLAnimationBuffer`; eight bytes after
that relocation is a local pointer to an index header, followed by index
count and local index-data pointer. For example, RM0's count/data fields are
at`+0x6c/+0x70`, full environment-map blocks at`+0x74/+0x78`, and continuation
blocks at`+0x5c/+0x60`. The helper has no animation-buffer binding: its header,
count and data fields are at`+0x50/+0x54/+0x58`.

All11,674 stored indices decode as uint16 and are in their stream's vertex
range. None is a restart sentinel. Expanding each entire index sequence as
one alternating-parity triangle strip gives:

| Check | Count/result |
|---|---:|
| Triangle resources checked | 41/41 |
| Repeated-index degenerate triplets omitted | 5,605 |
| Emitted triangles | 5,987 |
| `Direction` helper triangles among those | 11 |
| Textured fighter triangles | 5,976 |
| Additional zero-area triangles at area threshold`1e-12` | 0 |
| Out-of-range index triplets | 0 |

Strip parity must advance through the degenerate connectors; dropping those
indices before expansion changes the subsequent topology/winding. The checked
convention is `(i-2,i-1,i)` at even index positions and `(i-1,i-2,i)` at odd
positions, omitting triangles with repeated vertex indices only after parity
selection.

Packed normals were independently decoded as signed X11/Y11/Z10 bit fields.
Before normalizing, their vector lengths lie in approximately0.9978–1.0000,
consistent with unit normals quantized to this layout. For every nondegenerate
triangle, compare its normalized geometric cross-product against the normalized
sum of its three stored normals:

- The expansion above yields a **negative** dot product for5,977/5,987
  triangles, with median`-0.98556`.
- Reversing every emitted triangle produces a **positive** dot product for
  5,977/5,987, with median`+0.98556`.
- All ten remaining sign outliers are in RM0 (`nospec`, around the mouth/head
  region). Every other triangle resource, including all cloth/skin/jewelry/
  alpha/helper blocks, agrees after the same reversal.

Thus the exporter should reverse the expanded triangles for glTF/Three.js's
CCW front-face convention **while retaining source XYZ coordinates**. If a
later coordinate conversion reflects an axis, account for its negative
determinant exactly once; an extra reversal would invert the result again.
Do not conceal an incorrect orientation with universal double-sided materials.
The handful of RM0 normal disagreements should remain recorded as source
normal/geometry exceptions, not trigger per-face guesswork that alters the
original triangle organization.
