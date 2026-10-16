> Historical research imported from DefJamFFNY-recomp at `f71ab64f62e4f54bf35233c34b26c144bb3008f1`. Paths and line numbers describe that checkout; see the current guides for commands.

# Restoration pilot: Blaze, Nyne and Trejo texture mapping

Read-only metadata investigation, 2026-10-15. Sources are the owner's extracted USA Xbox dump and the retained local faithful-HD corpus. No game/build/run, PNG export, rendering or image generation was performed. Only this source-only report was written. No game XML is reproduced wholesale and no artwork is embedded.

## Result

The bounded pilot comprises **five fighter model/state variants, fifteen unique texture source IDs and nineteen archive/image aliases**: five main 512x512 atlases, ten secondary 256x256 images, and four cinematic aliases sharing main-atlas IDs. Start the first three-asset/two-look audition with Blaze `V2IP_113A` slot0, Nyne `V2IP_009A` slot0 and Trejo `V2IP_112A` slot0. Preserve the two additional Blaze states and all secondary images in the review inventory.

## Fighter names and model variants

Local name evidence is `/Users/vlad/Code/defjam-data/extracted/fighter.xml` (line numbers below). File-level XML parsing fails on malformed unrelated markup at line564; the five complete selected `<fighter>` blocks were read individually and checked with line-numbered text. No repair or alteration of the dump was made.

| Display identity | Internal fighter name | Fighter ID | coreID | Model/texture stem | Name/model evidence |
|---|---|---:|---:|---|---|
| Nyne | `NYNE` | 2 | 55 | `V2IP_009A` | fighter.xml:34-39 |
| Trejo | `TREJO` | 7 | 23 | `V2IP_112A` | fighter.xml:104-109 |
| Blaze1 | `BLAZE` | 56 | 5 | `V2IP_113A` | fighter.xml:790-795 |
| Blaze2 | `BLAZE2` | 81 | 6 | `V2IP_113B` | fighter.xml:1140-1145 |
| Blaze3 | `BLAZE3` | 82 | 7 | `V2IP_113C` | fighter.xml:1154-1159 |

These `ID`, `coreID` and unrelated character-table IDs are separate namespaces. `gamedata.xml:29-30`, `:113-114`, `:263-264` separately names Blaze1003, Trejo1017 and Nyne1042; do not use those values as the fighter index for harness configuration. Historical in-game evidence already identifies Blaze fighter56 / `V2IP_113A` (`docs/research/hd-lanczos-game-pilot.md:9-18`).

`assets/entity.xml` confirms model/texture connections and shared uses:

- `CHAR_BLAZE` uses `V2IP_113B` (1070-1075); `CHAR_BLAZE2` uses `V2IP_113C` (1081-1086), preceded by the explicit `Bloody Blaze` annotation at1079. Label113C as a state variant, not an assumed cosmetic outfit. The relation between113A and113B also needs visual/game inspection before an outfit description is assigned.
- `CHAR_TREJO` uses `V2IP_112A` (1211-1216); `CHAR_BOUNCER2` reuses that same stem (1351-1356).
- `CHAR_SUITOR` uses `V2IP_009A` (1501-1506), also Nyne's fighter stem. A content-key replacement can therefore affect this shared story entity.
- Generic entity definitions connect model and texture names for009A (1645-1649),112A (1843-1847),113A (1852-1856),113B (1861-1865),113C (1870-1874).

Only one Nyne and one Trejo variant are named in fighter.xml. Fresh directory-prefix checks of `v2ip.viv` and `v2ip_cin.viv` found no additional009/112/113 texture stems beyond those listed here; that bounded result does not claim absence of unrelated UI portraits or other shared textures.

## Exact texture IDs and archive aliases

All five gameplay members have source type0x7b (paletted), swizzle flag0x2000, 256-entry BGRA palettes, and NV2A identity format0x0b. Each has index0 (512x512) named for the model, index1 `br01` (256x256), and index2 `br02` (256x256). Palette metadata was read from the owner's SHPX attachment chains. Source IDs were freshly recomputed from the complete original index bytes, complete palette and current five-field descriptor, and matched the retained corpus for all **19** selected aliases. The bytes were not written anywhere.

Table `source_id` values are original-content lookup candidates; they are not generated-output hashes. `decoded_id` values below come from retained corpus records and were not newly pixel-decoded in this review. Runtime IDs still require capture/correlation rather than being assumed equal to every archive identity.

