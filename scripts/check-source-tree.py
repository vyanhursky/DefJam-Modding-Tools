#!/usr/bin/env python3
"""Reject private assets and verify pinned dependencies in tracked source."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BLOCKED={'.iso','.xiso','.xbe','.viv','.mad','.xsh','.o','.obj','.bin','.glb','.gltf','.blend','.blend1','.fbx','.stl','.dds','.tga','.png','.jpg','.jpeg','.gif','.webp','.bmp','.ppm','.mp4','.wav','.zip','.7z','.rar','.exe','.dll','.log'}
PRIVATE={'data','private','workspaces','models','captures','logs','build','dist','.venv'}


def main():
    files=subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z'],text=True).split('\0')
    errors=[]
    for name in filter(None,files):
        p=Path(name)
        if p.suffix.lower() in BLOCKED or p.parts[0] in PRIVATE or name=='local.json' or name.endswith('.local.json'):
            errors.append(name+': private/binary artifact')
            continue
        raw=(ROOT/name).read_bytes()
        try:raw.decode('utf-8-sig')
        except UnicodeDecodeError:errors.append(name+': non-text file')
        if b'\0' in raw:errors.append(name+': binary content')
    vendor=ROOT/'src/defjam_tools/resources/vendor/three'
    pins=json.loads((vendor/'provenance.json').read_text())
    for name,record in pins['files'].items():
        if hashlib.sha256((vendor/name).read_bytes()).hexdigest()!=record['sha256']:
            errors.append('Three.js pin changed: '+name)
    if (ROOT/'AGENTS.md').read_bytes()!=(ROOT/'CLAUDE.md').read_bytes():errors.append('Agent instruction mirror differs')
    for message in errors:print(message,file=sys.stderr)
    print(str(sum(bool(n) for n in files))+' source files; '+str(len(errors))+' policy failures')
    return bool(errors)


if __name__=='__main__':sys.exit(main())
