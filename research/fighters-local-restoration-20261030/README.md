# Local fighter comparison pass — 2026-10-30/31

Vlad explicitly accepted conventional local upscaling/cleanup after discussion
of the10 ImageGen refusals and4 incomplete studies. This pass makes14 new local
comparison candidates:3 main atlases and11 supplemental injury maps. It makes
zero new ImageGen requests. Original refusals/partial studies remain historical
records, not successful retries. New children require final owner review; no
packaging/publication/install/selection/native approval/push is inferred.

## Method and source boundaries

Official [RealESRNet checkpoint](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth),
67,040,989 bytes, SHA256
`a820b9bde89a874d7599d545567308ce6c128fc8754a53208eda016d40aa81df`.
The [official model project](https://github.com/xinntao/Real-ESRGAN) and
[RRDB architecture reference](https://github.com/XPixelGroup/BasicSR/blob/master/basicsr/archs/rrdbnet_arch.py)
describe the model family. Our small Torch inference graph loads all702 tensors
strictly with weights_only; no BasicSR/torchvision/CUDA dependency. Inference is
FP32 on the Mac MPS GPU,128native tiles with32context, x4 RGB only. Tile padding
is not a proof of full-image numerical equivalence; raw/final comparisons were
inspected for visible grid boundaries. No source model/UV/normal data changes.

Use a separate inference venv (actual run:Python3.13,Torch2.15.0,NumPy2.5.4,
Pillow13.0). The gallery/assembly main environment remains unchanged. Model
weights/venvs/art remain PRIVATE and outside Git. `infer.py` pins the checkpoint,
validates source/cache hashes and rejects output within the source tree. The
private actual-run frozen processor/hash receipts are the authority for delivery;
the reusable inference script also adds source/cache/output hygiene checks.

Main2048RGBA drafts use the own Faithful source chroma and painted shading.
Only bounded fine luminance differences from the local model transfer (±6LabL,
strength0.85). Edge-padded low-pass avoids artificial canvas border brightening.
Actual paired source skin seam cores remain exact (0.75native core/3native taper).
Each own full alpha and inspected auxiliary/uncertain hold rectangle remains
byte-identical. Source chroma is the assembly target, with RGB/gamut conversion
differences: median Lab chroma drift0, p95<0.395, isolated maximum6.771. Banner's flag rectangle[0,255,139,359] stays exact Faithful RGBA,
including original contours; no locally inferred detail applied inside it.

Eleven1024RGBA injury maps use the pinned clean reference plus original own state
RGB delta, then bounded local-model fineL±3*.8 only inside exact source-change
support. Seven references are existing restored main candidates; four Xzibit/
Banner references are these new own-source local mains. No incomplete old study
is silently promoted. Own alpha/holds, clean exterior and outside-active baseline
remain exact. Runtime state switching/materialalpha/UV/mips remain unverified.

Local inference is smoother and less detailed than ImageGen peers, especially
Xzibit/Banner skin/hair. Unknown lettering remains uncertain; no recovered text,
new pores or authenticated injury-geometry claim. Original coarse mark edges and
source chroma flecks remain. Injury baseline clipping7,985 events and reported
local gamut clipping12,766 events may overlap. These are review drafts.

## Validation and review

PYTHONPATH=src with the shared tools venv:124tests+23subtests pass, including3 new synthetic local assembly checks for own
alpha/holds/seams, rejection of a flat model color shift, and shape/hold bounds.
The first private diagnostic V1 exposed a border-filter issue in the synthetic
flat-color check. V2 fixes it; V1 retained unimported and V2 only adopted.
Independent source/raw/reference/final pins and pixel checks pass for14 outputs.
All prior1131 candidate files/metadata/reviews/session/requests/view choices were
preserved through import.14 live PNGs and3 model embedded RGBA textures verified.
One recovery restart kept the same origin, profile, workspace and saved reviews;
no schema migration. Source art/weights/reviews are not tracked.

Private `experiments/fighters-local-restoration-20261030/` has plan.json,
ready-for-import.json, results.json, imports.json, technical-audit.json,
live-verification.json, review-index.md, frozen processors, source/model/alpha/
hold pins, raw-local outputs and independent QA. New IDs/hashes/method:
[selection.json](selection.json). Source algorithms: `local_restoration.assemble`;
batch recipes `infer.py`, `assemble.py`, `audit.py` here (private paths configured
in the immutable local batch plan; use a fresh output stage).

Gallery Full texture library → clear other filters → search
`fighters-local-restoration-20261030` (14results). Combined old completion tag now
has108results:94prior+14local. All213 fixed-core IDs now have comparison children;
this is candidate availability, not approval or full recovery of missing details.
Shared effects and separate created-player work stay outside this213 count.
Model viewer76options:choose Xzibit,DavidBanner,CarmenB and Latest restoration.
Injury maps remain2D source-bound comparisons. Finalreview precedes1.0 approval;
Bonecrusher reminder stays NEXT test-pack preparation. Published0.2 unchanged.

## Persistent checkout recovery

At midnight, temporary-directory cleanup removed457 older tracked source files
and the worktree link. Surviving edits were backed up privately; the existing
shared Git history was intact. Moved the checkout to the persistent local tools
worktree and restored only missing tracked files from HEAD. All124 tests passed
again. One live writer restarted with the same origin/profile/workspace after
review backup and unsaved-note inspection. Reviews/session/requests remained
exact through restart; browser smoke then intentionally saved Xzibit's local/Face
view and the gallery local filter/Banner/RGB/50% choices. No art was regenerated.
Machine paths/process details remain in ignored .local-handoff.md and private
source-recovery.json / persistent-environment.json. Inference env/checkpoint are
also installed durably outside temporary directories.
