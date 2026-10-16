# Ownership and compatibility

This repository owns texture/model authoring. DefJamFFNY-recomp owns runtime
replacement, launcher/mod management, setup and gameplay validation. The shared
contract is files: versioned corpus metadata, texture IDs/runtime aliases, review
schemas and supported pack manifests. The current exporter writes schema 1;
future PR17 packaging needs an explicit tested adapter.

The first extraction is from recomp commit recorded in provenance.json. Its
installer retains byte-identical hd_assets.py, hd_corpus.py, hd_corpus.html and
runtime aliases as a frozen compatibility snapshot. Setup still builds offline
without installing this application. The original hashes are recorded in both
repositories. Future core development belongs here, and a separate reviewed pin
update plus setup checks integrates changes back into the recomp.

The package uses relative imports and packaged resources. This changes source
hashes used for NEW corpus recipes; existing accepted corpora are read in place,
with their IDs, paths, images and reviews unchanged. There is no startup rebuild.

## Private data

local.json (gitignored) resolves dump/corpus/workspace paths. The corpus is
read-only. The workspace holds workshop.json, candidates/, raw/, exports/,
model-viewer.json and models/. Review writes remain atomic/versioned and the
existing process lock prevents concurrent writers. Never put those files in
source, even for a private GitHub repository. Git is not their backup.

## Components

- texture_workshop: 2D review, queue/prompts, technical assembly and pack export.
- defjam_model: bounded original static geometry to private GLB conversion.
- model_workshop/resources/model_viewer: model endpoints and synchronized 3D UI.
- hd_assets/hd_corpus: extraction, texture identity, lossless input decode and
  Lanczos corpus generation; imported legacy helpers retain their data contracts.
- hd_review/hd_swinir_review: optional older local-upscaler auditions. Existing
  Windows font/CUDA assumptions remain; they are not the primary authoring UI.
- cli: profile-aware commands; resources: browser files, FFNY aliases and Three.

No code here installs a pack or changes game archives, saves or runtime settings.
Art approval and in-game verification remain explicit separate steps.
