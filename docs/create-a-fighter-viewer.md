# Create-a-Fighter texture inspection

The CAF fitting room assembles original customization parts in a static source
pose and compares texture revisions on the equipped model. It is a companion to
the texture workshop, with its own outfits and inspection queue. The existing
workshop, accepted corpus, artwork, reviews and fighter model caches are read-only.

## Start it

Build a new private cache from your own extracted Xbox dump and existing corpus:

```sh
defjam-tools caf build --dump /private/extracted --corpus /private/corpus \
  --output /private/caf/cache-v2
defjam-tools caf serve --corpus /private/corpus \
  --workspace /private/texture-workshop --catalog /private/caf/cache-v2 \
  --state-dir /private/caf/inspection --port 8780
```

Use absolute paths on every platform. On Windows, use the corresponding drive
paths and virtual-environment executable. Output must be outside source, the dump
and the accepted corpus. The state folder must be separate from the cache and
production workshop. A second process cannot write the same inspection state.
An existing cache is never overwritten: build to a fresh directory after decoder
changes, preserving the previous cache for rollback. No accepted corpus rebuild
or workshop schema migration is needed.

Open [the fitting room](http://127.0.0.1:8780/caf-viewer). It serves bundled Three.js
locally and does not need a running game, network access or an image-generation API.

## Build an outfit

Choose a source body build and skin palette. Expand Clothing, Hair & grooming,
Jewelry, Tattoos, or Body & face in the left sidebar. Search by category, resource
name or exact source ID. Clothing entries use the game's own English item and
color names, read from the owner's shop database and localization. The item name
is prominent and the texture resource ID remains below it. Sidebar previews are
the actual texture maps, rather than guessed shop thumbnails.

Expand Tops and choose a named garment, then a color and wearing style. The
sidebar buttons and inspector selectors stay synchronized. Styles such as open,
half buttoned and buttoned up select the corresponding source model. Changing
color retains the wearing style where available. The same navigation covers
pants, shoes, hats, left wristbands, gloves and eyewear. Items with one option
show that option without inventing alternatives. If the original fitting text
is missing or a technical placeholder, the tool labels it "Source style".

Source resources remain available in an additional disclosure for each mapped
category. **Source controls** also opens every original design/color choice on a
retail-mapped model; **Garment controls** returns to the named options. Other
customization groups keep their original design/color controls.
Tops, pants, shoes, scalp/hair, facial
hair, headwear, jewelry and the nine tattoo placements can be combined. Replacing
a slot replaces that slot's geometry and texture choices. Body skin is composed
under tattoos and clothing using the source atlas coordinates.

The six source builds A–F use the game's actual mesh deltas and full neck fits.
Cache decoder 2 also applies the default face's build-dependent fitting morph,
which closes the A/B and E/F face-to-neck boundary without moving the head or
editing the textures. Decoder-1 caches remain readable; build a fresh decoder-2
cache to obtain the new fits and shop names. Existing outfits, queue entries and
revision IDs use the same schema and require no migration.
The tool deliberately retains these source names: correspondence with retail
M/L/XL/XXL labels has not been established. Shoes, hands, rings and facial hair
use the original shared-fit rules; necklaces retain independent build fits.

The retail wardrobe is a navigation layer over the existing XML selections.
It is independent of Story unlocks and purchases. Automatic shop compatibility
rules, such as removing conflicting jewelry or pairing wrist accessories, are
not simulated. Left and right wrists remain explicit separate slots; right-wrist
resources keep the source controls until paired behavior is verified.

Save named outfits to reuse the same context. Each stores the build, skin,
equipped items, exact design/color resources, palette choices and per-source
revision IDs. The session also saves camera and display settings.

## Compare revisions

Select the texture map, then choose Version A and B: Original, Lanczos 4×, or an
immutable imported revision. Quick selectors above the model work on narrow
windows too. Use **Showing A/B**, **Hold A**, or synchronized side-by-side views.
Only the selected source texture changes between sides; all other equipped
revisions, geometry and cameras remain fixed. Shared source aliases necessarily
share the same texture version.

**Keep B on this outfit** retains that version while you inspect a different
item. Equipping another color resource selects its own source identity and history.
**Refresh texture revisions** discovers new imports without restarting the
production writer. Revisions are checked against their stored SHA-256 before use.

Orbit with left drag, pan with right drag and zoom with the wheel. Front, Back,
Fit, Selected item, Face, Chest, Pants and Shoes offer repeatable framing. Texture
RGB is the default; Studio adds approximate lighting. Wireframe and selected-part
isolation help inspect distorted lettering, seams, islands and small jewelry.

Original sampling is reconstructed with bilinear interpolation inside the common
inspection atlas; Lanczos and imported pixels retain their own interpolation.
This is an offline comparison, not a captured game rendering pipeline.

Named `plNN` palettes reproduce the indexed source colors (and a Lanczos preview
of that selected palette). Imported RGB revisions remain as authored. The service
rejects applying an indexed palette to a restored RGB candidate instead of
guessing a recoloring operation. Choose Authored RGB when inspecting those drafts.

## Secondary inspection

The updated 2D gallery has **Secondary inspection · CAF** for customization
textures. It opens the separate service with the exact source and reviewed
revision; it does not change the gallery's notes or approvals. The default link
targets port 8780. Custom service ports require adjusting the link manually.

Any authoring gallery can use this link shape, substituting its exact IDs:

```text
http://127.0.0.1:8780/caf-viewer?asset=SOURCE_ID&revision=REVISION_ID
```

From the fitting room, **Send B to secondary inspection** pins that exact revision
and its image hash in the durable queue. Opening a queue entry equips its explicit
XML-related item/resource and selects the pinned revision. When one source has
multiple uses, prefer its currently equipped use or choose the intended item in
the wardrobe. Unmapped sources remain unresolved; no visually similar substitute
is selected.

Record Pending, Inspected or Needs work and revision-specific notes. Notes have
browser draft recovery and an unsaved-navigation warning; Save inspection commits
them immediately. Conflicting saves from another tab are refused. These records
do not approve artwork, select a pack, install a mod or claim game verification.
Back up the inspection folder and use **Back up outfits & inspection queue** for
a JSON copy. Artwork and the accepted corpus require their existing separate
backups; the inspection JSON is not an artwork backup.

## Evidence and limits

The initial own-dump build indexed 38 XML groups / 879 entries, 5,319 texture
resources and 483 static mesh resources, with no rejected mesh/build conversion
in the final cache. Entry counts include non-geometric decals, face blend shapes
and internal templates; they are not counts of supported garments. Face blend
shape controls and internal templates are excluded from the equip browser.

[Assembly evidence](research/caf-static-assembly.md) records the source attachment,
palette, morph and layer rules. Geometry, original UVs, normals and material
partitions are preserved. Texture alpha and hidden RGB remain independent during
resizing; tattoos are composed from their alpha-bearing source artwork. A narrow
shoe variant's vertex-color morph is explicitly omitted from RGB inspection,
consistent with the existing fighter viewer.

This is an inspection preview. It does not reproduce animation, face blend-shape
editing, the complete hat/hair compatibility rules, injury switching, game
irradiance/specular effects, palette adaptation of restored RGB art, or sparkle
effects. Source rest-pose alignment does not establish animated fit or exact game
appearance. Confirm representative outfits, colors, decals and seams in the game
before treating artwork as native-verified. No game mesh export/reimport or
automatic installation is added.

Only code and synthetic tests belong in Git. All catalogue JSON, decoded models,
source palette data, images, inspection state, captures and private receipts stay
outside the repository.
