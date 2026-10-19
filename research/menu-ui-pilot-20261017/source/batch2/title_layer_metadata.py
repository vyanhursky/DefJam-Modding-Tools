#!/usr/bin/env python3
"""Offline metadata only: prestart near-city/tower mesh, timeline and source alpha.

Uses the existing pilot ELF/APT reader. Does not save or transform images.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import struct
from PIL import Image

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
reader = REPO / 'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'
namespace = {}
exec(reader.read_text().split('results = []')[0], namespace)
hd = namespace['hd_assets']
apt = namespace['apt']
inner = dict(hd.archive_entries(hd.unpack_refpack(namespace['outer']['screens/intMain/prestart.big'])))
data, symbols, rels, file_offset = namespace['object_info'](inner['prestart.o'])
buf, consts, movie, chars, _ = apt.load_movie('screens/screens.viv', 'screens/intMain/prestart.big')
corpus_root = Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
corpus = json.loads((corpus_root / 'corpus.json').read_text())
frame_count, frame_array = struct.unpack_from('<II', buf, movie['offset'] + 8)
raw_images = {rec['index']: (rec, image) for rec, image in hd.shpx_images(inner['prestart.xsh'], indices={1, 2, 13, 14})}
output = dict(schema=1, note='Metadata only; matrix interpretation and packed decoding follow the pilot report.', layers=[])
for label, shape, sprite, depth, height in [('near-city', 7, 8, 4, 310), ('tower-roof', 12, 13, 8, 446)]:
    bbox_off = symbols[f'__BBOX:::{shape}']['offset']
    bbox = struct.unpack_from('<6f', data, bbox_off)
    apt_bbox = struct.unpack_from('<4f', buf, chars[shape]['offset'] + 8)
    assert list(apt_bbox) == [bbox[0], bbox[1], bbox[3], bbox[4]]
    assert list(apt_bbox) == [0, 0, 640, height]
    model_off = symbols[f'__Model:::{shape}']['offset']
    scale = struct.unpack_from('<4f', data, model_off + 92)
    layer = dict(label=label, shape=shape, sprite=sprite, root_depth=depth, nominal_height=height,
                 apt_shape_offset=chars[shape]['offset'], bbox_offset=bbox_off, bbox=list(bbox),
                 model_offset=model_off, inferred_scale=list(scale), sprite_frames=chars[sprite]['frames'], parts=[], events=[])
    for part in (0, 1):
        rm_off = symbols[f'__RM:::__GP_RM_{shape}_{part}']['offset']
        texture_symbol = rels[rm_off + 72]
        image_name = int(re.search(r'SHAPENAME=(\d+),', texture_symbol).group(1))
        mat_off = struct.unpack_from('<I', data, rm_off + 88)[0]
        matrix = struct.unpack_from('<16f', data, mat_off)
        vb_off = symbols[f'__VB:::__GPvb_9_{part}_{shape}']['offset']
        vertex_off = struct.unpack_from('<I', data, vb_off + 16)[0]
        encoded = [struct.unpack_from('<3h', data, vertex_off + i * 6) for i in range(4)]
        decoded = [[(q[j] + 16384) * scale[j] / 16384 for j in range(3)] for q in encoded]
        record = alias = None
        for asset in corpus['assets']:
            matching = next((a for a in asset.get('aliases', []) if '/prestart.big::' in a['source'] and a['name'].strip() == str(image_name)), None)
            if matching:
                record, alias = asset, matching
                break
        assert record is not None
        original_path = corpus_root / record['original']
        original_bytes = original_path.read_bytes()
        assert hashlib.sha256(original_bytes).hexdigest() == record['original_hash']
        image = Image.open(original_path).convert('RGBA')
        raw_record, raw_image = raw_images[alias['index']]
        assert raw_record['source_id'] == record['source_id']
        assert raw_image.tobytes() == image.tobytes()
        alpha = image.getchannel('A')
        hist = alpha.histogram()
        active = image.crop((0, 0, image.width, height))
        padding = image.crop((0, height, image.width, image.height))
        padding_colors = collections.Counter(padding.get_flattened_data())
        alpha_info = dict(extrema=alpha.getextrema(), zero=hist[0], opaque=hist[255], partial=sum(hist[1:255]),
                          active_alpha_bbox=active.getchannel('A').getbbox(), full_alpha_bbox=alpha.getbbox(),
                          padding_alpha_extrema=padding.getchannel('A').getextrema(), padding_colors=padding_colors.most_common())
        layer['parts'].append(dict(part=part, image_name=image_name, shpx_index=alias['index'], dimensions=image.size,
                                   source_id=record['source_id'], original_path=str(original_path), original_hash=record['original_hash'],
                                   material_offset=rm_off, matrix_offset=mat_off, matrix=list(matrix),
                                   vertex_descriptor_offset=vb_off, vertex_data_offset=vertex_off,
                                   encoded_xyz=encoded, inferred_xyz=decoded, alpha=alpha_info))
    assert layer['parts'][0]['encoded_xyz'][2][0] == layer['parts'][1]['encoded_xyz'][0][0]
    state = {}
    for frame in range(frame_count):
        count, pointers = struct.unpack_from('<II', buf, frame_array + frame * 8)
        for index in range(count):
            ptr = struct.unpack_from('<I', buf, pointers + index * 4)[0]
            if not ptr:
                continue
            kind, event = apt.parse_frame_item(buf, ptr)
            if kind not in ('PlaceObject', 'RemoveObject') or event.get('depth') != depth:
                continue
            assert kind != 'RemoveObject'
            body = ptr + 4
            color = list(buf[body + 36:body + 44]) if event['flags'] & 8 else None
            layer['events'].append(dict(frame=frame, flags=event['flags'], matrix=event.get('matrix'), color=color))
            if event.get('matrix') is not None:
                state['matrix'] = event['matrix']
            if color is not None:
                state['color'] = color
        if frame == 134:
            layer['settled_frame_134'] = dict(state)
    output['layers'].append(layer)
output['raw_shpx_rgba_matches_originals'] = True
print(json.dumps(output, indent=2))
