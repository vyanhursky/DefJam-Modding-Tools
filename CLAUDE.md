# Agent instructions for Def Jam Modding Tools

Read this file then PROGRESS.md at the start of a session. AGENTS.md and CLAUDE.md
must remain byte-identical. This repository owns authoring tools, not the game
runtime. The owner is Vlad. Implement authorized work fully; ask only for real
missing decisions and preserve an active review session during changes.

## State and data

- Update PROGRESS.md in the same turn: current status, decisions, tests, remaining
  work and exact next steps. Keep it concise. Archive long history under ignored
  docs/worklog/. local.json and .local-handoff.md carry machine-specific paths.
- Game dumps, textures, generated artwork, references, models, Blender files,
  review JSON and exports remain in the configured PRIVATE workspace outside Git.
  Never commit them, captures, checkpoints, API keys or built game code. Use only
  synthetic test fixtures. Run the source checker and git add -A --dry-run before
  a source-only commit; push only when the owner requests it.
- Preserve corpus/source/revision IDs, hashes, schemas, review versions, relative
  image paths, parent provenance and the resolved workspace path. Schema changes
  require explicit versioned migration and backup/rollback. Never reset an old
  workspace, silently re-approve art or regenerate its accepted corpus.
- There is one writer lock per workspace. The live review uses exactly
  http://127.0.0.1:8768; changing host/port changes browser draft storage. Check
  for unsaved browser notes before reload/restart. Never run two writers on the
  same workspace. Preserve data, snapshot review JSON and verify compatibility
  before a server cutover; leave the working server available afterward.

## Art direction

- New generations are Rich Original Detail only. Keep earlier stylized drafts
  as history. Preserve likeness/proportions/expression. On 2026-10-28 Vlad
  explicitly included face, hair, head and headwear restoration for all five
  fighters, aiming for slightly more realistic skin/hair. Keep child drafts
  unapproved until reviewed. Match clothing, footwear and headwear color to the
  original after generation, preserving restored fine detail and matched skin.
- Original atlases and faithful enlargements control composition, UVs, animal
  silhouettes, tree positions and handwriting paths. Semantic descriptions do
  not authorize redesign. Use references; have Vlad approve uncertain detail.
- Owner-authorized cleanup uses the existing archived review tag and Show
  archived revisions controls. Keep all PNGs, notes, prompts, parent links and
  hashes. Published0.1, approved/selected and saved comparison choices stay
  visible; never silently delete art or change approval flags.
  Current/shared stale notes may be reconciled to explicit owner feedback only
  with an exact private prior-notes backup and optimistic review-version checks.