| Fighter/model | Slot/name | Dimensions | Alpha range in retained corpus | Canonical source_id |
|---|---|---|---|---|
| Nyne `V2IP_009A` | 0 / `A009` | 512x512 | 0..255 | `a25c4fdd4998993c94d18ad0f5169c7ad6e6b898c711482777303c7ba3a18517` |
| Nyne `V2IP_009A` | 1 / `br01` | 256x256 | 103..255 | `00ae19d45b1c21fe642613b3b61e01eba7cfb6748facb97206f56b10ccf10582` |
| Nyne `V2IP_009A` | 2 / `br02` | 256x256 | 103..255 | `37a1b5eb0da7e729f2b52e979906015ef45550807f6fe377d5ecc6aa06d615d1` |
| Trejo `V2IP_112A` | 0 / `A112` | 512x512 | 0..255 | `1900051b32443a33a745c088a08231d039d80c9eb96483f4b43456a2a3f68f24` |
| Trejo `V2IP_112A` | 1 / `br01` | 256x256 | 0..255 | `41adb017f286df32b84684b0ff8ace38cb59f9d247daaf7672e9b2d75c0cb1ff` |
| Trejo `V2IP_112A` | 2 / `br02` | 256x256 | 0..255 | `20b85ff40848d22e65eeff377e84d74d8e2724feb32343791b07bce565987ec6` |
| Blaze `V2IP_113A` | 0 / `A113` | 512x512 | 1..255 | `5c9b3229151c2853656113a8df7e3f91effdef5ae68c9bdd567e5a71bbe9c91a` |
| Blaze `V2IP_113A` | 1 / `br01` | 256x256 | 102..255 | `dddcaca17fde0c91aeedcf2eb3fd46f477e8905aaa28d6f73e47847ede056305` |
| Blaze `V2IP_113A` | 2 / `br02` | 256x256 | 102..255 | `669c02423a6587161fb3f13e3436b32c3f1f2b93577e33f4c488b5391dd0d339` |
| Blaze2 `V2IP_113B` | 0 / `B113` | 512x512 | 1..255 | `df031556e345c259b1d1c0ce054a04eda28fc96b356e849c3af3cd116236e52b` |
| Blaze2 `V2IP_113B` | 1 / `br01` | 256x256 | 103..255 | `e9a4e5bac524c4f1a97dae6533ee367df03fe8a2282db6476cc7cfa7212c7a34` |
| Blaze2 `V2IP_113B` | 2 / `br02` | 256x256 | 103..255 | `2e2e20c0db9b39795b88736579efc3e0f4c1f30f8268df61ce47c1a4eeef3c5e` |
| Blaze3 `V2IP_113C` | 0 / `C113` | 512x512 | 1..255 | `2ea9a0b3e28beed974042c06ae30fb478e759bd1a736e92690205f1f953e3075` |
| Blaze3 `V2IP_113C` | 1 / `br01` | 256x256 | 103..255 | `d67be9b5b1c0f9673fbd8c975e03809037e1d4df7ca434ac17f62a6d355136ab` |
| Blaze3 `V2IP_113C` | 2 / `br02` | 256x256 | 103..255 | `e7488160472144aea7ae48062272c1e44eb17f7c0c5dd3f19724802889a41ce8` |

Every table row has gameplay alias `assets/v2ip.viv::<model>.xsh`, with the exact slot/name shown. Main-atlas cinematic aliases are:

| Model | Additional exact source alias | Identity behavior |
|---|---|---|
| `V2IP_009A` | `assets/v2ip_cin.viv::assets/V2IP_009A.viv::V2IP_009A.xsh` | slot0 `A009`; identical source_id to gameplay main |
| `V2IP_112A` | `assets/v2ip_cin.viv::assets/V2IP_112A.viv::V2IP_112A.xsh` | slot0 `A112`; identical source_id to gameplay main |
| `V2IP_113B` | `assets/v2ip_cin.viv::assets/V2IP_113B.viv::V2IP_113B.xsh` | slot0 `B113`; identical source_id to gameplay main |
| `V2IP_113C` | `assets/v2ip_cin.viv::assets/V2IP_113C.viv::V2IP_113C.xsh` | slot0 `C113`; identical source_id to gameplay main |

No `V2IP_113A` member was present in the inspected cinematic archive directory. Each of the four selected cinematic SHPX files contains only the main image; no `br01`/`br02` aliases from those cinematic members were found. Therefore a review candidate should retain both gameplay and cinematic provenance on one main texture record, rather than duplicate identical art.

## Decoded identities

