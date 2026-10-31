"""Bounded source-only mapping for six candidate menu background resources.

Reads only the named .big entries, corresponding XSH aliases, APT/object
metadata, and approved-source ID ledger. Emits hashes/coordinates/alpha
statistics only; no pixel arrays or image files are written.
"""
from pathlib import Path
import contextlib, csv, hashlib, io, json, re, runpy, struct
from PIL import Image

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
DATA = Path('/Users/vlad/Code/defjam-data')
with contextlib.redirect_stdout(io.StringIO()):
    d = runpy.run_path(str(REPO / 'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
h, apt, outer = d['hd_assets'], d['apt'], d['outer']
ALIASES = list(csv.DictReader((REPO / 'logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open()))
BY_SOURCE = {}
BY_ID = {}
for row in ALIASES:
    row['name'] = row['name'].strip()
    row['index'] = int(row['index'])
    row['width'] = int(row['width'])
    row['height'] = int(row['height'])
    BY_SOURCE.setdefault(row['source'], {})[row['name']] = row
    BY_ID.setdefault(row['id'], []).append(row)
APPROVED = json.loads((REPO / 'config/menu-ui-approved-artwork.json').read_text())
REVIEWED = {x['source_id']: x for x in APPROVED['reviewed_sources']}

# The tournament candidates are the largest square source sheets in that
# bounded movie; companion materials are recovered from their complete shapes.
TARGETS = [
    ('story/choosGF2', 'screens/story/choosGF2.big', 'choosGF2.xsh', [16, 30]),
    ('story/choosGF4', 'screens/story/choosGF4.big', 'choosGF4.xsh', [2, 1]),
    ('story/choosPart', 'screens/story/choosPart.big', 'choosPart.xsh', [2, 1]),
    ('story/charDec', 'screens/story/charDec.big', 'charDec.xsh', [2, 1]),
    ('options/cribOptions', 'screens/options/cribOptions.big', 'cribOptions.xsh', [8, 4]),
    ('story/tournament', 'screens/story/tournament.big', 'tournament.xsh', [2, 5, 8]),
]

def object_info(obj):
    return d['object_info'](obj)[:3]

def bounds(points, count=2):
    return [min(p[i] for p in points) for i in range(count)] + [max(p[i] for p in points) for i in range(count)]

def source_identity(source, image):
    row = BY_SOURCE.get(source, {}).get(str(image))
    if row is None:
        return None
    covered = REVIEWED.get(row['id'])
    return {'source_id': row['id'], 'alias_source': row['source'], 'alias_index': row['index'],
            'alias_name': row['name'], 'canvas': [row['width'], row['height']],
            'alpha_extrema_inventory': json.loads(row['alpha']),
            'reviewed_136_status': covered['status'] if covered else 'not in 136 reviewed source IDs',
            'reviewed_family': covered.get('family') if covered else None,
            'reviewed_aliases': covered.get('aliases', []) if covered else [],
            'same_id_aliases': [{'source': x['source'], 'index': x['index'], 'name': x['name'],
                                 'canvas': [x['width'], x['height']]} for x in BY_ID[row['id']]]}

def alpha_metadata(image):
    alpha = image.getchannel('A')
    hist = alpha.histogram()
    return {'alpha_bbox': list(alpha.getbbox()) if alpha.getbbox() else None,
            'alpha_extrema': list(alpha.getextrema()),
            'alpha_counts': {'zero': hist[0], 'partial': sum(hist[1:255]), 'opaque': hist[255]}}

output = {'schema': 1,
          'method': 'Bounded per-resource APT/object and SHPX mapping; coordinates, hashes, source IDs and alpha statistics only; no image bytes written.',
          'review_ledger': {'path': 'config/menu-ui-approved-artwork.json', 'source_id_count': len(REVIEWED)},
          'limits': ['APT stage size is reported, but root timeline use, active frame, and parent transforms are not resolved here.',
                     'Target selection is limited to the named wall/background image names in TARGETS; no claim that all menu backgrounds are inventoried.'],
          'resources': []}
assert len(REVIEWED) == 136
for label, entry, xsh, target_names in TARGETS:
    stem = Path(entry).stem
    members = dict(h.archive_entries(h.unpack_refpack(outer[entry])))
    obj, xsh_bytes = members[stem + '.o'], members[stem + '.xsh']
    apt_data, _, movie, chars, _ = apt.load_movie('screens/screens.viv', entry)
    data, symbols, relocs = object_info(obj)
    source = f'screens/screens.viv::{entry}::{xsh}'
    materials = {}
    for symbol_name, symbol in symbols.items():
        match = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', symbol_name)
        if not match:
            continue
        shape, part = map(int, match.groups())
        tex = relocs.get(symbol['offset'] + 0x48, '')
        image_match = re.search(r'SHAPENAME=(\d+),', tex)
        if image_match:
            materials.setdefault(shape, {})[part] = int(image_match[1])
    matched_shapes = sorted(shape for shape, parts in materials.items()
                            if set(parts.values()) & set(target_names))
    assert matched_shapes, (entry, target_names)
    shape_image_names = sorted({image for shape in matched_shapes for image in materials[shape].values()})
    alias_rows = [BY_SOURCE[source][str(name)] for name in shape_image_names if str(name) in BY_SOURCE.get(source, {})]
    decoded = {record['index']: (record, image) for record, image in
               h.shpx_images(xsh_bytes, indices={row['index'] for row in alias_rows})}
    assets = {}
    for name in shape_image_names:
        identity = source_identity(source, name)
        if not identity:
            assets[str(name)] = {'image_name': name, 'identity_missing_from_alias_csv': True}
            continue
        record, image = decoded[identity['alias_index']]
        assets[str(name)] = {'image_name': name, **identity, 'shpx_record': record,
                             'decoded_alpha': alpha_metadata(image)}
    shape_records = []
    for shape in matched_shapes:
        parts = []
        for part, image_name in sorted(materials[shape].items()):
            rm = symbols[f'__RM:::__GP_RM_{shape}_{part}']['offset']
            matrix_offset = struct.unpack_from('<I', data, rm + 0x58)[0]
            matrix = struct.unpack_from('<16f', data, matrix_offset)
            scale = struct.unpack_from('<4f', data, symbols[f'__Model:::{shape}']['offset'] + 92)
            vb = symbols[f'__VB:::__GPvb_9_{part}_{shape}']['offset']
            _, byte_count, stride, _, vertex_offset = struct.unpack_from('<5I', data, vb)
            enc = [struct.unpack_from('<3h', data, vertex_offset + i * stride)
                   for i in range(byte_count // stride)]
            xyz = [[(q[j] + 16384) * scale[j] / 16384 for j in range(3)] for q in enc]
            uv = [[p[0] * matrix[0] + p[1] * matrix[4] + matrix[12],
                   p[0] * matrix[1] + p[1] * matrix[5] + matrix[13]] for p in xyz]
            parts.append({'part': part, 'image_name': image_name, 'texture_symbol': relocs.get(rm + 0x48, ''),
                          'source': assets.get(str(image_name)), 'vertex_count': len(enc), 'stride': stride,
                          'encoded_xyz': [list(x) for x in enc], 'geometry_xyz': xyz, 'uv_pixels': uv,
                          'geometry_bounds_xy': bounds(xyz), 'uv_bounds': bounds(uv)})
        non_geometry_symbols = []
        for symbol_name, symbol in symbols.items():
            match = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', symbol_name)
            if match and int(match[1]) == shape and int(match[2]) not in materials.get(shape, {}):
                non_geometry_symbols.append({'part': int(match[2]),
                                             'texture_symbol': relocs.get(symbol['offset'] + 0x48, ''),
                                             'reason': 'no numeric SHAPENAME material with matching vertex buffer'})
        shape_records.append({'shape': shape,
                              'apt_bounds': list(struct.unpack_from('<4f', apt_data, chars[shape]['offset'] + 8)),
                              'object_bbox': list(struct.unpack_from('<6f', data, symbols[f'__BBOX:::{shape}']['offset'])),
                              'parts': parts, 'non_geometry_symbols': non_geometry_symbols})
    output['resources'].append({'label': label, 'entry': entry, 'xsh': xsh,
                                'apt_sha256': hashlib.sha256(apt_data).hexdigest(),
                                'object_sha256': hashlib.sha256(obj).hexdigest(),
                                'xsh_sha256': hashlib.sha256(xsh_bytes).hexdigest(),
                                'stage': [movie['screen_width'], movie['screen_height']],
                                'requested_images': target_names, 'assets': list(assets.values()),
                                'matched_shapes': shape_records,
                                'root_or_transform': 'not mapped; bounds are local APT shape bounds'})

out = REPO / 'logs/ui-restoration-20261020/menu-widescreen-background-gaps-metadata.json'
out.write_text(json.dumps(output, indent=2) + '\n')
print(out)
for r in output['resources']:
    print(r['label'], 'stage', r['stage'], 'shapes',
          [(s['shape'], s['apt_bounds'], [(p['part'], p['image_name'], p['source']['source_id'] if p['source'] else None)
                                          for p in s['parts']]) for s in r['matched_shapes']])
