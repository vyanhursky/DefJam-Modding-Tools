# Focused fighter feedback —2026-10-29

Owner feedback: Freeway lacks 1972 cap lettering; Bonecrusher seems visually OK,
with a playtest reminder requested when preparing the next HD Fighters test pack;
Mack 10/Scarface arm tattoo wording remains unreadable without usable references;
Elephant Man's figurine needs improvement using two owner-supplied photos.

## New children

- Freeway r-147f669c58b940a3, parent r-2436393d909b4317. Original has 19 left/72 right
  of the middle cap seam. Focused built-in edit reconstructs those four small
  digits at original positions/scale; 5,085 changed pixels. Two native masks
  [138,269,149,283] and [152,269,164,283]; center seam stays byte-exact.
  SHA256 ee4caf285052abf161f783eda07522765b959396526c3632e7cb1ae22aa428bf.
- Elephant Man r-c3a6e6f47f6c4cf8, parent r-83ef708e60d1426b. Prior figurine tile
  was interpreted as jeweled letters. Original matching crop is the edit target
  and layout authority; two supplied photographs guide figurine/metal detail.
  New figurative pendant keeps original atlas orientation/placement. 96,400 changed
  pixels inside [0,194,100,256]. Source tile includes 3,064 unmapped native padding
  pixels, cleared of prior erroneous lettering; no mapped non-jewelry material
  is touched. Source alpha and all other parent pixels remain byte-exact.
  SHA256 02b35d36bbb6c2ee7e5b5420ccaae125576973ad0bd349648cd7b291e1ee8808.

Both use built-in imagegen, raw 1254 square normalized to their original square crop
for technical 2048 RGBA atlas assembly. `feature_detail.restore` matches original
coarse palette only within scoped feature masks. Input/source/parent/geometry/raw/
processor hashes pinned. Final private assembled-v2 reproduces inspected v1 PNGs
exactly; only v2 imported. Exact prompts, photos/raw PNGs and decoded models remain
private. New children are unapproved/unselected/not game verified. Their likeness
and figurine authenticity require owner review; small references do not establish
perfect sculptural reconstruction. No artwork or model data is tracked here.

## Tattoo recommendation and reminder

Source crops are ambiguous at letter level. Recommend retaining exact source
letter paths/spacing rather than inventing legible words. A contour-preserving
cleanup can refine existing ink edges, but cannot verify intended wording. Seek a
matching period photograph/video frame or higher-resolution version of the same
art. Generated/OCR transcriptions are not evidence. No Mack 10/Scarface tattoo
pixels or revisions were changed in this pass. Reference-needed review tags and
notes preserve the unresolved question; no inferred tattoo text is adopted.
A bounded online search did not establish a usable transcription source; none
of its results were used as texture or lettering authority.

Bonecrusher r-ea740e0041cb4e30 carries playtest-next-pack and owner-visually-ok
review tags. Tentative visual acceptance is recorded without formal approval or
native game verification. The reminder is an event checkpoint for next test-pack
preparation, as explicitly chosen by the owner; no timed notification is claimed.
Check shorts/shoes material behavior and skin/clothing appearance in-game.

## Verification and persistence

Two source/current/final crop sheets and front/back CPU RGB UV diagnostics were
inspected; Freeway's cap digits and Elephant Man's pendant visible on source
geometry. Diagnostic ignores alpha/game shaders; it is not browser/game QA.
Both live PNG hashes and model GLB embedded RGBA/revision IDs match. 6 existing
focused feature/scope tests pass; core/HTTP/UI logic unchanged. Prior full suite
baseline 104 tests+15 subtests remains recorded, not newly rerun for this art pass.

One existing writer retained on8768, no restart/reload. All 81 prior candidate
metadata/PNG hashes preserved, including unrelated customization drafts. 83 total
candidates/25models. Intentional feedback notes appended with current optimistic
versions and exact pre-feedback backups; other reviews, requests/session/cameras/
comparison choices exact. Current right choices retained; save browser notes,
refresh and choose Latest restoration. Prior browser URL policy remains; no bypass.
No pack/upload/manifest/install/game/runtime/save changes. Public0.2 remains exact.
