# Def Jam Modding Tools — progress and handoff

## Current status

**2026-10-29: Warren complete back crest repaired; second ten-fighter batch live.**
Owner reported half the back P remained low-resolution, approved Ludacris/Flava
latest children and requested ten more. Both separate Warren back-cloth UV
fragments now restored with one focused built-in edit and scoped source-palette
assembly. New Warren v3 r-a2b301c58a8c4680 remains UNAPPROVED/unselected; accepted
script/head/skin/clothing elsewhere and alpha exact.89,078 changed pixels out of
91,008 safe, per-fragment 98.04%/97.67%. PNG/GLB pixels verified. See source recipe
research/warren-back-logo-20261029/ and private same-named experiment/review-index.md.
Final rebuilt v2 assembly equals already imported v1 bytes; no duplicate import.

Ludacris r-9b80bbe05e6a4b59 and Flava r-9d997f2360fe4bd5 now approved complete
through optimistic API review updates with exact prior-notes backups. Their seven
first-batch peers were already approved. No new pack selection/game verification.
Old notes/history retained; Warren's latest child still needs owner review.

**Second ten:** Freeway, Magic, Bonecrusher, Bubba Sparxxx, Capone, N.O.R.E.,
Mack 10, Scarface, Elephant Man, Bless. Exact identities, source/baseline and
geometry hashes measured; unchanged static decoder. Ten built-in whole-atlas
Rich Original Detail edits successful. Actual raw 1254 square, assembled 2048 RGBA;
head/face/hair/headwear, skin, clothing/shoes and safe opaque jewelry included.
Source palette matches both skin AND clothes. Source alpha, declared tiny-word/
mouth/eye/unknown holds and measured paired skin seam cores retained exactly.

New fighter_scopes module adds final named-feature omission checks, explicit
alpha-cloth RGB opt-in and zero-UV-coverage source tile handling. Bonecrusher
cloth RGB restored despite alpha material; alpha exact. N.O.R.E. flag tile has
zero static UV coverage and is restored in2D, with game usage unproven. Elephant
jewelry shorthand corrected after source rotation; original prompt stays immutable.
Final named feature crops and CPU front/back RGB UV diagnostics inspected;
projection ignores alpha/game lighting.26 features change 47.4–99.9%; every editable
component 16+native pixels changes≥25%, global 2.85–3.23M. Counts flag omissions,
not authenticity. Narrow uncertain source text stays held, not reconstructed.

All ten final assembled/SLUG-v2 PNGs match inspected v1 bytes, imported once,
unapproved/unselected/not game verified with exact prompts/source-specific notes.
Private frozen processor/plan hashes and review index retained. Same8768 single
writer backed-up cutover authorized by owner: all notes saved; restart when ready.
No schema/corpus migration. Current PID42722/exec17349;25models,79candidates,
30requests. Every 69 prior candidate metadata/file hash and all prior reviews,
requests/session/views/cameras retained. Disk JSON byte-exact through restart.
Ten new PNG and model GLB revisions/RGBA plus Warren verified. Prior browser URL
policy remains; no fresh browser visual QA/bypass. Owner visual review pending.

104pytest tests+15subtests pass, including six synthetic scope/UV tests. Public
HD Fighters0.2, active game installation/settings/saves and frozen runtime HD
snapshot unchanged. Source work stays in isolated tools branch, local until push
requested. Exact older PROGRESS archived unchanged under ignored docs/worklog/.

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
  research/warren-back-logo-20261029/, research/fighters-batch20-20261029/.
- Calibration: docs/fighter-restoration.md + fighter-restoration-prompts.txt;
  source-specific coordinates are examples only. Private same-named experiments
  contain exact prompts, inputs/raw/art, masks/receipts/frozen processors, import
  IDs and API/disk backups. review-index.md links final images/prompts/checks.
- 104 pytest tests+15subtests pass. Six new meaningful synthetic tests cover split
  feature omission, alpha cloth opt-in, mapped hold override refusal, UV top-left/
  back orientation, nearest depth/RGB ignoring alpha, and aspect-preserving framing.
- Source hygiene:529 tracked text files,0 policy failures; staged diff check and
  AGENTS/CLAUDE byte identity pass. No private art or models staged.
- Existing gallery persistence/auth/conflict/model export checks retained. Final
  HTTP/GLB revisions/pixels and every 69 prior candidate retained;25models/79candidates.
  Browser URL policy prevented fresh browser visual tests; no bypass. Atlas,
  feature crops and offline RGB UV projections inspected. Native playtest pending.
- Prior release catalogue14tests, metadata/signature/remote content and install
  checks pass; no catalogue/pack changes this turn. No JS/UI logic changes.

## Handoff

1. Leave the single writer live at8768/model-viewer. Source checkout branch
   codex/hd-fighters-beta, exact machine paths/restart command in ignored
   .local-handoff.md. Current writer PID42722/exec17349. Do not use a second writer.
2. Owner refreshes after saving notes; choose Latest restoration to avoid saved
   older choices. Review Warren Back plus both crest halves at2D100/200%. New
   r-a2b301c58a8c4680 stays pending. Luda/Flava latest children are approved.
3. Review new ten, all unapproved. Use Original versus latest, unlit Front/Back/
   Face/Chest/Pants/Shoes and both head/neck sides, clothes and focal features.
   Preserve flagged notes/review versions. Exact IDs/paths/prompts: private
   fighters-batch20-20261029/review-index.md and imports.json. Some undecipherable
   tiny source script remains intentionally held; no authenticity claim.
4. Keep original approved five and all older art/history exact. No further pack
   publication/install requested. Next release needs exact new-child approval
   and a NEW immutable version; never replace public0.2 bytes/manifests.
5. Source-only continuation commit local until push requested. Runtime/menu
   checkout source untouched; original tools ignored handoff points here.
