> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Offline 3D texture review and Blender bridge

2026-10-16. Bounded read-only research requested by Vlad. Only this report was
written: no build, game run, archive modification, model export or game-byte
dump. **Verified** means inspected project/pinned-toolkit source or own-dump
metadata. **Proposed** means new work, not an available feature. External
documentation was checked on this date; links are primary sources.

## Answer and recommendation

**Yes, an offline orbit/zoom/A-B texture viewer is a practical goal.** After a
one-time geometry conversion, the same model can show original, faithful-HD
and Rich Original Detail revisions instantly without repeatedly launching a
fight. Blender can use that converted geometry too. **The missing capability
is a verified Xbox model decoder; building the viewport alone does not solve
that part.** Neither the current gallery nor the texture-pack hook loads or
exports 3D meshes.

**Proposed first milestone:** decode one complete Trejo `V2IP_112A` model into
an unchanged static preview, retain its UVs/material partitions, map its main
texture to the existing workshop source ID, and demonstrate a synchronized
original-versus-Rich-Original-Detail comparison in the local browser. Export
the same result as glTF for Blender. Do not gate this texture-review milestone
on editing models, importing them back into the game, animation export or a
complete venue. An unchanged *export* needs structural/visual validation;
game-compatible no-op *round-trip* tooling is a separate later requirement.

Vlad now prefers **Rich Original Detail only for future generations**. Keep
existing Stylized Remaster candidates as revision history; the useful A/B is
original or faithful baseline versus the chosen detailed candidate.

## Implemented foundations and remaining gaps

| Area | Verified now | Still needed for the viewer |
|---|---|---|
| Texture decoding | `scripts/hd_assets.py:473-505` exports selected SHPX images; corpus/workshop already retain original, faithful and revision PNGs | Connect each mesh material/texture slot to those stable records |
| Texture review | Workshop stores immutable candidates, hashes, parent revisions, flags, notes and normalized atlas regions | 3D viewport, model manifest, camera state and optional surface-to-UV annotation |
| Fighter identity | `fighter.xml`/`entity.xml` map Trejo to `V2IP_112A`, Nyne to009A, Blaze to113A and variants | Decode all mesh pieces/dependencies for a named rendering variant |
| Model containers | Prior bounded inspection found data-only ELF with named buffers, resources, bones and relocations | Vertex/index layouts, bone-space interpretation, hierarchy/bind transforms, materials and complete dependency graph |
| Renderer | Current pinned toolkit fetches attributes, builds triangle lists, runs vertex programs, exposes constants and binds texture stages | An export/capture observer; semantic model identity; a verified object/world-space export |
| Replacement packs | Existing schema1 texture replacements work | None for an offline preview; mesh replacement/import remains separate research |

The established fighter ELF findings are in
[character mesh review](character-mesh-enhancement-review.md); exact texture
IDs and aliases are in [pilot mapping](restoration-pilot-fighter-mapping.md).
This review did not re-decode the four earlier fighter samples or infer a mesh
format from the `.o` extension.

## Two extraction routes

### A. Read original model data directly — recommended first

**Proposed.** Extend the existing BIG/RefPack readers with a narrowly scoped,
read-only ELF asset reader. Follow section/symbol/relocation metadata to the
selected model's vertex streams, index/primitive resources, material groups
and transform data. Check every offset/count/stride and bound decompression;
record unknown resources instead of guessing. Start with the principal Trejo
member and enumerate its required companions, including the `_F.o` family
whose pose role is not yet fully decoded.

The first useful output needs correct positions, triangles, UVs and material
assignments for the *whole visible model*. It may be a fixed static pose. Do
not call it a T-pose until bind/rest transforms are established: positions may
be bone-local or otherwise require assembly. Original normals/colors and
secondary UVs should be retained if decoded; recomputed normals are a labeled
preview approximation, not a recovered original attribute.

**Why first:** it operates entirely on the owner's local dump, avoids a runtime
change and can ultimately obtain parts not submitted in a captured view. It
also supplies a reusable Blender bridge. **Unknown:** named ELF resources do
not yet establish their private layouts; this is a bounded reverse-engineering
spike with a concrete pass/fail output, not a claim of a ready generic importer.

