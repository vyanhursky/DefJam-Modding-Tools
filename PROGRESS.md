# Def Jam Modding Tools — progress and handoff

## Current status

**2026-10-29: Freeway cap digits and Elephant Man figurine repaired; review live.**
Owner reports missing 1972 on Freeway, tentatively accepts Bonecrusher visually and
requests a playtest reminder at NEXT HD Fighters test-pack preparation. Mack 10/
Scarface tattoo wording remains unreadable; owner has no references. Two supplied
photos guide Elephant Man's figurine repair. No other art approval inferred.

Two successful focused built-in edits, raw 1254 square, assembled 2048 RGBA:
- Freeway v2 r-147f669c58b940a3, parent r-2436393d909b4317. Original 19 | 72 split
  across cap seam restored at source scale/placement. 5,085 changed pixels; both
  pairs individually checked, middle gold seam exact. SHA256
  ee4caf285052abf161f783eda07522765b959396526c3632e7cb1ae22aa428bf.
- Elephant Man v2 r-c3a6e6f47f6c4cf8, parent r-83ef708e60d1426b. Prior figurine
  became jeweled letters. Original tile controls layout; two owner photos guide
  metal/sculptural detail. 96,400 changed pixels; 3,064 native unmapped tile padding
  pixels included to clear prior lettering, without touching mapped non-jewelry.
  SHA256 02b35d36bbb6c2ee7e5b5420ccaae125576973ad0bd349648cd7b291e1ee8808.

Both full alpha and all parent pixels outside feature masks exact; source palette
matched. Final assembled-v2 equals inspected v1 PNGs, imported once. Exact prompts,
input/reference/source/parent/geometry/raw hashes, frozen processors and receipts
private. New children UNAPPROVED/unselected/not game verified. Original geometry
unchanged. Source/final crop sheets and CPU RGB UV Front/Back diagnostics inspected;
projection ignores alpha/game shaders. Figurine is reference-assisted reconstruction,
not authenticated jewelry. Both live PNG and GLB embedded RGBA/revisions exact.

Bonecrusher r-ea740e0041cb4e30 unchanged, tagged playtest-next-pack and
owner-visually-ok; tentative acceptance recorded without formal/native approval.
Remind Vlad when preparing next test pack, especially shorts/shoes material
behavior and skin/clothing in game lighting/motion. Event checkpoint saved in
private next-test-pack-checklist.json; no timed notification claimed.
Mack 10/Scarface unchanged; reference-needed/tattoo-lettering flags saved. Recommend
retaining original letter paths/spacing. Contour cleanup can improve ink edges,
but cannot verify words. No guessed text/generated/OCR transcription adopted.

Same live writer PID42722/exec17349, origin8768; no restart/reload.25models,
83candidates/30requests. All 81 prior candidate metadata/files retained (includes
unrelated customization drafts). Review feedback appended with optimistic versions
and exact pre-feedback backups; all other reviews/session/requests/cameras/choices
exact. Refresh after saving browser notes, then Latest restoration. Prior browser
URL policy remains; no new browser visual QA or bypass. Public0.2 and game install/
saves/settings/frozen runtime snapshot unchanged. 6 existing focused feature/scope
tests pass; core/UI/API code unchanged. Prior full baseline 104 tests+15subtests.

**Retained prior work:** original five approved/published in0.2; first ten nine
approved complete, Warren v3 r-a2b301c58a8c4680 still awaits complete-back-crest
approval. Luda r-9b80bbe05e6a4b59 / Flava r-9d997f2360fe4bd5 approved. Second ten:
Freeway, Magic, Bonecrusher, Bubba Sparxxx, Capone, N.O.R.E., Mack 10, Scarface,
Elephant Man, Bless; unchanged model decoding/source UVs. Full calibration and
source-palette matching retained. Bonecrusher alpha-cloth RGB opt-in, exact alpha;
N.O.R.E. flag tile lacks static UV coverage (game use unproven). Tiny undecipherable
source scripts remain held, not reconstructed. All private history retained.

## Published baseline

- HD Fighters0.2.0-beta.1: testing/prerelease, min game0.12.1. Only approved five:
  Blaze/Redman v4, Nyne/Trejo v3, Henry Rollins v6.2048RGBA, png_mips=channels.
  Exact revisions/hashes: research/hd-fighters-0-2-beta-20261029/selection.json.
- ZIP34,424,972B; unpacked34,417,307B;8files; SHA256
  1a10e9a714c0c2df00e6c68203213381b1cc628622ce14ae3eb20187c78a8561.
  Immutable Cloudflare size/hash/206range verified. Catalogue PR8 merged as
  d552860160f3ba72e30358f39ca45ad8346d9344; protected publish40914786807 succeeded,
  signed catalogue revision8; existing approval/signing protections retained.
- Released0.12.1 helper/package checker agree; released key verifies public index;
  fresh disposable install exact; stable channel excludes beta; sentinels intact.
  Owner playtested0.1 successfully. Native0.2 acceptance still pending. Neither
  subsequent ten-fighter batch is included. No approved five bytes changed.

## Decisions

- 2026-10-29: owner requests missing Freeway 1972 and reference-assisted Elephant
  figurine repair. Keep original feature layout and all surrounding parent pixels
  exact. Two new children remain unapproved. Verify actual source content survives,
  not just increased pixel/detail counts; a figurine must not become typography.
