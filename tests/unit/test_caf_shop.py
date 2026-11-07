"""Synthetic retail metadata; no dump text, model or texture bytes in fixtures."""
import copy
import struct
from types import SimpleNamespace

import pytest

from defjam_tools.caf_shop import Binary, Locale, ShopDatabase, clean, text_hash, wardrobe


def localization(values):
    pairs = sorted(values.items())
    base = 36 + len(pairs) * 8
    raw = bytearray(struct.pack("<4s4I4s3I", b"LOCH", 20, 0, 1, base, b"LOCT", 16, 123, 0))
    for i, (key, _) in enumerate(pairs):
        raw.extend(struct.pack("<2I", key, i))
    section = bytearray(16 + 4 * len(pairs))
    for i, (_, text) in enumerate(pairs):
        struct.pack_into("<I", section, 16 + i * 4, len(section))
        section.extend(text.encode("utf-16le") + b"\0\0")
    struct.pack_into("<4s3I", section, 0, b"LOCL", len(section), 0, len(pairs))
    return bytes(raw + section)


def database():
    raw = bytearray(24)
    def add(data):
        while len(raw) % 4:
            raw.append(0)
        offset = len(raw)
        raw.extend(data)
        return offset
    def words(*values):
        return add(struct.pack("<" + "I" * len(values), *values))
    def mapping(tag, pairs, stride=1):
        data = (tag or b"") + struct.pack("<2I", len(pairs), stride)
        data += struct.pack("<" + "I" * len(pairs), *pairs)
        data += b"".join(struct.pack("<" + "I" * stride, *value) for value in pairs.values())
        return add(data)
    internal, design = add(b"synthetic\0"), add(b"Q01\0")
    color, fit = words(0, 3, 5), words(0, 2, 0)
    colors, fits = words(1, color), words(1, fit)
    record = words(0, 1, 1, colors, 0, 2, fits, 10, 0)
    rows = mapping(struct.pack("<I", ShopDatabase.CLOTHING), {77: (record,)})
    index = mapping(None, {ShopDatabase.CLOTHING: (rows,)})
    table = words(ShopDatabase.CLOTHING, index, 0, 1)
    data = mapping(b"DATA", {ShopDatabase.CLOTHING: (table,)})
    fields = (0x9f891e31, 0x965e3fb9, 0xac3e66a4, 0x0cfa401e, 0xca10191c, 0x7c853fa8, 0xc86e0a21, 0x0e334dc7)
    schema = mapping(b"SKMA", {ShopDatabase.CLOTHING ^ key: (i, 1) for i, key in enumerate(fields, 1)}, stride=2)
    strings = add(b"STRT" + struct.pack("<I8I", 4, 0, internal, 0, design, 100, 0, 200, 0))
    struct.pack_into("<4s5I", raw, 0, b"SODB", 2, 0, schema, data, strings)
    return bytes(raw), localization({100: "@Synthetic#Garment", 200: "Deep Blue", text_hash("FIT_111_0003"): "Open"})


def test_source_database_and_localization_resolve_names_and_offsets():
    sod, text = database()
    db = ShopDatabase(sod, Locale(text))
    row, = db.clothing()
    assert row["name"] == "Synthetic Garment"
    assert row["colors"] == [dict(id="0", name="Deep Blue", source_name="Deep Blue", number=5)]
    assert row["fits"] == [dict(id="0", offset=2, flags=0)]
    assert db.locale.get(text_hash("FIT_111_0003")) == "Open"
    assert db.locale.get(999) is None
    assert clean("@A#B  C") == "A B C"


def test_join_keeps_original_indices_and_uses_actual_model_offset():
    sod, text = database()
    db = ShopDatabase(sod, Locale(text))
    original = dict(id="12:3", model="V2CP_111_0003_C", styles=[
        dict(variants=["V2CP_111_0003_OTHER_01"]),
        dict(variants=["V2CP_111_0003_Q01_02", "V2CP_111_0003_Q01_05"])])
    groups = [dict(id="12", items=[original])]
    before = copy.deepcopy(groups)
    result = wardrobe(db, groups)
    assert not result["unresolved"]
    garment, = result["groups"]["12"]
    fit, = garment["colors"][0]["fittings"]
    assert fit["name"] == "Open"
    assert fit["selection"] == dict(item="12:3", style=1, color=1, palette="default")
    assert groups == before
    result = wardrobe(db, [])
    assert result["groups"]["12"][0]["colors"] == []
    assert result["unresolved"] == [dict(item="77", color="0", fitting="0")]


def test_geometry_first_join_handles_shared_hat_texture_and_duplicate_alias():
    row = dict(id="hat", name="Synthetic Cap", category=12, order=3, model=1, design="Q01",
               colors=[dict(id="0", name="Green", number=1)], fits=[dict(id="0", offset=1, flags=0)])
    locale = SimpleNamespace(get=lambda key: "Sideways")
    db = SimpleNamespace(clothing=lambda: iter([row]), locale=locale)
    groups = [dict(id="15", items=[dict(id="15:1", model="V2CP_141_0001_C", styles=[dict(variants=["V2CP_141_0001_Q01_01"])]),
                                   dict(id="15:2", model="V2CP_141_0002_C", styles=[dict(variants=["V2CP_141_0001_Q01_01"]), dict(variants=["V2CP_141_0001_Q01_01"])])])]
    fit = wardrobe(db, groups)["groups"]["15"][0]["colors"][0]["fittings"][0]
    assert fit["selection"]["item"] == "15:2"
    assert fit["selection"]["style"] == 0
    assert fit["aliases"] == [dict(item="15:2", style=1, color=0, palette="default")]


def test_distinct_textures_with_same_suffix_use_native_resource_name():
    row = dict(id="pants", name="Synthetic Pants", category=6, order=1, model=4, design="Q01",
               colors=[dict(id="0", name="Green", number=1)], fits=[dict(id="0", offset=0, flags=0)])
    db = SimpleNamespace(clothing=lambda: iter([row]), locale=SimpleNamespace(get=lambda key: "Standard"))
    item = dict(id="13:56", model="V2CP_122_0004_C", styles=[dict(variants=["V2CP_122_0003_Q01_01"]),
                                                            dict(variants=["V2CP_122_0004_Q01_01"])])
    fit = wardrobe(db, [dict(id="13", items=[item])])["groups"]["13"][0]["colors"][0]["fittings"][0]
    assert fit["selection"]["style"] == 1
    assert fit["resource"] == "V2CP_122_0004_Q01_01"
    assert not fit["aliases"]
    item["styles"][1]["variants"] = ["V2CP_122_0005_Q01_01"]
    result = wardrobe(db, [dict(id="13", items=[item])])
    assert result["unresolved"][0]["reason"] == "Ambiguous source textures"


@pytest.mark.parametrize("offset,value", [(4, 9), (12, 999999), (16, 999999), (20, 999999)])
def test_database_rejects_unknown_version_or_outside_pointers(offset, value):
    sod, text = database()
    bad = bytearray(sod)
    struct.pack_into("<I", bad, offset, value)
    with pytest.raises(ValueError):
        ShopDatabase(bytes(bad), Locale(text))


def test_localization_rejects_duplicate_or_outside_index_without_scanning_unbounded():
    _, text = database()
    bad = bytearray(text)
    struct.pack_into("<I", bad, 40, 99999)
    with pytest.raises(ValueError):
        Locale(bytes(bad))
    with pytest.raises(ValueError):
        Binary(b"abcd").text(0)
    with pytest.raises(ValueError):
        Binary(b"abcd").words(0, 100001)
