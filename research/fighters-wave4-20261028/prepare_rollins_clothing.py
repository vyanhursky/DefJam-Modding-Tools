#!/usr/bin/env python3
"""Assemble a separate clothes-only restoration; skin/tattoos/head stay exact."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
from defjam_tools import clothing_detail


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['root','corpus','workspace']: ap.add_argument('--'+key,type=Path,required=True)
    args=ap.parse_args(); root=args.root
    state=json.loads((root/'before-workshop.json').read_text(encoding='utf8'))
    aid='4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d'; parent='r-230c857e841f4273'
    c=next(c for c in state['candidates'][aid] if c['id']==parent)
    path=args.workspace/c['path']; assert sha(path)==c['sha256']
    source=args.corpus/'textures'/f'{aid}.png'; raw=root/'raw/rollins-clothing-v4.png'
    geometry=args.workspace/'models/rollins/geometry.json'
    assert sha(geometry)==json.loads(geometry.with_name('index.json').read_text(encoding='utf8'))['geometry_sha256']
    result,report,mask=clothing_detail.repair(Image.open(source).convert('RGBA'),Image.open(path).convert('RGBA'),
        Image.open(raw),json.loads(geometry.read_text(encoding='utf8')),(0,0,2048,2048),[(0,0,2048,2048)])
    output=root/'assembled/rollins-clothing-v4.png'
    if output.exists(): raise ValueError('Output exists; use a new run directory')
    result.save(output,compress_level=3);mask.save(root/'assembled/rollins-clothing-mask.png')
    row=dict(fighter='rollins',asset=aid,parent=parent,parent_sha256=sha(path),source_sha256=sha(source),
             raw_path=str(raw),raw_sha256=sha(raw),geometry_sha256=sha(geometry),
             processor_sha256=sha(Path(clothing_detail.__file__)),output=str(output),output_sha256=sha(output),
             report=report,body_skin_tattoos_head_exact_v3=True,body_skin_restoration='incomplete; generation blocked',
             prompt=json.loads((root/'rollins-clothing-prompt.json').read_text(encoding='utf8'))['prompt'])
    (root/'rollins-clothing-receipt.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf8')
    print('Restored clothing',report['changed_pixels'],'of',report['safe_pixels'],'safe pixels; all other pixels exact')


if __name__=='__main__': main()
