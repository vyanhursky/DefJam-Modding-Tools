# Menu lettering restoration and private project records

The tools repository owns reusable authoring code and procedures. The game owns
runtime loading, settings, installer integration and in-game diagnostics. The
catalogue owns released version metadata, compatibility, download pins and concise
release notes. Each pack's detailed production history belongs in its private
workspace, independently backed up outside any disposable Git worktree.

## Restore a word or banner

1. Identify the exact source texture, original canvas, sampled UV area and alpha
   role. Assemble adjoining materials into one logical artwork before generation.
2. Use the original at its actual dimensions as the geometry and palette authority.
   A faithful enlargement helps inspect it; an accepted remaster is a style reference.
3. Generate a new immutable draft. Keep the submitted prompt, reference hashes,
   raw result and derived preview together under a stable revision ID.
4. Register the complete result to measured original bounds, spacing and baseline.
   Split joined materials from that one registered master. Register font-page glyphs
   individually to their original cells. Preserve atlas context and proven gutters.
5. Compare original and draft at 1x, a 1440p reference scale and enlarged detail.
   Keep fighter-select dark lettering on the pale select-paper backdrop; loading
   light lettering needs a portrait/dark backdrop. Distinguish baked paper, ink,
   alpha, shadows and separate runtime layers before removing any of them.
6. Record explicit owner approval of exact hashes. In-game validation and publishing
   are separate steps. Use isolated packs/saves and serialize native game runs.

## Reusable prompt template

> Restore this exact source artwork at higher resolution. Preserve the literal
> lettering, type style, individual glyph shapes, cap height, width, spacing,
> baseline, stroke weight, counters and stencil gaps shown in the original.
> Keep its original ink palette, material and intended wear. Resolve pixelation
> into clean edges and believable fine detail without redesigning the lettering.
> Preserve flat ink where the source is flat; add no bevel, extrusion, extra outline,
> drop shadow or outer depth rim. Keep every letter and ornament in the same place.
> Preserve intended transparency. The original controls structure and colour;
> other references guide texture detail only.

Add source-specific observations instead of relying on the template alone. Plain
music-list lettering must retain enough original stroke weight at 1x. Distressed
serif headings need the original face proportions and cap height. Fighting-style
labels need their source-specific stencil cuts, including gaps on curved letters.
Result stamps need the source frame softness and transparent interior. Match reds,
cream and gray to the original; a crisp edge must not brighten or saturate the ink.
Remove accidental green edge contamination only after identifying intentional
colour and protected effect layers. A prompt cannot guarantee a pixel lock.

See [native registration](menu-native-registration.md) for mechanical geometry and
[lossless PNG staging](lossless-png.md) for exact RGBA/metadata preservation. Preserve
raw imagegen masters; optimize final staged native exports. Rebuilding a ZIP need
not reproduce identical archive bytes. Publish a new immutable version and pin
its actual size/hash whenever an artifact changes.

## Keep one complete private project

Retain original IDs/aliases, reference and raw image hashes, exact prompts, every
revision and approval, crop/UV geometry, generated previews/viewer data, native
exports, build receipts, captures and checkpoints. Historical rejected drafts help
explain later corrections. Keep schemas, parent provenance and relative image
paths intact. An inventory or backup pointer is not an artwork backup.

Before reorganizing a project, copy records byte-exactly, verify a manifest, retain
an independent backup and preserve the original workspace. Do not move/delete the
live review files or change its port: browser notes may depend on the origin.
Record machine paths in ignored local configuration or a private handoff. Public
source may include synthetic examples and reusable recipes; actual production
review ledgers and checkpoint pointers stay private. Publish compact release
metadata and an integration summary with references to their owning repositories.
