"""Reproducible transcription of the successful inline gym APT audit.

Reads only the named gym shapes and scans popup SHAPENAME relocations in the
screens archive. Emits coordinates/identities only, no game assets.
"""
from pathlib import Path
import contextlib, csv, hashlib, io, json, re, runpy, struct

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
DATA = Path('/Users/vlad/Code/defjam-data')
with contextlib.redirect_stdout(io.StringIO()):
    d = runpy.run_path(str(REPO / 'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
h, apt, outer = d['hd_assets'], d['apt'], d['outer']

def shape_parts(obj, apt_data, chars, shape):
    data, symbols, rels, _ = d['object_info'](obj)
    parts = []
    for sym_name, sym in symbols.items():
        match = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', sym_name)
        if not match or int(match[1]) != shape:
            continue
        part = int(match[2])
        tex_symbol = rels.get(sym['offset'] + 0x48, '')
        image_match = re.search(r'SHAPENAME=(\d+),', tex_symbol)
        if not image_match:
            continue
        image = int(image_match[1])
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
        parts.append({'part': part, 'image_name': image, 'texture_symbol': tex_symbol,
                      'shape_bounds': list(struct.unpack_from('<4f', apt_data, chars[shape]['offset'] + 8)),
                      'matrix': list(matrix), 'encoded_xyz': [list(q) for q in encoded],
                      'geometry_vertices': [list(p) for p in pos], 'uv_vertices': [list(p) for p in uv]})
    return sorted(parts, key=lambda x: x['part'])

# Alias rows are the recorded canonical source inventory; preserve exact full IDs.
rows = list(csv.DictReader((REPO / 'logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open()))
by_name = {int(r['name'].strip()): r for r in rows
           if r['source'].endswith('::gym.xsh') and r['name'].strip().isdigit()}
packed = outer['screens/story/gym.big']
inner = dict(h.archive_entries(h.unpack_refpack(packed)))
obj = inner['gym.o']
apt_data, _, _, chars, _ = apt.load_movie('screens/screens.viv', 'screens/story/gym.big')
gym = {'entry': 'screens/story/gym.big', 'object_sha256': hashlib.sha256(obj).hexdigest(),
       'apt_sha256': hashlib.sha256(apt_data).hexdigest(), 'shapes': []}
for shape in (50, 60, 64):
    parts = shape_parts(obj, apt_data, chars, shape)
    for p in parts:
        row = by_name.get(p['image_name'])
        if row:
            p.update(source_id=row['id'], alias_source=row['source'], alias_index=int(row['index']),
                     alias_name=row['name'].strip(), canvas=[int(row['width']), int(row['height'])])
    gym['shapes'].append({'shape': shape, 'apt_bounds': list(struct.unpack_from('<4f', apt_data, chars[shape]['offset'] + 8)),
                          'parts': parts})

# The popup archives are in misc.viv, not screens.viv. Preserve the negative
# APT-reference finding from the bounded scan of nested screens .big objects.
searched = 0
hits = []
for entry, packed_screen in outer.items():
    if not entry.lower().endswith('.big'):
        continue
    try:
        nested = h.unpack_refpack(packed_screen)
        resources = h.archive_entries(nested)
    except Exception:
        continue
    for name, blob in resources:
        if name.endswith('.o'):
            searched += 1
            names = sorted(set(re.findall(rb'SHAPENAME=(tex[PNFT]),', blob)))
            if names:
                hits.append({'entry': entry, 'object': name, 'names': [x.decode() for x in names]})

misc = dict(h.archive_entries((DATA / 'extracted/assets/misc.viv').read_bytes()))
metadata = {'schema': 1, 'method_note': 'Transcription of the successful inline audit; helper formulas and source are identified in the report.',
            'gym': gym,
            'popup_apt_scan': {'archive': 'screens/screens.viv', 'nested_big_object_count': searched,
                               'shapename_hits': hits,
                               'misc_archive_entries': sorted(n for n in misc if n.lower().startswith('popup')),
                               'misc_popup_archives_sha256': {n: hashlib.sha256(misc[n]).hexdigest()
                                                              for n in sorted(misc) if n.lower().startswith('popup')}}}
out = REPO / 'logs/ui-restoration-20261017/uv-audit/next-menu-batch-metadata-20261020.json'
out.write_text(json.dumps(metadata, indent=2) + '\n')
print(out)
print('gym parts:', [(s['shape'], [(p['part'], p['image_name'], p.get('source_id')) for p in s['parts']]) for s in gym['shapes']])
print('popup scan:', metadata['popup_apt_scan'])
