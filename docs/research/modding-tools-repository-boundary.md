> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Proposed dedicated Def Jam modding tools repository

2026-10-16. Recommendation following the owner's question; creation, migration
and publication have not been requested by this question. Evidence: local source
at `2c2a60d`. Existing review workspaces remain the durable source of art history.

A dedicated `DefJam-Modding-Tools` repository makes sense now. The workshop is a
standalone authoring application whose development need not follow game-port
releases. Keep FFNY as the initial supported game and retain its actual format
limits; extracting the tools does not add support for other titles or platforms.

## Ownership

| Location | Responsibilities |
|---|---|
| Tools repository | Texture inventory/classification, extraction and model conversion, 2D/3D viewers, revision/review workflow, prompt templates and art direction, technical assembly/pixel protection, modpack exporters, documentation, synthetic tests and pinned viewer libraries |
| Recomp repository | Runtime replacement hooks/loader, launcher and mod manager, installer integration, game settings, runtime compatibility and in-game acceptance tests |
| Private workspace outside both repos | Own-dump files, original/faithful images, generated candidates and exact per-revision prompts, references, notes/flags/approval history, camera sessions, decoded meshes/GLBs/Blender projects and exported pack artifacts |

Reusable prompt templates and operating instructions belong in tools source.
Actual submitted prompts, image references, generation results and review
decisions remain attached to their immutable candidate in the private workspace.
A source checkout alone is not a backup of that workspace.

## Current coupling to handle

- `texture_workshop.py` loads `config/hd-runtime-aliases.json` relative to the
  repository. Package it as versioned FFNY profile metadata or an explicit input.
- `model_workshop.py` serves the workshop files and `thirdparty/three/` through
  repository-relative paths. Package these as application resources.
- `defjam_model.py` imports archive/RefPack helpers from `hd_assets.py` and uses
  corpus source IDs. Preserve those identities and its private-output guard.
- `scripts/build-hd-pack.py` imports **both** `hd_assets.py` and `hd_corpus.py`;
  `scripts/package-setup.py:HD_SOURCES` explicitly includes them in setup payloads.
  Setup and branding also consume the existing corpus/alias contract. Moving or
  deleting these modules outright would break the recomp's current pipeline.

The tools repo should own the reusable core. Once integrated, the recomp should
consume a pinned, vendored subset or packaged version of that core, with a
recorded version/license/checksum. Installers must keep working offline. Maintain
one upstream source and an explicit update process; avoid independently editing
two copies. Leave the currently released installer implementation in place until
the replacement dependency is proven equivalent.

## Suggested extraction sequence

1. Start from the committed, working workshop and its tests. Give the standalone
   application a package, dependency declaration, CLI and its own agent/handoff
   instructions. Keep corpus/workspace paths configurable and preserve the
   current live server during preparation.
2. Extract the authoring UI, backend, model conversion, templates, relevant
   documentation and pinned Three.js resources with their provenance. Establish
   an explicit shared-core boundary for extraction, texture identity and pack
   metadata before changing the installer's imports.
3. Resume against the **existing** corpus and workshop folders. Preserve source
   IDs, corpus IDs, revision IDs, image hashes, review versions and relative image
   paths. Reading existing work must not regenerate art, reset approvals or
   require moving the data. Provide versioned migrations for future schema changes.
4. Verify a standalone checkout, the 29 current workshop/model tests, saved
   review/session compatibility and a selected-pack export with identical keys,
   images and channel policies. Exercise original/restored 3D comparisons again.
5. Retire the recomp's authoring copies once the standalone app passes. Integrate
   any shared-core dependency update separately with HD setup/package checks.

The interoperability boundary is versioned files: corpus metadata, texture/source
identities, runtime aliases, and the supported modpack manifests. Today's exporter
uses schema 1; PR17's proposed packaging needs a separately validated adapter when
implemented. This split must not silently assume schema 2 is already accepted.

Existing workflow guides: [texture workshop](../texture-workshop.md),
[model viewer](../model-viewer.md), and
[modpack compatibility](imagegen-modpack-review.md).
