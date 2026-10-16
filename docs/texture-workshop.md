# Local texture workshop

The workshop reviews the existing texture corpus without changing it. The pilot
is **Blaze, Nyne and Trejo**. Following the initial comparison, new generations
use **Rich original detail** only (owner decision, 2026-10-16). Earlier
**Stylized remaster** candidates remain available as history. Preserve faces and likeness; a specific
low-resolution defect can be flagged for a separate correction. Use references
for recognizable tattoos, logos and clothing inscriptions, and leave uncertain
details for Vlad's approval.

For recognized artwork, the original atlas controls composition: existing animal
silhouettes, tree positions, handwriting paths, letter spacing and flourishes.
Descriptions such as "bear/deer/forest" or "Debbie Danielle" clarify ambiguous
marks; they do not authorize a new arrangement or font. Supply the original
atlas and its faithful enlargement as visual references during regional repair.
Check edited interiors against the source as well as pixels outside the edit
boxes; a perfectly preserved exterior does not establish interior fidelity.

## Open and resume

Requires Python 3.10+ and Pillow. Use the same isolated Python environment as
the HD tools; no package installation or paid image API is needed by the gallery.

```sh
defjam-tools serve --corpus /path/to/existing/corpus --workspace /path/to/review-workspace --port 8768
```

