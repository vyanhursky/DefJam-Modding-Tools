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

VERSION = 2
FIGHTERS = {
    "redman": ("Redman", "V2IP_109A", "61ca4a5526f266aa676e52bff3ac615eff3bb85f8d32f6375e81cce2da374c6b"),
    "rollins": ("Henry Rollins", "V2IP_131A", "4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d"),
    "trejo": ("Trejo", "V2IP_112A", "1900051b32443a33a745c088a08231d039d80c9eb96483f4b43456a2a3f68f24"),
    "blaze": ("Blaze", "V2IP_113A", "5c9b3229151c2853656113a8df7e3f91effdef5ae68c9bdd567e5a71bbe9c91a"),
    "nyne": ("Nyne", "V2IP_009A", "a25c4fdd4998993c94d18ad0f5169c7ad6e6b898c711482777303c7ba3a18517"),
    'd-mob': ('D-Mob', 'V2IP_014A', '0463ab7e782b97c6de0232b2f3382e22769010e4ffccb6b4f651184382aa4969'),
    'sticky-fingaz': ('Sticky Fingaz', 'V2IP_114A', '3a81ec057bec2cbd5e853a670b102cb77111a9aef6ce88d10a8daefc3348f9a7'),
    'ludacris': ('Ludacris', 'V2IP_123A', '949af9177d65df1880bfadc753b63a9e35c3ec3594510134766ab86c2bf07476'),
    'ice-t': ('Ice-T', 'V2IP_132A', 'c967f154df41f21005d5432660f8b2f04dcbf13df4360cbc5b1ba088463867a9'),
    'crow': ('Crow', 'V2IP_126A', '250a7396a0e3d7ef8b45d09b5abdfe5e1b7eabd3ffe18dde018121f4a9a94713'),
    'sean-paul': ('Sean Paul', 'V2IP_125A', '7e73c842a6ad6b252e7762c4f58823011d1b35573855aa14f31ed0359da9d33b'),
    'crack': ('Crack', 'V2IP_106A', '6c14e433f615b6401295670c238b92e24994dd38ea37ab0ab7cc06c192f87f51'),
    'flava-flav': ('Flava Flav', 'V2IP_110A', 'f58429a6b89a6a31ec5038dc852d3e7dc029585cc06a2c329f49955d46345cc7'),
    'wc': ('WC', 'V2IP_303A', '26048b0205f6f35bc6716bbc5dfb37fe6543ccdec70be2d59e80269f641ca41f'),
    'warren-g': ('Warren G', 'V2IP_306A', '2eb0820cba3e88633bca5012077c74e7c16781ee6484f8a6871772ba2b0b5c83'),
    'freeway': ('Freeway', 'V2IP_301A', '0e3909a900505ab99904b464fe40d08496300b2c5cdd02251ddd2e6496a05b49'),
    'magic': ('Magic', 'V2IP_128A', 'abf06932e051feaeeff4bc4e9c5122067f4829465e629bae3b4194f3c6914146'),
    'bonecrusher': ('Bonecrusher', 'V2IP_111A', 'c0a248ffa6105d05980cee7e437f91567a3e4c6aaf9d1a420c053d2b80a489dd'),
    'bubba-sparxxx': ('Bubba Sparxxx', 'V2IP_107A', '5a973af22d60c16de7e13ba911bf9a7e9dcd4e932803eeab918fef4bdd0d5f42'),
    'capone': ('Capone', 'V2IP_105A', '8c8a131c7c9a0c4cb924aa3abdcb372f0ca1c5c872580c480f9a55a872f48d79'),
    'nore': ('N.O.R.E.', 'V2IP_104A', '28798df3dc3cedd0e3ddd17c55340e2545fae47be1019303538a4415c25e25db'),
    'mack-10': ('Mack 10', 'V2IP_117A', '4530b6dfa373113e81e35039755e9d061a9c8a75a5f72a853c9d590777c9a9b3'),
    'scarface': ('Scarface', 'V2IP_116A', '31ff1fe0325562b59bccba33c4108d5ccdd6c27ccd32bc74fc46e8bc71a3741e'),
    'elephant-man': ('Elephant Man', 'V2IP_127A', '9420e8b7ef3b7dc42c28b0a17d6370516d2042a41eb556855fb551cda4529eca'),
    'bless': ('Bless', 'V2IP_101A', 'd24f625333ec870323ec5b5a185684c69bfcb7e32ba47641fb69e22352956707'),
    'havoc': ('Havoc', 'V2IP_118A', '43c403d1fb85ae45808b51ae4288d7f07f73501b4e2954e831a70cb1f9f62ada'),
    'fam-lay': ('Fam-Lay', 'V2IP_120A', '947f1d84cd0fa57f5126b1f01240591f2e0aa49a198d3f4dfc349a1641fef42f'),
    'slick-rick': ('Slick Rick', 'V2IP_130A', 'a95a975591bad4fbcfbae8eb42f41915690d776d557f2f2704c732dca2eb1615'),
    'memphis-bleek': ('Memphis Bleek', 'V2IP_103A', '65cb1cc4a81fe427bb929837ca0e16dc1702e1fd0dbae698e6789272da0710d1'),
    'comp': ('Comp', 'V2IP_304A', '7a905ee4d0212c43ee603111d40ff26932c1e244e0d325a531dee9f93b00b77e'),
    'oe': ('O.E.', 'V2IP_308A', '93a5512f8fcbbfcc417d352c07cde196c42039ec38e24847dcb650962e15bf3d'),
    'crazy-legs': ('Crazy Legs', 'V2IP_121A', '75ff0e46b2f0558f74c5f5bf0eaa5bc56d926a8e2d9caf52082a611c837894fe'),
    'erick-sermon': ('Erick Sermon', 'V2IP_102A', '54eec9f0ddb8a147d6a1474a9e6aa2f97df4bb3396f68485a92d497d5297f436'),
    'trick': ('Trick', 'V2IP_013A', '12c1fcf2ac0b8f6abdcbcc91676e068c12e7247ef53d76de3fa075b0f77b1c26'),
    'skull': ('Skull', 'V2IP_018A', 'd8c60b8e0549510641a705daef5b7c4b904bad670db04d8862c640bf091e5ca2'),
    'solo': ('Solo', 'V2IP_011A', 'a7338171f0627969a8b73264682ff2294508c4eea7705beeffd0b921ed0fd5d1'),
    'chiang': ('Chiang', 'V2IP_006A', 'f3460794f3fa9bf3b33f3722be4907845a80034946a533e98df9c4242b1d782e'),
    'masa': ('Masa', 'V2IP_005A', 'cdfd7978607c31a38d4761390a57462e031c509aa5f04d2555f14e51817b97cd'),
    'baxter': ('Baxter', 'V2IP_015A', 'fdaa8f07bf7596c66a5a73d5e6f6adc4289caebb2d99103185e1f123617e040e'),
    'rome': ('Rome', 'V2IP_010A', 'cd4ff188371a50644224a4cba0f7ae310c1e8a561a4eae82d0f8b365226640a6'),
    'snowman': ('Snowman', 'V2IP_002A', 'dd29023eebaab22449199a521ec09d11071e7675f4e35dc25129726cc45366cb'),
    'stingray': ('Stingray', 'V2IP_016A', 'bbafd1c4bafcc37407973f5891815a3f12126d89e8ccc1fe73c936506af07e0a'),
    'pockets': ('Pockets', 'V2IP_001A', '61a41808040bafc000925d2404d1b55b28cd027ba012515e31fd93a3ad5d825d'),
    'starks': ('Starks', 'V2IP_203A', '936b7b65f2ecb08346302b6dcab16c3db1d48ab673bdae22d4efe128b937d50c'),
    'jacob': ('Jacob', 'V2IP_129A', 'c26a16a8374d050a8a091f1df8000a19df3775cfa73fbd4d21a885b3861873de'),
    'cruz': ('Cruz', 'V2IP_007A', 'ed4a82ec39715339682b716a869da76185ff2c93542776cf88ccff153e0e5cc4'),
    'meca': ('Meca', 'V2IP_201A', '80583d125d979983f258c5e30d16f463abfe0b10cb497219d8f348d32b8ae08e'),
    'kimora': ('Kimora', 'V2IP_407A', '0c233032698b57f1455149737e01551ee87b2625f487313af2815cce9c1e80de'),
    'shawnna': ('Shawnna', 'V2IP_406A', 'fb0cd2babfc0dbed20604db7587e22f51471a2e44ff0987fdc1a1b4c43d2563a'),
    'cindy-j': ('Cindy J', 'V2IP_403A', 'ce13dde34046b73540217690840b80a7ba6fd901bbdec3a928ef7b58f3b23659'),
    'carmen-electra': ('Carmen Electra', 'V2IP_401A', '12c99396e3f3b286292af53ae56869a27b5bc1ce562b2adffd31273596dbea11'),
    'lauren': ('Lauren', 'V2IP_405A', '598868911b428ea846e0f6fc6ce3d6eb4a0cf94004307f2484498620a4c49373'),
    'teck': ('Teck', 'V2IP_305A', 'da8db4a6a832e85d22b1b2f6017136f8176c9544d558e7392a8bd8125d7100bc'),
    'dan-g': ('Dan-G', 'V2IP_004A', '4ad1c317e29b8e13ec983e93b0a6caa6ad64852c5825dafd9a3a50035ec75544'),
    'chris': ('Baby Chris', 'V2IP_122A', 'c22970480d8e2e06c6400b47207a38613cb5e134e17f54574bb671975ef93a38'),
    'ghostface': ('Ghostface Killah', 'V2IP_108A', '1db2188a2573b0fc6163e90760e24dab2d1f9c55708bd8bcdd8d64e7316c6574'),
    'joe-budden': ('Joe Budden', 'V2IP_302A', '7757c9bd6b5c016e226836b62f2e0aaa02e64ec49a108864c58fd65ede498f44'),
    'jervis': ('Jervis', 'V2IP_202A', 'b4f1087429773408acdc7daef6c90659b401aafcbcf3300d5c99801f7343505b'),
    'lil-kim': ('Lil Kim', 'V2IP_404A', '44d7b4fc03d64580146c9f45393044cd400d28efa4bbf2c08ff8acc5ccfef336'),
    'manny': ('Manny', 'V2IP_008A', 'd7d3dff45cc77f6efc0fb2690f72e3d5634ac574abb7498c875707b1a7ec7682'),
    'prodigy': ('Prodigy', 'V2IP_119A', '3a5c8f7b441aa4e23018a341ae05049f124c0ecabe0cdaaca286f0702b472253'),
    'd-mob-b': ('D-Mob — Costume B', 'V2IP_014B', '7dfa2af4c0005258aeefcff3ef52427b8906d511b9858c5f2bbf48ede7ab5f2a'),
    'd-mob-c': ('D-Mob — Costume C', 'V2IP_014C', 'e25435681ff9a692bf052051fd1bc04de5dbb07cf88d0ad299db0a3f9b0bff42'),
    'blaze-b': ('Blaze — Costume B', 'V2IP_113B', 'df031556e345c259b1d1c0ce054a04eda28fc96b356e849c3af3cd116236e52b'),
    'sticky-fingaz-b': ('Sticky Fingaz — Costume B', 'V2IP_114B', '7a0450588f199e1d379890739bbaafae99d00e20210d62883a4809a516dcfd58'),
    'house': ('House', 'V2IP_003A', '93256b656fae07299bd850194894daa21b6dfe2fea12a06bbc0f183c93395bfb'),
    'bo': ('Bo', 'V2IP_012A', '219a7ab28c2db0e729c73fe94292ebce24df12352687a099334ea3055f9726b0'),
    'lil-flip': ('Lil Flip', 'V2IP_307A', '0f8ff17c1df8fa85c4f5a0ba66d1351cb2a489aa27cbf80ed88a136cde459a6f'),
    'david-banner': ('David Banner', 'V2IP_124A', 'b01045e0decbb534592cc6378412496742b00f2ae135e31b35763b3fbf793ef0'),
    'xzibit': ('Xzibit', 'V2IP_115A', '93a8060dcf706b6328f124a58073c335313ba022bbdc9047f7a1596bf95b6d25'),
    'santos': ('Santos', 'V2IP_204A', '17f6a830532cc2e3346b6f76b1d828a63070c2c8a850fef8bd47a15c5e9668fa'),
    'suspect': ('Suspect / Shadowy Figure', 'V2IP_501A', '9910286b7f5203dd4e027f9070425a05d0abfa76eb4fa67714bf0d56a2cd43d6'),
    'blaze-c': ('Blaze — Story injury state C', 'V2IP_113C', '2ea9a0b3e28beed974042c06ae30fb478e759bd1a736e92690205f1f953e3075'),
    'carmen-electra-b': ('Carmen Electra — State B', 'V2IP_401B', '1916eac6bcb3a1fcc183ba0be464bf385275543dcab889eb2ae7512809433d08'),
    'd-mob-d': ('D-Mob — Story injury state D', 'V2IP_014D', '0c65cd13d0cdf44b9c4b1af78f884629eb93a5696a1fd4eea0601674646199b2'),
    'magic-b': ('Magic — Story injury state B', 'V2IP_128B', '445272fe820b0249e0bb20b156209db92bb1eeca2d5ba774d5f695bba19ef94c'),
}

