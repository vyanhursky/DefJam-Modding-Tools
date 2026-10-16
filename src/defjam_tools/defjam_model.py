#!/usr/bin/env python3
"""Read-only FFNY fighter static mesh conversion (own dump -> private GLB).

Supported EAGL ELF32 data resources only. No executable code, rig reconstruction,
game reimport, animation or material-shader emulation. Output MUST stay outside
the source tree. See docs/model-viewer.md for the measured layout and limits.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import struct

from PIL import Image
from .hd_assets import archive_entries, unpack_refpack, MAX_BLOB

VERSION = 1
FIGHTERS = {
    "trejo": ("Trejo", "V2IP_112A", "1900051b32443a33a745c088a08231d039d80c9eb96483f4b43456a2a3f68f24"),
    "blaze": ("Blaze", "V2IP_113A", "5c9b3229151c2853656113a8df7e3f91effdef5ae68c9bdd567e5a71bbe9c91a"),
    "nyne": ("Nyne", "V2IP_009A", "a25c4fdd4998993c94d18ad0f5169c7ad6e6b898c711482777303c7ba3a18517"),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ModelError(ValueError):
    pass


class ElfData:
    """Bounds-checked ELF32 REL reader. Local relocations are resolved explicitly."""
    def __init__(self, blob):
        self.blob = blob
        if len(blob) < 52 or len(blob) > MAX_BLOB or blob[:7] != b"\x7fELF\x01\x01\x01":
            raise ModelError("Expected bounded little-endian ELF32")
        h = struct.unpack_from("<HHIIIIIHHHHHH", blob, 16)
        if h[0] != 1 or h[1] != 8 or h[7] != 52 or h[10] != 40 or not 1 <= h[11] <= 32 or h[12] >= h[11]:
            raise ModelError("Unsupported ELF resource header")
        self.cut(blob, h[5], h[10] * h[11])
        sections = [struct.unpack_from("<10I", blob, h[5] + i * 40) for i in range(h[11])]
        names = self.cut(blob, sections[h[12]][4], sections[h[12]][5])
        self.sections = []
        for s in sections:
            self.sections.append(dict(name=self.string(names, s[0]), type=s[1], flags=s[2],
                                      data=self.cut(blob, s[4], s[5]), link=s[6], info=s[7], size=s[5], entsize=s[9]))
        if any(s["flags"] & 4 or s["name"] == ".text" for s in self.sections):
            raise ModelError("Executable sections are not model data")
        self.data_index = next(i for i, s in enumerate(self.sections) if s["name"] == ".data")
        self.data = self.sections[self.data_index]["data"]
        st = next(s for s in self.sections if s["type"] == 2)
        if st["entsize"] != 16 or st["size"] % 16 or st["link"] >= len(sections):
            raise ModelError("Invalid ELF symbol table")
        strings = self.sections[st["link"]]["data"]
        self.symbols = []
        for p in range(0, st["size"], 16):
            n, v, size, info, other, section = struct.unpack_from("<IIIBBH", st["data"], p)
            self.symbols.append(dict(name=self.string(strings, n), value=v, size=size, section=section))
        self.relocs = {}
        for s in self.sections:
            if s["type"] != 9:
                continue
            if s["info"] != self.data_index or s["entsize"] != 8 or s["size"] % 8:
                raise ModelError("Unsupported relocation target")
            for p in range(0, s["size"], 8):
                off, info = struct.unpack_from("<II", s["data"], p)
                if info & 255 != 2 or info >> 8 >= len(self.symbols) or off in self.relocs:
                    raise ModelError("Unsupported or duplicate relocation")
                self.u(off)
                self.relocs[off] = self.symbols[info >> 8]

    @staticmethod
    def cut(blob, off, size):
        if off < 0 or size < 0 or off + size > len(blob):
            raise ModelError("Resource range is outside its section")
        return blob[off:off + size]

    @staticmethod
    def string(blob, off):
        end = blob.find(b"\0", off)
        if off < 0 or off >= len(blob) or end < 0:
            raise ModelError("Invalid string offset")
        return blob[off:end].decode("ascii")

    def unpack(self, fmt, off):
        self.cut(self.data, off, struct.calcsize(fmt))
        return struct.unpack_from(fmt, self.data, off)

    def u(self, off):
        return self.unpack("<I", off)[0]

    def ptr(self, off):
        s = self.relocs.get(off)
        if not s or s["section"] != self.data_index:
            raise ModelError("Expected a relocated pointer into model data")
        dest = s["value"] + self.u(off)
        self.cut(self.data, dest, 1)
        return dest

    def symbol(self, prefix):
        found = [s for s in self.symbols if s["name"].startswith(prefix) and s["section"] == self.data_index]
        if len(found) != 1:
            raise ModelError("Expected one " + prefix + " resource")
        return found[0]["value"]


def normal_111110(word):
    def component(value, bits):
        sign = 1 << (bits - 1)
        return max(-1, ((value & (sign - 1)) - (value & sign)) / (sign - 1))
    n = [component(word, 11), component(word >> 11, 11), component(word >> 22, 10)]
    length = math.sqrt(sum(v * v for v in n))
    if length < .1:
        raise ModelError("Invalid packed source normal")
    return [v / length for v in n]


def triangles_from_strip(strip, count):
    """Degenerate joins still advance parity; reject unsupported restart markers."""
    if any(i < 0 or i >= count for i in strip):
        raise ModelError("Triangle strip index outside vertex stream")
    out = []
    for i in range(2, len(strip)):
        a, b, c = strip[i - 2:i + 1]
        if len({a, b, c}) < 3:
            continue
        out.extend((b, a, c) if i % 2 else (a, b, c))
    return out


def decode(blob, name, source_id):
    e = ElfData(blob)
    vb = {}
    rm = {}
    for s in e.symbols:
        m = re.match(r"__VB:::__GPvb_(\d+)_(\d+)_", s["name"])
        if m:
            vb.setdefault(int(m[2]), []).append((int(m[1]), s["value"]))
        m = re.match(r"__RM:::__GP_RM_.+_(\d+)$", s["name"])
        if m:
            rm[int(m[1])] = s["value"]
    if not rm or len(rm) > 1024:
        raise ModelError("No supported render mesh resources")
    model = e.symbol("__Model:::")
    group_count = e.u(model + 0x9c)
    if not 1 <= group_count <= 128:
        raise ModelError("Invalid material group count")
    names, table = e.ptr(model + 0xa0), e.ptr(model + 0xcc) + 4
    groups = {}
    for i in range(group_count):
        label = e.string(e.data, e.ptr(names + i * 4))
        n = e.u(table); table += 4
        if n > len(rm):
            raise ModelError("Invalid render group size")
        for j in range(n):
            p = e.ptr(table + j * 4) - 0x38
            number = next((k for k, v in rm.items() if v == p), None)
            if number is None or number in groups:
                raise ModelError("Unresolved/duplicate render group")
            groups[number] = label
        table += n * 4
    meshes, skipped = [], []
    for number, p in sorted(rm.items()):
        label = groups.get(number)
        if not label:
            raise ModelError("Render mesh has no material group")
        refs = [(off, s["name"]) for off, s in e.relocs.items() if p <= off < p + 0xe0]
        parent = e.relocs[p + 0x1c]["name"]
        if parent == "ParentRM_DJFXSparkle_Skin" or label == "Direction":
            skipped.append(dict(group=label, rm=number, reason="Point-sprite sparkle" if "Sparkle" in parent else "Untextured direction helper"))
            continue
        if parent not in ("ParentRM_IrradTexture_Skin", *("ParentRM_DJIrradTextureEnvmap_Skin" + str(i) for i in range(1, 5))):
            raise ModelError("Unsupported material shader: " + parent)
        state = next((s for _, s in refs if "SetPrimitiveType=" in s), "")
        # Some child render meshes inherit primitive state from their parent.
        if state and "PT_TRIANGLESTRIP" not in state:
            raise ModelError("Unsupported primitive topology")
        streams = sorted(vb[number])
        if len(streams) != 5:
            raise ModelError("Unsupported vertex stream count")
        arrays = []
        count = e.u(streams[0][1] + 4) // 12
        if not 3 <= count <= 65535:
            raise ModelError("Invalid vertex count")
        for (_, q), stride in zip(streams, (12, 8, 4, 4, 2)):
            size = e.u(q + 4)
            if e.u(q + 8) != stride or size < count * stride or size > count * stride + 2:
                raise ModelError("Unsupported vertex stream layout")
            arrays.append(e.ptr(q + 16))
            e.cut(e.data, arrays[-1], count * stride)
        positions = [list(e.unpack("<3f", arrays[0] + i * 12)) for i in range(count)]
        uv = [list(e.unpack("<2f", arrays[1] + i * 8)) for i in range(count)]
        normals = [normal_111110(e.u(arrays[3] + i * 4)) for i in range(count)]
        colors = [list(e.unpack("<4B", arrays[2] + i * 4)) for i in range(count)]
        # Locate index resources by the animation-buffer parameter, independent
        # of optional inherited state and shader constant parameter counts.
        animation = [off for off, s in refs if s == "__const MATRIX4:::EAGLAnimationBuffer"]
        if len(animation) != 1:
            raise ModelError("Expected one animation-buffer binding")
        at = animation[0]
        n, ip = e.u(at + 12), e.ptr(at + 16)
        if n > 1_000_000 or e.u(at + 4) != 1 or e.u(e.ptr(at + 8)) != n:
            raise ModelError("Unsupported index header")
        indices = triangles_from_strip(list(e.unpack("<" + str(n) + "H", ip)), count)
        for i in range(0, len(indices), 3):
            indices[i], indices[i + 1] = indices[i + 1], indices[i]
        if not indices or any(not math.isfinite(v) or abs(v) > 10000 for a in positions + uv for v in a):
            raise ModelError("Invalid mesh coordinates")
        # Source strips face clockwise relative to the stored normals. Reverse
        # once for glTF CCW; keep coordinates and top-left UV convention.
        meshes.append(dict(name=label + " / RM" + str(number), group=label, rm=number,
                           positions=positions, uv=uv, normals=normals, colors=colors,
                           indices=indices, transparent="_ALPHA" in label))
    all_pos = [p for m in meshes for p in m["positions"]]
    bounds = [[min(p[i] for p in all_pos) for i in range(3)], [max(p[i] for p in all_pos) for i in range(3)]]
    return dict(schema=1, decoder=VERSION, name=name, source_id=source_id, source_sha256=sha(blob),
                meshes=meshes, bounds=bounds, skipped=skipped,
                vertices=len(all_pos), triangles=sum(len(m["indices"]) // 3 for m in meshes),
                limitations=["Static source rest pose; no animation or rig export", "Unlit RGB reference; studio lighting is approximate",
                             "Game specular/irradiance shaders and sparkle effects are not reproduced"])


def make_glb(model, image, revision="original"):
    """Self-contained glTF2 for browser/Blender, retaining UV splits/materials."""
    with Image.open(io.BytesIO(image)) as im:
        out = io.BytesIO(); im.convert("RGBA").save(out, format="PNG"); png = out.getvalue()
    binary = bytearray()
    doc = dict(asset=dict(version="2.0", generator="DefJam static preview " + str(VERSION)),
               extensionsUsed=["KHR_materials_unlit"], scene=0, scenes=[dict(nodes=[])], nodes=[],
               meshes=[], materials=[], accessors=[], bufferViews=[], buffers=[],
               images=[], textures=[dict(source=0, sampler=0)],
               samplers=[dict(magFilter=9729, minFilter=9987, wrapS=33071, wrapT=33071)],
               extras=dict(source_id=model["source_id"], source_sha256=model["source_sha256"],
                           revision=revision, texture_input_sha256=sha(image), static_preview=True,
                           source_member=model.get("source_member", "synthetic"),
                           coordinate_units="Original game units; physical scale uncalibrated", limitations=model["limitations"]))
    def view(raw, target=None):
        binary.extend(b"\0" * (-len(binary) % 4)); at = len(binary); binary.extend(raw)
        v = dict(buffer=0, byteOffset=at, byteLength=len(raw))
        if target: v["target"] = target
        doc["bufferViews"].append(v)
        return len(doc["bufferViews"]) - 1
    def accessor(values, kind, fmt, component, dims, target):
        flat = [x for row in values for x in row] if dims > 1 else values
        a = dict(bufferView=view(struct.pack("<" + str(len(flat)) + fmt, *flat), target),
                 componentType=component, count=len(values), type=kind)
        if kind == "VEC3" and fmt == "f":
            a.update(min=[min(row[i] for row in values) for i in range(3)], max=[max(row[i] for row in values) for i in range(3)])
        doc["accessors"].append(a)
        return len(doc["accessors"]) - 1
    doc["images"].append(dict(bufferView=view(png), mimeType="image/png"))
    materials = {}
    for m in model["meshes"]:
        group = m["group"]
        if group not in materials:
            materials[group] = len(doc["materials"])
            doc["materials"].append(dict(name=group, pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=0, roughnessFactor=1),
                                         extensions=dict(KHR_materials_unlit={}), alphaMode="BLEND" if m["transparent"] else "OPAQUE",
                                         doubleSided=False))
        attrs = dict(POSITION=accessor(m["positions"], "VEC3", "f", 5126, 3, 34962),
                     NORMAL=accessor(m["normals"], "VEC3", "f", 5126, 3, 34962),
                     TEXCOORD_0=accessor(m["uv"], "VEC2", "f", 5126, 2, 34962))
        # Source vertex color is retained in the private decode, deliberately
        # excluded from the RGB review material until its shader role is proven.
        indices = accessor(m["indices"], "SCALAR", "H", 5123, 1, 34963)
        doc["meshes"].append(dict(name=m["name"], primitives=[dict(attributes=attrs, indices=indices, material=materials[group], mode=4)]))
        node = len(doc["nodes"])
        doc["nodes"].append(dict(name=m["name"], mesh=len(doc["meshes"]) - 1, extras=dict(group=group, rm=m["rm"])))
        doc["scenes"][0]["nodes"].append(node)
    binary.extend(b"\0" * (-len(binary) % 4))
    doc["buffers"] = [dict(byteLength=len(binary))]
    header = json.dumps(doc, separators=(",", ":"), allow_nan=False).encode()
    header += b" " * (-len(header) % 4)
    return (struct.pack("<III", 0x46546c67, 2, 28 + len(header) + len(binary)) +
            struct.pack("<II", len(header), 0x4e4f534a) + header +
            struct.pack("<II", len(binary), 0x004e4942) + binary)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--fighter", choices=FIGHTERS, default="trejo")
    args = ap.parse_args()
    from .paths import source_root
    source_tree = source_root()
    dest = (args.workspace / "models" / args.fighter).resolve()
    if dest.is_relative_to(source_tree):
        ap.error("Derived models must live outside the source tree")
    name, stem, ident = FIGHTERS[args.fighter]
    archive = (args.dump / "assets/v2ip.viv").read_bytes()
    matches = [raw for member, raw in archive_entries(archive) if member.lower() == (stem + ".o").lower()]
    if len(matches) != 1:
        raise ModelError("Fighter member not unique")
    raw = matches[0]
    if int.from_bytes(raw[:2], "big") & 0x3eff == 0x10fb: raw = unpack_refpack(raw)
    model = decode(raw, name, ident)
    model["source_member"] = "assets/v2ip.viv::" + stem + ".o"
    image = (args.corpus / "originals" / (ident + ".png")).read_bytes()
    glb = make_glb(model, image)
    dest.mkdir(parents=True, exist_ok=True)
    geometry = json.dumps(model, separators=(",", ":"), allow_nan=False).encode()
    receipt = {k: v for k, v in model.items() if k != "meshes"}
    receipt.update(geometry_sha256=sha(geometry), glb_sha256=sha(glb), groups=sorted({m["group"] for m in model["meshes"]}),
                   parts=len(model["meshes"]))
    # Receipt is published last. New incompatible exports require a new decoder
    # version; this CLI never changes archives, reviews or candidate files.
    (dest / "geometry.json").write_bytes(geometry)
    (dest / "model.glb").write_bytes(glb)
    (dest / "index.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(fighter=name, vertices=model["vertices"], triangles=model["triangles"],
                          parts=len(model["meshes"]), bounds=model["bounds"], path=str(dest)), indent=2))


if __name__ == "__main__": main()
