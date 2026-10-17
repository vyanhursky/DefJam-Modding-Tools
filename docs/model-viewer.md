# Local fighter model comparison

The texture workshop now has a static 3D comparison at
`http://127.0.0.1:8768/model-viewer`, linked from the gallery sidebar.
It reads exported models from the workshop's private data folder. The original
game archives, faithful corpus, reviews and candidate images are not modified
by conversion. The viewer needs no running game or external service.

The first supported fighters are **Trejo, Blaze and Nyne**, main outfits only.
Their original geometry, UV islands, normals and material partitions are used;
this is not a generated replacement body. Textures can be compared in their
original rest pose before choosing a revision for an in-game test.

## Use it

1. Choose the fighter. The left pane starts with Original, the right pane with
   the latest Rich Original Detail candidate. Both selectors also offer Faithful
   HD and earlier revisions. Stylized drafts remain labelled as history.
2. Drag either pane to orbit, scroll to zoom, right-drag to pan. Both cameras
   follow the same target and position. Front, Back, Fit model, Face detail,
   Chest detail, Belt detail, Pants detail and Shoe detail provide repeatable
   starting views. The new detail crops scale with fighter height and viewport
   aspect; the shoe view looks slightly downward to show laces and toe details.
3. Hide material groups to inspect clothing, skin or jewelry separately. Use
   Texture RGB for art review. Studio adds approximate lighting to show surface
   shape; Wireframe reveals the original triangles.
4. Hold the original button to temporarily compare the right pane with its
   source texture. Release to return to the selected revision.
5. Write notes or flag the **right texture**, then click **Save notes**. These are
   the same revision-bound reviews used by the 2D gallery. Notes are not an art
   approval or an in-game verification. Use the gallery for regional rectangles,
   review decisions and test-pack selection.
6. Download the right model as a self-contained `.glb`. It contains the full
   textured model, including material groups hidden only for preview, with the
   selected right texture embedded. Downloads verify geometry and image hashes.

Camera, texture choices, lighting, wireframe and visible groups are saved per
fighter in `WORKSPACE/model-viewer.json`. They do not replace the 2D gallery's
session. The final view is flushed when changing fighter or leaving the page.
Save notes commits immediately; switching fighter or right revision also saves
pending notes first. A browser draft and navigation warning protect other
unsaved changes. Conflicting edits from another tab are rejected, leaving the
draft available for merging after reload.

For body/face color mismatches, see the proposed
[color-preservation workflow](color-preservation.md).

## Build the private models

Use the same Python with Pillow as the existing texture workshop. With an
extracted own dump and an existing accepted texture corpus:

```sh
defjam-tools model --dump /path/to/extracted \
  --corpus /path/to/corpus --workspace /path/to/workshop --fighter trejo
defjam-tools model --dump /path/to/extracted \
  --corpus /path/to/corpus --workspace /path/to/workshop --fighter blaze
defjam-tools model --dump /path/to/extracted \
  --corpus /path/to/corpus --workspace /path/to/workshop --fighter nyne
defjam-tools serve --corpus /path/to/corpus \
  --workspace /path/to/workshop --port 8768
```

The workspace must be outside the repository. Each `models/FIGHTER/` holds
`geometry.json` (private decoded arrays), `model.glb` (original texture export)
and `index.json` (conversion receipt, hashes and preview limits). The browser
download is generated from the verified geometry and selected candidate. It is
a Blender preview, not a game mesh modpack. Copy the entire workshop folder to
preserve candidates and review history when moving machines or worktrees.

## Blender

Import the downloaded file through **File → Import → glTF 2.0**. Its texture is
embedded; use Material Preview to inspect it. Preserve the UVs when experimenting
with smoothing muscles or remodeling chains. Save experiments separately from
the exported baseline. Coordinates retain the game's original Y-up units;
physical metric scale is uncalibrated.

This export has no armature, skin weights, animations or working return path into
the game. Mesh enhancement in Blender is now possible as an offline experiment;
deploying it still needs a verified rig/weight decoder and mesh replacement
format. Texture modpack export remains the separate gallery workflow.

