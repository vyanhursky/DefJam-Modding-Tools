> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Imagegen texture restoration: proposed authoring workflow

2026-10-15. Owner-requested design review. No new artwork, installed pack,
runtime change, public upload or mod-manager implementation in this review.
The owner selected fighters for the pilot, references with approval of uncertain
detail, and a side-by-side audition of both proposed looks. Follow-up D117 picks
Blaze/Nyne/Trejo and preserves faces except reviewed low-resolution damage.

**Implementation follow-up:** the persistent local authoring gallery is built.
Use [the workshop guide](../texture-workshop.md) for current commands and behavior.
It is a separate server over the read-only corpus (D118); the design below records
the original proposal. No imagegen candidates or game-tested restoration yet.

## Recommendation

Reuse the existing static corpus, local review server and source-ID texture
replacement loader. Add an authoring layer for semantic tags, immutable imagegen
candidates, regional revision requests and explicit approved selections. Export
small external override packs above faithful HD. Begin with three primary fighter
atlases and two styles each (six candidates), then expand to roughly 8–12 source
textures only after the first comparison and companion-map identification.

The earlier Lanczos acceptance remains the baseline. The owner now wants a more
imaginative, stylized restoration experiment, so the earlier rejection of neural
redraw is not a blanket prohibition on this separate pass.

## What was actually inspected