Open [the local workshop](http://127.0.0.1:8768). `--corpus` is the folder containing
`corpus.json`, `originals/`, `textures/` and `thumbs/`. `--workspace` must be a
separate local data folder, outside tracked source. Reuse both paths next time.
The server binds only to loopback and permits one writer per workspace. Stop
it with Ctrl+C; restart with the same command to resume.

Notes, flags, regions, candidate decisions, the imagegen queue and the last view
are saved in `workshop.json`. Imported PNGs remain under `candidates/`; exports
are separate. Atomic saves and version checks prevent a stale tab from silently
overwriting a newer note. A browser draft is retained after a failed save;
reload, review the current record and choose **Restore draft** to merge it.
Copy the whole workspace when moving computers. **Back up review** exports JSON
notes/history; it does not embed image files or make the corpus portable by itself.
Keep the matching corpus and the candidate PNGs as well.

The [fighter model viewer](model-viewer.md) now provides synchronized 3D A/B
comparison for Trejo, Blaze and Nyne, using the original mesh and UVs. Open it
from the sidebar, choose a revision, and inspect it in the source rest pose.
Camera settings persist separately; notes and flags share the gallery reviews.
It also downloads the selected texture on a static model as a private Blender
GLB. Animation, venue conversion and game mesh replacement remain future work.

## Browse and compare

- **Pilot · main atlases** shows the three primary battle textures. **Pilot ·
  all variants & maps** includes all fifteen source images across five models.
  Blaze's story and bloody variants are labeled separately. Secondary-map
  purposes are unverified; their names do not establish alpha/material semantics.
- **Full texture library** browses the supported corpus, with categories, search,
  paging and filters for flags, notes, candidates and selections. Portraits,
  customization thumbnails and venue previews have extra provenance filters.
  Shared images can appear in several categories.
- Original and faithful HD are real retained images. The two candidate lanes
  remain empty until a real PNG is imported. They never relabel a baseline as a
  generated restoration.
- Zoom and pan are synchronized at a common atlas scale, with **25%, 50%,
  100%, 200%, 400%** and **Fit**. **100%** displays the
  faithful 4x output at one pixel per CSS pixel; the original is enlarged to match.
  RGB/alpha views, checker/light/dark backgrounds and holding **Original** help
  inspect detail and masks. Open the full PNG for a separate unrestricted view.

Choose **Reviewing** to attach notes to the original asset or an exact candidate
revision. **Mark region** lets you drag a rectangle, choose protect/revise/reference
and save a note. Rectangles use normalized atlas coordinates and are shared across
comparison views. A protection annotation is an instruction, not a pixel mask:
it does not alter the PNG or guarantee a generation model preserves that area.

## Generate and revise with Codex

**Prepare imagegen brief** combines the art direction, saved notes and regional
instructions. Save it to the Codex queue. Codex can read the workspace and use the
built-in imagegen tool; the gallery itself makes no cloud/API calls. Queueing a
request does not start generation. Both style directions can be queued separately.
Original/baseline hashes are checked when queueing; a candidate-parent request
names that exact PNG and its hash as the edit target.

Import the resulting PNG with **Import candidate PNG**, assigning a label,
direction, parent revision and exact prompt/reference notes. The full atlas must
retain its dimensions at a uniform integer scale of 1–8x. A square image alone
does not prove UV islands, face regions or inscriptions stayed registered.
Every import is a new revision, including a revision with identical bytes;
earlier PNGs and decisions remain available in the lane selectors.

For Codex or command-line import while the server runs:

```sh
defjam-tools workshop import --server http://127.0.0.1:8768 --asset ORIGINAL_SOURCE_ID --image /path/to/candidate.png --label "Detail pass 1" --style faithful --prompt-file /path/to/prompt.txt
```

Use `--style remaster` for the other direction and `--parent REVISION_ID` for a
child. Reload the gallery to see an import performed outside the browser. Without
`--server`, supply `--corpus` and `--workspace` and close the running server first.
No generation output has automatic approval.

Prompts alone cannot lock facial pixels. When a generated draft has the same
aspect ratio but a different resolution, Codex can explicitly normalize it and
restore protected regions and the full alpha channel from faithful HD:

```sh
defjam-tools workshop import --server http://127.0.0.1:8768 --asset ORIGINAL_SOURCE_ID --image /path/to/raw-draft.png --label "Protected draft 1" --style faithful --prompt-file /path/to/prompt.txt --assemble-scale 4 --protect-region 0.5,0,0.5,0.5 --request-id QUEUED_REQUEST_ID
```

Each protection rectangle is normalized `x,y,width,height`; repeat the option
for separate patches. Choose coordinates after inspecting that specific atlas.
This technical assembly retains the raw generated PNG under `raw/`, records its
hash and dimensions, and records every copied pixel box and baseline hash.
Resize preserves independent RGB and alpha channels. A mismatched aspect ratio
is rejected. It does not fix shifted UV islands or invented artwork: those still
need review and game tests. The pilot's raw outputs may be smaller than the
requested 2048 pixels; assembly records the actual generation resolution.

For a targeted revision, add `--parent REVISION_ID` and repeat
`--edit-region x,y,width,height` for the areas that may change. Assembly copies
generated pixels only inside those boxes and retains the parent elsewhere,
then applies any explicit baseline alpha/protected-region restoration. Parent
hash and resolution are checked and the edit boxes are recorded. This is an
explicit pixel operation, separate from the gallery's instructional annotations.
Use the matching parent PNG as imagegen's edit target and retain the exact prompt
and owner feedback. Earlier candidates and their notes remain available.

## Local test-pack export

Approve a candidate's atlas, confirm face preservation or its reviewed correction,
check texture channels/layout, and select it for export. Only one revision per
original source ID is selected. **Verified in game** is recorded separately;
exporting a local test pack is how a selected candidate can reach that test.

**Export test pack** writes a new version under `workspace/exports/`. It copies
approved PNGs, writes schema1 manifests and a hash-bound receipt, and separates
transparency/material-channel mip policies. It does not install or enable packs.
The receipt says which candidates have game evidence. Changed PNG bytes fail
export and must be imported/reviewed as a new revision.

Copy the component folders into the game's `mods/` folder. List faithful HD
first and these components last, then restart. Setup's optional faithful-HD
regeneration can reverse that priority, so check order after repair/update.
Unmapped keys inherit earlier packs; a malformed winning replacement uses the
console original. Known runtime aliases are included, but the existing alias
map is bounded: confirm actual loads in game before claiming coverage.

The game archives, profiles, settings, original corpus and accepted HD packs are
never modified by this tool. Generated art, screenshots and review data remain
local. PR17's external mod-manager integration and public pack distribution are
separate work; current exports are ordinary local texture packs.

Implementation: `src/defjam_tools/texture_workshop.py` and its packaged resources.
Synthetic persistence/export/HTTP tests: `tests/unit/test_texture_workshop.py`.
