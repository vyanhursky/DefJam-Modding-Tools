# Twenty restorations after the first 45 previews —2026-10-29

Owner approved19 exact previous drafts, requesting only Starks badge CITY POLICE,
and requested another 20. Three agents assisted bounded roster/decoder investigation,
disjoint built-in generation and independent final visual QA. Root owned source,
assembly, tests, authenticated imports and single-writer cutover. As remaining
unique fighters encountered generation rejections, owner explicitly authorized
alternate costumes. This batch contains16new unique fighters plus4costumes:
D-Mob B/C, Blaze B, Sticky Fingaz B. Supported total65outfits covering61fighters.
New art remains unapproved/unselected/not native verified/outside public 0.2.

| Outfit | Resource | New revision |
|---|---|---|
| Cruz | V2IP_007A | r-238aa783251f423d |
| Meca | V2IP_201A | r-3e423ed54f3b4d8f |
| Kimora | V2IP_407A | r-ebeb95655dbf4497 |
| Shawnna | V2IP_406A | r-7cde240229f84bfe |
| Cindy J | V2IP_403A | r-24f3dfe403664cac |
| Carmen Electra | V2IP_401A | r-4db931d3cd6646b3 |
| Lauren | V2IP_405A | r-36ccdaf73e564749 |
| Teck | V2IP_305A | r-53b22996a45d49f6 |
| Dan-G | V2IP_004A | r-d9fdae63bbea4d38 |
| Baby Chris | V2IP_122A | r-633c50f546934ad9 |
| Ghostface Killah | V2IP_108A | r-43eb5b1b77704af6 |
| Joe Budden | V2IP_302A | r-53a8ff0354654ef4 |
| Jervis | V2IP_202A | r-514bac26d4854e0d |
| Lil Kim | V2IP_404A | r-6e8a5dfbcae84c8b |
| Manny | V2IP_008A | r-78182410fd904a83 |
| Prodigy | V2IP_119A | r-259a96c52b75405e |
| D-Mob — Costume B | V2IP_014B | r-469c54ada4974a5b |
| D-Mob — Costume C | V2IP_014C | r-d72b4f50a3a3416f |
| Blaze — Costume B | V2IP_113B | r-29da836a7fd04eeb |
| Sticky Fingaz — Costume B | V2IP_114B | r-8d42bdc3652b4a88 |

## Decoder and material evidence

Decoder 2 supports the audited direct-index header as well as the existing long
single-draw header. Direct indices are followed immediately by vertex count and
the first vertex-array pointer; verify both against actual streams. Bounds,
strip parity/winding, all valid source normals, positions and UVs remain checked.
Do not misread the direct header as multiple draw packets. Existing decoder 1
caches remain accepted without rewriting them. All 45 adopted caches retained;
source vertex/UV/normal/color/index arrays compare exact under the new decoder.
Shaniqua is not adopted: two referenced zero source normals remain unsupported,
no synthetic normal repair was introduced. Suspect is a playable source candidate,
previously excluded too broadly, but not generated/adopted in this batch.

Verified external tape meshes use SHAPENAME=tape,1 and are explicitly omitted
from the primary-atlas preview (Kimora, Cindy, Carmen, LilKim). They are not proven
disposable or unused in game. Shawnna's21vertex/24triangle mouth auxiliary uses
primary A406 but has unresolved mouth UV/shader semantics; its exact group/TAR is
separately omitted and labeled. No blanket group-name skip. All 1000 retained parts
bind their own main/costume atlas, including B014/C014/B113/B114. Shared tape art
is untouched; preview omissions require native assessment, not a restoration claim.
Supplemental injury/damage atlases remain original. Runtime transitions unverified.

RGB restoration permits explicit audited hair groups (including ASym/L_Hair
spelling), Cruz alpha-skin hair and narrow mixed-alpha regions: Cindy rear hair
without eyelashes, Kimora lower fringe. Other mapped alpha/unknown/eye holds win;
all output alpha stays exact. Small <=2 native-texel UV overshoots rasterize by
canvas clipping only, without changing source UVs or clamping triangle vertices.
Selected overshoot TARs explicitly clamp; current preview is CLAMP_TO_EDGE.
Explicit local ABM_BLEND enables preview blending even without_ALPHA in the label.
Hair inherited rendering and studio lighting remain approximations; source alpha
range alone does not establish full source shader behavior.