- Current source at `282ef7c`; existing HD tools, gallery, settings and Setup.
- PR17's complete design at
  [8e3d2dbe](https://github.com/vyanhursky/DefJamFFNY-recomp/blob/8e3d2dbe8f8debbc76d1e317307e3c23f77ba2e3/docs/research/mod-system-design.md),
  still an open, documentation-only proposal when fetched.
- The populated sibling toolkit, after confirming its HEAD equals the current
  gitlink `837e2c7ea65a3e8e9149978c7cc125810d2c4e35`; no submodule changes.
- The existing Mac Setup corpus metadata: 18,971 unique supported textures,
  24,266 aliases, one unresolved texture, 24 font and 94 movie entries. This was
  a fresh metadata read, not a fresh full-image hash or visual certification.
- Original decoded samples from Blaze `V2IP_113A.xsh`, customization
  `V2CP_A_A.xsh`, Foundation `V2BG_02A.xsh`, portrait `1_2p.xsh` and the
  `buyrewards.xsh` UI. Scratch PNGs stayed outside source control.

The Mac corpus exists under the PR19/20 installation's data root, so it need
not be rebuilt to begin reviewing. Its recipe differs from the historical
Windows corpus; preserve both identities and validate inputs before importing
old review decisions. Source evidence is detailed in
[pipeline review](imagegen-existing-pipeline-review.md) and
[packaging review](imagegen-modpack-review.md).

## Catalog all supported assets, then review useful groups

Use categories for browsing and independent tags for treatment. Classify aliases
and regions without changing the original texture identity. Keep an explicit
unknown queue and evidence/confidence for inferred labels.

| Browse group | Subgroups and treatment tags |
|---|---|
| Menus and UI | Backgrounds, panels, buttons, icons, loading screens, static lettering |
| HUD and tutorials | Health bars, markers, control legends, tutorial illustrations |
| Portraits and selection art | Fighter portraits, alternate poses, versus art, venue previews |
| Named fighters | Face/hair, skin/tattoos, clothes, shoes, jewelry; linked outfits/variants |
| Character customization | Body bases, tattoos, hair, garments, footwear, accessories; separate shop thumbnails |
| Venues | Floors/walls, signage/graffiti, scenery, vehicles, lighting-baked surfaces |
| Props and crowds | Weapons, breakables, spectator atlases |
| Special resources | Effects/masks, animation sequences, environment maps; explicit technical review |
| Separate workflows | Fonts/vector APT primitives and prerecorded movies |

Current gallery filters already contain 11,261 UI/menu, 4,988 customization,
1,585 venue and 213 fighter source IDs. These filters overlap through aliases.
Fresh Mac metadata finds 4,620 unique IDs with a `screens/shopthumbs/` alias,
2,132 with a `screens/portrait/` alias and 76 with a `screens/venuethumbs/`
alias. These are provenance groups, **not counts of complete portraits or
independent garments**: atlases, fragments and shared UI resources are included.
They demonstrate why subdividing UI matters more than running another upscale.

Record material separately: skin, cloth, leather, metal, brick, text/logo,
tattoo, opacity alpha, material/data alpha, tiling axes, UV regions and animation
family. A source ID can have several uses; its replacement affects all matching
uses. Conflicting selections across categories must be resolved before export.
The bounded static census is not every visual resource on disc.

## Author texture detail without damaging the asset

For each asset, provide the original atlas, a faithful HD comparison, relevant
in-game context and any verified design reference. Establish a small style sheet
from approved samples: stylized anatomy and faces, the existing palette,
painted/baked shading, strong shapes and original grime/wear. Richer detail must
remain readable at gameplay distance. Do not automatically introduce modern
photographic pores, specular highlights or physically based material channels.

The inspected Blaze atlas mixes face, jersey, denim, jewelry and tattoos in one
512-square image. Some lettering is split or mirrored for its UV mapping.
Treating it as a normal flat illustration, correcting mirrored letters, moving
features or changing perspective can break the model. Inspect full-atlas
registration even when editing one small tattoo or garment region.

The owner chose to audition both looks. Candidate A should add richer detail
while preserving the source's shapes, palette and grit. Candidate B may interpret
materials more strongly as a modern stylized remaster. Preserve character
identity, original costume designs and atlas registration in both. Uncertain
tattoo/logo/lettering interpretations require the owner's approval, using
references where possible. The owner chose Blaze, Nyne and Trejo (D117).
Start with each primary colour atlas, not unverified companion/material maps.

Use three levels of intervention:

1. Restore known design information from clear references, with exact text.
2. Add plausible fabric, stitching, wear and tattoo line detail within approved
   artistic bounds; label inferred detail explicitly.
3. Hold or request a reference for ambiguous identity-critical lettering,
   logos, tattoos or face changes until the owner chooses the policy.

Imagegen is suitable for proposing the authored detail; exact placement and
preservation need validation. OpenAI documents remaining limitations in text,
brand/character consistency and structured composition, and states that a mask
guides an edit without guaranteeing its exact shape.
See the [image guide](https://developers.openai.com/api/docs/guides/image-generation?api=responses)
and [prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide).

Proposed import/assembly tooling should retain original/approved alpha and data
channels, restore unedited regions explicitly and enforce full-atlas geometry.
Do not ask imagegen to infer whether alpha is transparency or material data.
Keep tiling boundaries/gutters fixed and inspect repeated tiles; review animated
frames and linked outfits together. Cropped generation is only an intermediate:
the installed result must preserve the original atlas and uniform integer scale.
Resizing alone cannot repair moved UV islands or invented garment spelling.

## Compare, revise and select

Extend `hd_corpus.py` / `hd_corpus.html`, reusing the multi-model audition ideas
from `hd_review.py`. The minimum useful comparison has original, faithful HD and
selected imagegen candidate at a common display scale, with synchronized pan/zoom,
RGB/alpha views and backgrounds. Add revision switching, blink/wipe comparison,
region bookmarks and notes. Keep a clean full-resolution image separate from
annotation overlays. Include an in-game reference pane when available.

Preserve every candidate under a stable source ID and unique revision. Store
parent revision, exact prompt and references, available tool/model metadata,
output hashes, region/edit scope, alpha source, assembly steps and review notes.
Do not invent an exposed seed or promise identical generative regeneration.
Retaining exact approved pixels makes an accepted release reproducible.

Suggested states are queued, generated, needs revision, atlas approved,
game verified and selected for export. Approval names the candidate revision
and output hash. Any changed pixels require renewed review. Rejection keeps
the baseline; it does not destroy history. Existing good/concern notes stay
intact and must not become approval of a different output automatically.

Use Codex's built-in imagegen for the first small, conversational pilot. The
local reviewer should queue an asset and a precise revision request for Codex;
a browser button cannot directly invoke this conversation's imagegen tool.
An unattended API-backed queue would be a separate, explicitly chosen mode with
credentials and spending limits, not a prerequisite for the pilot. Available
built-in arguments do not expose a pixel mask, so do not promise a mask API in
that mode. Repeat the original invariants on each regional edit.

## Test locally, then package for PR17

Export selected candidates to ordinary schema1 PNG packs now. Keep a few short
component names; split opacity and independent-channel mip policies because
the current loader applies that choice per pack. Keep optional category choices
in authoring metadata and assemble chosen components rather than enabling one
pack per texture. Preserve original runtime keys and verified aliases, never
use generated output hashes as the replacement lookup key.

Load faithful components first and restoration components last, or test
restoration alone over console originals. No new replacement hook is needed
for this supported static-texture pilot. Validate each chosen image's dimensions,
straight alpha, scale, channels, output hash and aliases before export.

Check local appearance at gameplay distance and close range, across model seams,
face/skin tone, exact words/logos, alpha edges, animation and mips. Use matched
route/settings/seed where possible; existing fight captures are not guaranteed
pixel-aligned. Confirm actual replacement loads, keep capture off for performance
measurements, and use the harness's complete-save-root guard. Begin at 4x for
comparison with faithful HD; compare 2x where detail survives and measure memory
and first-show behavior on target platforms. No new performance claim is made.

Two existing behaviors need explicit handling:

- Setup can append regenerated faithful packs after custom packs, reversing
  intended priority. The pilot must check order; PR17 should own/reconcile it.
- A missing creative key can inherit faithful HD; a malformed winning image
  falls to the console original, without retrying the earlier faithful entry.
  Do not describe those as the same fallback.

PR17 is not a prerequisite for authoring. Its future helper/index can wrap the
same approved files as versioned, hash-pinned downloads. Derived imagegen art
belongs to the proposal's third-party `linked` class. Keep the main repository
source-only and all generated artwork/review captures local until an external
release is separately requested. Players install curated output; they do not
need to regenerate it through imagegen. Human-guided cloud edits are not the
proposal's existing allow-listed local recipe model.

Before schema2 integration, the design needs to preserve opacity/channel mip
policies, group physical components into logical mods and preserve override
priority across Setup updates. Keep these integration choices separate from
the art pilot rather than expanding this review into the full manager.

## Owner answers and remaining questions

Answered in this review: use references where possible and seek approval for
uncertain details; use fighters for the pilot; compare both proposed looks
before choosing (D116). This is an art-direction audition, not bulk generation
or publication approval.

Follow-up answers (D117): Blaze/Nyne/Trejo; everything except faces unless a
specific small-texture defect warrants review; functional local browser gallery
with persistent flags, notes and sessions. The gallery is implemented (D118),
with six briefs queued and real candidate lanes still empty. Mac is the current
authoring host. Optional category packaging and wider platform acceptance can
be decided once a candidate pack exists.

Next artwork step: use the saved briefs to audition three primary fighter atlases
in two styles before expanding the set. Verify all face-protection instructions,
source registration and uncertain referenced details before approving a candidate.
Hosting/signing/index administration can wait
until an approved external pack exists.
