# Extraction validation — 2026-10-16

Authoring moved from DefJamFFNY-recomp `f71ab64` into this standalone application.
Its original core bytes and extraction provenance are in provenance.json.
Recomp's installer core remains frozen; only authoring copies were retired.

- 56 synthetic tests plus 12 subtests pass locally and from a fresh Git clone.
- A separately installed wheel loads its packaged UI, Three.js/license/pins,
  FFNY aliases and corpus HTML without a recomp checkout. Browser renders the
  existing Trejo v4 on the original mesh with no console errors on that probe.
- Existing catalog and full fighter details compare equal across old/new apps.
- Six original/faithful fighter GLBs and Trejo v4 GLB compare byte-for-byte equal.
- An explicitly selected pack exported from disposable old/new workspace copies
  has identical manifest keys, images and channel policies.
- At live cutover, workshop.json and model-viewer.json match their pre-cutover
  hashes; all 11 candidate PNGs match recorded hashes. No workspace relocation,
  corpus rebuild, ID/schema change or approval reset occurred.
- Live server switched to the same loopback origin/port; a metadata backup lives
  in the private workspace. Browser confirms the existing notes/candidates.
- Recomp focused HD/setup/core-pin/instruction tests pass34/34.

The private probes and screenshot remain outside tracked source. Source-only
GitHub CI is configured for Linux, Windows and macOS; its remote results are
separate from the local evidence above. No native Blender import, in-game
regression, runtime update, art generation or game data publication was performed.

Windows CI initially exposed default-codepage decoding of UTF-8 review JSON.
All implicit module text reads now specify UTF-8; a simulated cp1252 roundtrip
checks non-ASCII notes and queued prompts. Linux/Mac initial CI passed; rerun
Windows after this fix.
