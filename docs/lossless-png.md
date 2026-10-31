# Lossless PNG optimization for texture packs

Use `defjam-tools optimize-png` after approval and native atlas assembly, before
building a release archive. It writes a new private PNG staging tree and a JSON
verification receipt. It never edits the input files, imports a revision, changes
approval state, installs a pack or publishes a release. Keep artwork masters and
all original prompts/provenance unchanged.

## Install the optimizer

The Python app uses its existing Pillow dependency. Install Oxipng separately;
the tested version is **10.2.1**. On macOS:

```sh
brew install oxipng
oxipng --version
```

On other platforms, use the upstream [Oxipng releases](https://github.com/oxipng/oxipng/releases).
The executable must be on PATH, or pass `--oxipng /absolute/path/to/oxipng`.
The wrapper requires an Oxipng version supporting the switches below; it reports
an optimizer failure and retains the source bytes if a version rejects them.

## Run on a copy

From the tools checkout, with output **outside** this source repository:

```sh
.venv/bin/defjam-tools optimize-png \
  --input /private/workspace/native-pack \
  --out /private/workspace/native-pack-png-optimized \
  --jobs 4
```

Output must be new and disjoint from the input. Relative PNG paths are preserved;
non-PNG files, manifests, DDS files and signatures are **not copied**. This is not
an installable pack directory. Keep a separate release staging copy, and adopt
verified PNGs there only after inspecting the receipt. Do not point this command
at an active review workspace and do not replace a published immutable package.

To optimize selected files from several locations, use a UTF-8 JSON manifest:

```json
[
  {"input": "/private/workspace/revision-a.png", "output": "textures/source-id.png"},
  {"input": "relative-to-manifest.png", "output": "wide/background.png"}
]
```

```sh
.venv/bin/defjam-tools optimize-png \
  --manifest /private/workspace/selected-pngs.json \
  --out /private/workspace/selected-pngs-optimized
```

Source symlinks, path traversal and case-insensitive output collisions are rejected.
A failed or interrupted run can leave partial output: inspect its receipt if present,
keep it for diagnosis, then retry into another new directory. The command never
resumes by overwriting an existing output.

## What is verified

Each optimizer invocation receives a frozen input byte snapshot through stdin,
never the original path:

```text
oxipng -o 4 --nx --interlace keep --threads 1 --timeout 60 --out candidate.png -
```

Four file workers are used by default. `--level 0..6` controls search effort;
`--jobs 1..32` controls concurrent files. The wrapper also applies a 180-second
subprocess timeout. `--nx` disables image transformations: bit depth, colour type,
palette and interlace stay unchanged. No `--alpha`, quantization, palette reduction,
16-to-8-bit conversion or metadata stripping is enabled.

Before accepting a smaller candidate, the wrapper verifies:

1. PNG signature, chunk bounds, CRCs and complete ending.
2. The exact payload and sequence of **every non-IDAT chunk**, including IHDR,
   colour metadata, palette, text and private chunks.
3. Identical dimensions and every decoded RGBA8 byte, including RGB hidden under
   zero alpha. Straight-alpha values and partially transparent edges are preserved.
4. Unchanged input file hash after optimization and exact output write bytes.

It retains the original bytes when the candidate is not smaller. If verification
or the optimizer fails, it writes the original, records the reason and exits nonzero.
Raw imagegen PNGs may contain a `caBX` provenance chunk. Oxipng 10.2.1 removes
that chunk; the verifier rejects the candidate and retains the original with a
metadata failure. Keep those raw masters immutable. Optimize approved native
exports instead; do not strip provenance from a master to obtain a passing result.

16-bit PNGs and APNGs are explicitly retained unchanged, with a skipped status;
RGBA8 equality is not presented as proof for those formats. Inputs with broken
chunk CRCs fail preflight before the output directory is created.

`optimization-receipt.json` records optimizer version, module hash, profile,
completion, file/skip/failure counts, elapsed time, before/after sizes and hashes,
and per-file RGBA/metadata verification. Require `complete: true`, `failures: 0`
and review any `skipped` entries before adopting output. A hash verifies bytes;
it does not establish art fidelity or in-game correctness.

## Release procedure

After native layout/UV/gutter/alpha validation, freeze the approved input manifest
and its SHA-256 hashes. Run this command into a new staging tree. Review its receipt,
then copy only its verified PNGs into a separate complete pack staging tree.
Rebuild the pack manifest/archive with the game's existing packaging tool. Recompute
archive length and SHA-256, catalogue entries and signatures **after** optimization.
Test that exact final artifact through the supported installer/loader and relevant
native scenes. Keep the prior release for rollback; never mutate its archive or
reuse its signatures. No game-runtime change is needed merely to recompress an
otherwise identical PNG, but the newly packaged release still needs its normal tests.

PNG optimization reduces disk/download bytes. It does not reduce decoded RGBA
memory or GPU texture allocation. ZIP compression alone usually adds little for
already compressed PNGs; measure the actual final archive. Avoid JPEG for UI with
transparency and avoid lossy PNG quantization for these approved edges. BC/DDS
compression is a separate runtime-format and visual-quality decision, not this
lossless experiment. Do not drop hidden RGB or alter palette/channel structure
just because two browser screenshots look the same.

## References and measured results

[Oxipng documentation](https://github.com/oxipng/oxipng) explains optimization and
why alpha optimization is a separate, potentially pixel-changing option.
The [PNG specification](https://www.w3.org/TR/png-3/) defines lossless image storage,
alpha and ancillary chunks. The wrapper deliberately uses stricter preservation
than visually lossless alpha or metadata stripping.

Measured menu/UI results, 2026-10-30 (Oxipng 10.2.1, conservative profile):

| Dataset | PNGs | Before bytes | After bytes | Saved bytes |
|---|---:|---:|---:|---:|
| Published 1.3 PNGs | 1,704 | 682,774,940 | 573,469,182 | 109,305,758 (16.01%) |
| Approved queued review crops | 949 | 648,007,579 | 574,491,068 | 73,516,511 (11.35%) |

All files in both datasets passed full RGBA and non-IDAT chunk equality, with zero
failures/skips; input bytes remained unchanged. These are actual full datasets,
not a sample extrapolation. The approved crops still require native atlas assembly.
For the existing release ZIP, exact member-level DEFLATE level 1 payload comparison
saved 108,045,093 bytes (15.90%);
unchanged-header projection: 679,627,331 → 571,582,238 bytes.
No release archive/catalogue was rebuilt or published. Four new raw imagegen PNGs
were a separate negative control: all retained unchanged when the optimizer dropped
caBX provenance metadata. Private manifests and per-file receipts stay outside Git.