### B. Capture decoded draws — fallback and cross-check

**Verified source:** pinned toolkit commit
`837e2c7ea65a3e8e9149978c7cc125810d2c4e35`, read from the populated sibling
checkout. The following paths are relative to that toolkit, not the game repo:

- `src/kernel/nv2a_pb_exec.c:650-729`: `fetch_attr` decodes float, color,
  byte/short and packed11:11:10 attributes from guest arrays or inline data.
- `:3250-3354`: GPU path gathers used float4 inputs and reindexes primitive
  batches into triangle lists. These are program inputs, not guaranteed fully
  posed object-space geometry.
- `src/kernel/nv2a_vsh_cpu.h`: program hash/used inputs/constants are exposed;
  `NvVshOutput.pos` is screen-space output, not a mesh position export API.
- `src/nv2a/nv2a_pgraph_d3d11.c:1612-1645`: draw receives inputs/indices plus
  vertex program and constants before backend submission.
- `nv2a_pb_exec.c:2885-2915` and `:3077-3092`: texture-source construction and
  additional stage bindings provide a correlation point for stable content IDs.
- `:614-648`, `:3209-3225`, `:3460-3558`: existing batch capture selects frames,
  traces attributes/first-vertex execution and logs extents/material state.
  **It does not serialize a complete textured model.**

**Proposed.** If direct decoding stalls, add an opt-in bounded observer at this
shared decoded-draw layer. Capture one selected character/pose once, then cache
the result for offline review. Preserve indices, all used attributes, program
identity/constants, texture content IDs, UV scaling, render/material state and
per-draw instance identity. Do not export only the post-viewport screen-space
vertices; determine a verified pre-projection posed/object-space point or
correctly reconstruct view space with the actual transforms. Skinning and
projection may be mixed inside the game program, so this still needs analysis.

One atlas hash can select body draws but cannot prove all eyes, mouth, jewelry,
secondary maps or other passes belong to that fighter. Conversely a shared
texture is not a unique model ID. Deduplicate shadow/outline/multipass draws
without merging genuinely distinct components. A capture only contains what
the title submitted; a complete rest-pose mesh, hidden geometry, skeleton and
animation do not automatically follow. A static captured pose may nevertheless
be enough to inspect Trejo's tattoo and belt.

This route requires a bootstrap run, possibly a suitable character-select or
other standing display if confirmed, then no fight for subsequent texture
iterations. Which front-end display exposes all parts is unverified. Generic
toolkit changes would follow the isolated-worktree/focused-test/game-regression
rules; none were made here.

