> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Texture workshop persistence review

Read-only implementation review, 2026-10-15. Inspected only `scripts/texture_workshop.py`, `.js` and `.html`. No server, browser, build or game was run, and no implementation file was changed. The failures below are established from control flow; the main agent should reproduce them with delayed promises/requests before fixing. Line references describe the source inspected for this report.

## Follow-up status — all six findings addressed

Re-read only the current `.js` and `.py` after the main agent's fixes. **No remaining P1 data-loss path was identified in this bounded follow-up.** The original findings below are retained as historical explanations, not current open defects. No implementation was executed during this follow-up.

| Original finding | Current status and source evidence |
|---|---|
| P1 navigation replaces pending edits / stale save callback contaminates another asset | **Resolved in the reviewed UI flow.** `exclusive()` sets all editor/navigation surfaces inert before awaiting and rejects overlapping operations (`texture_workshop.js:16-22`); `openAsset` holds it through flush, fetch and image loading (`:112-131`). Review-save cache mutations now check the asset ID (`:45-53`). |
| P1 restore-draft / flag response applies to another asset | **Resolved in the reviewed UI flow.** Both actions hold the same exclusive operation lock, keeping the active asset/target stable until completion (`texture_workshop.js:195-204`). |
| P1 cancelled import attaches PNG to another asset | **Resolved.** Import captures asset/label/style/parent/prompt in an immutable job before FileReader awaits, sends that job and reloads its original asset; exclusive navigation blocking remains active until completion (`texture_workshop.js:228-234`). Cancelling the dialog may dismiss it, but it cannot redirect the import to another asset. |
| P2 selected revision leaves another revision's version stale | **Resolved for the same-tab case reported.** Successful selection updates other locally selected reviews to `selected=false` and increments their versions, matching the backend transaction (`texture_workshop.js:51-52`; `texture_workshop.py:269-280`). Concurrent edits in another tab still correctly produce an optimistic-version conflict. |
| P2 browser drafts collide across workspaces | **Resolved for separate workspace paths.** Draft keys now include the resolved workspace string (`texture_workshop.js:15`; config exposes it at `texture_workshop.py:415-417`). Moving a workspace changes the browser draft namespace; saved disk reviews move with its files, while unsaved browser drafts remain under the former path. This is a portability limitation, not the reported cross-workspace overwrite. |
| P2 candidate revision brief instructs editing original | **Resolved.** Copied briefs identify the selected parent and its SHA (`texture_workshop.js:213-216`); queued briefs use the parent-aware generator, validate original/baseline/parent hashes and carry the exact parent PNG path/hash (`texture_workshop.py:78-91`, `:314-335`). |

The main agent separately reported browser verification of notes across navigation/reload/server restart, regional annotations, synthetic file selection/import/approval/export/reload, fourteen passing synthetic backend tests and zero UI errors. That execution evidence is attributed to the main agent; this follow-up independently checks source resolution only.

## Original findings — historical, resolved above

## P1 — Navigation can replace edits made while the next asset is loading

Evidence: `texture_workshop.js:101-118`, `:25-48`.

Reproduction sequence:

1. Open texture A with no outstanding changes.
2. Click texture B. `openAsset(B)` flushes A and starts the asset GET at102, leaving A's notes editable.
3. While that GET is pending, type a note on A. `changed()` updates A's `state.review`, writes A's browser draft, sets `dirty=true` and schedules an autosave at30-31.
4. Resolve B's GET before450ms. It replaces `state.asset` at102 and `setReview` replaces `state.review` and the visible notes at118/53-57, without saving that newer A edit or resetting/binding `dirty` to A.
5. The existing timer calls `flush()`, which reads B's identity and B's review at36, saves B and clears its draft. A's edit never reaches disk; only the browser draft under A's key survives.

This breaks the durable autosave promise even though a browser-local recovery may remain. If A's save has already started when B resolves, its completion writes the returned A review into the current B object's review at42-43, outside the identity guard at39. Subsequent B review operations can display and submit A's notes. Multiple `openAsset` calls also have no request token, so an older GET can overwrite the more recently chosen asset.

Bind dirty review state and save callbacks to immutable asset/target contexts; serialize or cancel navigation, flush edits made during pending navigation, and prevent stale asset responses from committing. Avoid mutating current-asset caches outside the same context check.

## P1 — Restore-draft and flag callbacks can write one asset's review into another

Evidence: `texture_workshop.js:181-189`.

