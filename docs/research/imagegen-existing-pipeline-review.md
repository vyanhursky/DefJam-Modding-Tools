> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Existing HD pipeline: suitability for an image-generation restoration pass

Read-only source review, 2026-10-15. No game, extraction, build or generation was run. This report contains metadata and source references only. Historical counts below describe recorded work, not a fresh census of the current machine.

## Finding

The proposed first step has largely been implemented: there is a deduplicated static texture census, provenance categories, original exports, a full-corpus local comparison gallery, saved review notes, runtime capture/identity correlation, and external replacement packs. Reuse these foundations. The missing layer is an art-direction and revision system for arbitrary generated candidates, with per-texture approved selections and a small overriding pack. The shipped Lanczos corpus should remain the baseline.

## What exists

| Capability | Existing behavior | Evidence |
|---|---|---|
| Archive traversal | Reads `.viv`, `.xsh`, `.mad`; nested BIG4/BIGF and bounded RefPack; 128 MiB blob limit and depth limit. | `scripts/hd_assets.py:18`, `:32`, `:50`, `:90`, `:244` |
| Texture extraction | Validated SHPX decoding for DXT1/3/5, paletted and BGRA textures, swizzle handling, full RGBA PNG exports; unsupported formats remain error records. Mip-bearing SHPX is rejected pending layout validation. | `scripts/hd_assets.py:136-223` |
| Census and deduplication | Full census retains every archive/image alias, exports selected images separately, then corpus generation processes one representative per source ID. The supported recorded corpus is 18,971 images / 24,266 aliases, plus one unsupported image. | `scripts/hd_assets.py:244-281`; `scripts/hd_corpus.py:176-191`; `docs/research/hd-full-lanczos-corpus.md:10-25` |
| Categories | Provenance-based classification already includes UI, HUD/tutorials, fighters, customization, venues, props, crowds, cinematic variants, animation, effects/masks, environment maps, loading emblems and other. One image can appear in multiple category filters through its aliases. | `scripts/hd_assets.py:226-241`; `scripts/hd_corpus.py:58-88`, `:184-189`, `:233-245` |
| Full-corpus review | Search name/archive/hash; category, status and size/name/category sorting; 48 cards/page; original-versus-Lanczos comparison with synchronized pan/zoom; fit/100%/200%; RGBA, true RGB and alpha; checker/black/white; full PNG links. | `scripts/hd_corpus.html:5-34`; `docs/hd-texture-workflow.md:64-69` |
| Durable review notes | Localhost-only server stores concern/good/unreviewed status, one topic and a note per source ID in `reviews.json`; atomic save, reload and export. Existing topics include tattoo, logo, material, alpha and seam. | `scripts/hd_corpus.py:254-327`; `scripts/hd_corpus.html:13`, `:23-34` |
| Multi-model audition | A separate 40-asset gallery already compares original, Lanczos, RealESRNet, RealESRGAN at 2x/4x and saves scale-specific choices. SwinIR was another separate experiment. | `docs/hd-texture-workflow.md:22-30`, `:39-45`; `docs/research/hd-representative-review.md:64-74` |
| Resume/provenance | Corpus recipe hashes decoder, runner and inventory; image records retain source/decoded/pixel IDs, image paths/hashes, dimensions and alpha treatment. Resume checks all three image hashes. Batch upscaling adds executable/model hashes and time. | `scripts/hd_corpus.py:107-171`, `:192-199`; `scripts/hd_assets.py:323-383` |
| External replacement | Standard `manifest.ini` maps original content IDs to external PNG/DDS files. Multiple packs stack in order; last pack wins. Launcher/overlay settings or environment enable them after restart. Missing/malformed entries retain original textures. | `docs/hd-textures.md:56-101` |
| Runtime confirmation | Lossless runtime PNGs plus `textures.jsonl` provide authoritative source IDs and decoded IDs; an existing bounded alias map contains 13 runtime-to-archive IDs. | `docs/hd-textures.md:103-117`; `config/hd-runtime-aliases.json:1-19` |

## Category implications

Historical gallery counts: UI/menus 11,261; customization 4,988; venues 1,585; cinematic environments 1,055; props 296; environment maps 215; fighters 213; crowds 212; other 89; HUD/tutorials 58; cinematic characters 55; animated textures 47; effects/masks 8; loading emblems 6; unresolved 1. These overlap when aliases share a source ID. Source: `docs/research/hd-full-lanczos-corpus.md:70-90`.

