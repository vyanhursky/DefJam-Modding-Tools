#!/usr/bin/env python3
"""Reassemble omitted headwear from existing raw v3 detail; no live mutation."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from defjam_tools import clothing_detail


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for arg in ['workspace', 'corpus', 'root']:
        ap.add_argument('--'+arg, type=Path, required=True)
    args = ap.parse_args()
    state = json.loads((args.root/'before-workshop.json').read_text(encoding='utf8'))
    prior = args.workspace/'experiments/fighters-wave3-20261028'
    plans = json.loads((prior/'review-import-receipt.json').read_text(encoding='utf8'))['imported']
    regions = {'redman': [(1024,850,2048,1024), (1824,380,2004,560), (1724,750,1874,850)],
               'blaze': [(1224,700,1644,1024)]}
    records = []
    for name, boxes in regions.items():
        plan = next(p for p in plans if p['fighter']==name)
        aid, parent = plan['asset'], plan['revision']
        candidate = next(c for c in state['candidates'][aid] if c['id']==parent)
        path = args.workspace/candidate['path']
        assert sha(path)==candidate['sha256']==plan['sha256']
        source = args.corpus/'textures'/f'{aid}.png'
        raw = prior/'raw'/f'{name}-head-v3.png'
        geometry = args.workspace/'models'/name/'geometry.json'
        index = json.loads(geometry.with_name('index.json').read_text(encoding='utf8'))
        assert sha(geometry)==index['geometry_sha256'] and index['source_id']==aid
        result, report, mask = clothing_detail.repair(
            Image.open(source).convert('RGBA'), Image.open(path).convert('RGBA'),
            Image.open(raw), json.loads(geometry.read_text(encoding='utf8')),
            (1024,0,2048,1024), boxes)
        assert all(r['changed_pixels']>0 for r in report['regions'])
        output = args.root/'assembled'/f'{name}-headwear-v4.png'
        if output.exists():
            raise ValueError('Output exists; use a new run directory')
        result.save(output, compress_level=3)
        mask.save(output.with_name(name+'-repair-mask.png'))
        sheet = Image.new('RGB', (1536,560), '#1b211c')
        draw = ImageDraw.Draw(sheet)
        for i, (label, im) in enumerate([('Original', Image.open(source)), ('v3 before repair', Image.open(path)), ('v4 missed headwear recovered', result)]):
            draw.text((i*512+12,12), label, fill='white')
            sheet.paste(im.crop((1024,0,2048,1024)).convert('RGB').resize((512,512)), (i*512,40))
        sheet.save(args.root/'assembled'/f'{name}-head-comparison.png')
        records.append(dict(fighter=name, asset=aid, parent=parent,
                            parent_sha256=sha(path), source_sha256=sha(source),
                            raw_path=str(raw), raw_sha256=sha(raw), geometry_sha256=sha(geometry),
                            processor_sha256=sha(Path(clothing_detail.__file__)),
                            output=str(output), output_sha256=sha(output), report=report))
        print(name, report['safe_pixels'], 'safe pixels;', report['changed_pixels'], 'changed', flush=True)
    (args.root/'assembly-receipt.json').write_text(json.dumps(dict(schema=1, records=records), indent=2)+'\n', encoding='utf8')


if __name__=='__main__':
    main()
