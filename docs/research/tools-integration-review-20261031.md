# Long-term Modding Tools integration review — 2026-10-31

Recommendation: integrate the reusable fighter authoring work, with focused
cleanup and tests. Preserve the full source history, but do not treat the entire
fighter branch as a maintained application or merge its files over current main.
No implementation, merge, push, server restart or private review change is part
of this review.

Reviewed fighter HEAD `338bbf07f03043c81fe0c18c2a4f3f2f5cede790` against freshly
fetched main `f1477e32250278b60021f895ba7327a06ca3949d`. Main already contains the
core model viewer and Face/Pants/Shoe presets. The branch-only diff has19 source
files (~1,012 added lines),13 test files (~591 added lines) and71 research files
(~15,199 added lines). Most of its volume is history/data, not application logic.
Static inspection and independent bounded viewer, documentation and release
reviews informed this recommendation. Existing branch tests passed124+23subtests
at publication; the combined main/integration tree has not yet been built/tested.

## Maintain in Modding Tools

| Work | Long-term value | Integration treatment |
|---|---|---|
| Decoder2, nested source routing, strict normals/indices and decoder1 cache reads | Enables more real game assets without inventing geometry | Merge with synthetic decoder/route fixtures; preserve old caches/IDs. |
| Revision-aware model/atlas review, shared notes, archived history and explicit revision labels | Needed for every future review category | Merge after the archive/saved-choice issue below is fixed and tested. |
| Original-palette correction, skin seams, cloth masks, protected alpha and regional/feature assembly | Reusable for tattoos, logos, clothes, hair and accessories | Keep parameterized library strategies and tests; document inputs/limits. |
| Registered clean-head/state-difference assembly | Reuses accepted detail without inventing new injury marks | Keep as an offline art operation with separate runtime acceptance. |
| UV/material feature coverage and offline projections | Helps identify split islands and missed logos | Keep diagnostic labels; it is not game shader or animation emulation. |
| Calibrated prompting, source/reference rules and review/pack contracts | Makes further fighter/customization work repeatable | Promote maintained guides/manual templates; remove dated pilot status. |

Relevant modules include `face_detail`, `clothing_detail`, `feature_detail`,
`region_detail`, `material_palette`, `fighter_scopes`, `skin_scope`,
`damage_detail` and `uv_preview`. They generally accept images, geometry, masks
and parameters rather than private workspace paths. Their distinct strategies
solve different problems: a face-edge blend, an edge-touching emblem repair and
an injury-state transfer should not be collapsed into one automatic filter.

## Turn repeated batch work into a small supported runner

The library operations are more reusable than their orchestration. Current CLI
commands do not expose the new assembly methods as a general batch workflow
(`src/defjam_tools/cli.py:10`). Dated `assemble.py` scripts repeatedly load plans,
check pins, assemble masks/detail, write comparisons/receipts and import results.
Some take useful explicit arguments; others embed dates and private paths.

Extract only the repeated plumbing into a versioned job/plan format and CLI:
explicit source/parent hashes, operation, material scope/holds, palette settings,
output stage and provenance receipt. Keep imports/reviews/approval separate from
assembly. Read paths from the existing private profile or arguments. Do not build
a new general framework or provider/plugin system merely to replace small scripts.
Keep the gallery's generator queue as a brief/import workflow; queueing a brief
must not start paid generation or deployment.

The duplicated catalogues should become one validated source-only data inventory:
76 `FIGHTERS` preview entries,81 `PILOT` alias entries and five hardcoded gallery
filter names currently describe different subsets. Preserve legitimate aliases
and unsupported assets, not just a count. Per-fighter material exceptions need
explicit data/reasons, while decoder mechanics and source validation stay code.

## Preserve as historical/experimental material

- Keep published0.1/0.2/1.0 recipes, selections, hashes and reports frozen for
  provenance. A future generic builder must not rewrite the implementation or
  receipts associated with existing immutable ZIPs.
- Keep dated fighter/feature/Rollins batch scripts and exact masks/coordinates
  as reproduction evidence, not supported entry points or required startup steps.
  Archive/index them without silently moving paths that frozen scripts depend on.
- Preserve the local-neural audition code as explicitly experimental. Its tests
  show pixel invariants, not acceptable restoration quality; the owner rejected
  detail loss and no such output entered1.0. Do not make it the default pipeline
  or add Torch/model weights to the main installation.
- Keep machine-specific reconnect/import/review-reconciliation commands private
  or historical. Replaying an old script must never reset a current workspace,
  overwrite notes or reapply old approval decisions.