## Restoration and final checks

All 20 body/outfit raw outputs are1254 square built-in edits of matching512original
atlases. Final technical assembly is2048RGBA. Rich Original Detail only; slightly
more realistic skin/hair, original likeness/sculpt/UV/layout/baked shading and
source palette for BOTH skin and garments/shoes/headwear. Exact prompts/raw origins
saved before import. Santos, Xzibit and Banner failed output moderation; exact
requests/errors retained privately, no retry/workaround/provider switch. Earlier
House/Bo/LilFlip refusals also remain held. No failed input counted as restored.
Blaze C was excluded as an injury copy; Crow B fails strict normals. Alternate
costumes are explicitly labeled, never counted as new distinct characters.

215final named feature crops inspected, with status counts
{'detail-present-needs-review': 211, 'pending-held': 4}. Inventory checks include every BLAZE/31 fragment, headwear,
rotated jewelry, actual four Cindy buttons and three Teck bandages. Some original
inventory wording/coordinates were corrected without rewriting submitted prompts:
Joe boot wordmark is a lace strip; Sticky small metal/pocket boxes include palm
skin. Final source/raw/model interpretation controls conclusions, not a label.
Prodigy uncertain tattoo areas retain original contours and word paths, adding
generated luminance detail only inside source ink. No guessed transcription is
authenticated. Four low-change components are exact flat black source material
(Meca/Cindy/Carmen/LilKim), not missing detail; guards were not weakened.

Strict zero-static-UV padding finishes named Cruz cross/chain, Meca chain, Kimora
cross, Joe crest and Jervis button tiles. All mapped holds remain exact; static
absence does not prove runtime non-use. Neighboring already-editable feather
edges may differ by <= 1 RGB level between stages; do not claim every mapped old
stage pixel byte-identical. Full original alpha, declared holds and seam cores
are exact in every final output. Final-stage map/plan/hash receipts retained.

Starks focused child r-aeba1996ca364784 (see sibling source report) restores exact
CITY/POLICE on existing plates, only 5016 pixels changed vs accepted-component
parent, full alpha/outside-lettering pixels exact. Jervis initial mirrored last E
was fixed with the same already-generated correct POLICE lower-band detail:
2255 pixels changed vs its draft, all outside lower mask exact, own palette/ornament
retained. Jervis v3 equals visually checkedv2 bytes; extra processing provenance
completed. Both final words checked after correction, not merely in raw output.

## Review preservation and limits

Full 113 pytest tests + 21 subtests pass. Synthetic additions cover direct index bounds,
exact tape skips, explicit blending, decoder 1/2 compatibility, bounded overscan,
named hair/skin-alpha permissions and mixed-alpha overlap guards. Private final
technical audit verifies every PNG/geometry/processor hash and exact alpha/holds/
seam cores. Current source catalogue validates65 caches read-only without starting
a second writer. Backend image/model checks are recorded privately; browser visual
testing remains unavailable under the prior URL policy, no bypass attempted.

Twenty final drafts imported through the existing token-authenticated writer.
All 282 pre-import candidate metadata/files retained,
302 total at verification, including unrelated customization work.
All pre-import reviews, session, requests, cameras and choices exact.19approvals
saved with optimistic versions and exact prior backups. Starks remains pending.
No pack/manifest/runtime/install/save/settings/frozen snapshot changes. Public0.2
approved five immutable. Bonecrusher NEXT test-pack playtest reminder retained.
Source commits local until owner requests push. No private artwork/models in Git.

On 2026-10-30 the owner confirmed browser notes saved and authorized restart.
The same-origin viewer now exposes 65 outfits across 61 fighters. Pre-stop and
final-stopped JSON backups retained; workshop bytes and saved model-view state
match the stopped snapshot. All 20 new live PNG hashes and GLB embedded RGBA and
revision identities pass; all 331 current candidates retained. This verifies
backend delivery and persistence, not browser/native visual parity.
