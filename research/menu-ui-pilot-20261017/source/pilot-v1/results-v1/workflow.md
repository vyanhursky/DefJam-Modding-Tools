
## High Scores approval / result-paper batch — 2026-10-19 D154-D155

High Scores v1 APPROVED by owner: "High Scores is approved lets move on".
`hiscores-approval-20261019.json` freezes13current artwork files; earlier raws,
rejected proposals and native game acceptance excluded. Battle/Rewards/HighScores
approval manifests total92pins,all exact. Other earlier approvals remain in their
own manifests. No approved PNG changed.

Next batch `pilot-v1/results-v1/`: six source-shaped paper panels,18source tiles:
rematch1;matchSm1 11/10/9/8;matchSm2 18/17/16/19;matchSm3 21/19/18/20;
matchSm4 15/14/13/16;rewardun1. All6 drafts unapproved. Source UVs/material/root
matrices/ancestors/frames audited in `next-scope/result-panels-metadata.json`.
`references.json` preserves source IDs/full hashes and stage placements.

Six built-in image_gen edit calls,101pilot total; no CLI. `jobs.json` is the exact
request set. `generations.json` adds input/raw hashes and adoption decisions.
All inputs were viewed before generation. All raws requested true transparency
and remain unmodified, along with normalized proposals. Generated silhouettes,
alpha, printed ink, crease placement and broad lighting are excluded from
assembly: source alignment/alpha stay authoritative after prior black-fill
feedback. No newly invented text, scores, stars, boxes or rows are adopted.

`prepare.py`: immutable source copies, native APT mosaic and4x reference.
`assemble.py`: tile-aware4xLanczos faithful RGBA basis (same resampling as individual
tile exports). Active mosaic is assembled from those exact tile candidates.
Use only fine RGB luminance residual from Gaussian4 raw at*.14 capped±1.25L,
remove mask-weighted mean, retain source Lab a/b before8bit rounding. Safe paper
must be fully opaque after25pxMinFilter, L>61,RGB spread<85; source gradients
>20 across8px are expanded25px and protected. Paper-detail masks feather4px
inside safe area. Entire printed bands/header/score cells are excluded; rematch
safe y64..143,results safe y112..232 or337..355. Reward card protects full
native[12,15,443,312],including every red/star/black graphic. Source tile/UV edges
have4nativepx guards; all tile outer16output pixels and unusedUV are exact.
Max actual RGB delta4/255 (reward3),adopted changes only0.22%reward and6.06..9.47%
other active pixels; hue means limited by8bit roundoff (abs mean a/b<.0021).
Full masks/statistics/checksums are in `assembly-receipt.json`.

Special geometry: matchSm4 bottom-right starts y255,not256; source1row overlap
and mapping preserved. Narrow edge tiles/padding retained,not stretched.
Stage placements at640×480:rematch184,233;Sm1 194,66;Sm2 50,60;Sm3 43,65;
Sm4 44,66;reward110.5,68. Exact APT matrices retained in audit. Preview rounds
Sm2 .05native materialshift and reward110.5×3 to332 (-1/6nativepx); these are
review studies,not runtime geometry changes. Five1440-high stage sizes1920,
2304,2560,3360,5120:transparent larger margins,original scale/placement and4:3
viewport centered. No panel outpaint or widescreen stretching; backdrop/live
text/lighting/animation remain separate.30original/draft pairs have exactcenters.

Verification:1161priorPNGs unchanged,92Battle/Rewards/HighScorespins exact,
18tile alphas/unusedUV/edgeguards and6mosaic alpha/protected pixels exact.
Browser6panels×5ratios×2stage images +6×2refs×2channels×5texture/raw images load;
checker/dark/light backgrounds expose true transparency,img CSS transparent;
wipe50%,draft-only/side,bounds75%/12.5%at16:9,HighScoresapprovedstatus pass,
no horizontaloverflow/consoleerrors. `browser-verification.json`,`review-proof.png`.
Review defaults4player/original/RGBA/checker/side;stage16:9collapsed.

Source report `docs/research/menu-result-rematch-panels-2026-10-19.md` and both
projects' handoffs updated. Private immutable archive
`<data>/scratch/menu-ui-results-v1-hiscores-approved-20261019`;apply overlay to
COPY of earlier pilot;do not overwrite earlier archives. Authoring writer8768,
17workshop candidates andTrejo untouched. No import/install/game/build/runtime/
core edits/commit/push. Nextownerpaperreview;then Extrasnotes,Storyphone and
remaining frames after mapping. Nativegame acceptance stillpending.