- Art, models, generated references, review/session JSON, model weights, credentials
  and release archives stay outside Git. Source-only historical hash metadata can
  remain in the repo; ad-hoc does not mean delete valuable provenance.

## Packaging is reusable; a dated release script is not its API

The existing workshop export is useful and tested, but it writes selected local
packs. Three release builders repeat an expanded pipeline. The1.0 builder fixes
version/counts/date/storage details in code (`research/hd-fighters-1-0-20261031/build.py:25`,
`:57`,`:107`,`:114`); the private uploader and managed-install runner also bind
machine paths and one release. Retain these snapshots; extract new code separately.

Modding Tools should own offline selection validation, source identity, exact-byte
staging, deterministic pack/ZIP creation, measured descriptors and local verification.
New supported commands should take an explicit selection ledger and calculate
counts. Candidate, Lanczos baseline and native original must be distinct origins;
labels/tags or "latest" must not establish eligibility or approval.

Before treating that extraction as production tooling, replace assert-only
validation, preserve duplicate archive-member detection, hash the bytes actually
staged, reject alias/path collisions, pin verifier compatibility, and define what
concurrent review changes invalidate a selection. Test these with synthetic images
and archives, including a source change between validation and staging. Keep
art approval, packaging authorization, publication authorization and native
verification separate. A free-text approval field alone is not an authorization
mechanism; immutable release selection must carry validated evidence/pins.

DefJamFFNY-mods should own shared R2 upload/public verification, catalogue-entry
generation, append-only publication, protected signing and disposable released-client
smoke checks. It already owns the authoritative distribution contract. Extract
the useful private scripts there with configurable inputs and fake AWS/HTTP tests.
Keep runtime loader/installer behavior and actual game acceptance in the recomp.
Do not add publishing or real game installation to the gallery's local Export button.

## Concrete fixes before integration

1. **Archived saved revisions can be replaced in comparisons.** Model viewer
   filters every archived candidate at `resources/model_viewer.js:140`, then
   substitutes a different right revision at`:146` and saves the view through
   `updateView()` at`:162`. Gallery does the same at
   `resources/texture_workshop.js:121`/`:126`/`:144`. An archived approved, selected
   or saved/current revision needs to remain available/pinned; visibility changes
   must not silently rewrite comparison choices. This is a static code finding;
   no private user state was manipulated to demonstrate it. Add targeted browser
   or extracted pure-selection tests for both panes and archive toggles.
2. **Method is currently overloaded onto style/labels/tags.** The newest candidate
   with style `faithful` might be a native original or Lanczos fallback, not an
   ImageGen restoration. Preserve backwards compatibility, then introduce explicit
   source/method semantics through a documented versioned metadata change. Keep
   approval independent from method; do not silently migrate existing records.
3. **Entry documentation contradicts the current workflow.** `docs/WORKFLOW.md:22`
   still says Rollinsv5 studies await review. `docs/ARCHITECTURE.md:7` calls PR17
   packaging future. README/model guide still mix65 previews/current76 and old
   pilot-only support. Make maintained guides timeless; put release status in
   dated records. Condense AGENTS.md to durable rules and links instead of the
   full fighter-by-fighter approval chronology.
4. **The fighter branch lacks newer main work.** Main includes `optimize-png`,
   `png_optimize`, `menu_native`, their tests and maintained guides. Start an
   integration worktree from current main and preserve those capabilities. Do not
   replace main's CLI/docs/tree with a fighter-branch snapshot.

## Recommended sequence

1. Preserve the complete source-only fighter branch remotely, with its release
   provenance, before any cleanup. No art/workspace files go with it.
2. **Authoring integration PR:** decoder/cache compatibility, review/diagnostic
   improvements, reusable assembly libraries, focused tests and corrected guides.
   Fix archive selection first; consolidate catalogue data without breaking IDs.
   Use a separate worktree; leave the live port8768 writer and private workspace
   untouched. Verify the installed package as well as source tests on main's
   combined menu/fighter functionality.
3. **Portable job/pack PR:** extract plan-driven batch operations and offline
   release builder/contract, preserving current import/export semantics and all
   frozen published recipes. Small documented commands, not replay scripts.
4. **Catalogue automation PR:** parameterize shared upload/publication verification
   in DefJamFFNY-mods and retain normal signing/history/environment protections.

The first integration does not need to wait for complete release automation.
The durable viewer/decoder/assembly work is worth merging now after the bounded
fixes above. Full end-to-end automation should be claimed only once those later
portable commands and their tests exist.
