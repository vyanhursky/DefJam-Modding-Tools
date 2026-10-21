#!/usr/bin/env python3
"""Offline metadata audit for matchLoa, oldMLoad and tips loading APTs.

Reads only these three named entries from the user's screens/screens.viv plus
the existing alias inventory. Writes hashes and decoded coordinates, never
texture pixels or archive bytes.
"""
from pathlib import Path
import contextlib, csv, hashlib, io, json, re, runpy, struct

REPO = Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
DATA = Path('/Users/vlad/Code/defjam-data')
with contextlib.redirect_stdout(io.StringIO()):
    d = runpy.run_path(str(REPO / 'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
h, apt, outer = d['hd_assets'], d['apt'], d['outer']
aliases = list(csv.DictReader((REPO / 'logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open()))
index = {(r['source'], r['name'].strip()): r for r in aliases}

def sha(b): return hashlib.sha256(b).hexdigest()

def audit(entry):
    stem = Path(entry).stem
    members = dict(h.archive_entries(h.unpack_refpack(outer[entry])))
    obj = members[stem + '.o']
    apt_data, _, movie, chars, _ = apt.load_movie('screens/screens.viv', entry)
    data, symbols, relocs, _ = d['object_info'](obj)
    section = struct.unpack_from('<I', obj, 32)[0]
    entsize, count, names_index = struct.unpack_from('<HHH', obj, 46)
    sections = [struct.unpack_from('<10I', obj, section + i * entsize) for i in range(count)]
    names_sec = sections[names_index]
    names = obj[names_sec[4]:names_sec[4]+names_sec[5]]
    byname = {names[s[0]:].split(b'\0')[0].decode(): s for s in sections}
    symsec = byname['.symtab']; strsec = sections[symsec[6]]
    strings = obj[strsec[4]:strsec[4]+strsec[5]]
    symbols_full = {}
    for pos in range(symsec[4], symsec[4]+symsec[5], 16):
        ni, val, size, info, other, shndx = struct.unpack_from('<IIIBBH', obj, pos)
        n = strings[ni:].split(b'\0')[0].decode()
        if n: symbols_full[n] = val
    apt_shapes = {i: struct.unpack_from('<4f', apt_data, c['offset']+8)
                  for i,c in enumerate(chars) if c['type'] == 'Shape'}
    mats = {}
    for name, off in symbols_full.items():
        m = re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)', name)
        if m:
            shape, part = map(int,m.groups())
            sym = relocs.get(off+0x48, '')
            im = re.search(r'SHAPENAME=(\d+),', sym)
            if im: mats.setdefault(shape,{})[part] = (int(im[1]), name, sym, off)
    source = f'screens/screens.viv::{entry}::{stem}.xsh'
    parts_out=[]
    for shape, parts in sorted(mats.items()):
        if shape not in apt_shapes: continue
        model = symbols_full.get(f'__Model:::{shape}')
        bbox = symbols_full.get(f'__BBOX:::{shape}')
        if model is None or bbox is None: continue
        bbox6 = struct.unpack_from('<6f', data, bbox)
        scale2 = struct.unpack_from('<4f', data, model+92)
        for part,(image,rmname,texsym,rmoff) in sorted(parts.items()):
            matptr = struct.unpack_from('<I',data,rmoff+0x58)[0]
            matrix = struct.unpack_from('<16f',data,matptr)
            vname = f'__VB:::__GPvb_9_{part}_{shape}'
            voff = symbols_full.get(vname)
            if voff is None: continue
            ptr,nbytes,stride,flags,vo = struct.unpack_from('<5I',data,voff)
            if stride != 6 or nbytes % stride: continue
            xyz = [struct.unpack_from('<3h',data,vo+i*stride) for i in range(nbytes//stride)]
            pos = [[(q[j]+16384)*scale2[j]/16384 for j in range(3)] for q in xyz]
            uv = [[p[0]+matrix[12],p[1]+matrix[13]] for p in pos]
            alias = index.get((source,str(image)))
            parts_out.append(dict(shape=shape,part=part,image=image,apt_bounds=list(apt_shapes[shape]),
                elf_bbox=bbox6,material=rmname,texture_symbol=texsym,material_matrix=list(matrix),
                vertex_symbol=vname,stride=stride,encoded_xyz=xyz,decoded_xy=pos,uv_pixels=uv,
                source_id=alias['id'] if alias else None,canvas=[int(alias['width']),int(alias['height'])] if alias else None,
                alpha_extrema=json.loads(alias['alpha']) if alias else None))
    root_events=[]
    for fi, frame in enumerate(movie['frames']):
        for op, values in frame:
            if op in ('PlaceObject','RemoveObject'):
                root_events.append(dict(frame=fi,event=op,depth=values.get('depth'),
                    character=values.get('character'),name=values.get('name'),
                    matrix=list(values['matrix']) if values.get('matrix') else None,
                    clip_depth=values.get('clip_depth')))
    sprite_events=[]
    for ci, char in enumerate(chars):
        if char['type'] != 'Sprite': continue
        for fi, frame in enumerate(char.get('frames', [])):
            for op, values in frame:
                if op == 'PlaceObject':
                    sprite_events.append(dict(sprite=ci,frame=fi,character=values.get('character'),
                        name=values.get('name'),depth=values.get('depth'),
                        matrix=list(values['matrix']) if values.get('matrix') else None,
                        clip_depth=values.get('clip_depth')))
    return dict(resource=entry,apt_sha256=sha(apt_data),object_sha256=sha(obj),
                stage=[movie['screen_width'],movie['screen_height']],
                frames=len(movie['frames']),character_count=len(chars),root_events=root_events,
                sprite_events=sprite_events,parts=parts_out)

result = dict(schema=1,method='ELF material/vertex decoding inferred as documented in menu-battle-background-shape-audit-2026-10-17.md; APT bounds and aliases independently cross-checked.',
    resources=[audit('screens/battle/matchLoa.big'),audit('screens/battle/oldMLoad.big'),audit('screens/battle/tips.big')])
out=REPO/'logs/ui-restoration-20261020/prefight-loading-uv-metadata.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(out)
print(json.dumps({r['resource']:{'stage':r['stage'],'frames':r['frames'],'parts':len(r['parts'])} for r in result['resources']},indent=2))
