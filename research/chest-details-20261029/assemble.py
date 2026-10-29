#!/usr/bin/env python3
"""Build three chest-only children; hold all accepted parent pixels elsewhere.

Private plan contains exact source/parent paths and hashes. Source geometry
supplies cloth/jewelry coverage, then inspected named feature regions narrow it.
The tiny unreadable clock signatures remain held; the rest of its dial is edited.
This script neither writes review state nor installs/publishes a texture pack.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from defjam_tools import feature_detail
from defjam_tools.color_trial import rgb_to_lab,box_blur
from defjam_tools.paths import require_private_output

REGIONS={
 'ludacris': [('shirt print',[76,54,216,124])],
 'flava-flav':[('clock dial and inner bezel',[28,200,134,294])],
 'warren-g':[('left cropped crest',[0,298,40,374]),('Phat script',[79,338,128,400]),('Farm script',[162,335,218,396])],
}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def material_mask(g,prefix,size):
    chosen=Image.new('L',(size,size));others=Image.new('L',(size,size))
    for m in g['meshes']:
        target=chosen if m['group'].startswith(prefix) and 'ALPHA' not in m['group'].upper() else others
        draw=ImageDraw.Draw(target)
        for at in range(0,len(m['indices']),3):
            draw.polygon([tuple(np.array(m['uv'][i])*size) for i in m['indices'][at:at+3]],fill=255)
    return (np.asarray(chosen)>0)&~(np.asarray(others.filter(ImageFilter.MaxFilter(3)))>0)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--experiment',type=Path,required=True);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=require_private_output(args.output)
    if out.exists():ap.error('Use a fresh immutable assembly stage')
    plan=json.loads((args.experiment/'plan-with-prompts.json').read_text());out.mkdir(parents=True);receipts=[]
    for r in plan['jobs']:
        slug=r['slug'];parentpath=args.workspace/r['parent']['path'];basepath=Path(r['baseline']['path']);rawpath=args.experiment/'raw'/(slug+'.png')
        assert sha(parentpath)==r['parent']['sha256'] and sha(basepath)==r['baseline']['sha256'] and sha(r['original']['path'])==r['original']['sha256']
        parent=Image.open(parentpath).convert('RGBA');reference=Image.open(basepath).convert('RGBA');generated=Image.open(rawpath)
        gpath=args.workspace/'models'/slug/'geometry.json';g=json.loads(gpath.read_text());index=json.loads(gpath.with_name('index.json').read_text());assert sha(gpath)==index['geometry_sha256'] and g['source_id']==r['source_id']
        prefix='emc3_jewelry' if slug=='flava-flav' else 'emc4_cloth';safe=material_mask(g,prefix,512)
        region=Image.new('L',(512,512));draw=ImageDraw.Draw(region)
        for name,(x0,y0,x1,y1) in REGIONS[slug]:
            if slug=='flava-flav':draw.ellipse((x0,y0,x1-1,y1-1),fill=255)
            else:draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
        mask=safe&(np.asarray(region)>0);holds=[]
        if slug=='flava-flav':
            holds=[[70,232,92,240],[74,254,89,263]]
            for x0,y0,x1,y1 in holds:mask[y0:y1,x0:x1]=False
        hd=np.repeat(np.repeat(mask,4,0),4,1);box=[v*4 for v in r['box']]
        result,report=feature_detail.restore(reference,parent,generated,box,hd,source_size=512,radius_source=8,feather_source=1.5,strength=1.)
        before=np.asarray(parent);after=np.asarray(result);changed=np.any(before!=after,axis=-1)
        regions=[]
        for name,(x0,y0,x1,y1) in REGIONS[slug]:
            mm=hd[y0*4:y1*4,x0*4:x1*4];cc=changed[y0*4:y1*4,x0*4:x1*4];fraction=float(cc[mm].mean())
            if fraction<.2:raise ValueError(name+' still largely held')
            regions.append(dict(name=name,source_box=[x0,y0,x1,y1],safe_HD_pixels=int(mm.sum()),changed_HD_pixels=int(cc[mm].sum()),changed_fraction=fraction))
        dest=out/slug;dest.mkdir();result.save(dest/'atlas.png',compress_level=3);Image.fromarray(hd.astype('uint8')*255).save(dest/'mask.png')
        displaybox=tuple(v*4 for v in r['box']);sheet=Image.new('RGB',(1536,536),'#171717');draw=ImageDraw.Draw(sheet)
        for at,(title,im) in enumerate([('Original',reference),('Accepted surroundings / previous detail',parent),('Chest detail revision',result)]):
            sheet.paste(im.convert('RGB').crop(displaybox).resize((512,512),Image.Resampling.LANCZOS),(at*512,24));draw.text((at*512+5,5),title,fill='white')
        sheet.save(dest/'comparison.png')
        # A larger detail crop remains available without display downscaling.
        result.crop(displaybox).save(dest/'detail.png')
        receipt=dict(schema=1,fighter=r['label'],source_id=r['source_id'],parent=r['parent']['id'],parent_sha256=sha(parentpath),baseline_sha256=sha(basepath),original_sha256=sha(r['original']['path']),geometry_sha256=sha(gpath),raw_sha256=sha(rawpath),raw_size=list(generated.size),output_sha256=sha(dest/'atlas.png'),assembly=report,regions=regions,held_source_boxes=holds,approved_parent_outside_exact=bool(np.array_equal(before[~hd],after[~hd])),alpha_exact=bool(np.array_equal(before[...,3],after[...,3])),visual_review_required=True,approved=False,processor_hashes={p.name:sha(p) for p in [Path(__file__),Path(feature_detail.__file__)]})
        (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');receipts.append(receipt)
        print(json.dumps(dict(fighter=r['label'],changed_pixels=int(changed.sum()),regions=regions,sha256=receipt['output_sha256'])),flush=True)
    (out/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')

if __name__=='__main__':main()