**Optional diagnostics:** RenderDoc supports mesh/UV inspection before and after
vertex shading plus buffer export. Its current supported host list covers
Windows/Linux and relevant D3D11/Vulkan APIs; macOS/Metal is not a supported
capture route in its published table. It is therefore a possible Windows or
Linux investigation aid, not the recommended Mac authoring dependency or a
one-click Blender exporter. No capture of this port was attempted.
[RenderDoc features](https://github.com/baldurk/renderdoc/blob/v1.x/docs/getting_started/features.rst),
[mesh viewer](https://github.com/baldurk/renderdoc/blob/v1.x/docs/window/mesh_viewer.rst),
[API/platform table](https://github.com/baldurk/renderdoc#api-support).

## Browser viewer and Blender use the same local conversion

**Proposed browser experience:** add a 3D tab beside the existing flat atlas
comparison. Orbit, pan and zoom the original mesh; provide front/back and
tattoo/buckle bookmarks. Two synchronized views or a hold-to-toggle control
use exactly the same model, camera, pose, material settings and lighting, while
switching only the chosen texture revision. Keep original/faithful/Rich Original
Detail selectors, saved notes and flags. Save model hash, revision IDs, camera,
pose and lighting mode so the next session opens the same review.

Three.js provides a glTF loader and orbit/pan/zoom controls; these are viewport
components, not Def Jam decoders. Pin and serve dependencies locally with the
workshop. A/B material switching can be application logic. Its loader lists
material variants as an additional plugin, so an MVP need not depend on that
extension merely to compare two PNGs.
[GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html),
[OrbitControls](https://threejs.org/docs/pages/OrbitControls.html).

**Proposed shared interchange:** use glTF2 with per-primitive material groups,
positions/normals/UVs/colors and source IDs in `extras`, plus a private sidecar
for game-specific fields. Keep geometry fixed while the browser resolves the
selected PNG from the workshop. Use `.gltf` + `.bin` and separate local PNGs
for transparent authoring/provenance; an optional `.glb` is convenient to open
in Blender but embeds derived data just as the separate files do. Blender's
documented importer supports meshes, textures, unlit/materials and skinning;
it does not decode this Xbox ELF asset family.
[Blender glTF manual](https://docs.blender.org/manual/en/5.0/addons/import_export/scene_gltf2.html).
[Official Blender importer/exporter source](https://github.com/KhronosGroup/glTF-Blender-IO)
confirms that the glTF bridge is bundled with Blender; no Def Jam decoder is supplied by it.

Once decoded, full skinning can be represented by joint/weight attributes,
joint nodes and inverse-bind matrices. The title's joint palettes and weights
must be translated correctly; bone names alone are insufficient. A frozen
static export omits that requirement. glTF also preserves scene nodes and
material alpha modes, but does not directly describe arbitrary NV2A register
combiner programs.
[glTF specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

**Blender's role:** UV inspection, detailed painting, manual reference work and
future geometry authoring. A scripted setup can create original/faithful/detail
materials and cameras once the conversion works. Keep node/light settings
constant during A/B. Do not silently merge seam vertices, apply subdivision,
rebake textures, change UVs or substitute physically based shading during an
unchanged restoration review. A successful Blender import does not establish
a working exporter back to the game.

Searches found an AKI `.model` Blender add-on and a Def Jam *PSP* RenderWare
animation issue. Neither establishes support for these Xbox ELF/EAGL resources;
do not rename files and assume compatibility. No maintained ready-to-use Xbox
Def Jam importer was verified in this bounded search.
[AKI add-on](https://github.com/dotGrx/AKI-Model-Blender-IO-Addon),
[PSP-specific issue](https://github.com/Psycrow101/Blender-3D-RW-Anm-plugin/issues/16).

## Texture, UV and material correctness

These are **required validation points**, not claims of decoded meanings:

1. Map each primitive's material/texture slot to the original source ID,
   archive/member/index alias, source hash and candidate output hash. Reuse
   [the pilot IDs](restoration-pilot-fighter-mapping.md); do not persist a guest
   texture address as identity. Runtime/archive aliases still require correlation.
2. Preserve every split/mirrored UV, per-slot UV set, wrap/clamp/filter and any
   pixel-coordinate normalization. Check a labeled diagnostic atlas locally
   to catch flips and transpositions. Record handedness/up axis/unit conversion
   once; image dimensions changing512²→2048² must not change normalized UVs.
3. Preserve alpha separately. Fighter `br01`/`br02` purpose remains unverified;
   do not label them normal/specular maps from their appearance. Texture alpha
   can be a material-control input, not skin transparency. Capture alpha test,
   blend factors, culling and combiner use before assigning opaque/masked/blended
   materials. A PNG's minimum alpha is not enough to decide.
4. Provide an unlit/RGB inspection mode first, with alpha shown separately;
   label a simple lit preview as approximate. Later implement a verified game
   material mode where needed. Standard PBR can add highlights and reshape the
   apparent tattoo/detail through lighting, hiding the comparison's purpose.
5. Make color handling explicit. The current game pack loader has no automatic
   sRGB conversion; do not let web/Blender defaults create an unreported gamma
   change. Compare fixed reference swatches/captures, and record the chosen
   conversion. Three.js exposes texture color-space, vertical flip, mip and
   premultiplication controls; these settings must follow the established
   pipeline rather than defaults.
   [Three.js Texture](https://threejs.org/docs/pages/Texture.html).
6. Mipmaps matter at actual game distance. Carry the workshop's `opacity` versus
   independent `channels` policy into the preview's mip construction or clearly
   label the approximation. Generic browser/Blender mips do not establish that
   both policies match the runtime. Inspect seam/gutter behavior at several
   distances, not only magnified tattoo crops.

A later surface annotation can store model hash, primitive/triangle and UV
along with the existing source ID/revision note. Reflected/repeated UVs may
map several surfaces to one atlas area; show those uses before a regional edit.

## Venues are a second, larger export target

**Fresh own-dump metadata:** `assets/v2bg.viv` contains860 members:499 `.o`,
77 `.xsh`,110 `.irr`,31 `.cli`,75 `.xml`,43 `.jdi`,25 `.pfx`.
`v2bg_cin.viv` contains26 nested `.viv` plus one `.xsh`; `props.viv` contains
41 nested `.viv`. These counts are archive entries, not counts of complete
venues, meshes or materials. No asset bytes were written.

The Foundation is named `V2BG_02A` in `venue.xml:37-52`. Its selected main
`.o` is101,856 stored bytes/281,552 decompressed bytes, with `.data`, string/
symbol tables and `.rel.data`, no `.text`;237 nonempty symbols include render
resource branch names. This suggests reuse of the outer ELF-reader work,
**not proof of an identical inner vertex/scene format**. Scene layout remains
unknown. `entity.xml` separately shows named model/texture groups, environment
maps and extra components (for example `:17-43` ropes and `:45-109` multi-part
sets). Exporting one main mesh will not necessarily reconstruct a whole venue.

**Proposed sequence:** after one fighter, decode one static venue main model
and original textures; then assemble local transforms/instances and secondary
components. Add props, animated crowd, decals, particles, lights, environment
maps and baked-lighting/irradiance data only as their roles are established.
File extensions alone do not identify those roles. Venue review needs a
fly/orbit camera, named component isolation and repeat/tile inspection; a
fight scene adds characters, lighting state and runtime effects. Treat these
as different completeness levels in the UI.

## Acceptance and staged delivery

| Stage | Concrete pass condition |
|---|---|
| 1: One original fighter | Complete Trejo static geometry with valid finite attributes, indices in range, recognizable parts and correct UVs/material IDs; uncertainty and missing parts enumerated |
| 2: Reusable local preview | Original/faithful/Rich Original Detail textures swap on unchanged geometry; camera/lighting synchronized; face regions and alpha unchanged; notes/camera survive restart; no game running during review |
| 3: Blender hand-off | Same original model opens with expected orientation/scale, UVs and material partitions; linked original/detail PNGs and exact provenance remain local |
| 4: Accuracy check | Compare a matched original in-game reference against viewer framing, seams, material response and all visible parts; viewer approximation documented; texture changes still receive final game validation |
| 5: Broaden | Repeat for Nyne/Blaze; then one static venue; add rig/poses and fuller scene/material fidelity independently |

Run a local glTF validator to catch references, accessor/index bounds, invalid
numbers and other structural errors. A clean validator report does not prove
that a recovered bear/tattoo/UV/material matches the game.
[Khronos validator](https://github.com/KhronosGroup/glTF-Validator).

Keep conversions under a private data-root folder such as
`<data>/hd-work/model-preview/`, keyed by source/container/model hashes and
decoder version. Original archives and accepted texture corpus remain read-only;
cache newly converted meshes and manifests separately. Serve them only through
the local workshop. Do not put `.glb`, `.bin`, `.blend`, model JSON with vertex
arrays, texture PNGs, captures or derived previews in tracked source. The source
repository can contain the decoder/viewer code, schemas, synthetic fixtures and
metadata-only documentation. No asset publication or mod installation follows
from this research.

The first implementation should stop and report a specific undecoded resource
if it cannot produce correct original geometry. It should not substitute a
generic human model or texture-on-sphere mockup and call the requested model
viewer complete.