- On2026-10-29 owner approved all five complete models, including Rollins v6,
  and authorized HD Fighters0.2(beta) publication plus ten new fighters using
  the calibrated method. Preserve exact approved bytes: Blaze/Redman v4,
  Nyne/Trejo v3, Rollins v6. New ten stay outside0.2. On the next feedback the
  owner approved seven complete new models and all other components of Ludacris,
  Flava Flav and Warren G, requesting only their shirt logo/clock/jacket script
  repairs. The three new feature children require review; keep accepted pixels
  outside their masks exact. Name and check focal chest details individually.
  Broad source holds leave a logo/prop pending, not restored; tiny uncertain
  marks alone may stay held. See the focused prompt and source-specific recipe.
  The owner subsequently approved the repaired Ludacris and Flava Flav children;
  Warren's new both-fragment back-P child still requires review. A feature can
  span distant UV islands: check every copy/fragment and assembled Front/Back,
  not just one crop or global change counts. Ten additional drafts bring the
  static model total to25. They remain unapproved and outside public 0.2.
  The owner then approved Freeway's repaired1972 child and Elephant Man's figurine
  child, and requested twenty MORE, explicitly authorizing parallel subagents.
  The first twenty remain outside0.2. On subsequent feedback the owner approved
  nineteen; Starks badge needs CITY POLICE. Child r-aeba1996ca364784 fixes only
  lettering and remains unapproved. Owner requests 20 more and explicitly permits
  alternate costumes to fill shortfalls. Source supports 65 outfit previews over
  61 fighters:16 new identities plus D-Mob B/C, Blaze B, Sticky Fingaz B. All new
  twenty stay unapproved/outside0.2. Do not count costumes as new characters.
  Keep one live writer; delegate disjoint private art/QA tasks only. Record every
  result independently. Keep rejected requests honest and choose other compatible
  fighters when selection was delegated. Alpha jewelry RGB and an opaque others
  group require exact audited opt-ins; keep full source alpha and other holds.
  Decoder 2 direct headers validate actual vertex count/pointer; old decoder 1
  caches remain readable without rewriting. Retained source arrays/UVs/normals
  stay exact. Explicit audited external tape and Shawnna mouth-tape omissions
  must remain visible limitations, never non-use/restoration claims. Source alpha
  and all other mapped holds remain exact; use narrow audited mixed-alpha hair
  regions and bounded canvas clipping only. No synthetic normal repair adopted.
  On2026-10-30 owner chose supplemental damage/injury restoration after roster
  exhaustion. Private40texture/20fighter drafts use own256head sources,1024finals
  and measured registration to each512main head quarter. Reuse exact clean HD
  detail plus original state RGB difference; generated bounded luminance only in
  source change support. Preserve own per-slot Faithful alpha and actual auxiliary
  holds, never borrow sibling alpha. No guessed new injury marks or severity;
  reject raw drift through technical masks. Record clipping and original mark
  boundary limits. Exact clean RGB outside declared transition/holds. Do not hold
  an entire previously restored garment/logo as an auxiliary tile. Runtime br01/02
  switching, UV transforms and shader/alpha meaning remain unverified; separate
  2D source-bound review first. Do not count injury maps as new fighters or replace
  a whole512main atlas with a256head. Five output-rejected pairs remain held;
  five distinct restored fighters fill the adopted twenty without retries.
  Owner approved19batch60 outfits; Prodigy other components accepted, MOBBDEEP
  back-neck header repaired in a new unapproved child. Preserve original care
  marks, hem label, accepted parent elsewhere and fullalpha exactly. Do not infer
  approval of this child. On2026-10-30 owner visually approves all40 injury maps;
  native/selection remain unchanged. Scope now every fighter-used texture: main/
  outfit/Story states, injury maps, shared materials and created-player dependencies.
  Count source IDs, not aliases; core213 is not an all-material grandtotal. Read
  research/fighter-coverage-20261030/README.md before choosing more work.
  Owner then requests finishing all108 remaining fixed-core texture IDs before
  final review and separate1.0 HD Fighters packaging approval. New108 outputs
  stay unapproved/unselected/not native verified; no pack/push authorization yet.
  Parallel disjoint private art workers are allowed; root is sole live importer.
  Preserve failed requests honestly; technical continuity studies are distinct
  from new generated injury detail and never a false completed-restoration claim.
  Completion pass staged94unreviewed drafts,4privatepartial studies,10refusals;
  14sources remain incomplete. Preserve failures; no silent retries/providerchange.
  Live viewer76models;4additionalatlases2Donly,blockedmainsoriginalpreviewonly.
  Seven immutable main receipts have a malformed editable_hair_groups metadata
  field; actual pinned masks/plans/geometry/override define scope. Keep errata.
  On2026-10-30/31 owner accepts conventional LOCAL upscaling/cleanup comparison
  for14 remaining IDs. This authorizes own-source local model processing of the
  3blocked mains and11injury maps; zero newImageGenrequests, no bypass/fragment
  generation.14local drafts pending, original errors/studies retained. Keep model
  weights/Torch env separate/private; own alpha/holds/skinseams exact, source
  chroma/shading retained. Banner flag exactFaithful. All213fixedIDs have comparison
  candidates, not automatic full-restoration/approval/native/pack completeness.
  Combinedcompletiontag108; localtag14. Preserve prior1131 candidates/notes/views.
  Bonecrusher reminder remains NEXT pack.
  On2026-10-31 owner rejects local-neural detail loss: CarmenB original native,
  seven named injury maps Lanczos4x. Xzibit whole-original ImageGen retry succeeds
  r-5714f48923784e36 and is explicitly approved. Banner permanent plain-flag edit
  refused outputsexual; owner FINAL choice existingLanczos4xunchanged, no further
  changes/generation, superseding flag removal. Prior errors/trials retained.
  Owner now approves HD Fighters1.0 and explicitly Cloudflare/catalogue publication.
  Release selection218IDs:200RichOriginalDetail,12Lanczos4x,6native originals;
  excludes ALL local-neural trials, including four remaining Xzibit/Banner injury
  maps conservatively replaced by Lanczos. Five shared shader/tape inputs native.
  No CAP/customization/portrait/menu/video completeness claim. Keep runtime/native
  flags honest and remind Bonecrusher at this pack. Exact218recipe hashes authority;
  bulk packageapproval receipt separate from historical per-candidate review flags.
  Published1.0.0 stable via cataloguePR10/mergeab9dc9e, protectedrun41223718965,
  signedrevision10. ZIP669255742B/221files/SHA1bea1239abb8e6b86fff85ecb9fbd0d805df2b1567183e6e8a16b6f131725e0f.
  Released-key stable managedinstall verified; real game install untouched. Native
  injury/Story/alpha/mips and Bonecrusher playtest still pending. Prior versions retained.
  The earlier Rollins whole-atlas moderation failures and v5A/v5B studies are
  retained as history; final v6 used successful regional art/material inputs.
  Never infer new-child approval from a parent's acceptance. Check displayed
  revision IDs; use actual material UV masks and inspected narrow tile holds,
  not copied pilot head quadrants/eye/mouth rectangles or Rollins seam counts.
  Source-palette matching must include clothing/headwear/footwear as well as skin.
  See docs/fighter-restoration.md and its calibrated prompt template.
