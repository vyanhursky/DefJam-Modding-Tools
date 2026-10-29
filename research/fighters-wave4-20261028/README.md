# Headwear gap recovery and review reconciliation —2026-10-28

Vlad accepts Nyne/Trejo, identifies old headwear on Redman, missing body
restoration on Rollins, and an untouched head/vivid palette on Blaze. Keep bulk
calibration provisional until the remaining three are accepted.

The saved Blaze right comparison was published v1 `r-af704d282bab415a`, not the
already available v3 `r-c82bf031a7cb4726`. The v3 bytes do contain head/face/hair
restoration and skin/cloth palette correction. The viewer now shows revision IDs,
review status and a warning when a newer active restoration exists; saved manual
comparisons remain supported.

A read-only geometry audit found broad eye/mouth/nipple rectangle holds clipping
actual headwear. Redman had two entirely original strips and part of a white
panel; Blaze had a small cap corner. `clothing_detail.repair` recovers saved raw
v3 detail only under safe cloth triangles intersecting the omitted holds,
subtracting other material coverage plus1sourcepx guard. It applies source-guided
detail and cloth palette assembly, then copies only those mask pixels to v3.
Redman39,119changed/39,200safe px; Blaze4,707/4,720. Full alpha and all nonmask
pixels remain exact v3. No new generation was needed for these two.

| Fighter | Current right revision | Review state |
|---|---|---|
| Nyne |r-c781fcc1ff7e43e9|Owner visually accepted; art unchanged|
| Trejo |r-a41e97bb2dc3445f|Owner visually accepted; art unchanged|
| Redman |r-615ab80f98c34738|v4 recovered headwear; needs owner check|
| Blaze |r-75cda6b939fc4c88|v4 cap repair over restored/palette-matched v3; needs owner check|
| Henry Rollins |r-0ca085cea9db4beb|v4 restored head + trousers/boots; body skin/tattoos incomplete|

One new built-in Rollins body generation failed with output moderation category
sexual; no image was returned/imported. The exact prompt/error/request ID is
private. This is a service blocker for completing that skin/tattoo pass.
A separate, narrower clothing-only request succeeded: its input and edit scope
contain only trousers/boots with all skin, tattoos, hair and head omitted.
`prepare_rollins_clothing.py` assembles source-palette detail through verified
cloth coverage;943,831changed/951,008safe pixels. All noncloth pixels and alpha
remain exact v3. `import_rollins_clothing.py` imports that partial v4 via the
live writer and retains the incomplete skin status. No blocked body output or
alternate generation service was used.

`prepare.py` performs private immutable assembly; `import_review.py` uses only
the live API, backs up notes and checks review versions. Twelve current/shared
reviews were reconciled to the owner's feedback before the separate Rollins
clothing addition; no face/channel/game/selection
booleans inferred. Nyne/Trejo exact v3 review status is approved from explicit
owner feedback. New children remain unapproved. Obsolete face-protection guidance
on Blaze's shared review becomes a likeness reference under the newer head
authorization. Five more older revisions receive the reversible archived tag;
all artwork/history and published0.1 remain. Saved camera, left choice, lighting,
groups and active fighter are preserved; only Redman/Blaze/Rollins saved right IDs change.

Private experiment `experiments/fighters-wave4-20261028/` contains before-workshop
and before-models backups, headwear audit, prompts/error/raw output, assembly receipts/masks,
head comparisons, import/review receipt with exact prior notes, processor copies
and live verification. No direct live JSON edits, server restart, forced browser
reload, game install or publication. Save browser drafts before refreshing;
concurrent review conflicts retain the browser draft for merging.

Draft future method: `docs/fighter-restoration.md` and prompt/reference template.
It distinguishes restored detail from a high-resolution original, verifies small
UV components, and records actual displayed revision IDs. It cannot be frozen as
a five-fighter bulk recipe until Rollins is complete and the remaining owner
review gates close.

Validation:83tests+15subtests,8Node tests, JS syntax and source hygiene pass.
Live verification covers all five PNG hashes/material alpha, GLB decoded RGBA,
old candidate metadata/files/requests and preserved camera preferences. Final
workspace31candidates/27live requests/17archived revisions. Browser visual check
is still blocked by URL policy; owner visual review is pending.
