# Logo/emblem restoration review — 2026-10-17

City approved under D133; sequence D134: title logo and menu emblems first,
then Options/Jukebox and Battle setup/selection. Nine new art trials are NOT
approved/installed. Mode Select keeps its conditional right-edge lighting review.

Reproduce source references with prepare-native-references.py from the original
recomp working directory (private retained corpus path is recorded), then run
prepare-emblems.py with the reviewed emblem-geometry.json. The exact original
35reference hashes and8active assemblies remain. Generations.json saves all9
built-in calls/prompts/input hashes/raw paths and dimensions. No API key/CLI used.

Run restore-branding.py with the authoring .venv Python, Pillow/NumPy and its
source color_trial helper. The exact helper source snapshot and runtime versions
are retained for reproducibility. Generated visible bounds align a surface
proposal only; strong source structure, Faithful4xalpha,seams,padding remain
held. AI broad lighting/chroma/geometry/alpha are rejected. Fine L residual at
35%,bounded2L is deliberately subtle. Credits remains essentially FaithfulHD.
Tile splits preserve21original canvases/IDs and unused texels.

verify-branding.py independently checks reference hashes,9protected/alpha pairs,
21split reassemblies/padding and all old/new approved scenery pins. Browser
72comparisons/backdrops/approval states are recorded in verification.json.

The current parent review.html includes the new section. update-review.py can
add it once to a disposable COPY of the city-approved pre-branding page; the
original pre-city/pre-branding page is retained as review-before-branding.html.
Do not replay the HTML patch on a live already-patched page.

This is private artwork/provenance, not a game pack. Writer8768 untouched.
