# Fighter cutscene texture sharing — full bounded census

2026-10-30. Read-only own-dump investigation; no game, build, binary/art export, generation, live API write or source edit. Metadata evidence is `/private/tmp/fighter-cutscene-sharing-20261030.json`.

## Answer

**Most in-engine cinematic fighter atlases are exactly the same content as gameplay atlases, but coverage is not universal.** One content-addressed replacement entry should cover identical runtime source bytes/descriptors wherever they are bound, including a cinematic copy. That is a loader/source inference, not native cutscene acceptance. Separate story costume/damage atlases, shared accessory textures, created-player data and prerecorded movies require separate accounting.

## Fresh archive and content identity measurements

Walked both full archives in memory with the existing bounded BIG/RefPack readers. Recomputed every XSH image identity with `shpx_images(decode=False)`: all271 image records matched the retained corpus alias's exact source ID, with no errors. This rechecks original packed pixel/index bytes, full palette and descriptor, rather than comparing labels or rendered thumbnails.

| Scope | Aliases/records | Unique source IDs |
|---|---:|---:|
| Entire gameplay v2ip.viv | 215 | 213 |
| Entire cinematic v2ip_cin.viv | 56 | 55 |
| Fixed fighter main atlases in gameplay, excluding999 | 77 | 77 |
| Fixed fighter main atlases in cinematics, excluding999 and shared tape | 54 | 53 |
| Fixed cinematic main IDs also in gameplay | — | 50 |
| Fixed cinematic main IDs absent from gameplay | 3 | 3 |
| Union of fixed gameplay/cinematic main IDs | — | 80 |
| Fixed cinematic main IDs represented by current65 outfit previews | 40 | 40 |

Cinematic totals also include one created-player999 main atlas and one32×64 `tape` image. With these included,51cin IDs are shared with gameplay and4 are exclusive relative to **v2ip.viv**, not necessarily exclusive to the whole game. The fixed cinematic main54aliases collapse to53IDs because Crow126E's image equals126B's image despite its `E126` name.

All cinematic main images are512×512, paletted type0x7b, NV2Aformat0x0b,256palette entries. There is no separate higher-resolution cinematic head image in these XSH resources. None of the cinematic XSH resources contains br01/br02; those are gameplay supplemental states and their runtime use remains unresolved.

Archive SHA256:

- assets/v2ip.viv: `b437838337d96eed2ae1c03f6f547f500e19ed9ad534bedef20ae784aba5af96`
- assets/v2ip_cin.viv: `cf1ed538948cc750ae0ec86255efccf4994dfeb1499e18c69fd815208b1f9679`

## Cinematic main atlases still outside the current65

There are14cinematic resource aliases /13unique fixed main IDs outside the current65 outfit-source IDs:

| Resources | Identity/role evidence |
|---|---|
| 003A | House, fighter.xml; generation hold |
| 012A | Bo, fighter.xml; generation hold |
| 115A | Xzibit, fighter.xml; generation hold |
| 307A | Lil Flip, fighter.xml; generation hold |
| 402A | Shaniqua, fighter.xml; current decoder limitation |
| 501A | Explicit SHADOWYFIGURE / Shadowy Figure in fighter.xml and CHAR_SHADOWYFIGURE in entity.xml; prior authoring audit labels the intentional-shadow identity Suspect |
| 113C | Bloody Blaze annotation/entity CHAR_BLAZE2; separate state atlas |
| 014D | Cinematic-only D-Mob variant; CHAR_DMOB4; prior visual audit reports injuries |
| 126B and126E | Crow variant and CHAR_CROWSUIT; share one exact source ID, unresolved/current unsupported preview variants |
| 126D | Cinematic-only Crow atlas; separate content; wardrobe/state relationship remains unresolved |
| 128B | Cinematic-only Magic variant; CHAR_MAGIC2; prior visual audit reports injuries |
| 401B | Carmen cinematic state, separate image ID although prior visual audit finds same wardrobe; runtime role not inferred |
| 403B | Cindy cinematic state, separate image ID although prior visual audit finds same wardrobe; current model limitation |

The three fixed cinematic-exclusive IDs are:

- 014D /D014: `0c65cd13d0cdf44b9c4b1af78f884629eb93a5696a1fd4eea0601674646199b2`
- 126D /D126: `e5473d72ffed6694e62e9ae15405cde7aae5bc6a65046335c2f0537e93ba0fc6`
- 128B /B128: `445272fe820b0249e0bb20b156209db92bb1eeca2d5ba774d5f695bba19ef94c`

