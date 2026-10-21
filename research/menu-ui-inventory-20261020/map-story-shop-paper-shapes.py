"""Bounded source/geometry audit for ten requested paper-panel groups.

Reads only the listed screens .big resources and emits identities, hashes,
decoded geometry and UV coordinates. It does not export or inspect image bytes.
"""
from pathlib import Path
import contextlib, csv, hashlib, io, json, re, runpy, struct

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
DATA = Path('/Users/vlad/Code/defjam-data')
with contextlib.redirect_stdout(io.StringIO()):
    d = runpy.run_path(str(REPO / 'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
h, apt, outer = d['hd_assets'], d['apt'], d['outer']
rows = list(csv.DictReader((REPO / 'logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open()))

TARGETS = [
    ('story/barber', 'screens/story/barber.big', 'barber.xsh', [113, 111]),
    ('story/clothing', 'screens/story/clothing.big', 'clothing.xsh', [144, 141]),
    ('story/jeweller', 'screens/story/jeweller.big', 'jeweller.xsh', [135, 132]),
    ('story/wardrobe', 'screens/story/wardrobe.big', 'wardrobe.xsh', [109, 106]),
    ('story/chooseStyle', 'screens/story/chooseStyle.big', 'chooseStyle.xsh', [4, 2]),
    ('memoryCard/saveWarn', 'screens/memoryCard/saveWarn.big', 'saveWarn.xsh', [4, 5]),
    ('memoryCard/memWarn', 'screens/memoryCard/memWarn.big', 'memWarn.xsh', [3, 4]),
    ('options/conSetup', 'screens/options/conSetup.big', 'conSetup.xsh', [1]),
    ('story/tattoo', 'screens/story/tattoo.big', 'tattoo.xsh', [173, 171]),
    ('story/trophies', 'screens/story/trophies.big', 'trophies.xsh', [4, 2]),
]

def object_info(obj):
    data, symbols, rels, _ = d['object_info'](obj)
    return data, symbols, rels

def part_record(data, symbols, rels, apt_data, chars, shape, part):
    rm_name = f'__RM:::__GP_RM_{shape}_{part}'
    sym = symbols[rm_name]
    tex_symbol = rels.get(sym['offset'] + 0x48, '')
    image = int(re.search(r'SHAPENAME=(\d+),', tex_symbol).group(1))
    model = symbols[f'__Model:::{shape}']
    scale = struct.unpack_from('<4f', data, model['offset'] + 92)
    matrix_offset = struct.unpack_from('<I', data, sym['offset'] + 0x58)[0]
    matrix = struct.unpack_from('<16f', data, matrix_offset)
    vb = symbols[f'__VB:::__GPvb_9_{part}_{shape}']
    _, byte_count, stride, _, vertex_offset = struct.unpack_from('<5I', data, vb['offset'])
    encoded = [struct.unpack_from('<3h', data, vertex_offset + i * stride)
               for i in range(byte_count // stride)]
    pos = [tuple((q[j] + 16384) * scale[j] / 16384 for j in range(3)) for q in encoded]
    uv = [(p[0] * matrix[0] + p[1] * matrix[4] + matrix[12],
           p[0] * matrix[1] + p[1] * matrix[5] + matrix[13]) for p in pos]
    source_path = f'screens/screens.viv::{next(t[1] for t in TARGETS if t[1] == active_entry)}::{active_xsh}'
    candidates = [r for r in rows if r['source'] == source_path and r['name'].strip() == str(image)]
    alias = candidates[0] if candidates else None
    return {'part': part, 'image_name': image, 'texture_symbol': tex_symbol,
            'source_id': alias['id'] if alias else None,
            'alias_source': alias['source'] if alias else None,
            'alias_index': int(alias['index']) if alias else None,
            'alias_name': alias['name'].strip() if alias else None,
            'canvas': [int(alias['width']), int(alias['height'])] if alias else None,
            'matrix': list(matrix), 'encoded_xyz': [list(q) for q in encoded],
            'geometry_vertices': [list(p) for p in pos], 'uv_vertices': [list(p) for p in uv]}

output = {'schema': 1, 'method': 'Bounded per-resource APT/object symbol and packed-vertex mapping; source hashes only; no image bytes.', 'groups': []}
for label, entry, xsh, target_names in TARGETS:
    active_entry, active_xsh = entry, xsh
    nested = dict(h.archive_entries(h.unpack_refpack(outer[entry])))
    obj = nested[Path(entry).stem + '.o']
    apt_data, _, _, chars, _ = apt.load_movie('screens/screens.viv', entry)
    data, symbols, rels = object_info(obj)
    mats = {}
    for symbol_name, symbol in symbols.items():
        match = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', symbol_name)
        if not match:
            continue
        shape, part = map(int, match.groups())
        tex = rels.get(symbol['offset'] + 0x48, '')
        image_match = re.search(r'SHAPENAME=(\d+),', tex)
        if image_match:
            mats.setdefault(shape, {})[part] = int(image_match.group(1))
    target_shapes = sorted(s for s, parts in mats.items() if set(parts.values()) & set(target_names))
    assert target_shapes, (entry, target_names)
    shape_records = []
    for shape in target_shapes:
        shape_bounds = list(struct.unpack_from('<4f', apt_data, chars[shape]['offset'] + 8))
        parts = [part_record(data, symbols, rels, apt_data, chars, shape, part)
                 for part in sorted(mats[shape])]
        assert set(target_names).intersection(p['image_name'] for p in parts)
        non_geometry_symbols = []
        for name, symbol in symbols.items():
            match = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', name)
            if match and int(match[1]) == shape and int(match[2]) not in mats[shape]:
                non_geometry_symbols.append({'part': int(match[2]), 'texture_symbol': rels.get(symbol['offset'] + 0x48, ''),
                                             'reason': 'no __VB:::__GPvb_9_<part>_<shape> vertex buffer'})
        shape_records.append({'shape': shape, 'apt_bounds': shape_bounds, 'parts': parts,
                              'non_geometry_symbols': non_geometry_symbols})
    output['groups'].append({'label': label, 'entry': entry, 'object_sha256': hashlib.sha256(obj).hexdigest(),
                             'apt_sha256': hashlib.sha256(apt_data).hexdigest(),
                             'requested_images': target_names, 'matched_shapes': shape_records})

out = REPO / 'logs/ui-restoration-20261020/story-shop-paper-shapes.json'
out.write_text(json.dumps(output, indent=2) + '\n')
print(out)
for group in output['groups']:
    print(group['label'], [(s['shape'], [(p['part'], p['image_name'], p['source_id']) for p in s['parts']])
                           for s in group['matched_shapes']])