The current categories are a useful starting filter, not semantic truth. There is no dedicated portrait classification, anatomical region map, tattoo/logo/text region map, fighter-to-variant relationship graph, or material/UV annotation. `screens/` takes UI precedence even if a member contains a character name (`scripts/hd_assets.py:228-231`, `scripts/hd_corpus.py:62-65`), so portraits may be mixed into UI. Fighter versus customization provenance is established: `v2ip.viv` carries named fighter atlases; `v2cp_*.viv` carries create-player parts. A generic create-player atlas is not established to be a face (`docs/hd-textures.md:170-174`).

Use two independent dimensions: **where it is used** (UI, portrait, fighter, customization, venue, etc.) and **what it needs** (tattoo, lettering, fabric, skin, tiling, mask, animation, etc.). Retain all original aliases and allow several tags. Manually identify the first pilot's fighter/part/variant using XML provenance and in-game capture rather than treating an atlas filename as proof.

## Identity and replacement contract

`source_id` is SHA-256 over `XRTEX01\0`, five little-endian uint32 values (format, visible width, height, palette count, row texel width), tightly relevant base-level source texels/blocks, and full BGRA palette. Addresses are excluded. A decoded identity uses format `0x12`, tight BGRA pixels and no palette. See `scripts/hd_assets.py:26-29`, `:217-219` and `docs/hd-textures.md:111-117`.

**The replacement key remains the original texture ID even when generated output pixels change.** Output hashes identify revisions; they must not become lookup keys. Keep canonical archive ID, authoritative runtime ID(s), decoded ID, aliases and independent output hash in a revision record. Archive IDs can match directly but may differ if the game transforms palettes/pixels before upload. Do not infer full coverage from the 13 aliases or from an attractive offline gallery. The older four-field census IDs are obsolete (`docs/research/hd-full-lanczos-corpus.md:36-41`).

The current manual pack contract is:

```text
<data>/mods/restored-pilot/manifest.ini
<data>/mods/restored-pilot/textures/<original-source-id>-r0003.png
```

```ini
[pack]
schema=1
name=Restored pilot
png_mips=channels
[textures]
<authoritative-original-runtime-id>=textures/<original-source-id>-r0003.png
```

`channels` above is only an example for a reviewed material-alpha texture; transparent UI generally needs `opacity`. The policy is pack-wide, so split outputs into separate opacity/channels packs as needed. Names/paths must use accepted ASCII characters, stay relative and avoid `..`. Runtime accepts straight-alpha PNG at uniform integer scale 1x-8x with the same full-atlas aspect/layout; guest dimensions and UV coordinates stay original. Runtime PNG mip behavior is alpha-weighted RGB for `opacity` and independent channel filtering for `channels`; alpha semantics are not auto-detected. Classic BC1/2/3 DDS with validated supplied mips is accepted; BC7/DX10/arrays/cubes/volumes are unsupported and DDS row-padding cases fall back. No automatic sRGB switch occurs (`docs/hd-textures.md:79-101`).

The current default replacement cache is **2,048 MiB**, set by `TEXTURE_CACHE_MB` (`src/hooks/pc_settings.c:43-51`); the 512 MiB figure in `docs/hd-textures.md:98` is historical. The source explains that a four-fighter match holds about 2 GiB of replacements, while 512 MiB caused repeated eviction/decoding on the Steam Deck. First-use decode/upload stalls are documented separately (`docs/hd-textures.md:31-40`). 4x each axis is 16x texel count; choose 2x or 4x by visible benefit, then inspect actual game distance and performance. Edited files/manifests require restart; the current loader is not a hot-reload texture painting system (`docs/hd-textures.md:101`).

## What the existing generators do and do not support

`build-hd-pack.py` is a **fixed faithful Lanczos builder**, not an arbitrary pack authoring API. It regenerates the census, creates immutable code/input-recipe directories, invokes `hd_corpus.build`, and assembles checked outputs. Assembly requires every selected output to be RGBA exactly 4x the original dimensions and to match the corpus's stored file hash. It generates `faithful-hd-<recipe-prefix>-opacity` and `...-channels`, creates ownership markers, and links/copies output files. Existing changed targets are rejected. See `scripts/build-hd-pack.py:33-102`, `:105-133`.