- 2026-10-29: Bonecrusher seems visually OK; owner chooses reminder at next test-
  pack preparation, not a date. Save event checklist/review tags; native verification
  stays false. Mack 10/Scarface ambiguous tattoo words retained pending evidence;
  no speculative spelling or new tattoo art. Existing strokes control cleanup.


- 2026-10-29: owner approves repaired Ludacris/Flava children and requests complete
  Warren back P plus ten more fighters. Restore BOTH UV fragments; preserve all
  other accepted parent pixels. Never infer approval of a new child.
- 2026-10-29: choose ten new compatible main outfits, avoiding aliases and already
  restored characters. Joe Budden rejected for unsupported index header; older
  Xzibit/Ghostface/David Banner limitations remain. No decoder scope expansion.
- 2026-10-29: final named feature/fragment checks and Front/Back inspection are
  mandatory. Broad logo/prop holds remain pending. High global change counts
  cannot establish complete detail. Inspect rotated jewelry/numbers and every
  repeated cap/back copy; correct inventory without rewriting submitted prompts.
- 2026-10-29: permit verified cloth RGB under explicit alpha material opt-in while
  holding alpha; separately allow declared source tiles only with zero coverage
  across all static UV masks. Never override mapped material holds or infer game
  non-use. No pilot mask/skin anatomy/seam constant is a bulk default.
- 2026-10-29: owner confirms all browser notes saved and authorizes same-origin
  single-writer restart. Exact review/view backups and compatibility checks first;
  no corpus/schema reset, no forced browser reload, no old revision deletion.
- Prior approvals retained: original complete five approved and HD Fighters0.2
  published; first batch nine approved complete, Warren latest child pending.
  Rich Original Detail only; faces/hair/head/headwear included, slightly more
  realistic skin/hair, original likeness/illustrated geometry and restrained
  source palette for ALL materials. Uncertain detail needs owner review.
- Trejo caption Debbie Danielle; original bear/tree/script paths control design.
  Trejo v3 accepted. Rollins v6 uses successful regional tattoo/material inputs;
  earlier whole-atlas failures/studies retained. Frozen accepted bytes unchanged.
- Cleanup uses reversible archived tags; keep PNGs/IDs/prompts/parents/hashes,
  published baselines and saved comparisons. Reconcile notes only with feedback,
  exact backup and optimistic versions. No new-child/pack/game approval inferred.
- Authoring belongs here; runtime/loader/setup remain in recomp with frozen
  compatibility snapshot. No private art/model/review files in Git. Push on request.

## Evidence and validation

- Source recipes: research/hd-fighters-0-2-beta-20261029/,
  research/fighters-batch10-20261029/, research/chest-details-20261029/,
  research/warren-back-logo-20261029/, research/fighters-batch20-20261029/,
  research/fighter-feedback-20261029/.
- Calibration: docs/fighter-restoration.md + fighter-restoration-prompts.txt;
  source-specific coordinates are examples only. Private same-named experiments
  contain exact prompts, inputs/raw/art, masks/receipts/frozen processors, import
  IDs and API/disk backups. review-index.md links final images/prompts/checks.
- 104 pytest tests+15subtests pass. Six new meaningful synthetic tests cover split
  feature omission, alpha cloth opt-in, mapped hold override refusal, UV top-left/
  back orientation, nearest depth/RGB ignoring alpha, and aspect-preserving framing.
- Source hygiene:532 tracked text files,0 policy failures; staged diff check and
  AGENTS/CLAUDE byte identity pass. No private art or models staged.
- Existing gallery persistence/auth/conflict/model export checks retained. Two new
  live PNG/GLB pixels exact; all 81 pre-feedback candidates retained;25models/83candidates.
  Six existing feature/scope tests rerun and pass; prior104+15 full suite is baseline.
  Browser URL policy prevented fresh browser visual tests; no bypass. Atlas,
  feature crops and offline RGB UV projections inspected. Native playtest pending.
- Prior release catalogue14tests, metadata/signature/remote content and install
  checks pass; no catalogue/pack changes this turn. No JS/UI logic changes.

## Handoff

1. Leave current writer PID42722/exec17349 live at8768/model-viewer. Source branch
   codex/hd-fighters-beta in isolated tools checkout; ignored .local-handoff.md has
   exact paths/restart command. No restart needed for these art imports.
2. Owner saves browser notes, refreshes, chooses Latest restoration. Review Freeway
   v2 cap digits r-147f669c58b940a3 at Front/Face and Elephant v2 figurine
   r-c3a6e6f47f6c4cf8 at Chest. Both unapproved. Exact final files/prompts/pins/
   reference photos/checks: private fighter-feedback-20261029/review-index.md.
3. At NEXT HD Fighters test-pack preparation, remind Vlad to playtest Bonecrusher
   r-ea740e0041cb4e30. Read private next-test-pack-checklist.json and review tags.
   It is visually acceptable tentatively; do not mark native verified until tested.
4. Mack 10 and Scarface lettering needs references or explicit interpretation choice.
   Preserve source paths; no guessed words. No tattoo art changed in this pass.
   Review other pending second-ten models and Warren latest complete-back-P child;
   no approval of unseen revisions inferred. Keep nine approved first-batch peers.
5. Keep approved five/public0.2 bytes immutable. No new publication/install requested.
   A future release needs exact new-child approval and NEW immutable version.
   Source-only continuation commit local until push requested; original menu/tools
   checkout source unchanged; private handoffs point to this isolated checkout.