Do not promote an existing A atlas into one of these states merely because the same person appears. Main injury/costume variants are separate from256-square br01/br02 supplements.

## Cinematic models and binding evidence

Read110cinematic ELF object symbol tables without exporting them:55main V2IP models and55support objects. All55main models reference their own expected A/B/C/D/E texture shape plus optional glints/tape; none references br01/br02. A model shape name alone does not contain its source hash: the XSH/source association above supplies that correlation.

There are51same-named main models in gameplay, including999. Their full ELF bytes and.data bytes differ, so they must not be described as identical files. However, all40cinematic counterparts represented by the current65 supported previews were also decoded in memory with decoder2: **retained mesh arrays compare exactly equal to the gameplay counterpart**, including positions, normals, UVs, indices/material groups/texture refs; all bounds, vertex counts and triangle counts match. This is strong evidence against a separate higher-polygon retained cinematic head for these40resources. It does not compare omitted effects or reconstruct rigs/animation.

Shawnna has an explicit omitted-auxiliary difference: cinematic material uses shared `tape,1`, while the gameplay mouth auxiliary binds A406. The retained mesh comparison still matches because both auxiliaries are explicitly omitted by the decoder. Four other female shared tape omissions and sparkle/studio approximations remain limitations; do not imply all cinematic passes are represented by the viewer.

## Story actor reuse

Read complete `<entity>` blocks individually to avoid treating the malformed whole XML as valid.60CHAR_* declarations with explicit V2IP bigfile references resolve to47stems, including999. Relevant exact references in assets/entity.xml:

- CHAR_DMOB/2/3/4 use014A/B/C/D (entity blocks start1029/1039/1049/1059).
- CHAR_BLAZE uses113B (1069); Bloody Blaze /CHAR_BLAZE2 uses113C (1079–1086).
- CHAR_CROW/CHAR_CROW2/CHAR_CROWSUIT use126A/B/E (1090/1100/1110).
- CHAR_MAGIC/CHAR_MAGIC2 use128A/B (1190/1200).
- CHAR_TREJO andCHAR_BOUNCER2 reuse112A (1210/1350); CHAR_SUITOR reuses Nyne009A (1500).
- CHAR_ENEMY1 reuses Ice-T132A (1250); CHAR_ENEMY2 reuses Prodigy119A (1260); CHAR_DOC reuses Redman109A (1170).
- CHAR_OMAR/ALLY1 reuse O.E.308A (1370/1310); CHAR_SKETCHARTIST reuses Lauren405A (1330).

These prove shared model/texture declarations, not which shots are actually reached or rendered in a particular playthrough. Generic story actor names do not imply new independent art is required when their source ID is already shared.

## Loader implication and acceptance boundary

Reviewed `/Users/vlad/Code/DefJamFFNY-recomp/tools/xboxrecomp/src/nv2a/texture_pack.c`, toolkit checkout commit `e81806613baf5a8c20e9b2a09e61cb103f7160fd`:

- `texture_pack_hash`, lines233–258, hashes XRTEX01 plus format,width,height,palette entry count,row texels and tightly selected source bytes/full palette. It does not hash archive/member/fighter/scene names or memory address.
- `texture_pack_bind`, lines703–775, resolves that content ID with `lookup(id)` after cache/source validation. A cinematic copy at another memory address with the same descriptor and content therefore resolves the same pack entry.
- Equal decoded appearance alone does not imply equal source ID: palette ordering/full palette, packed format, row width or runtime modifications can change it. This census proves archive identities, not every observed runtime draw's descriptor.
- Dynamic texture mutation and source revalidation can change lookup behavior; no claim that damage transitions or all cinematic shader/material passes are natively verified.

Thus the40already-restored cinematic main IDs generally need no duplicated generation just for their archive aliases. Publish a replacement once per content ID, but playtest representative cinematic draws and the special states before claiming full story coverage.

## Prerecorded movie boundary

Freshly checked the seven extracted `movies/*.mad` files; every file begins MADk: intro,attract,soulplan,eagames,thx,SoulTrai,extra. Existing source investigation `docs/widescreen/08-fmv-ai-pipeline.md` documents decoded movie dimensions/timing; `06-cutscenes-movies-and-ai.md` explicitly distinguishes in-engine scenes from these prerecorded movies. A fighter's material texture replacement does not rewrite faces/clothing baked into MAD video frames. Improving those is a separate video workflow; no new movie decode/export or native video test was performed here.