Do not replace accepted cached PNGs in place. They can share hard links with installed faithful packs. A separate overriding pack avoids mutating the baseline and its reviewed receipts (`scripts/build-hd-pack.py:74-93`; `scripts/hd_corpus.py:149-155`; `docs/hd-textures.md:42-46`).

`config/hd-recipes.example.json` is explicitly an early runtime-capture pilot: defaults unapproved, many categories 2x or excluded, and only three texture overrides approved. It is not the shipped corpus recipe (`docs/hd-texture-workflow.md:29`; config lines 3-80). `hd_assets.batch` merges defaults, category settings and per-runtime-ID overrides, leaves unapproved/unknown entries in `review.json`, and currently accepts **only** `lanczos`, `realesrnet-x4plus`, `realesrgan-x4plus` at 2x/4x. It has no imagegen runner or arbitrary candidate import (`scripts/hd_assets.py:390-440`).

Some workflow documentation records historical release holds or describes widescreen as future work despite later releases. Use current `PROGRESS.md` for release status and code for capability; do not reopen completed release gates based on old handover prose.

## Missing layer for imaginative restoration

1. **Revision metadata:** one stable asset record plus immutable candidate revisions (parent revision, original/baseline/output hashes, prompt, referenced image identities, tool/model where available, generation date, edit scope, masks/regions, notes). Avoid claiming deterministic regeneration from a generative service; retained exact output is the reproducible artifact.
2. **Candidate import and validation:** import manually generated/edit outputs, verify dimensions/aspect/channels, restore separately approved alpha, retain the whole atlas placement and gutters, and reject accidental flips, crops, altered islands or unexpected silhouettes. The existing Lanczos hard-coded builder is unsuitable unchanged.
3. **Review UI extensions:** original + accepted Lanczos + chosen candidate; switch/history among arbitrary revisions; region annotations and targeted revision notes; approve/reject/select a revision rather than only good/concern for one fixed output. Existing review records key only source ID and have no revision/output hash, so a vote can otherwise silently refer to changed art.
4. **Pack publication from explicit selection:** export only approved candidates to a small overlay pack, resolve all verified runtime aliases, split alpha mip policies, record what was installed, and retain rollback to faithful HD. Existing gallery flags do not change pack processing or manifests.
5. **In-game evidence:** record original/faithful/candidate captures using matched harness routes, settings and RNG seeds where possible. This does not guarantee pixel-aligned frames: poses, crowds, cameras and loading timing can vary, and the prior pilot explicitly warns that captures are appearance reviews rather than synchronized comparisons (`docs/research/hd-lanczos-game-pilot.md:70`, `:108`). UV seams, material channels, lighting response, animation consistency and readability cannot be established by flat-image comparison alone.

## Suggested bounded pilot

Pick roughly 8-12 assets spanning one named fighter's skin/tattoo and clothing atlases, one customization garment, one portrait/UI image, one venue tile, and a lettering/logo example. Start from originals plus accepted Lanczos; keep a stylized low-poly-era appearance, existing shapes, dirt/wear and game art direction. For known spelling/logo/tattoo detail provide a verified reference rather than pretending the tiny source contains recoverable detail. Separate intentional redesign from evidence-based restoration in notes.

Request alternatives for a single asset, inspect them at whole-atlas and crop level, then revise a bounded region of the selected output. Preserve alpha/material channels unless deliberately reviewed. Keep wrapping boundaries and UV islands fixed; test repeating textures as a tiled preview and animation variants together. A sufficiently expressive selective pass can be substantially more imaginative without processing all 18,971 images blindly.

Only after the comparison/revision pilot works should bulk categories be queued. Preserve the faithful pack; put approved experiments after it in pack order. External modpack packaging can wrap the same replacement directories without changing the texture lookup hook, subject to the separate PR17 integration review.

## Owner questions raised by this source review

- Which specific fighter/customization garment/venue should define the first look?
- Should visible logos, tattoos and words be exact restorations from supplied references, or may ambiguous areas receive new interpretations?
- How much change to faces and likeness is intended? The earlier Lanczos decision explicitly avoided face restoration; the new request authorizes a more imaginative experiment but does not define this boundary.
- Is the target output 2x/4x for pilot review, and which platform/performance budget should gate final acceptance?
- Should new candidates be reviewed in a local extension of the existing gallery, with explicit per-revision approval and notes, before joining an external modpack?

Originals, generated artwork, captures, models and review HTML outputs remain outside source control. This report does not authorize distribution or publication of any game-derived art.
