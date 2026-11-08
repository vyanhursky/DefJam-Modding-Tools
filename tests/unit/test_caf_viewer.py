"""Synthetic CAF composition, source identity, morph and isolated-state tests."""
import copy
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import pytest
from PIL import Image

from defjam_tools import caf_assets as a, caf_viewer as v
from defjam_tools.texture_workshop import Conflict, Invalid


def png(color, size=(2, 2)):
    out = io.BytesIO()
    Image.new("RGBA", size, color).save(out, format="PNG")
    return out.getvalue()


def morph_fixture(semantic=b"Coordinates", count=4, flags=0xc0000000, offset=0, with_colors=False):
    data = bytearray(0x100)
    data[0:len(semantic) + 1] = semantic + b"\0"
    struct.pack_into("<I", data, 0x30, 1)
    struct.pack_into("<4I", data, 0x34, 0, 1, 0, 1)
    struct.pack_into("<4I", data, 0x44, flags | 48, count, offset, 0)
    struct.pack_into("<12f", data, 0x54, *([1, 2, 3] * 4))
    relocs = [(0x34, 2)]
    if with_colors:
        struct.pack_into("<I", data, 0x30, 2)
        data[0xe0:0xe8] = b"Colours\0"
        struct.pack_into("<8I", data, 0x84, 0xe0, 1, 0, 1, 0x10000010, 4, 0, 0)
        relocs.append((0x84, 2))
    names = b"\0.data\0.shstrtab\0.strtab\0.symtab\0.rel.data\0"
    strings = b"\0__Morph:::synthetic\0"
    symbols = struct.pack("<IIIBBH", 0, 0, 0, 0, 0, 1) + struct.pack("<IIIBBH", 1, 0x20, 4, 17, 0, 1)
    payloads = [b"", data, names, strings, symbols, b"".join(struct.pack("<2I", *r) for r in relocs)]
    blob = bytearray(52)
    sections = []
    for i, raw in enumerate(payloads):
        pos = len(blob)
        blob.extend(raw)
        label = ("", ".data", ".shstrtab", ".strtab", ".symtab", ".rel.data")[i].encode()
        sections.append((names.index(label) if i else 0, (0, 1, 3, 3, 2, 9)[i], 0, 0,
                         pos, len(raw), 3 if i == 4 else 4 if i == 5 else 0, 1 if i == 5 else 0,
                         4, 16 if i == 4 else 8 if i == 5 else 0))
    shoff = len(blob)
    for section in sections:
        blob.extend(struct.pack("<10I", *section))
    blob[:16] = b"\x7fELF\x01\x01\x01" + b"\0" * 9
    struct.pack_into("<HHIIIIIHHHHHH", blob, 16, 1, 8, 1, 0, 0, shoff, 0, 52, 0, 0, 40, 6, 2)
    return bytes(blob)


