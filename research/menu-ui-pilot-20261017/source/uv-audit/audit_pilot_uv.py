#!/usr/bin/env python3
"""Read two source resource objects and emit coordinates/identities only, no assets.

This scratch investigation script is local. Geometry decoding is inferred from
its scale vectors and independently checked against APT/ELF bounding boxes.
"""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
sys.path.insert(0, str(REPO / 'scripts'))
import hd_assets
spec = importlib.util.spec_from_file_location('apt_dump', '/Users/vlad/Code/DefJamFFNY-recomp/scripts/apt-dump.py')
apt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apt)
os.environ['DEFJAM_DATA'] = '/Users/vlad/Code/defjam-data'
outer = dict(hd_assets.archive_entries(Path('/Users/vlad/Code/defjam-data/extracted/screens/screens.viv').read_bytes()))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def object_info(obj):
    assert obj[:6] == b'\x7fELF\x01\x01'
    shoff = struct.unpack_from('<I', obj, 32)[0]
    entsize, count, names_index = struct.unpack_from('<HHH', obj, 46)
    sections = [struct.unpack_from('<10I', obj, shoff + i * entsize) for i in range(count)]
    names_sec = sections[names_index]
    names = obj[names_sec[4]:names_sec[4] + names_sec[5]]
    sections_by_name = {names[s[0]:].split(b'\0')[0].decode(): s for s in sections}
    data_sec = sections_by_name['.data']
    data = obj[data_sec[4]:data_sec[4] + data_sec[5]]
    sym_sec = sections_by_name['.symtab']
    str_sec = sections[sym_sec[6]]
    strings = obj[str_sec[4]:str_sec[4] + str_sec[5]]
    symbols = []
    for pos in range(sym_sec[4], sym_sec[4] + sym_sec[5], 16):
        name, value, size, info, other, section = struct.unpack_from('<IIIBBH', obj, pos)
        symbols.append(dict(name=strings[name:].split(b'\0')[0].decode(), offset=value, size=size, section=section))
    rel_sec = sections_by_name['.rel.data']
    relocations = {}
    for pos in range(rel_sec[4], rel_sec[4] + rel_sec[5], 8):
        offset, info = struct.unpack_from('<II', obj, pos)
        relocations[offset] = symbols[info >> 8]['name']
    return data, {s['name']: s for s in symbols if s['name']}, relocations, data_sec[4]


results = []
for base, shape in [('prestart', 3), ('mainMenu', 6)]:
    inner = dict(hd_assets.archive_entries(hd_assets.unpack_refpack(outer['screens/intMain/' + base + '.big'])))
    obj = inner[base + '.o']
    data, symbols, rels, data_file_offset = object_info(obj)
    apt_data, consts, movie, chars, _ = apt.load_movie('screens/screens.viv', 'screens/intMain/' + base + '.big')
    shape_offset = chars[shape]['offset']
    apt_bounds = struct.unpack_from('<4f', apt_data, shape_offset + 8)
    bbox_offset = symbols['__BBOX:::' + str(shape)]['offset']
    bbox = struct.unpack_from('<6f', data, bbox_offset)
    model_offset = symbols['__Model:::' + str(shape)]['offset']
    scale2 = struct.unpack_from('<4f', data, model_offset + 92)
    scale4 = struct.unpack_from('<4f', data, model_offset + 76)
    output = dict(movie=base, shape=shape, apt_bounds=list(apt_bounds), bbox=list(bbox),
                  apt_shape_offset=shape_offset, data_section_file_offset=data_file_offset,
                  bbox_offset=bbox_offset, model_offset=model_offset, scale2=list(scale2),
                  scale4=list(scale4), object_sha256=digest(obj), apt_sha256=digest(apt_data), parts=[])
    for part in (0, 1):
        rm_name = f'__RM:::__GP_RM_{shape}_{part}'
        rm_offset = symbols[rm_name]['offset']
        texture_symbol = rels[rm_offset + 0x48]
        image = int(re.search(r'SHAPENAME=(\d+),', texture_symbol).group(1))
        matrix_offset = struct.unpack_from('<I', data, rm_offset + 0x58)[0]
        matrix = struct.unpack_from('<16f', data, matrix_offset)
        vb_name = f'__VB:::__GPvb_9_{part}_{shape}'
        vb_offset = symbols[vb_name]['offset']
        ptr, byte_count, stride, flags, vertex_offset = struct.unpack_from('<5I', data, vb_offset)
        assert byte_count == 24 and stride == 6
        encoded = [struct.unpack_from('<3h', data, vertex_offset + i * stride) for i in range(byte_count // stride)]
        inferred_positions = [tuple((q[j] + 16384) * scale2[j] / 16384 for j in range(3)) for q in encoded]
        inferred_uv_pixels = [(pos[0] + matrix[12], pos[1] + matrix[13]) for pos in inferred_positions]
        output['parts'].append(dict(part=part, image=image, material_symbol=rm_name, material_offset=rm_offset,
                                    texture_relocation_offset=rm_offset + 0x48, texture_symbol=texture_symbol,
                                    matrix_offset=matrix_offset, matrix=list(matrix), vertex_symbol=vb_name,
                                    vertex_descriptor_offset=vb_offset, vertex_data_offset=vertex_offset,
                                    byte_count=byte_count, stride=stride, encoded_xyz=encoded,
                                    inferred_positions=inferred_positions, inferred_uv_pixels=inferred_uv_pixels))
    assert output['parts'][0]['encoded_xyz'][2][0] == output['parts'][1]['encoded_xyz'][0][0] or base == 'mainMenu'
    assert list(apt_bounds) == [bbox[0], bbox[1], bbox[3], bbox[4]]
    results.append(output)
print(json.dumps(dict(schema=1, note='Coordinates and hashes only; compressed-vertex formula is inferred, see report.', results=results), indent=2))
