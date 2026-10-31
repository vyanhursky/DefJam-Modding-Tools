# Fighter texture coverage — 2026-10-30

**2026-10-31 follow-up:** [local comparison pass](../fighters-local-restoration-20261030/README.md)
adds14 unreviewed local candidates, with zero new ImageGen calls. All213 fixed-core
IDs now have comparison candidates and the completion tag finds108 results.
Earlier refusal/partial counts below are historical; they remain preserved.
Candidate availability does not establish approval or full detail recovery.

Owner scope: every texture used by all game fighters, including main outfits,
Story variants, supplemental injury states, shared materials and the created
Story player. This is a deduplicated source inventory and work checklist;
resource presence is not proof every resource is used by a reached runtime draw.
All corpus images already have a Faithful HD enlargement. Remaining below means
no adopted richer restoration candidate, not a missing file or absent upscale.

Follow-up: the [completion108 pass](../fighters-completion108-20261030/README.md)
adds94 review drafts. Current fixed-core coverage is199/213;10 rejected sources
and4 partial studies remain incomplete. The tables below preserve the original
pre-generation audit snapshot and source-sharing evidence.

## Fixed-fighter core (pre-generation snapshot)

| Source images | Unique total | Restoration drafts | Without restoration |
|---|---:|---:|---:|
| Main/outfit/state atlases, gameplay plus cinematics |80|65|15|
| Supplemental injury/secondary maps, fixed fighters |133|40|93|
| Core union |213|105|108|

The65 main maps cover61 identities; four are additional costumes. Latest main
metadata:62 approved and3 corrected children pending (Warren back P, Starks
CITY POLICE, Prodigy MOBBDEEP). Current owner feedback approves the40 injury
maps only. Eight older batch20 approvals were reconciled to earlier explicit
owner acceptance, retaining private prior reviews and all native/selection flags.
The40 injury IDs/RIDs/hashes are in the separate approval record; import-time
pending receipts remain historical. No image bytes, saved choices or requests
changed. Visual approval is separate from release and native draw verification.

### Fifteen main atlases remaining

| Identity / source resource | Outstanding work |
|---|---|
| House003A | Prior generation hold |
| Bo012A | Prior generation hold |
| Lil Flip307A | Prior generation hold |
| David Banner124A | Prior generation hold |
| Xzibit115A | Prior generation hold |
| Santos204A | Prior generation hold |
| Shaniqua402A | Strict source-normal decoding unsupported |
| Suspect / Shadowy Figure501A | Intentional shadow appearance; treatment held |
| Blaze113C | Separate bloody Story state, based on outfitB |
| Crow126B / cinematic126E | One source ID; alternate outfit, unsupported normals |
| Carmen401B | Separate source/state, same wardrobe; runtime role unresolved |
| Cindy403B | Separate source/state, same wardrobe; unsupported normals |
| D-Mob014D | Cinematic-exclusive bloody suit/state |
| Crow126D | Cinematic-exclusive separate image; outfit/state role unresolved |
| Magic128B | Cinematic-exclusive injury state |

Checho017 is named in fighter data but no corresponding observed model/atlas was
found in these gameplay/cinematic archives. Keep an unresolved resource/use audit
item; do not invent another used image count. Generation holds are historical
failures, not a claim that restoration is impossible. No retries were made here.

### Injury counts and aliases

The complete br01/br02 corpus has137 unique IDs:133 fixed-fighter IDs,2 created
player999 maps and2 shared created-body customization maps. Thus93 remain for
fixed fighters,97 if all four created-player maps are included. Carmen401B also
has a br03 alias, but br01/br02/br03 all share one exact source ID; it adds no new
image. Shop/gym copies share gameplay IDs. Each remaining source requires role,
channel and registration inspection before using the existing injury recipe.

## Additional work for every fighter-used texture

These are outside the213 core count; do not present213 as a complete grand total.

- Five concrete external images: four64-square jewelry sparkle inputs (blg1..4)
  and one shared32x64 tape image. All have Faithful baselines, no saved restoration
  child at audit. Inspect channel/blend use before deciding technical restoration
  or an intentional original hold; ImageGen is not required for synthetic masks.
- Four spectexture symbolic inputs remain unmapped to runtime image identities.
  Shadow resource names likewise are not proven extra image IDs. Resolve actual
  bindings and deduplicate before counting or generating anything.
- Eye/dental/auxiliary blocks and tiny reference-limited lettering remain held
  inside some existing atlases. See shared-material findings for named exceptions,
  including Mack10/Scarface tattoo wording. These are not extra texture IDs.
  Previously repaired chest logos, clock, Warren P, Freeway1972, Elephant figurine,
  Starks badge and Prodigy header must not be re-counted as missing restoration.
- Created-fighter customization has4988 unique category IDs/5526 aliases. A dated
  concurrent-work snapshot has462 IDs with candidates (247 latest approved,
  215 pending),4526 without candidates. This stream is active; preserve its latest
  state. Candidate presence is not whole-item/native verification. The two shared
  created-body injury IDs above overlap this set: do not double-count them.
- Created-player template999, item/variant routes and all runtime shared materials
  still need a joined dependency audit. Portraits/menu art are a separate existing
  HD-Menu/non-model workstream; this report does not claim they are exhaustive.

## Story cutscenes

Most in-engine Story fighter textures share exact gameplay source IDs. Fresh
archive hashing checked271 XSH records with no identity mismatch. Cinematics have
53 unique fixed main images:50 also occur in gameplay,3 are cinematic-exclusive.
Current65 main restorations cover40 of those53;13 remain (including the3 unique
D-Mob014D, Crow126D and Magic128B states). Generate once per source ID, not once
per archive alias. Separate Story actors often reuse roster models (Trejo as a
bouncer, Nyne as a suitor, Redman as Doc, for example).

For all40 supported counterparts, retained source mesh arrays, normals and UVs
match exactly; complete ELF files differ, omitted effects/rigs were not compared.
The texture loader hashes source descriptors/bytes, not scene/archive names, so
identical runtime content should use the same pack entry. This is source evidence,
not native Story acceptance. Verify representative scenes, changed states and
shared tape/alpha behavior in the game before claiming complete Story coverage.
No separate higher-resolution cinematic head source was found in these resources.

Prerecorded MAD movies contain baked video frames. Fighter texture replacements
do not upgrade them; that would require a separate video restoration workflow.

## Next practical sequence

1. Small native test of injury draw/source identity, both state transitions,
   alpha/mips and a representative Story scene before generating remaining93.
2. Restore remaining supported fixed main/state and supplemental IDs, keeping
   held/unsupported sources explicit rather than filling counts with duplicates.
3. Resolve shared shader/tape/auxiliary dependencies and finish the parallel
   created-player item/variant inventory; record intentional source holds.
4. Review the three corrected main children and make an explicit pack selection.
   Remind owner to playtest Bonecrusher when preparing the next HD Fighters pack.

Public HD Fighters0.2.0-beta.1 still contains only the original approved five.
No new pack, manifest, install, generation, runtime change, push or server restart
was performed for this audit. Detailed archive/source evidence is in
[cutscene-sharing.md](cutscene-sharing.md) and
[shared-materials.md](shared-materials.md); full per-ID metadata stays private.