| Model / slot | Retained decoded_id |
|---|---|
| `V2IP_009A` / 0 | `c6989ef1a1cf0bcbf737f3a09dbd09527267c2aa8d9ea83442ec36a20bbf4e49` |
| `V2IP_009A` / 1 | `52b4521e66c75d6ddda24113590aa3d9ef0ad66c817d0147c79713890b48813f` |
| `V2IP_009A` / 2 | `fa40d57837086b40eab6e6c0b8843ba3af9120b72deeb2beb51955b3b85a0f35` |
| `V2IP_112A` / 0 | `66ead9e9e4d0fa8e5f68054e7ac6aa7724994f07ad6100318283f8092eccc6ce` |
| `V2IP_112A` / 1 | `9bc9cfea42c1de217d0a3fa2760b0ae5f0b5f1345e7fc5b562aced8115b6a14a` |
| `V2IP_112A` / 2 | `ea791f5e29e667127cfde0fcf1638633c47bc90268af2c302f8d6b59b07fdc45` |
| `V2IP_113A` / 0 | `d2243c9236cd1457da12784c1a2eeb8d1625cebb2a8b64de26e80ef2f6ba9f58` |
| `V2IP_113A` / 1 | `4d0593b114a431221e87d050e487137c0ca29a1ebe1287bcb8e5345b921dbe23` |
| `V2IP_113A` / 2 | `e64d40099439f890fbfc2e045fd1701f839c28efb294348960d337a2ea6e9987` |
| `V2IP_113B` / 0 | `3f33bc98220c7d117295552e595ff562af360ef172a1d165513222bd562c796c` |
| `V2IP_113B` / 1 | `c2358eafbdbd36dc5c6675bf3c555972362336461cb0d63eaef2479a068731c7` |
| `V2IP_113B` / 2 | `91d4ffc3e42e40888382673f768bca712eeb094b28da87127a71e8497a9e3101` |
| `V2IP_113C` / 0 | `7a95eff99743e6cca9bb6a22c3edfbc284206502c10a5648f488745fe85cadc9` |
| `V2IP_113C` / 1 | `fda4bad31a7b13e709265511d32d04132a9af0433f3289dc5c9b48e4a081015d` |
| `V2IP_113C` / 2 | `554d22e9c3539a160d4390710b03d797add2f49b689193ab7286a2b639a0de22` |

## Main versus secondary: safe conclusions

“Main” means only the model-named512x512 slot0 and “secondary” means the two smaller `br01`/`br02` slots. Archive name, slot position, resolution and alpha extrema do **not** prove skin, clothing, facial region, damage, transparency or material-channel semantics. The `br` prefix must not be silently expanded into a proven bruise/damage classification. In particular, neither secondary is approved for face editing on the strength of this metadata.

Owner scope: restore everything except faces unless a specific low-resolution-damage exception is approved. Whole main atlases can contain face pixels; the metadata supplies no facial UV rectangles or safe edit masks. The gallery should mark all face-edit exceptions as unapproved, let the owner identify/protect facial regions against the original, and composite preserved source/baseline face regions back after generation before any candidate can be approved. Do not infer face boundaries from these slot names. Alpha/material data also needs independent preservation and inspection.

For the first three-main pilot, the needed originals already exist as `originals/<source_id>.png`, accepted Lanczos as `textures/<source_id>.png` and thumbnails as `thumbs/<source_id>.jpg` beneath the corpus root. No extraction is necessary to open those files. Corpus paths must be checked against retained hashes before generation/import. A per-asset gallery record should keep fighter/model/state, source aliases, dimensions, source/decoded IDs, protected face regions, approval state and candidate output hashes.

## Sources and reproducibility

Own dump root: `/Users/vlad/Code/defjam-data/extracted`. Retained corpus root: `/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0`. No output artwork is included in this report.

| Source file | SHA-256 read during this investigation |
|---|---|
| `fighter.xml` | `21ff6088cebeb90bd9cf48285848e23898c094143fc5da8401e8c63371f9d870` |
| `gamedata.xml` | `685ccd452c1b7ef0d90ddc17f62202bd8fba006a43294c347ce048eeaba72c62` |
| `assets/entity.xml` | `d366e9f7ad6a651affb2776c924ec43ccf8f1191b72ab4771b9edfb2ec9d615b` |
| `assets/v2ip.viv` | `b437838337d96eed2ae1c03f6f547f500e19ed9ad534bedef20ae784aba5af96` |
| `assets/v2ip_cin.viv` | `cf1ed538948cc750ae0ec86255efccf4994dfeb1499e18c69fd815208b1f9679` |
| retained `corpus.json` | `b4b1433617bcd0687ab5242d5aa0ca63b395f06ee9174b8d9cbb35282d461089` |

Inspection used the existing bounded BIG/RefPack reader (`scripts/hd_assets.py:26-29`, `:32-101`) plus a small in-memory SHPX-header/palette reader, without image decoding or binary export. For these all-paletted selected images, original source identity is format0x0b, original width/height, 256 palette entries, row texel width equal to width, then original index bytes and full palette. Correlation limits and replacement rules remain those in `docs/hd-textures.md:103-117` and `docs/research/imagegen-existing-pipeline-review.md`.
