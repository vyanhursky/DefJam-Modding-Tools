# Making a fighter modpack

Draft for **Fighter Mod Support**, targeting recomp v0.15.0. Start with a copy
of an existing fighter, get it into a match, then change one component at a
time. You do not need to make a model, animations and a voice all at once.
A pack can contain one fighter or an entire roster.

This guide describes the local M5 development tools. Use a matching recomp
checkout containing `scripts/fighter-contract.py`; the published v0.13.0 game
does not include this workflow. A file that passes validation still needs a
playtest. Legacy `.mod` bundles are not automatically compatible.

## 1. What you are building

A fighter is a named character assembled from several pieces: its appearance,
how it moves, its sounds, menu pictures and a few rules. A modpack is a folder
that says which pieces belong to which fighters. The launcher installs a ZIP
of that folder and enables the entire pack together.

**Technical details.** `fighters.json` is the manifest: a UTF-8 JSON document
using `fighter-registry-draft-1`. Definitions refer to resources by stable keys
such as `my-roster/river-appearance`. They never choose memory addresses, native
core slots or executable hooks. The recomp assigns runtime bindings and builds
the native archives itself. The original extracted game stays unchanged.

| Piece | What a player notices | Manifest component | Input when authored |
|---|---|---|---|
| Appearance | Body, face, clothes, materials and skinning | `appearance` | Model `.o`, textures `.xsh`, facial palette `.o` |
| Moveset | Attacks, movement and their timing | `moveset` | Action selections and quaternion-track JSON |
| Voice | Reactions, taunts and spoken entry/exit sounds | `voice` | Mono PCM16 WAV, or supported compressed R2 streams, and category assignments |
| AI | How the CPU chooses actions | `ai` | Named tendencies in the manifest |
| Portrait | Pictures in selection and results | `portrait` | Six layout-specific SHPX `.xsh` files |
| Intro | The fighter's entrance | `intro` | Supported cinematic template plus track JSON |
| Victory | The winner's animation | `victory` | Supported cinematic template plus track JSON |
| Blazin | Activation shots and paired finishing moves | `blazin` | Four shot definitions, optional paired tracks |
| Stats | Health, speed, toughness and charisma | `stats` | Integer values in the manifest |

Skeletons, skin weights, materials and texture coordinates are parts of the
appearance resource, not independent top-level components. Motion events,
camera helpers, damage rules and native AI programs currently come from
verified templates; they are not arbitrary scripts supplied by a pack.

## 2. Set up your tools and folders

Keep your editable project separate from the folder you will zip. Your working
project may contain Blender files, layered artwork, recordings and notes. The
pack folder contains only the manifest and the final files it references.