`restore-draft` reads A's draft before awaiting GET A at184-185, but reads `state.target` after the await and then assigns into whichever `state.asset` is current at188. Start restoring A's draft, navigate to B while the GET is delayed, then resolve it. With both targets=`asset` and both disk versions equal, the code sets B's review to A's draft, `setReview` displays it under B, and `flush()` saves it as B. The equal-version case succeeds silently; an unequal version merely turns it into a conflict.

The flag handler has the same callback ownership issue. It submits A's flag review at182, then assigns the returned A review to `state.asset.review` after the await. If navigation to B completes in between, B's cached notes/version/flags become A's and `setReview('asset')` installs them in B's editor. The request correctly flagged A on disk; the local corruption can then be persisted to B by the next edit.

Capture asset ID, target, draft key and relevant object before awaiting. Reconcile a result only with the matching context, or discard the stale UI update; do not make the current asset a substitute for the operation's original asset.

## P1 — Cancelling an in-progress import can attach its PNG to a newly opened asset

Evidence: `texture_workshop.js:208-216`; `texture_workshop.html:41`; server `texture_workshop.py:285-309`.

Submit a candidate for A, then Cancel/Escape while FileReader is pending and open B. Only the submit button is disabled; the cancel button and dialog Escape remain available. After FileReader resolves at213, the code reads `state.asset.id` at214 and the current import controls rather than the original import context. Same-sized pilot atlases all pass the backend dimension check, so A's candidate can be imported into B without an error. Even when the POST already targeted A, its completion uses the then-current asset ID at215 to reopen another texture and may announce success in the wrong context.

Capture asset/style/parent/label/prompt and import context before the first await. If cancellation is intended to dismiss only, keep the operation attached to A and report completion there; otherwise cancel the request. Ignore stale UI completions after navigation.

## P2 — Selecting a new revision leaves other cached review versions stale

Evidence: server `texture_workshop.py:266-278`; browser `texture_workshop.js:38-43`, `:51-64`, `:177-179`.

Approve/select revision R1, then approve/select R2 for the same texture. The backend unselects R1 and increments R1's review version at269-274, but returns only R2. The browser updates only R2 at43. Switching review back to R1 loads its cached `selected=true` and old version at53. Any note change submits that stale version, and the server deterministically rejects it at241-242, demanding a reload for a conflict caused by the same tab. The UI also falsely shows R1 selected until refreshed.

Return all affected review states or refetch asset detail after selection; update every deselected revision's local version and selected state. Approval and export should continue using the backend's exact output hash checks.

## P2 — Browser draft keys do not identify the workspace

Evidence: `texture_workshop.js:15-17`, `:184-189`; `texture_workshop.py:402-406`.

Draft keys include corpus ID, asset ID and review target, but omit workspace identity. Stop a server with an unsaved A draft in workspace1, then run the same corpus with workspace2 on the same host/port. Browser localStorage shares the origin and the draft key is identical, so workspace2 offers workspace1's draft. Restore replaces its version with workspace2's current version and can overwrite workspace2's independently saved notes/selection. The config already exposes a workspace string, although a stable workspace ID would survive moves better.

Namespace recovery drafts by stable workspace identity as well as corpus/asset/target. Preserve old draft keys through an explicit migration rather than interpreting every same-corpus draft as belonging to any new workspace.

## P2 — Candidate revision briefs identify a parent but instruct editing the original

Evidence: browser `texture_workshop.js:199-207`; server `texture_workshop.py:78-90`, `:311-323`.

Review a candidate R1 and prepare a regional revision. Queue metadata records `parent=R1`, but both the copied brief and queued prompt say “original texture atlas as edit target; faithful HD as comparison.” Queue paths contain only original and faithful, with no path/hash for R1. A consumer following the actual brief edits the original instead of the selected candidate and can discard all accepted R1 detail. The parent can be resolved separately through candidate metadata, but that conflicts with the explicit prompt and missing target-image path.

For a candidate revision, provide the immutable parent image/path/hash as edit target, retain the original/baseline as references, and make copied and queued briefs agree. New first candidates should continue to target original/baseline explicitly.

## Positive checks relevant to these findings

Candidate PNG imports create unique revision paths and do not mutate older candidate entries (`texture_workshop.py:298-309`). Review saves use optimistic version checks and atomic JSON transactions (`:224-242`). Export checks selected approval flags, the stored approved output hash and the actual PNG bytes before copying (`:334-345`). These protections are useful; the reported failures arise mainly from UI context changes and stale local state rather than a missing backend approval gate.
