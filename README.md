# Def Jam Modding Tools

Local texture restoration, review and static model comparison for **Def Jam:
Fight for NY (Xbox)**. This is the authoring companion to
[DefJamFFNY-recomp](https://github.com/vyanhursky/DefJamFFNY-recomp).

- Browse and categorize a texture corpus; compare original, faithful HD and
  immutable restoration revisions with synchronized 25–400% atlas zoom.
- Save flags, notes, regional instructions, approvals and revision requests.
- Inspect Trejo, Blaze and Nyne on their original static meshes, with synchronized
  3D cameras, material isolation and private Blender GLB downloads.
- Preserve protected pixels/alpha during assembly and export selected schema 1
  texture packs for later testing in the game.

Game data, generated artwork, reference images, review workspaces and models live
outside this repository. An existing corpus/workspace can be opened in place;
no regeneration or data move is required. The code license does not cover game art.

## Install and resume

Python 3.11+ is required. The main app uses Pillow and NumPy; it has no paid image
API dependency. Three.js is pinned and served locally.

```sh
python -m venv .venv
# macOS/Linux
.venv/bin/python -m pip install -e '.[dev]'
# Windows: use .venv\Scripts\python.exe and .venv\Scripts\defjam-tools.exe
cp local.example.json local.json
# Edit local.json to point at your existing dump, corpus and workspace.
.venv/bin/defjam-tools serve
```

Open [the texture gallery](http://127.0.0.1:8768/) or
[the model comparison](http://127.0.0.1:8768/model-viewer). Notes, prompts, candidate
images, model caches and camera state stay in the private workspace. Keep a backup
of that entire folder and its matching corpus. Only one server may write it.

To use a profile elsewhere: `defjam-tools --profile /path/to/local.json serve`.
Explicit flags override profile defaults. To make a model preview:
`defjam-tools model --fighter trejo` (also `blaze`, `nyne`).
Advanced import/export retains the previous command arguments through
`defjam-tools workshop import ...` and `defjam-tools workshop export ...`.

## Art workflow

New work uses **Rich Original Detail**. Preserve faces, original UV layout,
palette, painted shading, tattoo silhouettes, tree/animal placement and existing
handwriting. Use references and ask for approval of uncertain inscriptions.
Earlier Stylized Remaster drafts remain review history.

Generation runs through ImageGen in the authoring conversation. The gallery
saves briefs and imports results; queueing a request does not generate an image.
See [the workflow](docs/WORKFLOW.md), [texture guide](docs/texture-workshop.md),
[model guide](docs/model-viewer.md) and [prompt policy](prompts/README.md).

Static mesh export has no rig, animation or game mesh replacement path. Lighting
is approximate. Venue decoding is future work. Optional legacy audition commands
retain their original platform/tool requirements, including CUDA for SwinIR.

## Lossless pack compression

Use `defjam-tools optimize-png --input /private/native-pack --out /private/new-png-stage`
to make smaller copies with exact RGBA and PNG metadata verification. See the
[procedure and release checks](docs/lossless-png.md). Inputs and artwork masters
stay unchanged; the output contains PNGs plus a receipt, not an installable pack.

## Development

```sh
python -m pytest -q
python scripts/check-source-tree.py
python -m pip wheel --no-deps .
```

Read [AGENTS.md](AGENTS.md) then [PROGRESS.md](PROGRESS.md) before changing the
workflow. [Architecture](docs/ARCHITECTURE.md) defines the boundary with the recomp,
the frozen installer core and data compatibility. `provenance.json` records the
source extraction commit and the original shared-core hashes.