**Technical details.** Install Modding Tools into a Python environment from its
checkout. A virtual environment keeps its dependencies separate from other
projects; see the [Python instructions](https://docs.python.org/3/library/venv.html).
The following commands are for PowerShell, run inside the Modding Tools checkout:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e .
$tools = '.venv/Scripts/defjam-tools.exe'
$recomp = 'C:/work/defjam-fighter-mods'
$game = 'C:/games/ffny/extracted'
& $tools fighter --help
```

`$game` must contain the supported original `assets/djv2.sod`, `assets/*.viv`,
`motion` and `screens/screens.viv`. Supply your own extracted game. On macOS
or Linux use `.venv/bin/defjam-tools` and your own paths. Native platform
acceptance is separate from running these offline commands.

| Tool | Use it for | What it does not provide |
|---|---|---|
| `defjam-tools fighter` | Starter manifests, catalog, full validation, ZIP packaging and exact member extraction | Installation, code injection or automatic legacy compatibility |
| Recomp `fighter-registry.py` | Inspect native models, skin, geometry, textures, motion and animation envelopes | A successful inspection alone does not certify a complete pack |
| Modding Tools model viewer / Blender | Examine static exported meshes and prepare source art | The current GLB export has no verified game mesh/rig reimport path |
| Image editor such as GIMP | Editable texture/portrait artwork with transparency | Saving PNG does not turn it into native SHPX |
| Audacity or another PCM audio editor | Record, trim and export voice clips | MP3, stereo or float WAV is not the accepted voice format |
| Text editor with JSON support | Edit the manifest and track data | Unknown fields are rejected rather than ignored |

Do not rename `.fbx`, `.glb`, `.png` or `.mp3` to a native extension. Conversion
must change and validate the underlying data. Generic Blender-to-EAGL export,
arbitrary new facial curves and arbitrary native moveset imports are not
provided by this draft. These are real tooling/adapter limits, not missing
checkboxes in the launcher.

## 3. Make your first valid pack

The quickest first success is a new roster entry that borrows an existing
fighter's assets. This is called a **donor**. Your new fighter gets its own
identity and name while using the donor's appearance and behavior. Once this
works, replace only the components you want to change.

**Technical details.** List verified donor definitions, then create a pack:

```powershell
& $tools fighter catalog --recomp $recomp --game $game
& $tools fighter new --recomp $recomp --game $game --out 'C:/mods/my-roster' --id my-roster --donor retail/ludacris --fighter 'river=River'
& $tools fighter validate 'C:/mods/my-roster' --recomp $recomp --game $game
& $tools fighter package 'C:/mods/my-roster' --recomp $recomp --game $game --out 'C:/mods/my-roster-1.0.0.zip'
```

For two fighters, repeat `--fighter`, for example `--fighter 'river=River'
--fighter 'stone=Stone'` in the same `new` command. The tool never overwrites
an existing starter folder or output ZIP. A donor-only starter needs just
`fighters.json`; game assets are read from each player's own dump.

Game-free [single-fighter](../examples/fighters/single-fighter/fighters.json) and
[two-fighter](../examples/fighters/two-fighters/fighters.json) examples are included.
Copy one to a new folder or use the command above. The generated shape is:

```json
{
  "schema": "fighter-registry-draft-1",
  "id": "my-roster",
  "version": "1.0.0",
  "requires": {},
  "resources": [],
  "fighters": [
    {"id": "river", "name": "River", "inherits": "retail/ludacris", "components": {}}
  ],
  "overrides": []
}
```

In the matching development launcher, open **Mods > Fighters**, enter the ZIP
path, install it, enable its checkbox and choose Play. Installation alone does
not enable it. Browse the native fighter menu to your added entry.

## 4. Understand names, IDs, versions and dependencies

The name is what players read. The ID is how the game remembers who the
fighter is. You can rename “River” to “River Stone” without making a different
fighter, but changing its ID creates a different identity. Pick IDs before
sharing a pack and keep them stable in updates.

**Technical details.** Use lowercase letters and digits separated by single
hyphens. Creator commands conservatively limit IDs to 63 characters for launcher
folder compatibility. `my-roster/river` joins pack ID and fighter ID. References
to another pack require an exact dependency, such as
`"requires": {"shared-rigs": "1.0.0"}`. Versions use three integers; ranges and
prerelease syntax are not accepted by this fighter schema.

`inherits` copies a fighter's authored components. A child `stats` object merges
individual stat values with its inherited stats. For example,
`"components": {"stats": {"health": 60, "speed": 70}}` keeps the donor's
toughness and charisma. All four are integers from 0 to 100. A fighter authored
without inheritance must supply the complete native-required bundle and stats.

Do not put selection indexes or core IDs in your permanent names. More than
255 logical entries are supported through a separate native participant window;
four simultaneously active participants are still four participants. The
16,384-definition processing budget and 16,380 window-file record bound are
not promises that a huge fully authored roster fits every platform's memory.

## 5. Organize files and keep their hashes correct

Think of a file hash as a fingerprint. It tells the validator that the file you
tested is the one in the pack. If you deliberately edit an asset, its old hash
must be updated before validation. A mismatch can also mean a damaged download.

**Technical details.** Authored file descriptors have `path` and `sha256`.
The `fighter-voice-2` and `fighter-voice-3` sources additionally require `format` on every audio
descriptor (`wav-pcm16` or `ea-adpcm-r2`); other descriptors retain their
two-field shape. Paths are relative to the manifest folder, use `/`, and cannot
escape it. Compute the digest after editing, for example:

```powershell
(Get-FileHash 'C:/mods/my-roster/assets/river.wav' -Algorithm SHA256).Hash.ToLower()
```

A resource can reference `{"path":"assets/river.wav","sha256":"<actual 64 lowercase hex characters>"}`.
The angle-bracket example is a placeholder, not a valid digest. Files may be
shared by several resources with the same digest. Package only the declared
assets, `fighters.json`, and optional root `README.md`, `README.txt`,
`LICENSE.md` or `LICENSE.txt`. Keep receipts, layered masters and source projects
outside. Unknown files, linked paths, traversal and case collisions are refused.

The current package budget is 512 MiB, 64 MiB per asset and 1 MiB per documentation
file. Manifest input is bounded separately at 8 MiB; combined manifest input is
32 MiB. Additional appearance/portrait/behavior composition budgets also apply.
The validator reports the limit actually hit; splitting a shared dependency does
not evade the combined active-roster budgets.

## 6. Build the appearance: model, rig, skin and textures

The model is the shape, the texture is its painted surface, and the skeleton is
what moves it. Skin weights connect parts of the surface to bones. These must
agree: a nice-looking static model can still deform incorrectly in combat.
Start with a compatible donor and preserve its bone meaning and material layout.

**Technical details.** An `appearance` resource uses `eagl-appearance-1`:

```json
{
  "id": "river-body", "kind": "appearance",
  "compatibility": {"skeleton": "retail/binding-ludacris"},
  "source": {
    "format": "eagl-appearance-1", "donor": "retail/ludacris",
    "model": {"path": "assets/body.o", "sha256": "<model digest>"},
    "textures": {"path": "assets/body.xsh", "sha256": "<texture digest>"},
    "face": {"path": "assets/face.o", "sha256": "<face digest>"}
  }
}
```

Put this in `resources`, and set the fighter's
`components.appearance` to `my-roster/river-body`. The three paths must be distinct.
Input may be raw or supported RefPack-compressed native data. `.o` here is a
data-only EAGL ELF resource, not code to execute. The validator checks its layout,
skin selectors/weights, finite geometry, texture references, render templates,
bone names/order/topology and permutation. It rebuilds accepted geometry using
trusted rendering structures; unsupported layouts are refused.

The `face` file tells the game how facial bones move. It is separate from the
painted face texture and the menu portrait. You can reuse a compatible donor
face or supply a supported custom facial palette; do not replace a legacy
mod's face merely to make validation pass.

Technically, the local adapter reads a data-only `PosePaletteBank`, validates
its active samples and destinations against the matched body rig, and rebuilds
it in a verified donor envelope. The supported two-palette context requires at
least 13 and 15 sample frames respectively. Quaternions must be finite and unit
length within the documented tolerance; vector values must be finite and
bounded. Pointers, array sizes, destinations and overlapping channels are
checked. The native game itself does not protect these accesses.

All 46 Vendetta faces now compile through this path. One isolated native
component probe has reached combat with the rebuilt face data. Full facial
expression/cinematic coverage and complete Vendetta conversion remain in
progress; a compilation receipt is not a promise that every context was tested.

Inspect components before composing the whole pack:

```powershell
python "$recomp/scripts/fighter-registry.py" inspect-model 'C:/mods/my-roster/assets/body.o'
python "$recomp/scripts/fighter-registry.py" inspect-skin 'C:/mods/my-roster/assets/body.o'
python "$recomp/scripts/fighter-registry.py" inspect-geometry 'C:/mods/my-roster/assets/body.o' --textures 'C:/mods/my-roster/assets/body.xsh'
python "$recomp/scripts/fighter-registry.py" inspect-textures 'C:/mods/my-roster/assets/body.xsh'
```

The geometry-only inspection may report a missing shared sparkle atlas that the
full compiler resolves from the verified game libraries. Whole-pack validation
remains authoritative. To extract a known native member without changing the dump:

```powershell
& $tools fighter extract --archive "$game/assets/v2ip.viv" --member '<exact member name from inspection>' --out 'C:/work-assets/donor.o'
```

The output path must be new. This extracts one exact member and decompresses
RefPack if present; it does not infer a rig or convert arbitrary mesh formats.

## 7. Make menu portraits and results pictures

Players see your fighter in several layouts, not just one square thumbnail.
Supply every supported selection and results variant so the character remains
recognizable in two-, three- and four-player menus. Preserve the required alpha
edges and layout rather than stretching one image everywhere.

**Technical details.** `kind: "portrait"` uses empty `compatibility` and source
format `eagl-portrait-1`, a retail layout `donor`, and six file descriptors:
`selector_2p`, `selector_3p`, `selector_4p`, `result_2p`, `result_3p`, `result_4p`.
Every descriptor points to a different validated SHPX file. Required dimensions,
shapes and layout structure are checked against the donor. Set
`components.portrait` to this resource's full key.

PNG is a useful artwork master but is not accepted directly for these native
portrait slots. Existing texture-pack PNG replacement tools are a separate
workflow. A general portrait-image-to-SHPX creator command is not supplied here;
use compatible native outputs and validate all six variants. Do not include
replacement `chooseF2/3/4` movies: the runtime owns roster expansion and UI binding.
The selector uses 2D portraits. Verify the actual 3D model in entrances/combat.

## 8. Author movement and attacks

An animation shows a pose changing. A move also needs rules about when it starts,
what it hits and how it links to another action. Changing a punch animation alone
does not create a new damage rule. Keep the donor's known behavior until the
specific change you need has a supported authoring path.

**Technical details.** `fighter-moveset-1` source has exactly `format`, `donor`,
`selections` and `tracks`. The resource kind is `moveset`; compatibility has both
`skeleton` and `events`. `selections` maps action ordinals (JSON string keys) to
chosen integer actions from the same verified donor. It currently permits only
compatible one-/two-motion ordinary action families with matching control flags;
special actions and ambiguous intervals fail composition. `tracks` maps native
animation tokens to hash-checked quaternion JSON files. At least one selection
or track must be authored. Do not guess action ordinals from menu positions.

Track files use `fighter-quaternions-1` and contain exactly `schema`,
`rig_sha256`, `bone_count`, `poses`. Each pose lists `[x,y,z,w]` for every bone
in verified ordinal order. Values must be finite unit quaternions; adjacent
rotations must stay in a consistent hemisphere. The rig digest is checked against
the runtime's verified template, not accepted as an author's assertion. Samples
follow the matched native child-time profile, not an arbitrary Blender FPS.
Root motion, event timing and unsupported channels remain template-owned.

Use `inspect-motion-index --check-links`, `inspect-motion-record`, and
`inspect-animation-envelope --check-links --check-curves` to investigate a
template. These are diagnostic commands, not a complete animation authoring UI.
There is no supported “drop in main_all.dat/wres_all.viv” shortcut.

## 9. Record and assign a voice

A fighter's voice is a collection of short reactions and spoken lines. Keep
clips at a consistent loudness, trim unintended silence, and listen for clipping
in combat. A correctly encoded file can still be assigned to the wrong event.

**Technical details.** Use `kind: "voice"`, an `events` compatibility label and
`fighter-voice-1`. Source fields are `format`, `template_voice`, `samples`,
`intro`, `extro`. `samples` groups indexed clips under the case-sensitive
categories `Character`, `Taunts`, `Enviro`. Indices are string ordinals 0–254;
the chosen template's bank determines which slots exist and what they mean.
Missing sample overrides retain template clips; intro and extro descriptors
are mandatory for an authored voice source.

Export mono, uncompressed signed 16-bit PCM WAV at 8,000–48,000 Hz. Audacity's
[WAV export options](https://manual.audacityteam.org/man/wav_export_options.html)
provide channel and PCM-format choices. The runtime encodes its owned native
stream; it does not accept arbitrary legacy speech banks. A single clip is also
bounded by the native encoder's 4,000,000-sample limit. Do not normalize silence
into noise or substitute another voice without stating it in your pack's notes.

### Bring recordings out of an older mod

An older mod may store dozens of lines together in a speech bank. The audio
exporter separates them into editable WAV files and keeps their original slot
numbers. This is useful for listening and editing; it does not decide which
reaction each line belongs to or install the audio into a fighter.

**Technical details.** Supply local FFmpeg and FFprobe executables explicitly.
Obtain them through the [official FFmpeg download page](https://ffmpeg.org/download.html).
The exporter supports bounded mono EA revision3/ADPCM R2 streams, at their
original sample rate. It never downloads tools, resamples, downmixes or changes
loudness. For a single `.asf` stream, omit `--header`. For an HDR/DAT bank:

```powershell
defjam-tools fighter audio --source .\legacy\600.dat --header .\legacy\600.hdr --ffmpeg C:\Tools\ffmpeg.exe --ffprobe C:\Tools\ffprobe.exe --out .\work\voice-600
```

The new output directory contains `000.wav`, `001.wav`, and so on, plus
`audio-export.json`. The report records input/tool/output hashes, sample counts,
logical ordinals, normalized event-metadata identity and unreferenced source
ranges. Physical DAT order can differ from logical HDR order; assign WAVs by
reported ordinal. Duplicate references remain distinct logical slots. No bank
metadata is accepted into the game merely because this export succeeded.

The decoder reads the whole final 28-sample ADPCM block and keeps exactly the
source's declared samples, avoiding FFmpeg's otherwise truncated tail. PCM16 is
a **transcode**, not bit-identical to the game's float predictor. The native
comparison found small sample differences. Missing rate fields are explicitly
set to the game's 24 kHz default, avoiding FFmpeg's different 48 kHz default.
Do not describe WAV export alone as a fully faithful conversion.

For the new typed R2 adapter, preserve the coded audio instead:

```powershell
defjam-tools fighter audio --source .\legacy\600.dat --header .\legacy\600.hdr --encoding ea-adpcm-r2 --out .\work\voice-600-r2
```

This mode requires no FFmpeg and writes the exact bounded source streams as
`000.bin`, `001.bin`, etc. Keep `audio-export.json` outside the final pack, then
reference the needed files using `fighter-voice-2`. This source version has the
same resource fields as `fighter-voice-1`, but every file descriptor also states
its format explicitly:

```json
{"path": "audio/reaction.bin", "sha256": "<64 lowercase hex digits>", "format": "ea-adpcm-r2"}
```

Use `wav-pcm16` for WAV descriptors in the same version2 resource. The runtime
checks R2 block sizes, predictor indices, partial tails, packet counts and a
specific mono revision3 header profile. It rebuilds its own header while keeping
coded samples, the native 24 kHz default, and the source's software-decoder
selection. It accepts neither arbitrary audio codecs nor bank/event metadata.
All 2,865 source clips pass this typed rebuilding check, including native
signed sample-count semantics. A synthetic compressed test sound has been
identified in captured combat audio. A version3 probe now also requests the
original voice's explicit family and produces a matching original line in the
device capture. This is one playback observation, not complete voice-event or
whole-pack acceptance. Match event templates separately before calling a fighter
conversion faithful. Keep the original files.

### Choose a different event template for each category

Some voices combine reaction, taunt and environmental banks from different
templates. Their event-family numbers also matter: a valid clip will not play
if the game requests a different family. The third voice format lets you name
these choices separately, without importing an older mod's arbitrary metadata.

**Technical details.** `fighter-voice-3` replaces the top-level `template_voice`
and `samples` fields with `banks`. Supply exactly `Character`, `Taunts` and
`Enviro`; each contains `template_voice`, `family` and `samples`. For example,
the shape of a Character entry is:

```json
"Character": {
  "template_voice": 0,
  "family": 1,
  "samples": {
    "0": {"path": "audio/reaction.bin", "sha256": "<64 lowercase hex digits>", "format": "ea-adpcm-r2"}
  }
}
```

This is a fragment, not a complete voice source. Include the other two banks
and mandatory `intro`/`extro` descriptors. All descriptors use the explicit
`wav-pcm16` or `ea-adpcm-r2` format from version2. Allowed families are Character
0/1, Taunts 16625/16626 and Enviro 40962/40963. The compiler verifies each
template in the player's original archive, keeps its event metadata, and changes
only the declared family, allocated voice ID and bounded audio references.
Missing sample overrides still retain template clips. Missing whole categories
are not supported; do not invent silent banks to claim a faithful conversion.

The resource's `events` compatibility label must still match the fighter's
moveset. Choosing a permitted family does not prove that a particular action
requests it: test the relevant events in-game. There is no universal automatic
fallback between family0 and family1. All 129 supplied legacy banks (2,777
banked clips) now rebuild with their normalized event metadata preserved,
including 45 banks requiring an explicit family change. This is a compiler
check; native playback and missing-category accounting are separate gates.

## 10. Tune the CPU opponent

AI settings change tendencies such as attacking versus defending. Start with
small changes and test the fighter as a CPU at each difficulty. “More aggressive”
does not guarantee a better opponent in every venue or matchup.

**Technical details.** `kind: "ai"` has empty compatibility. `fighter-ai-1`
uses `template_profile` plus `tendencies`. Provide `easy`, `normal`, `hard`, each
with native slots `"0"` through `"3"`; every slot needs at least one named edit
with integer value 1–5. The allowed names are `EDITABLE` in the recomp's
`setup/fighter_ai.py`, including `Attack_versus_Defend` and
`Strike_versus_Grapple`. Unedited values and native stage/trigger programs remain
inherited. Raw AI XML or scripts are not accepted as pack behavior.

## 11. Add entrances, victories and Blazin

These are coordinated performances. An entrance can involve the fighter, camera
and sound. A finishing move involves both fighters. Editing only one participant
can leave the other floating, facing the wrong way or reacting at the wrong time.

**Technical details.** Intro/victory components both reference resources with
`kind: "cinematic"`, skeleton/events compatibility, and `fighter-cinematic-1` source fields
`format`, `template`, `track`. Supported templates are simple native `CI_XXXX`
or `CE_XXXX` plans; the composer checks the actual plan and rig. The track is a
complete quaternion JSON resource, not an opaque cinematic VIV.

`fighter-blazin-1` has four `shots`, in native phase order. Each shot has
`template` and optional `track`. Template names match `BT1_nn`, `BT2_nn`,
`BT3_nn`, `BT4Cnn` for their respective phases. Phase 4 keeps the native
venue-specific camera behavior. Optional `pairs` maps at most four supported
inherited finisher choices to both `subject` and `counterpart` track descriptors.
The runtime verifies ownership and matching timing; a pair is not a single
attacker animation. Unsupported branches, camera programs and event graphs
need general adapters rather than copied native dispatch code.

### Give the four finishing-move slots separate animations

A fighter has four finishing-move slots. Two slots may follow the same move
rules while showing different animations. The second Blazin format identifies
each slot separately, so one slot's animation does not replace every use of
the same move template.

**Technical details.** `fighter-blazin-2` has exactly `format`, `shots`, `slots`.
The four activation shots follow the version1 rules. `slots` has one to four
canonical string keys `"0"` through `"3"`. Each value contains exactly
`template_choice` (integer 0–81), `subject` and `counterpart` quaternion-file
descriptors. Unlike version1's `pairs`, these slots may select a different
verified retail behavior from the inherited moveset's original choice. Omitted
slots retain their inherited choice and animation. Do not include both `pairs`
and `slots`.

The compiler changes only the declared four packed choice fields and creates
independently owned paired motions. Native validation reconstructs those fields,
checks each binding against the actor's selected slot, and preserves the chosen
template's parameters, camera behavior, timing and root motion. Choosing the
same template for two slots does not merge their animation resources. The
current track format still cannot represent every legacy motion/helper graph;
slot support alone does not make those full animation banks importable. Focused
compiled-C checks pass. A large four-fighter fixture exposed limited space in the
original game's asset memory pool. A separate pool for custom animation data is
implemented and has passed a full four-fighter match plus native exit-to-menu
cleanup. Explicit playback coverage still needs slot1, so this version remains
experimental. Do not treat a successful pack build as proof that every fighter
and all four slots have been exercised in a match.

## 12. Validate, package and test with other mods

Validation catches structural problems before play. Playtesting catches things
you can only see or hear: a stretched shoulder, a bad portrait crop, an awkward
camera cut or a sound at the wrong time. Keep those two checks separate when
describing your release.

**Technical details.** `fighter validate` invokes the recomp's full resolver,
asset compilers and native menu composer in a temporary workspace. It checks
hashes again after compilation. `fighter package` reruns this check, packages
only the exact verified bytes, uses stable ZIP metadata, reads back the archive,
and refuses to replace existing output. Both commands return nonzero on failure.

```powershell
& $tools fighter validate 'C:/mods/my-roster' --with-pack 'C:/mods/shared-rigs' --recomp $recomp --game $game
& $tools fighter validate 'C:/mods/my-roster' --with-pack 'C:/mods/another-roster' --language 'C:/mods/my-language' --recomp $recomp --game $game
```

Repeat `--with-pack` for dependencies and coexistence tests. Only the first
folder is packaged; dependencies remain separate packs. An exact dependency
must also be enabled in the launcher. Displaying a manifest or opening one
model is not equivalent to this combined validation.

Test selection and Back/cancel in the native two-/three-/four-player layouts,
human and CPU roles, entrances, movement, attacks, received hits, victory/result
pictures, Blazin, repeated matches and Story's created fighter. Check languages
and texture mods that touch related UI. Use a disposable test profile first.
Report the exact runtime version, pack versions, tested combinations and remaining
limits; do not turn “compiled” into a claim of native acceptance.

## 13. Update a pack and resolve conflicts

An update should improve the same fighter without erasing their identity.
Keep a copy of each released ZIP and its editable source. If two packs disagree,
the safest fix is an explicit choice that the user can see, not whichever pack
happened to load last.

**Technical details.** Keep pack/fighter/resource keys stable, increment the
version and preserve dependency versions deliberately. Identical component edits
can compose; incompatible edits to the same component produce a conflict. Stats
are currently a single conflict group. The recomp's `suggest-compatibility`
command can create a reviewed override choice with exact dependencies; it does
not adapt incompatible assets. Inheritance, donor rig and event joins still apply.

The launcher validates updates and rollback before replacement. Disable a pack
before removing it, and disable its dependents first. Missing custom content
becomes dormant in managed saves. Restoring the same stable IDs recovers their
association. Never ship a save folder with a fighter pack or instruct players
to copy transient runtime indexes into their profiles.

## 14. Diagnose errors and understand legacy conversion

Read the first concrete error and fix that input before changing unrelated
files. Keep the original failing files so the cause can be reproduced. If an
adapter says a format is unsupported, changing the filename or hash cannot
make it supported.

**Technical details.** Common errors:

| Error | First action |
|---|---|
| Hash mismatch | Confirm the edit/download, then update the descriptor's digest |
| Undeclared file | Move source projects/reports out of the package folder |
| Missing dependency | Supply the exact required pack version to validation and activation |
| Skeleton/event mismatch | Match the actual donor/rig/template; do not relabel incompatible data |
| Unsupported facial palette | Check rig, capacities, sample values and destinations; retain a rejected legacy file for adapter investigation |
| Unsupported render layout | Keep the input and decoder report; do not copy opaque rendering commands |
| Voice WAV rejected | Export mono signed PCM16 within the supported sample-rate/length bounds |
| Pack changed after validation | Finish the editor write and package again to a new output |

The Vendetta `.mod` is a ZIP containing loose assets and replacements for shared
databases. A faithful conversion must recover each fighter's own components,
preserve intended behavior, remap references and account for global edits.
It must not replace retail databases wholesale or silently drop unsupported
faces/moves/cinematics. Current investigation found 46 added SOD characters,
not just the 44 advertised in metadata. All 46 appearances now compile,
including distinct facial palettes. Their ordinary combat animation banks
and action tables exactly match mapped retail donors and can be inherited
faithfully. Their four finisher selections differ, however, and the added
finisher motion data and cinematic helpers still need complete conversion
support. Facial and hand tracks choose poses from separate palettes; their
references must fit the particular fighter's face and the shared hand resource.
A motion's timing also includes its parent duration and playback scale, beyond
the visible list of animation keys. Those parts must survive conversion together.
Compressed voice samples and explicit bank families have supported component
paths, but explicitly absent voice categories still need a general adapter.
Reusing a gameplay template must not discard custom animations or recordings.

A full converted pack is not yet a supported output of this draft. The conversion
report must account for every changed component, including missing voice
categories, ancillary portrait art and any unrelated global edits. New adapter
R&D is part of M5; the creator commands above already work for the supported
formats and remain useful independently of this legacy mod.
