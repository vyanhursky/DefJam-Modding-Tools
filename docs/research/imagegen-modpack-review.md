> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Image-generated texture restoration: packaging review

2026-10-15. Read-only review; no art generation, game run, build, loader change or
mod-manager implementation. This report proposes an export contract, not a new
runtime format or an owner-approved art direction.

## Evidence and scope

- PR17 remains a proposal. Reviewed its complete design at
  [head 8e3d2dbe](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L1-L6).
- This worktree's toolkit is unpopulated. Inspected the sibling checkout's
  `src/nv2a/texture_pack.c` read-only after verifying its HEAD equals this
  project's pin, `837e2c7ea65a3e8e9149978c7cc125810d2c4e35`. Toolkit source links
  below point to that exact published commit.
- Inspected current `scripts/build-hd-pack.py`, `setup/engine.py`,
  `src/hooks/pc_settings.c`, texture docs and relevant unit-test source. No new
  tests were run for this research-only report.

## Recommended contract today

Use ordinary **schema 1 sparse texture packs**, containing only selected,
approved replacements. Keep the faithful Lanczos corpus and original game
archives unchanged. The existing runtime already provides the needed injection
point; image generation and review belong in local authoring tools above it.

```text
<data>/hd-work/restoration/           local authoring/review history
  originals/                        immutable own-dump inputs
  candidates/<asset-id>/<revision>/  full outputs, crops, masks, request records
  decisions.json                    exact approved output hashes
  releases/<release-id>/             export record and checksums

<data>/mods/restored-r001-o/manifest.ini
<data>/mods/restored-r001-o/textures/<source-id>.png
<data>/mods/restored-r001-c/manifest.ini
<data>/mods/restored-r001-c/textures/<source-id>.png
```

The two component folders are needed only when approved assets require both
mip policies. Short component names leave room in the current semicolon list.
Example opacity manifest:

```ini
[pack]
schema=1
name=Restored textures revision 001
png_mips=opacity
[textures]
<64 lowercase hexadecimal runtime source-id>=textures/<source-id>.png
```

The channels component uses `png_mips=channels`. Do not emit the proposal's
`[mod] schema=2` into a live pack today: the current parser requires
`[pack] schema=1` and rejects unsupported schemas
([parser](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L133-L185)).
Keep authoring metadata in a separate JSON sidecar/export receipt until a
future packaging validator explicitly permits it; the current runtime's
manifest need contain only its supported loader fields.

Every image must preserve the full original atlas and aspect ratio, use
straight alpha, and have a uniform integer scale from 1x through 8x. An
image-generation service's arbitrary canvas size is an intermediate result,
not an installable asset. Deterministic assembly must place edited regions back
into the original atlas geometry before export. PNG is the initial review and
distribution target; supplied DDS mips are a later per-material decision
(`docs/hd-textures.md:79-96`).

## Identity, categories and shared assets

Runtime source IDs are the binding key, not a display filename, character name,
or category. Keep archive aliases, decoded IDs and runtime correlation in the
authoring records. Archive IDs can need explicit runtime aliases; the current
builder already accepts and checks those (`scripts/build-hd-pack.py:49-56`).
The workflow records the distinction and 13 existing bounded aliases in
`docs/hd-texture-workflow.md:24-25,130-135`.

Category folders are a review aid; they do not make a shared texture local to
one fighter or menu. One source ID may have many archive/use aliases, and its
replacement affects every matching use. The export should enumerate all known
uses and flag conflicts when different category decisions select different
revisions for the same source ID. Review outfits, palettes, low-detail/cinematic
variants and animation sequences as linked groups.

## Order, dependencies and fallback

The current loader has one precedence rule: the last listed matching key wins.
It stores insertion order and selects the last equal ID after sorting
([sorting](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L127-L132),
[lookup](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L487-L492)).
Put the faithful opacity/channels components first, then the restoration
components, when the intended baseline is faithful HD. For a restored-only
pilot, enable only the restoration components; absent keys use console originals.
No dependency resolver exists today. Treat faithful HD as an optional baseline,
not a hard dependency, unless the owner explicitly wants the package to require
it. Record the order and intended baseline in the export receipt.

Three different fallback cases matter:

1. An asset absent from the restoration manifest can still use an earlier
   faithful pack. With no earlier match, it uses the game original.
2. A winning replacement that fails decoding or validation uses the game
   original. The loader does **not** retry the earlier faithful entry; it marks
   the selected entry failed ([load path](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L775-L789)).
3. A replacement still decoding in the background temporarily uses the original
   ([worker boundary](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L505-L509)).

Thus "keep original" in the reviewer must have explicit meaning when faithful
HD is enabled underneath. Omitting a creative candidate means "keep the
baseline", which may be Lanczos. Disabling all packs restores originals globally.
There is no current per-key original sentinel to assume in a future exporter.

An important Setup interaction already exists: `enable_hd_packs()` retains
custom pack names, then appends the generated faithful packs
(`setup/engine.py:1034-1048`; asserted by `tests/unit/test_hd_setup.py:102-110`).
Checking HD during repair/update can therefore put faithful packs after the
restoration and hide it. For the pilot, use explicit diagnostic ordering or
reorder after Setup. The future manager must reconcile this ownership/order rule.

