# Published texture library

Open **http://127.0.0.1:8768/packs** on the existing workshop server. This view
answers “what actually shipped?” independently of authoring candidate selections.
It reads locally available release ZIPs, verifies their pinned size and SHA-256,
and lists every native manifest mapping, widescreen slab/inner image and otherwise
unreferenced supporting PNG. Runtime `stretch` entries annotate their native row.
It does not download, install, re-encode or select a replacement.

## Review a release

Choose a collection, then search text, source IDs or archive/source paths. Filter
by category, native/widescreen/supporting component and the new review status.
Gallery offers 10, 25, 50, 100 or 200 items per page (default 50). The choice
persists in this browser and applies to paging and J/K navigation across page
boundaries. Changing it returns to the first matching page.
The gallery pairs original and published thumbnails. Click a card for original,
Faithful 4× and exact published comparisons. Add a workshop candidate or another
configured release in **Additional comparison**. Candidates are explicitly drafts;
only the Published panel represents the selected release.

Use Fit, 1×, 3× (1440p reference) or 6×. Roll the mouse wheel over an image
to zoom around the cursor; left-drag to pan. Every pane shares the same zoom
and original-canvas focus, including an optional fourth comparison. Double-click
an image to restore Fit. Wheel zoom spans 0.1×–16× and displays a Custom percentage.
The chosen scale persists; moving to another texture recenters its artwork.
Fixed scales register all panels to the original canvas; scrollbars/keyboard
panning also stay synchronized. Focus artwork
uses an optional normalized source crop equally across panels. Full canvas is
always available. Dark lettering can use pale paper, and light lettering a dark
portrait approximation. These are inspection backdrops, not game captures.
Use RGB/material for fighter textures whose alpha is a shader channel. RGBA is
appropriate for UI opacity; Alpha exposes the original channel separately.
Missing references are explicitly unavailable, never silently substituted.

Mark **Looks good**, **Needs revision** or **Question**, and add notes. Status
buttons save immediately; Save notes and Save & next also persist notes.
Navigation saves pending notes first and stops if saving fails. Unsaved drafts
are retained in this browser; a stale server version produces a conflict rather
than overwriting another tab. J/K move through the filtered list when focus is
outside form controls. Export review notes downloads a JSON revision queue.

This is a **new revision pass**, not a migration or reversal of art approvals.
Records are scoped to archive SHA-256, manifest entry and PNG SHA-256. Opening a
new release does not carry approvals forward. Existing workshop reviews, source
IDs, candidates, model views and selections are neither rewritten nor reset.

## Configure private pack inputs

Keep ZIPs, metadata and review data outside source control. Launch with the normal
profile and an additional private config:

```sh
defjam-tools --profile local.json serve --pack-library /PRIVATE/library.json
```

A schema-1 configuration (replace placeholders with real private paths and pins):

```json
{
  "schema": 1,
  "review_root": "/PRIVATE/published-review-pass",
  "packs": [{
    "id": "my-menu-pack-1.4.0",
    "name": "HD Menus",
    "version": "1.4.0",
    "archive": "/PRIVATE/my-menu-pack.zip",
    "size": 123456,
    "sha256": "FULL_ARCHIVE_SHA256",
    "metadata": "/PRIVATE/menu-labels.json"
  }]
}
```

`id` uses lowercase letters, digits, dots, underscores and hyphens (80 characters
maximum). `metadata` is optional. Archives must have one schema-1 `manifest.ini`
and PNGs inside its root. Absolute/traversal paths, duplicate case-insensitive
members, symlinks and missing/oversized images are rejected. Individual PNGs are
bounded to 64 MiB and 64 megapixels. The original release ZIP stays immutable;
changing it requires a new hash pin and produces an independent review scope.
There is no network/CDN dependency.

Original/Faithful references match **exact corpus source IDs**. Supplemental
metadata may explicitly link a `corpus_id` where an independently verified alias
is needed. Do not infer identity from filenames or partial hashes. A private
metadata index has this structure:

```json
{
  "schema": 1,
  "sources": {
    "FULL_SOURCE_ID": {
      "label": "Main Menu",
      "family": "Menu headings",
      "context": "Main menu heading",
      "crop": [0.1, 0.2, 0.9, 0.8],
      "backdrop": "portrait",
      "provenance": "Optional reference description",
      "original": {"path": "/PRIVATE/recovered-original.png", "sha256": "FULL_PNG_SHA256"},
      "faithful": {"path": "/PRIVATE/faithful-4x.png", "sha256": "FULL_PNG_SHA256"}
    }
  }
}
```

Fields other than the source key are optional. Crop is `[left, top, right, bottom]`
in normalized **full original canvas** coordinates. Explicit original/Faithful
references must be complete native canvases and hash-pinned. If creating a new
Lanczos 4× reference from a recovered original, document that provenance; do not
label a previously published reconstructed image as Faithful or downsample HD art
and label it Original. Wide pieces are displayed without fabricated registration
to a whole native texture. Aliases may supply the original corpus-style list for
search/navigation; they are descriptive, not an identity match.

## Storage, backup and cutover

New records live in `review_root/pack-reviews.json` (schema 1, optimistic version
checks and atomic replacement). A dedicated writer lock protects this directory;
it must be disjoint from both corpus and authoring workspace. Keep the directory,
private configuration, label indices and immutable ZIPs when moving source trees.
Export JSON is a review queue; it is not a backup of images. Browser drafts belong
to this host/port and hash scope.

Before replacing a live server, check that browser notes are saved, snapshot
`workshop.json` and `model-viewer.json`, preserve the live source revision and
profile, and stop the sole writer. Start the new code on the **same** 127.0.0.1:8768
origin. Verify those files, old candidate hashes and model catalogue before/after.
Do not replace a live feature branch with an older main checkout: apply the
additive library change to compatible source that retains its existing tools.
Test writes against an isolated review root before cutover, not owner reviews.
A server started without `--pack-library` still serves the old workshop normally;
`/packs` explains how to configure release inputs.
