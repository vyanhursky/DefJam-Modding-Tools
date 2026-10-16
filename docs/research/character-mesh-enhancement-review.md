> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Character mesh enhancement: feasibility review

2026-10-15. Read-only research. No game run, build, code change, model extraction
to disk or generated artwork. **V** means directly verified from source or
own-dump metadata; **I** means a proposed engineering route or inference that
still requires a spike. This report does not establish a functioning model
import/export pipeline.

## Conclusion

**I — Feasible in principle, with a separate geometry workstream.** Better
textures can make muscles and jewelry look more detailed immediately. Rounded
silhouettes and actual chain links require mesh changes. The useful first
geometry experiment is a small shape/normal edit that preserves topology and
the original rig; a new high-poly body or fully modeled jewelry requires
substantially more format, import and runtime work.

## What is supported now

**V — The current replacement hook changes texture bindings only.** Its public
interface exposes source texture dimensions, bytes and palette; it has no model,
bone, vertex-buffer or triangle replacement API. See the exact pinned toolkit's
[texture_pack.h](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.h#L6-L19).
`texture_pack_bind()` ultimately calls `SetTexture` and leaves the title's
combiners/addressing/filtering intact
([binding](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L775-L795)).

**V — No ready mesh importer/exporter was found** in this project's scripts,
hooks or research documentation. The existing bounded HD selection tool decodes
SHPX images, not character geometry (`scripts/hd_assets.py:473-497`). BIG and
RefPack readers can inspect the surrounding container
(`scripts/big-entry.py:24-48`, `scripts/refpack.py:20-86`); those readers are not
mesh decoders or game-compatible exporters.

**V — PR17 still labels fighter/stage replacement as research.** Its proposed
`[entries]` layer would replace an archive member, but is not built. It does
not define a standard mesh format or implement a geometry importer. See
[proposed layers](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L82-L112)
and [feasibility table](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L236-L244).
The current toolkit path hook receives a const path for observation; that hook
alone is not an archive-entry substitution API
([kernel_path.c](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/kernel/kernel_path.c#L20-L22)).

## Own-dump metadata findings

**V — Bounded inspection, no bytes reproduced.** Read the BIG directory and
four small selected members of the owner's
`<data>/extracted/assets/v2ip.viv` in memory, decompressing them with the existing
RefPack reader. The archive has **234 entries: 156 `.o` and 78 `.xsh`**. This
extension count does not prove 78 complete playable characters or LOD coverage.

| Sample | Stored bytes | Decompressed bytes | Verified structure |
|---|---:|---:|---|
| `V2IP_003A.o` | 119,673 | 264,848 | ELF data container |
| `V2IP_014A.o` | 129,744 | 287,424 | ELF data container |
| `V2IP_113A.o` | 119,716 | 266,224 | ELF data container |
| `V2IP_003A_F.o` | 1,678 | 2,704 | ELF data container; PosePaletteBank symbol |

All four identify as 32-bit, little-endian, relocatable ELF, with six sections:
the null section, `.data`, `.shstrtab`, `.strtab`, `.symtab` and `.rel.data`.
None has a `.text` section. Header machine field is 8; that field alone should
not be interpreted as a new game executable or as proof of platform-native
code execution. These are asset members of the Xbox dump.

**V — The main samples retain useful named metadata.** The Blaze and D-Mob
samples contain EAGL-style bone exports, vertex-buffer symbol prefixes `__VB`,
render-resource names `__RM`, shader references and relocation tables. Bone
names include `root.neck`, `root.Pendant1` and `root.Pendant2`. The selected
small `_F.o` exports a `PosePaletteBank` symbol. Exact vertex layouts, weights,
index formats, hierarchy, bind pose and the role of each referenced resource
were **not decoded** in this review.

**V — Character-to-asset mapping exists.** Own-dump `fighter.xml` maps Blaze to
`V2IP_113A`, with `113B/113C` alternatives, and D-Mob to `014A` with alternatives
later in the table. These are metadata facts, not a guarantee that editing one
member changes every rendering context. Existing game research also identifies
20 world-joint positions used by gameplay (`docs/research/fighter-record-fields.md:25-30`);
that list is not established as the complete rendering skeleton.

**I — The named buffers/relocations are promising starting points.** They make
a targeted decoder more plausible than blind GPU-memory searching. ELF is the
outer relocatable container; it does not make the private data inside a Blender
mesh, nor imply a generic ELF importer understands skinning or materials.
Pendant-named bones suggest an existing attachment/animation opportunity, but
do not prove current chain geometry or physical chain simulation.

## Three distinct levels of change

| Level | What changes | Expected benefit | Current status |
|---|---|---|---|
| Texture restoration | Existing atlas pixels | Tattoo, fabric and jewelry detail; painted lighting cues | **V:** existing hook works; cannot add silhouette geometry |
| Fixed-topology geometry edit | Existing positions and/or normals; preserve counts/order/indices/UVs/weights/rig | Refine contours or lighting on a selected body region | **I:** best first geometry spike; decoder, checked writer and override still needed |
| New geometry | Added vertices/triangles/material chunks; possibly changed skinning | Rounder silhouettes and actual jewelry/chain links | **I:** separate importer/recompiler effort; not established supported |

In ordinary mesh tooling, smooth shading and subdividing the actual surface
are different operations. Blender's Smooth modifier moves existing vertices
without adding vertices; Subdivision Surface splits faces into smaller faces.
These are useful authoring operations after a game-specific decoder exists,
not evidence of compatibility with this game's `.o` assets.
[Blender Smooth](https://docs.blender.org/manual/en/4.1/modeling/modifiers/deform/smooth.html),
[Subdivision Surface](https://docs.blender.org/manual/en/4.2/modeling/modifiers/generate/subdivision_surface.html).

**I — Same-topology edits have limits.** Better normals can reduce faceted
lighting but do not round the silhouette. Moving existing vertices can improve
shape, within the original triangle layout; unrestricted smoothing can also
shrink muscles, erase the exaggerated style and open seams. Local sculpted
adjustments with protected seams/joints are a more useful audition than a
global smoothing switch. Disconnected chain links cannot be created merely
by changing the existing surface's texture or normals.

## Minimum implementation/research path

These are proposed steps, **not completed work**:

1. **Map one original model.** Decode one main `.o` and matching texture into
   a local static view; establish the accompanying `_F.o` member's role and
   dependencies. Establish vertex/index formats,
   material groups, UVs, split vertices, bone IDs, weights, palette chunks,
   bind-pose matrices and relocations. Preserve original IDs and hashes. Do not
   guess these fields from symbol names alone.
2. **Prove a no-op round trip.** Build a writer that preserves all unknown
   sections and references. Start with an unchanged asset; require structural
   validation and ideally byte-identical reserialization. A usable Blender or
   glTF bridge would be new tooling unless a verified external implementation
   is found. Merely exporting an OBJ loses the rig/weights and is insufficient
   for a reliable animated replacement.
3. **Provide reversible injection.** For the smallest local experiment, either
   patch a disposable copy of the archive with a checked entry writer, or add a
   named archive-entry override around the game's loader. Preserve original
   data and validate compression/decompressed-size assumptions. PR17's future
   `[entries]` contract is a suitable destination once actually implemented;
   the existing texture manifest cannot install `.o` models.
4. **Try one fixed-topology edit.** Preserve vertex order, indices, UV seams,
   weights, bone mapping and materials; change only known positions/normals in
   a bounded region. Keep bounds/quantization correct. If the format permits
   an in-place edit, this avoids rebuilding variable-size resource tables,
   but that possibility is still unverified.
5. **Add geometry only after the round trip works.** New vertices need valid
   attributes, indices, weights and palette mapping; new chunks need material
   and shader bindings, resource sizes, offsets, relocations and bounds.
   Added detail should first reuse the existing skeleton and animation.
   Blender supports weighted armature deformation, but the game-compatible
   exporter must translate that data to this title's limits.
   [Blender Armature modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/armature.html).
6. **Verify animation and budgets.** Compare rest pose and full-motion fighting,
   especially elbows/shoulders/neck, grapples, knockdowns, close-ups, shadows,
   alternate outfits and four-fighter scenes. Determine actual index/palette/
   draw limits and guest/host memory costs before choosing a polygon target.
   Native rendering does not automatically remove the game's own allocation
   and asset-streaming limits. Measure local performance rather than promising
   a high-poly budget from the host GPU specification.

**I — For jewelry, begin with a rigid pendant on an existing bone, or a modest
existing accessory refinement.** It is a smaller proof than articulated links.
A chain following existing bones is a skinned/attached visual asset; freely
swinging links with collision need a separately designed simulation/animation
integration. More links do not automatically create chain physics. Whether
existing pendant bones can be reused must be checked in the model and live
animation path.

**I — A host-only geometry replacement is an alternative, not an available
shortcut.** It could avoid recooking game data, but would need stable model and
submesh identities, matching transforms/poses/materials, draw lifetime and
shadow-pass integration. The current GPU layer sees vertex draws and texture
bindings; it does not expose the semantic character-model API that this route
would need.

## Packaging consequence

**V — Texture and geometry are different mod payload kinds.** PR17's index
design already keeps derived assets external and proposes archive-entry
replacement. A future geometry pack can target the named model entry and
declare its required loader version after this works. Its extension allow-list
example does not explicitly name `.o`; decide how to validate this title's
data-only model containers before allowing ELF-named assets generally.
See [submission checks](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L187-L203).
Do not distribute the full original `.viv` just to replace one model.

**I — Recommended scope:** retain the immediate texture pilot, and separately
authorize a one-fighter decode/no-op-round-trip/fixed-topology prototype. Defer
a whole-cast high-poly promise until that experiment proves editable geometry,
animation compatibility and a viable injection/packaging path.
