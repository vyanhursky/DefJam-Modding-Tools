# HD Fighters 0.1 beta publication

The owner requested publication on 2026-10-26 before further fighter revisions.
This release packages three existing candidates byte-for-byte, preserving their
unapproved review state. It introduces no image generation, new art correction,
mesh changes, runtime changes or active-game installation.

`selection.json` pins Blaze/Nyne Rich Original Detail v1 and Trejo v4 Source
palette correction, including candidate IDs, PNG SHA-256, baseline hashes and
protected face rectangles. Historical stylized, superseded and Gentle drafts stay
in private review history and are excluded from this release.

The display name is **HD Fighters 0.1 (beta)**; the catalogue identifier is
`hd-fighters`, version `0.1.0-beta.1`, testing/prerelease channel. Three-part SemVer
is required by the existing catalogue. Minimum runtime 0.12.1 is conservative:
the exact released helper accepted the package; `textures-v1` is sufficient.
Faithful HD is optional. Place this pack after Faithful HD in Load Order.
HD Widescreen Menus has independent texture IDs and may remain enabled.

## Recipe and evidence

Run `build.py --help`. Supply the existing private workshop, the owner's extracted
dump, the installed channel-preserving Faithful baseline, the exact v0.12.1
helper source (`eeed26d4ae6871e78bcfae751437cb00e8b282a0`, setup/mods.py,
setup/mod_catalogue.py and config/mods/catalogue-keys.json), the catalogue source
checkout and a new private output directory. Do not write artwork inside Git.
The recipe validates inputs before creating output, refuses an existing output
and checks review JSON is unchanged. It does not need the gallery server.

The builder verifies each primary ID against `assets/v2ip.viv` image zero and
its 512×512 P8/256-entry palette descriptor, plus pinned Faithful baseline PNGs.
A separate read-only check confirmed all three IDs in the installed Faithful
manifest. Canonical IDs match existing runtime
hashing; no alternate alias was observed or invented. It checks all alpha and
protected face pixels exactly, then copies the existing PNG bytes unchanged.
`png_mips=channels` preserves material alpha semantics.

The six-file payload is three 2048×2048 RGBA PNGs, schema-1 manifest, README and
provenance receipt. Single root `hd-fighters-v0-1-0-beta-1`.

- ZIP: `hd-fighters-v0.1.0-beta.1.zip`
- Compressed bytes: 19,432,340; unpacked bytes: 19,427,988
- SHA-256: `bcba0164c1821f4121bba1089e806db4bf7111961a68cbef647d1c2991dfc62a`
- [Catalogue PR #6](https://github.com/vyanhursky/DefJamFFNY-mods/pull/6)
- [Cloudflare artifact](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/hd-fighters/0.1.0-beta.1/bcba0164c1821f4121bba1089e806db4bf7111961a68cbef647d1c2991dfc62a/hd-fighters-v0.1.0-beta.1.zip)

Cloudflare uses the existing HD-Menu workflow: immutable version/hash path,
public ZIP plus checksum and release-notes sidecars, SHA metadata, refusal to
overwrite a different object, full public download/hash/size and byte-range
verification. Private credentials remain in the existing named local profile.
Only artifact and sidecars are public; raw reviews, private paths, generated
source images and model caches are excluded.

Local validation: both released v0.12.1 helper and catalogue package validator
produce identical six-file hashes, exactly three texture IDs and textures-v1.
Catalogue metadata and 14 synthetic tests pass. Authoring 67 tests plus 12
subtests and eight Node tests pass; source-tree checker has zero policy failures.
The normal protected publication runs with bootstrap=false, checks prior signed
append-only history, downloads/validates/scans all active artifacts in a job
without signing credentials, then signs using the existing protected environment.

## Published verification

[Protected workflow 40453784754](https://github.com/vyanhursky/DefJamFFNY-mods/actions/runs/40453784754)
succeeded: package verification/ClamAV completed in 4m44s, then the ordinary owner
approval gate released signing/deployment. No protections or key pins changed.
Catalogue PR #6 merged as `053a8620ff8f72a5efbd2d8a2366b23892be636b`.
[Public signed catalogue](https://vyanhursky.github.io/DefJamFFNY-mods/index.json)
now has revision **6**, preserving all prior menu releases.

The exact released v0.12.1 helper fetched that catalogue using its pinned key,
verified the signature, matched all metadata against the reviewed source,
downloaded the public ZIP and installed in a disposable data root. All six
installed file hashes match the release. Stable-channel selection excludes the
beta. Synthetic settings/save sentinels and the real workshop JSON remained
byte-identical. Active game data was not used as an installation destination.

Private publication evidence is retained under
`<data>/scratch/hd-fighters-v0.1-beta1-published-20261026/`: artifact.json,
upload-plan.json, upload-receipt.json, managed-install-verification.json/log,
verify-managed.py, immutable ZIP/root and both validator outputs. There were no
publishing blockers. Native Trejo acceptance remains the owner's next step.

## Owner playtest

In game 0.12.1 or later, Mods → Show testing versions → Refresh catalogue →
HD Fighters → Install. Enable it in Installed mods, place it after optional
Faithful HD in Load Order, restart the game, and test Trejo's main outfit.
Installation alone does not enable the pack. The current game settings/save and
workshop reviews are untouched by this publication.

Compare neck/body color, tattoo strokes/script, animal/tree placement and buckle
against the original in-game. Blaze/Nyne skin warmth and Trejo fidelity remain
under review. Public beta publication is not stable art acceptance. Resume
revisions after the owner's Trejo playtest; use a new immutable release version
for changed bytes.