The runtime reads pack names into a 256-byte buffer and caps the combined entry
table at 65,536 ([limits](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L33-L35),
[pack list](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L187-L213)).
Do not export one enabled pack per texture. Use a small number of category or
release components and check the entire proposed list length before activation.

## Alpha and mip policy are a schema 2 gap

Today's `png_mips` applies to the entire pack. Unknown policies reject that
pack; the parser copies the final pack policy to every loaded entry
([policy handling](https://github.com/vyanhursky/xboxrecomp/blob/837e2c7ea65a3e8e9149978c7cc125810d2c4e35/src/nv2a/texture_pack.c#L155-L185)).
The shipped builder already splits faithful HD into opacity/channels packs
(`scripts/build-hd-pack.py:33-36,58-64,96-102`). Its category heuristic is an
existing default, not proof of material semantics for newly generated work.

PR17's schema 2 example carries `[textures]` but specifies no mip-policy
migration ([example](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L82-L112)).
Before implementation, choose either multiple components per logical mod,
retained per-pack policy with separate logical mods, or a new per-texture policy
field. Do not merge today's two manifests into one schema 2 manifest and lose
the distinction. The authoring/export records should store policy per asset so
either future representation can be generated without redoing the artwork.

## Approval and provenance

Retain every candidate as an immutable revision. Record source/runtime IDs,
source pixel hash, category/use aliases, original dimensions, full prompt,
reference/mask hashes, available model/tool metadata, request time, parent
revision, exact crop/assembly steps, output pixel and file hashes, alpha source,
mip policy and notes. Store only metadata the image service actually exposes;
do not invent a reproducible seed or immutable model version.

Separate "looks approved in the atlas" from "verified in game". A candidate's
approval must name its exact output hash and revision. A revision after approval
returns to review; changing the selected output must never silently preserve
approval from an older image. Export only chosen revisions that pass structural
checks and the agreed in-game gate. Retain a rejected/keep-baseline decision
without shipping its candidate. Existing review flags already persist locally
and do not automatically change the installed pack
(`docs/hd-texture-workflow.md:64-69,94-109`).

Use an immutable package version and checksum per export; a later correction
becomes another version, not changed bytes at the same version. Distinguish
logical mod ID, content/release hash, individual asset revision and tested
runtime/toolkit commits. PR17's index appends versions and pins size/SHA-256;
this will accept such exports later without depending on art-generation tooling
([version pinning](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L137-L170),
[submission rules](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L187-L203)).

## External packaging and portability

An approved restoration is derived artwork under the project's existing policy,
including an AI-edited result. Its eventual index entry is `class=linked` and
points to the owner's chosen third-party host. The main project hosts the
authoring tools/recipes and hash-only metadata, not these PNGs or previews
([owner answers](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L14-L24),
[classes](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L164-L170)).
Generated interpretation does not by itself make the whole texture the
author's original content or make the source project's MIT licence cover it.

The eventual archive needs only supported manifests, approved texture files,
checksums, credits and installation/version metadata. Do not include originals,
the full review tree, extracted archives, saves, checkpoints, executables,
credentials, absolute source paths, or filesystem links. Use portable relative
ASCII paths and reject traversal, links, duplicate archive paths and case-only
name collisions when packaging. The current parser checks lexical names;
package validation must independently enforce archive containment.

The same source-keyed PNG pack can be used on Windows, macOS and Linux; artwork
generation does not require a platform-specific replacement hook
(`docs/hd-textures.md:9-12`). State tested platforms honestly and measure cache
pressure/first-show behavior using actual game runs before release. The current
game settings default is 2,048 MiB (`src/hooks/pc_settings.c:43-52`); older texture
docs still say 512 MiB, so use current code when planning budgets.

PR17's local recipes are declarative inputs to an allow-listed, pinned local
tool; imagegen authoring with human revisions is not presently such a recipe
([recipe definition](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md#L172-L182)).
Publish deterministic atlas assembly/validation recipes and provenance, but
distribute the approved image results as immutable external linked content.
Do not imply every player must buy image generation or rerun subjective edits
to install the finished pack.

## Owner decisions needed

1. Is the first creative pack a sparse overlay above faithful HD, or a
   restored-only selection above console originals? This defines "keep baseline"
   and the local comparison conditions.
2. Should releases be independent category packs or one curated restoration
   with optional categories? Today each mixed-policy selection needs opacity and
   channels components; PR17 needs a multi-component or per-entry policy decision.
3. Which details are allowed to be inferred when the original is unreadable,
   and which tattoos, logos, lettering and face features require a supplied
   reference or an explicit owner decision? A visually plausible logo is not
   evidence of the original design.
4. Does atlas approval permit local test-pack export immediately, followed by
   separate in-game approval, or must every image be approved again before
   installation? No public upload follows from either local approval.
5. For eventual publication, which third-party host/account owns derived packs
   and previews? PR17 already answers "third-party", so the unanswered choice is
   the actual host and release workflow, not permission to put PNGs in source.
6. Should a rejected candidate inherit faithful HD or force console originals
   for that key? The latter needs an explicit loader/export design when other
   packs remain enabled.
7. How should Setup updates preserve restoration priority? The current append
   behavior can invert it; settle manager ownership before schema 2 integration.

The first four affect the local pilot. The host, signing-key owner, index
repository and manager language can wait until an approved pack exists.
