# Next fighter mapping — 2026-10-27

Read-only investigation for the owner’s next batch (Redman, Henry Rollins). No source code, active data, reviews, images, models, runtime or publication state was changed. Only this source-only report was written. No decoded image or mesh was exported. The source model decoder was exercised entirely in memory.

## Mapping and evidence

| Requested label | Exact fighter.xml name/display | Fighter ID | coreID | Main stem | Entity evidence |
|---|---|---:|---:|---|---|
| Redman (local internal alias: Doc) | DOC / Doc (MAR) | 55 | 10 | V2IP_109A | CHAR_DOC and V2IP_109A entity blocks both point to V2IP_109A model and texture |
| Henry Rollins | ROLINS / ROLINS (STF) | 75 | 72 | V2IP_131A | V2IP_131A entity block points to same model and texture |

Evidence: own dump `fighter.xml:775`–788 and `:1055`–1068; `assets/entity.xml:1170` onward (CHAR_DOC), `:1816` (109A), `:2050` (131A). Exact fighter blocks were located by bounded `<fighter>…</fighter>` matching, avoiding malformed markup elsewhere. Entity blocks were likewise inspected locally.

Naming limit: this dump’s XML never spells out “Redman” or “Henry Rollins”; the labels above normalize the requested real-world names to the expected Doc and ROLINS entries. The Redman-to-Doc association should receive a visual likeness check by the main agent during first atlas/model inspection, rather than claiming the XML itself explicitly proves the public name. This does not affect the measured IDs/stems below.

Both stems have precisely `.o`, `.xsh`, and `_F.o` members in `assets/v2ip.viv`. No B/C/other numbered variant was found for either 109 or 131 in this archive or in matching fighter/entity blocks. `_F.o` is a separate 2704-byte decompressed helper resource; its purpose was not decoded, and it is not evidence of an alternate outfit. Thus start with A only. Neither mapping requires collecting all other fighters or rebuilding the corpus.

## All texture slots

Existing `defjam_tools.hd_assets.archive_entries`, `unpack_refpack`, and `shpx_images(decode=False)` read the two XSH resources in memory. Both contain three actual texture directory entries (palette attachments are not extra textures). All six are paletted SHPX type `0x7b`, swizzled, NV2A format `0x0b`, 256 BGRA palette entries. IDs are the existing XRTEX01 source identity algorithm, not a new hash scheme.

| Stem | Index/name | Size | Source ID |
|---|---|---|---|
| V2IP_109A | 0 / A109 | 512×512 | `61ca4a5526f266aa676e52bff3ac615eff3bb85f8d32f6375e81cce2da374c6b` |
| V2IP_109A | 1 / br01 | 256×256 | `0e44a18b3a859519dea1d3917d3cdd689c221375530ea183456aa691ccd150ac` |
| V2IP_109A | 2 / br02 | 256×256 | `17825816ae71c00e6823dc2cbd9e382c9e99fbfde91a37a156090de96761148b` |
| V2IP_131A | 0 / A131 | 512×512 | `4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d` |
| V2IP_131A | 1 / br01 | 256×256 | `9ed8e7d03836060d48cc8171b7a4a7d0be6c29b7f54081525052657145088eb8` |
| V2IP_131A | 2 / br02 | 256×256 | `a3fe20cc78618e1cec50fbcb530566d538a77327e38cc1b39753a8a53999ac7a` |

Index0 is the primary character atlas used by the existing single-texture preview. The shader/material role of br01/br02 was not established; do not infer that these need artistic restoration or include them as redundant body atlases. Do not invent runtime aliases from these distinct textures.

## Minimal model-viewer additions

`src/defjam_tools/defjam_model.py:21` is the only fighter table. Proposed entries (no edit made):

```python
"redman": ("Redman (Doc)", "V2IP_109A", "61ca4a5526f266aa676e52bff3ac615eff3bb85f8d32f6375e81cce2da374c6b"),
"henry-rollins": ("Henry Rollins", "V2IP_131A", "4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d"),
```

`defjam_model.main` uses this table for CLI choices and selects the matching `<stem>.o`; `model_workshop.py` imports the same table, checks source identity, and enumerates prepared private models. No separate Blaze/Nyne/Trejo-only condition was found elsewhere in Python or model viewer HTML. The main agent must still export the private model from the recovered corpus and verify actual browser behavior. Existing authoring AGENTS.md's three-model statement and docs may need updating after that work.

In-memory decoding with the existing unchanged `decode` succeeds:

| Model | Vertices | Triangles | Parts | Omitted helper |
|---|---:|---:|---:|---|
| V2IP_109A.o | 5206 | 6015 | 41 | Direction RM40 |
| V2IP_131A.o | 4536 | 5810 | 30 | Direction RM29 |

Both resolve the same five group names supported by the current decoder: eye envmap1, skin envmap2, cloth envmap4, eyelid alpha, nospec. No unsupported shader/topology exception occurred. This establishes decoder compatibility, not image appearance, glTF validation or native-game parity; those remain main-agent verification. No exported geometry was retained.

## Provenance pins

| Source | Bytes | SHA-256 |
|---|---:|---|
| fighter.xml | 45931 | `21ff6088cebeb90bd9cf48285848e23898c094143fc5da8401e8c63371f9d870` |
| assets/entity.xml | 91595 | `d366e9f7ad6a651affb2776c924ec43ccf8f1191b72ab4771b9edfb2ec9d615b` |
| assets/v2ip.viv | 26686237 | `b437838337d96eed2ae1c03f6f547f500e19ed9ad534bedef20ae784aba5af96` |
| decompressed V2IP_109A.o | 282448 | `5abecf25169995d3beb9ac1c1640289d2f92607415e881f42e5f4872c08fff4f` |
| decompressed V2IP_109A.xsh | 397120 | `b18b77f6f1db8b8dd423adc2704908b5ead3fdb83791d894ed8652b7dc24c6d4` |
| decompressed V2IP_131A.o | 239664 | `59af734f44820645786e6b1bfeac8549e18c902a2f9f11287946091194d568e2` |
| decompressed V2IP_131A.xsh | 397120 | `c2c7cd706704c5a3492e9af3b83d5624f8bc215180d6258f85ebad92e598675d` |

Python was `/Users/vlad/Code/DefJam-Modding-Tools/.venv/bin/python`, with `PYTHONPATH=/private/tmp/defjam-tools-hd-fighters-20261026/src`. No model export/build/game invocation/image generation was run.

## Ten-line handoff

1. Redman maps to expected internal Doc entry ID55/core10, main stem V2IP_109A; visually confirm alias.
2. Henry Rollins is misspelled ROLINS internally, ID75/core72, main stem V2IP_131A.
3. Neither has another outfit stem in this archive or matching XML blocks.
4. Each has three actual texture slots: one512²main atlas, two256²br01/br02 textures.
5. Redman main ID is 61ca4a5526f266aa676e52bff3ac615eff3bb85f8d32f6375e81cce2da374c6b.
6. Rollins main ID is 4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d.
7. Existing decoder reads Redman5206vertices/6015triangles/41parts without modifications.
8. Existing decoder reads Rollins4536vertices/5810triangles/30parts without modifications.
9. Two FIGHTERS table entries plus private main-agent export should expose both through existing catalogue flow.
10. Nothing active was modified; source-only report, no raw art/XML/geometry copied or exported.