- Exact prompts/reference notes/raw outputs belong to immutable candidate
  history. Every import is a new revision. Keep alpha separate and technically
  restore protected pixels; a prompt alone is not a pixel lock.
- Trejo caption: owner says "Debbie Danielle". Buckle: bear left, deer right,
  smaller deer middle. Current v3 child retains the earlier tattoo work and is
  visually accepted. Do not infer new-child approval, pack selection, game
  verification or installation from that acceptance.

## Engineering

- Package code in src/defjam_tools; ship UI, aliases and pinned licensed browser
  dependencies as resources. No CDN is needed at runtime. Keep optional Torch,
  CUDA and neural-upscaler environments separate from the main app.
- Use rg first. Make focused tests for logic and persistence changes. Existing
  synthetic tests cover decoder bounds, source identity, protected assembly,
  revisions, stale-review conflicts, hashes, HTTP auth and view persistence.
  Use the browser to verify visible behavior after UI changes. Do not write
  tests merely mirroring a trivial reversible edit.
- Keep runtime loader/mod-manager/installer changes in DefJamFFNY-recomp.
  Its HD setup modules are frozen at the hashes in provenance.json. This repo
  owns future tool development. Synchronize a pinned compatibility snapshot
  deliberately with setup tests; do not maintain independent evolving copies.
- New corpus builds fingerprint code and may produce a new recipe identity.
  Reading an existing corpus/workspace must not change it.
- Model viewer supports76static outfit/state previews (65prior+11new): the accepted
  five plus D-Mob, Sticky Fingaz, Ludacris, Ice-T, Crow, Sean Paul, Crack,
  Flava Flav, WC, Warren G, Freeway, Magic, Bonecrusher, Bubba Sparxxx, Capone,
  N.O.R.E., Mack 10, Scarface, Elephant Man, Bless, Havoc, Fam-Lay, Slick Rick,
  Memphis Bleek, Comp, O.E., Jacob, Crazy Legs, Erick Sermon, Pockets, Starks,
  Trick, Skull, Solo, Chiang, Masa, Baxter, Rome, Snowman and Stingray; plus Cruz,
  Meca, Kimora, Shawnna, Cindy J, Carmen Electra, Lauren, Teck, Dan-G, Baby Chris,
  Ghostface Killah, Joe Budden, Jervis, Lil Kim, Manny, Prodigy and the four costumes.
  Completion108 adds House, Bo, Lil Flip, David Banner, Xzibit, Santos, Suspect,
  Blaze C, Carmen B, D-Mob D and Magic B. Blocked mains have original previews
  only; Shaniqua/Cindy B/Crow B/D remain2D due strict source normal validation.
  Preserve source geometry/UVs/normals/material partitions; label lighting
  approximations and omitted effects. No rig, venue or game reimport claim.
- Read-only independent investigations can be delegated while the main agent
  owns edit/test/cutover operations. Report evidence and validate claims that
  would change outputs. Do not delegate the serial migration or live writer.
