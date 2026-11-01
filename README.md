# Def Jam Modding Tools

Local texture restoration, review and static model comparison for **Def Jam:
Fight for NY (Xbox)**. This is the authoring companion to
[DefJamFFNY-recomp](https://github.com/vyanhursky/DefJamFFNY-recomp).

- Browse and categorize a texture corpus; compare original, faithful HD and
  immutable restoration revisions with synchronized 25–400% atlas zoom.
- Save flags, notes, regional instructions, approvals and revision requests.
- Inspect supported fighters and outfits on their original static meshes, with synchronized
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
`defjam-tools model --fighter trejo`. Run `defjam-tools model --help` for supported
preview keys; the catalogue also retains atlas-only aliases.
Advanced import/export retains the previous command arguments through
`defjam-tools workshop import ...` and `defjam-tools workshop export ...`.

## Art workflow

New work uses **Rich Original Detail**. Preserve likeness, original UV layout,
palette, painted shading, tattoo silhouettes, tree/animal placement and existing
handwriting. Use references and ask for approval of uncertain inscriptions.
Face, hair and headwear detail can be restored when included in the job scope;
keep identity, expression and source palette. Earlier Stylized Remaster drafts
remain review history.

Generation runs through ImageGen in the authoring conversation. The gallery
saves briefs and imports results; queueing a request does not generate an image.
See [the workflow](docs/WORKFLOW.md), [texture guide](docs/texture-workshop.md),
[model guide](docs/model-viewer.md), [fighter workflow](docs/fighter-restoration.md)
and [prompt policy](prompts/README.md).

Static mesh export has no rig, animation or game mesh replacement path. Lighting
is approximate. Venue decoding is future work. Optional legacy audition commands
retain their original platform/tool requirements, including CUDA for SwinIR.

See [native menu registration](docs/menu-native-registration.md) for source-shaped
atlas export, shared-master joins, glyph cells and protected runtime marks.

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

## Menu authoring and project ownership

[Lettering restoration](docs/menu-text-restoration.md) explains fidelity, prompts,
review backdrops and private project retention. The relocated [menu exporters](docs/menu-exporters.md)
accept explicit private inputs. Production review ledgers/checkpoint pointers remain
outside Git; release metadata belongs to the mod catalogue, runtime acceptance to
the game. Historical source excerpts under `research/` are examples, not an active
workspace or a replacement for its private production records.

### Review what shipped

The [published texture library](docs/published-texture-library.md) compares exact
release ZIP images with originals, Faithful 4× and optional drafts/older releases.
Filter by modpack and collect a separate, hash-scoped revision queue at `/packs`.
Private artwork, releases and review notes stay outside Git.