# Only these static resources live in a nested cinematic archive. Existing
# gameplay source routes and decoder semantics remain unchanged.
MODEL_ARCHIVES = {
    "d-mob-d": ("assets/v2ip_cin.viv", "assets/V2IP_014D.viv"),
    "magic-b": ("assets/v2ip_cin.viv", "assets/V2IP_128B.viv"),
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


def index_stream(e, at, vertex_count, first_vertex_array):
    """Read the two audited strip layouts after an animation-buffer binding.

    Long layout: one draw-count entry, total indices, index pointer.
    Direct layout: index count/pointer, followed immediately by vertex fields.
    Verify those vertex fields to reject arbitrary or multi-draw layouts rather
    than interpreting unknown parameter bytes as index data.
    """
    tag=e.u(at+4)
    if tag==1:
        n,ip=e.u(at+12),e.ptr(at+16)
        if e.u(e.ptr(at+8))!=n:
            raise ModelError("Unsupported index header")
    else:
        n,ip=tag,e.ptr(at+8)
        if e.u(at+12)!=vertex_count or e.ptr(at+16)!=first_vertex_array:
            raise ModelError("Unsupported direct index header")
    if not 3<=n<=1_000_000:
        raise ModelError("Invalid index count")
    return list(e.unpack("<"+str(n)+"H",ip))


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
        textures={match[1] for _,ref in refs
                  if (match:=re.search(r"^__EAGL::TAR:::.*;SHAPENAME=([^;]+);",ref))}
        if label=="tape" and textures=={"tape,1"}:
            skipped.append(dict(group=label,rm=number,texture_ref="tape,1",
                                reason="External shared tape texture; omitted from primary-atlas preview, game use unverified"))
            continue
        if label=="tape" and textures=={"A406,1"}:
            skipped.append(dict(group=label,rm=number,texture_ref="A406,1",
                                reason="Audited Shawnna mouth-tape auxiliary mesh; UV/shader use unresolved, omitted from static preview"))
            continue
        if len(textures)>1:
            raise ModelError("Ambiguous primary texture binding")
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
        indices = triangles_from_strip(index_stream(e, at, count, arrays[0]), count)
        for i in range(0, len(indices), 3):
            indices[i], indices[i + 1] = indices[i + 1], indices[i]
        if not indices or any(not math.isfinite(v) or abs(v) > 10000 for a in positions + uv for v in a):
            raise ModelError("Invalid mesh coordinates")
        # Source strips face clockwise relative to the stored normals. Reverse
        # once for glTF CCW; keep coordinates and top-left UV convention.
        meshes.append(dict(name=label + " / RM" + str(number), group=label, rm=number,
                           positions=positions, uv=uv, normals=normals, colors=colors,
                           indices=indices, transparent="_ALPHA" in label or any("ABM_BLEND" in ref for _,ref in refs)))
        if textures:meshes[-1]['texture_ref']=next(iter(textures))
    all_pos = [p for m in meshes for p in m["positions"]]
    if not all_pos:raise ModelError("No retained primary-atlas meshes")
    bounds = [[min(p[i] for p in all_pos) for i in range(3)], [max(p[i] for p in all_pos) for i in range(3)]]
    return dict(schema=1, decoder=VERSION, name=name, source_id=source_id, source_sha256=sha(blob),
                meshes=meshes, bounds=bounds, skipped=skipped,
                vertices=len(all_pos), triangles=sum(len(m["indices"]) // 3 for m in meshes),
                limitations=["Static source rest pose; no animation or rig export", "Unlit RGB reference; studio lighting is approximate",
                             "Game specular/irradiance shaders and sparkle effects are not reproduced"]+
                            (["External shared tape mesh is omitted; its game appearance cannot be reviewed here"]
                             if any(s.get('texture_ref')=='tape,1' for s in skipped) else [])+
                            (["Shawnna mouth-tape auxiliary mesh is omitted; primary texture is retained, runtime mouth effect unverified"]
                             if any(s.get('texture_ref')=='A406,1' for s in skipped) else []))


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


def source_model(dump, fighter):
    """Read exactly one registered own-dump model, including nested Story VIVs."""
    _, stem, _ = FIGHTERS[fighter]
    route = MODEL_ARCHIVES.get(fighter, ("assets/v2ip.viv",))
    raw = (Path(dump) / route[0]).read_bytes()
    source = route[0]
    for member in (*route[1:], stem + ".o"):
        matches = [blob for name, blob in archive_entries(raw)
                   if name.casefold() == member.casefold()]
        if len(matches) != 1:
            raise ModelError("Fighter member not unique: " + member)
        raw = matches[0]
        if int.from_bytes(raw[:2], "big") & 0x3eff == 0x10fb:
            raw = unpack_refpack(raw)
        source += "::" + member
    return raw, source


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
    raw, source_member = source_model(args.dump, args.fighter)
    model = decode(raw, name, ident)
    model["source_member"] = source_member
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