[Blender's glTF importer documentation](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)
describes the import and embedded-material workflow. Blender itself was not
installed on the authoring Mac for this validation; the files were checked with
Khronos' validator and the browser's glTF loader.

## What is decoded, and what is approximated

- The main fighter `.o` is a RefPack-compressed ELF32 data resource. The reader
  bounds-checks sections, symbols and `R_MIPS_32` relocations, resolving only local
  resource pointers. It rejects executable sections and unsupported layouts.
- Material names and render-group pointers come from the model resource. Five
  vertex streams encode float3 position, float2 UV, color, packed signed
  11:11:10 normal, and blend data. Only the proven static attributes are exported.
- Index data is found through the animation-buffer parameter's associated
  resource pointers. Triangle strips keep parity through degenerate joins.
  Winding is reversed once for glTF CCW, verified against original normals.
- Trejo's aggregate raw positions exactly match the resource bounding box when
  helper/sparkle geometry is included. A static body needs no guessed bone
  transforms. Its skeleton was inspected but is not used as a reconstructed rig.
- Original UVs use the glTF top-left texture convention. Replacement textures
  have `flipY=false`, sRGB color and the source shader's clamp behavior. Opaque
  partitions ignore atlas alpha; explicitly transparent groups retain it.
- Unlit RGB is the default. Environment/specular inputs, irradiation, game
  combiners, gamma and animation are not reproduced. The source vertex colors
  remain in the private decode but are not applied without verified shader
  semantics. Studio lighting is a plain rough material, not game parity.
- The Direction helper and additive point-sprite sparkle resources are omitted
  and listed in the receipt. Jewelry triangles remain. Venues and other outfits
  are not supported by this decoder version.

Detailed measured offsets and winding evidence are in
[Trejo pose/material research](research/trejo-pose-material-layout.md).

## Validation, 2026-10-16

| Fighter | Stored textured vertices | Triangles | Mesh parts | Material groups |
|---|---:|---:|---:|---:|
| Trejo | 5,024 | 5,976 | 40 | 8 |
| Blaze | 4,656 | 5,796 | 39 | 7 |
| Nyne | 5,253 | 5,948 | 43 | 7 |

All three original-texture GLBs pass Khronos glTF Validator
`2.0.0-dev.3.10` with **0 errors and 0 warnings**. Original positions, UVs and
source normals are retained rather than recomputed. A few source mouth triangles
have normals opposed to the majority winding; their topology is preserved.
The browser-downloaded Trejo v4 GLB also passes with zero errors/warnings; its
embedded 2048² RGBA pixels exactly match the selected immutable candidate.

The browser was exercised with all three actual models, original and restored
atlases, synchronized drag/orbit, detail presets, material isolation, studio
lighting, wireframe, camera reload and source/source comparison. Review/flag
saving and reload were tested in a separate synthetic browser workspace, without
changing owner notes. Ten synthetic decoder/export/HTTP/state tests and the
19 existing gallery tests cover bounds, parity, UVs, embedded images, material
alpha, checksum refusal, authentication, stale reviews and separate persistence.
There was no runtime, renderer, save, installer or game modpack change.

Face, Pants and Shoe detail presets were subsequently checked visually on all
three fighters (nine crops), including synchronized framing and a saved Nyne
shoe camera after reload. The complete standalone suite passes 56 tests plus
12 subtests. JavaScript syntax and source hygiene also pass.

Browser dependencies are MIT-licensed Three.js **r180 / 0.180.0**, vendored with
upstream URLs and SHA-256 values in `src/defjam_tools/resources/vendor/three/provenance.json`. Bare module
imports are rewritten to exact local routes when served; no CDN or inline script
is needed. The loopback server retains Host/token/origin checks and an exact
static-path allowlist. CSP permits local blob reads needed by embedded GLB images.

Models, decoded arrays, generated PNGs, `.blend` files and screenshots must remain
private. Only tooling, upstream library code/license, synthetic fixtures and
metadata documentation belong in source. The source checker and ignore rules now
also reject common exported model formats.