def model():
    return dict(meshes=[dict(rm=0, group="cloth", positions=[[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
                            normals=[[0, 0, 1]] * 4, uv=[[0, 0], [1, 0], [0, 1], [1, 1]],
                            indices=[0, 1, 2, 2, 1, 3], transparent=False, texture_ref="cp_a,1")],
                bounds=[[0, 0, 0], [1, 1, 0]], skipped=[])


def attachment_fixture(text="a,b,0,0,0", origin=(1, 2)):
    blob = bytearray(24)
    struct.pack_into("<4s3I", blob, 0, b"SHPX", 0, 1, 0)
    struct.pack_into("<4sI", blob, 16, b"0000", 24)
    blob.extend(struct.pack("<I2H2I", (32 << 8) | 0x7d, 2, 2, 0, 0))
    blob.extend(bytes([20, 40, 60, 255] * 4))
    blob.extend(struct.pack("<II2i", (16 << 8) | 0x7c, 1, *origin))
    raw = text.encode() + b"\0"
    blob.extend(struct.pack("<II", 0x6f, len(raw)) + raw)
    struct.pack_into("<I", blob, 4, len(blob))
    return bytes(blob)


def test_fsh_attachments_recover_exact_canvas_origin_and_copy_mode():
    blob = attachment_fixture("c,c,1,36,2", (96, 128))
    record = dict(offset=24, width=2, height=2)
    assert a.placement(blob, record) == dict(atlas="c", mode="c", origin=[96, 128],
                                            parameters=[1, 36, 2], text="c,c,1,36,2")
    assert a.placement(attachment_fixture("d,b"), record)["parameters"] == [0, 0, 0]
    for raw in (attachment_fixture("x,b"), attachment_fixture(origin=(255, 255)), blob[:-5]):
        with pytest.raises(ValueError):
            a.placement(raw, record)


def test_xml_preserves_type_instructions_model_style_and_color_order():
    xml = b'''<partslist><?TypeBody = "Ubody"?><head>1.1.X</head><parts><contents>
    <model><name>PART_C</name><texture><name>TEX_A</name><colour><name>TEX_B</name></colour></texture></model>
    </contents></parts><?TypeNonGeometry = "Tattoo_Back"?><head>4.3.X</head><parts><contents>
    <model><name>NON_GEOM</name><texture><name>INK</name></texture></model></contents></parts></partslist>'''
    groups = a.parts_xml(xml)
    assert groups[0]["slot"] == "Ubody"
    assert groups[0]["items"][0]["styles"][0]["variants"] == ["TEX_A", "TEX_B"]
    assert groups[1]["section"] == "Tattoos"
    assert groups[1]["items"][0]["model"] == "NON_GEOM"
    with pytest.raises(ValueError):
        a.parts_xml(b'<!DOCTYPE x><partslist/>')


def test_morph_adds_exact_source_deltas_without_changing_uvs_or_original():
    original = model()
    changed = a.apply_morph(original, morph_fixture())
    assert original["meshes"][0]["positions"][0] == [0, 0, 0]
    assert changed["meshes"][0]["positions"][0] == pytest.approx([.9999, 1.9998, 2.9997])
    assert changed["meshes"][0]["uv"] == original["meshes"][0]["uv"]
    assert changed["meshes"][0]["normals"] == original["meshes"][0]["normals"]
    assert changed["bounds"][1] == pytest.approx([1.9999, 2.9998, 2.9997])


def test_retail_fit_remaps_do_not_collapse_necklace_or_neck_builds():
    for slot in ("14", "18", "21", "28"):
        assert [a.fit_build(slot, c) for c in "ABCDEF"] == list("AACCFF")
    for slot in ("3", "12", "13", "16", "17", "22", "23", "24"):
        assert [a.fit_build(slot, c) for c in "ABCDEF"] == list("ABCDEF")


def test_face_fits_apply_slot_four_to_face_for_all_builds_including_c():
    objects = {}
    for index in range(1, 4):
        raw = bytearray(morph_fixture())
        # First synthetic vertex in each shape has a different jaw offset.
        struct.pack_into("<3f", raw, 52 + 0x54, index, -index, index / 2)
        name = f"v2cp_53{index}_0001_c"
        objects[name] = (name + ".o", bytes(raw))
    original = model()
    variants = a.face_fits(original, objects)
    for index, pair in enumerate(("AB", "CD", "EF"), 1):
        for build in pair:
            assert variants[build]["meshes"][0]["positions"][0] == pytest.approx(
                [index * .9999, -index * .9999, index * .9999 / 2])
            assert variants[build]["meshes"][0]["uv"] == original["meshes"][0]["uv"]
            assert variants[build]["caf_face_fit"] == f"v2cp_53{index}_0001_c"
    assert original["meshes"][0]["positions"][0] == [0, 0, 0]
    del objects["v2cp_533_0001_c"]
    with pytest.raises(ValueError, match="Missing default CAF face fit"):
        a.face_fits(original, objects)


def test_color_morph_omission_does_not_discard_valid_geometry_shape():
    changed = a.apply_morph(model(), morph_fixture(with_colors=True))
    assert changed["meshes"][0]["positions"][0] == pytest.approx([.9999, 1.9998, 2.9997])
    assert changed["caf_omissions"] == ["Vertex-color shape changes omitted from texture RGB inspection"]


@pytest.mark.parametrize("blob", [morph_fixture(count=5), morph_fixture(semantic=b"Normals"),
                                 morph_fixture(flags=0x80000000), morph_fixture(offset=12), morph_fixture()[:100]])
def test_unknown_morph_layouts_are_rejected(blob):
    with pytest.raises(ValueError):
        a.apply_morph(model(), blob)


def test_alpha_encoded_tattoo_blends_rgb_and_keeps_material_alpha():
    canvas = Image.new("RGBA", (3, 1), (100, 150, 200, 40))
    ink = Image.new("RGBA", (3, 1))
    ink.putdata([(0, 0, 0, 0), (0, 0, 0, 128), (12, 20, 30, 255)])
    v.composite(canvas, ink, (0, 0), "b")
    assert [canvas.getpixel((x, 0)) for x in range(3)] == [(100, 150, 200, 40), (50, 74, 99, 128), (12, 20, 30, 255)]
    v.composite(canvas, Image.new("RGBA", (1, 1), (8, 9, 10, 0)), (1, 0), "c")
    assert canvas.getpixel((1, 0)) == (8, 9, 10, 0)
    with pytest.raises(Invalid):
        v.composite(canvas, ink, (2, 0), "c")


def test_resize_keeps_hidden_rgb_and_original_sampling_distinct_from_lanczos():
    image = Image.new("RGBA", (2, 2), (100, 70, 40, 0))
    image.putpixel((0, 0), (250, 10, 5, 128))
    linear = v.rgba_resize(image, (8, 8), Image.Resampling.BILINEAR)
    lanczos = v.rgba_resize(image, (8, 8))
    assert linear.tobytes() != lanczos.tobytes()
    assert linear.getpixel((7, 7)) == (100, 70, 40, 0)


@pytest.fixture
def viewer(tmp_path):
    corpus, work, cache = (tmp_path / n for n in ("corpus", "workshop", "cache"))
    for d in (corpus, work, cache):
        d.mkdir()
    ident, ink = "a" * 64, "b" * 64
    assets = []
    for index, asset_id in enumerate((ident, ink)):
        original = png((200, 20, 10, 255) if index == 0 else (0, 0, 0, 128))
        faithful = png((220, 50, 20, 255), (8, 8)) if index == 0 else png((0, 0, 0, 128), (8, 8))
        for suffix, raw in (("original", original), ("faithful", faithful)):
            (corpus / (asset_id + "-" + suffix + ".png")).write_bytes(raw)
        assets.append(dict(id=asset_id, source_id=asset_id, width=2, height=2,
                           original=asset_id + "-original.png", original_hash=v.sha(original),
                           upscaled=asset_id + "-faithful.png", upscaled_hash=v.sha(faithful)))
    (corpus / "corpus.json").write_text(json.dumps(dict(corpus_id="synthetic", assets=assets)))
    child = png((10, 200, 30, 255), (8, 8))
    (work / "candidate.png").write_bytes(child)
    (work / "workshop.json").write_text(json.dumps(dict(schema=1, corpus_id="synthetic", reviews={"preserve": "owner notes"},
        candidates={ident: [dict(id="r-one", label="Restored v1", path="candidate.png", sha256=v.sha(child))]})))
    geometry = json.dumps(model()).encode()
    (cache / "mesh.json").write_bytes(geometry)
    base = png((100, 150, 200, 255), (256, 256))
    (cache / "skin.png").write_bytes(base)
    item = dict(id="12:0", model="TOP_C", geometry="top_c", styles=[dict(variants=["CLOTH"])], limitation="")
    tattoo = dict(id="30:0", model="NON_GEOM", geometry=None, styles=[dict(variants=["INK"])], limitation="")
    def resource(name, asset, mode):
        return dict(name=name, records=[dict(name="0000", index=0, width=2, height=2, asset=asset,
            placement=dict(atlas="a", mode=mode, origin=[1, 1], parameters=[0, 0, 0]))])
    resources = dict(cloth=resource("CLOTH", ident, "c"), ink=resource("INK", ink, "b"))
    for letter in "abcdef":
        for atlas in "abcd":
            resources[f"v2cp_{atlas}_{letter}"] = dict(images={f"pl0{i}": dict(path="skin.png", sha256=v.sha(base)) for i in range(1, 9)}, records=[])
    data = dict(schema=1, decoder=1, corpus_id="synthetic", groups=[
        dict(id="12", slot="Ubody", label="Tops", kind="Body", stage=3, section="Clothing", items=[item]),
        dict(id="30", slot="Tattoo_Chest", label="Chest", kind="NonGeometry", stage=1, section="Tattoos", items=[tattoo])],
        resources=resources, geometry=dict(top_c={"C": dict(path="mesh.json", sha256=v.sha(geometry))}),
        builds=[dict(id=c, label=c) for c in "ABCDEF"], errors=[], limitations=[])
    (cache / "catalog.json").write_text(json.dumps(data))
    return v.CafViewer(cache, v.SourceReader(corpus, work), tmp_path / "inspection")


def test_scene_changes_only_compared_texture_and_obeys_clothes_over_tattoo_order(viewer):
    original_metadata = (viewer.reader.root / "workshop.json").read_bytes()
    outfit = viewer.default_outfit()
    outfit["slots"]["30"] = dict(item="30:0", style=0, color=0, palette="default")
    scene = viewer.scene(dict(outfit=outfit, compare=dict(asset="a" * 64, a="original", b="r-one"), scale=1))
    images = viewer.renders[scene["key"]]["images"]
    assert Image.open(io.BytesIO(images["aa.png"])).getpixel((1, 1)) == (200, 20, 10, 255)
    assert Image.open(io.BytesIO(images["ba.png"])).getpixel((1, 1)) == (10, 200, 30, 255)
    assert Image.open(io.BytesIO(images["ba.png"])).getpixel((5, 5)) == (100, 150, 200, 255)
    for atlas in "bcd":
        assert images["a" + atlas + ".png"] == images["b" + atlas + ".png"]
    assert scene["compared_on_model"]
    assert original_metadata == (viewer.reader.root / "workshop.json").read_bytes()
    assert not viewer.file.exists()


def test_revision_checksum_and_path_escape_fail_before_render(viewer):
    (viewer.reader.root / "candidate.png").write_bytes(png((1, 2, 3, 255)))
    with pytest.raises(Invalid, match="checksum"):
        viewer.scene(dict(outfit=viewer.default_outfit(), compare=dict(asset="a" * 64, a="original", b="r-one")))
    metadata = viewer.reader.root / "workshop.json"
    data = json.loads(metadata.read_text())
    data["candidates"]["a" * 64][0]["path"] = "../corpus/" + "a" * 64 + "-original.png"
    metadata.write_text(json.dumps(data))
    with pytest.raises(Invalid, match="leaves"):
        viewer.image("a" * 64, "r-one")


def test_palette_recolors_source_and_lanczos_without_recoloring_rgb_candidate(viewer):
    resource = viewer.catalog["resources"]["cloth"]
    resource.update(palettes=["pl01", "pl02"], palette_path="palette.xsh", sha256=v.sha(b"palette"))
    (viewer.root / "palette.xsh").write_bytes(b"palette")
    outfit = viewer.default_outfit()
    outfit["slots"]["12"]["palette"] = "pl02"
    with patch.object(v, "palette_images", return_value={"pl02": b"blue"}), patch.object(
            v, "with_palette", return_value=Image.new("RGBA", (2, 2), (0, 0, 255, 255))):
        for baseline in ("original", "faithful"):
            scene = viewer.scene(dict(outfit=outfit, compare=dict(asset="a" * 64, a=baseline, b="r-one"), scale=1))
            images = viewer.renders[scene["key"]]["images"]
            assert Image.open(io.BytesIO(images["aa.png"])).getpixel((1, 1)) == (0, 0, 255, 255)
            assert Image.open(io.BytesIO(images["ba.png"])).getpixel((1, 1)) == (10, 200, 30, 255)
            assert any("r-one keeps authored RGB" in notice for notice in scene["notices"])
    outfit["slots"]["12"]["palette"] = "pl99"
    with pytest.raises(Invalid, match="does not belong"):
        viewer.scene(dict(outfit=outfit, compare=dict(asset="a" * 64, a="r-one", b="r-one")))


def test_documented_batch_handoff_preflights_retries_and_preserves_inspection(viewer, tmp_path):
    # Execute the exact copy/paste script shipped in the agent guide.
    doc = (Path(__file__).parents[2] / "docs/caf-secondary-inspection-agent-handoff.md").read_text()
    script = doc.split("```python\n", 1)[1].split("```", 1)[0]
    ident, revision = "a" * 64, "r-0123456789abcdef"
    metadata = viewer.reader.root / "workshop.json"
    data = json.loads(metadata.read_text())
    candidate = data["candidates"][ident][0]
    candidate["id"] = revision
    metadata.write_text(json.dumps(data))
    preserved = metadata.read_bytes()
    handler = v.handler_for(viewer, "synthetic-token")

    class FirstConflict(handler):
        conflict = True

        def do_POST(self):
            if FirstConflict.conflict:
                FirstConflict.conflict = False
                self.reply(409, dict(error="Concurrent save"))
            else:
                super().do_POST()

    server = ThreadingHTTPServer(("127.0.0.1", 0), FirstConflict)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        file = tmp_path / "send-caf-batch.py"
        file.write_text(script.replace("http://127.0.0.1:8780", f"http://127.0.0.1:{server.server_port}"))
        manifest = tmp_path / "batch.json"
        batch = dict(batch="synthetic", corpus_id="synthetic", items=[dict(asset=ident, revision=revision, sha256=candidate["sha256"])])
        manifest.write_text(json.dumps(batch))
        def run(*args):
            return subprocess.run([sys.executable, str(file), str(manifest), *args], text=True, capture_output=True)
        dry = run()
        assert dry.returncode == 0, dry.stderr
        assert not json.loads(dry.stdout)["queued"]
        assert not viewer.file.exists()
        queued = run("--queue")
        assert queued.returncode == 0, queued.stderr
        receipt = json.loads(queued.stdout)
        entry = viewer.state["queue"][0]
        assert receipt["items"][0]["queue_id"] == entry["id"]
        assert entry["status"] == "pending"
        viewer.save(dict(action="inspection", version=viewer.state["version"], id=entry["id"], status="needs_work", notes="Preserve owner feedback"))
        repeated = run("--queue")
        assert repeated.returncode == 0, repeated.stderr
        assert len(viewer.state["queue"]) == 1
        assert viewer.state["queue"][0]["notes"] == "Preserve owner feedback"
        assert json.loads(repeated.stdout)["items"][0]["status"] == "needs_work"
        before = viewer.file.read_bytes()
        batch["items"][0]["sha256"] = "0" * 64
        manifest.write_text(json.dumps(batch))
        assert run("--queue").returncode != 0
        assert viewer.file.read_bytes() == before
        assert metadata.read_bytes() == preserved
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_queue_outfits_notes_conflicts_and_disk_failure_preserve_owner_data(viewer):
    original = (viewer.reader.root / "workshop.json").read_bytes()
    state = viewer.save(dict(version=0, action="queue", asset="a" * 64, revision="r-one"))
    entry = state["queue"][0]
    assert entry["sha256"] == v.sha((viewer.reader.root / "candidate.png").read_bytes())
    with pytest.raises(Conflict):
        viewer.save(dict(version=0, action="outfit", name="stale", outfit=viewer.default_outfit()))
    state = viewer.save(dict(version=1, action="inspection", id=entry["id"], status="needs_work", notes="Check lettering"))
    assert state["queue"][0]["notes"] == "Check lettering"
    before = viewer.file.read_bytes()
    with patch.object(v, "atomic_json", side_effect=OSError("disk full")), pytest.raises(OSError):
        viewer.save(dict(version=2, action="outfit", name="unsaved", outfit=viewer.default_outfit()))
    assert viewer.state["version"] == 2
    assert viewer.file.read_bytes() == before
    assert (viewer.reader.root / "workshop.json").read_bytes() == original
    reopened = v.CafViewer(viewer.root, viewer.reader, viewer.state_root)
    assert reopened.state == viewer.state


def test_part_color_and_revision_must_belong_to_outfit(viewer):
    outfit = viewer.default_outfit()
    outfit["slots"]["12"]["color"] = 1
    with pytest.raises(Invalid, match="style/color"):
        viewer.validate_outfit(outfit)
    outfit = viewer.default_outfit()
    outfit["revisions"]["b" * 64] = "r-one"
    with pytest.raises(Invalid, match="revision"):
        viewer.validate_outfit(outfit)
    with pytest.raises(Invalid, match="separate"):
        v.CafViewer(viewer.root, viewer.reader, viewer.reader.root)


def test_loopback_host_origin_auth_and_read_only_routes(viewer):
    server = ThreadingHTTPServer(("127.0.0.1", 0), v.handler_for(viewer, "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    try:
        with urlopen(base + "/api/caf/catalog") as response:
            assert json.load(response)["token"] == "test-token"
        for headers in ({"Host": "evil.example"},):
            with pytest.raises(HTTPError) as caught:
                urlopen(Request(base + "/api/caf/catalog", headers=headers))
            assert caught.value.code == 403
        for headers in ({}, {"X-Workshop-Token": "test-token", "Origin": "https://elsewhere.example"}):
            with pytest.raises(HTTPError) as caught:
                urlopen(Request(base + "/api/caf/state", data=b"{}", headers=headers))
            assert caught.value.code == 403
        with pytest.raises(HTTPError) as caught:
            urlopen(Request(base + "/api/caf/state", data=b'[]', headers={"X-Workshop-Token": "test-token"}))
        assert caught.value.code == 400
        for route in ("/api/export-review", "/workshop.json", "/api/caf/render/nope/../../workshop.json"):
            with pytest.raises(HTTPError):
                urlopen(base + route)
        with urlopen(base + "/caf-viewer.js") as response:
            assert b"/vendor/three.module.min.js" in response.read()
        with urlopen(base + "/caf-wardrobe.js") as response:
            assert b"export function findSelection" in response.read()
        assert not viewer.file.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
