#!/usr/bin/env python3
"""Two focused private children: cap digits and reference-guided figurine RGB.

Keep all parent pixels outside audited source-feature/material scope and alpha
exact. The figurine's unmapped tile padding is cleared too, without overriding
any other mapped material. No review edits, imports, approval or pack publication.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from defjam_tools import feature_detail, fighter_scopes, uv_preview, color_trial
from defjam_tools.paths import require_private_output


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--experiment',type=Path,required=True)
    ap.add_argument('--workspace',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();out=require_private_output(args.output)
    if out.exists():ap.error('Use a fresh immutable stage')
    plan=json.loads((args.experiment/'plan-with-prompts.json').read_text())
    out.mkdir(parents=True)
    for row in plan['jobs']:
        slug=row['slug']
        if slug not in ('freeway','elephant-man'):continue
        for pin in row['input_pins']:
            assert sha(pin['path'])==pin['sha256']
        parentpath=args.workspace/row['parent']['path'];refpath=Path(row['baseline']['path'])
        assert sha(parentpath)==row['parent']['sha256'] and sha(refpath)==row['baseline']['sha256']
        assert sha(row['original']['path'])==row['original']['sha256']
        gp=args.workspace/'models'/slug/'geometry.json';assert sha(gp)==row['geometry_sha256'];g=json.loads(gp.read_text())
        assert g['source_id']==row['source_id']
        parent=Image.open(parentpath).convert('RGBA');reference=Image.open(refpath).convert('RGBA')
        rawpath=args.experiment/'raw'/(slug+'.png');raw=Image.open(rawpath)
        allowed,masks,_=fighter_scopes.scopes(g,512);scope=np.zeros((512,512),bool)
        if slug=='freeway':
            regions=[('19 left of original seam',[138,269,149,283]),('72 right of original seam',[152,269,164,283])]
            for _,(x0,y0,x1,y1) in regions:scope[y0:y1,x0:x1]=True
            scope&=allowed
            padding=0;feather=.25
        else:
            regions=[('sculptural figurine and tile padding',[0,194,100,256])]
            x0,y0,x1,y1=regions[0][1];scope[y0:y1,x0:x1]=True
            jewelry=np.zeros_like(scope);allmapped=np.zeros_like(scope)
            for group,mask in masks.items():
                allmapped|=mask
                if group.startswith('emc3_jewelry'):jewelry|=mask
            # This explicit source-tile padding has no decoded static UV coverage.
            # Keep every mapped non-jewelry pixel exact; no generic hold override.
            padding=int((scope&~allmapped).sum())
            scope&=(jewelry|~allmapped)
            feather=0
        scale=parent.width//512;assert parent.size==(2048,2048) and scale==4
        hd=np.repeat(np.repeat(scope,scale,0),scale,1)
        result,report=feature_detail.restore(reference,parent,raw,[v*scale for v in row['box']],hd,source_size=512,radius_source=8,feather_source=feather,strength=1)
        a=np.asarray(parent);b=np.asarray(result);changed=np.any(a!=b,axis=-1)
        assert np.array_equal(a[~hd],b[~hd]) and np.array_equal(a[...,3],b[...,3])
        checks=[]
        for name,(x0,y0,x1,y1) in regions:
            mm=hd[y0*4:y1*4,x0*4:x1*4];cc=changed[y0*4:y1*4,x0*4:x1*4]
            count=int(cc[mm].sum());assert count>20
            checks.append(dict(name=name,source_box=[x0,y0,x1,y1],safe_pixels=int(mm.sum()),changed_pixels=count,changed_fraction=float(cc[mm].mean())))
        if slug=='freeway':assert np.array_equal(a[269*4:283*4,149*4:152*4],b[269*4:283*4,149*4:152*4])
        dest=out/slug;dest.mkdir();result.save(dest/'atlas.png',compress_level=3);Image.fromarray(hd.astype('uint8')*255).save(dest/'mask.png')
        sheet=Image.new('RGB',(1536,536),'#171717');draw=ImageDraw.Draw(sheet)
        for n,(title,im) in enumerate([('Original source',reference),('Previous draft',parent),('Focused revision',result)]):
            crop=im.convert('RGB').crop([v*4 for v in row['box']]).resize((512,512),Image.Resampling.LANCZOS)
            sheet.paste(crop,(n*512,24));draw.text((n*512+4,5),title,fill='white')
        sheet.save(dest/'comparison.png');result.crop([v*4 for v in row['box']]).save(dest/'detail.png')
        lo,hi=g['bounds'];h=hi[1]-lo[1];cx=(lo[0]+hi[0])/2
        if slug=='freeway':bounds=(cx-h*.17,hi[1]-h*.30,cx+h*.17,hi[1]+h*.04)
        else:bounds=(cx-h*.2,hi[1]-h*.46,cx+h*.2,hi[1]-h*.06)
        for view in ('front','back'):uv_preview.render(g,result,view=view,bounds=bounds,size=(768,768)).save(dest/(view+'-UV-diagnostic.png'))
        processors=[Path(__file__)]+[Path(m.__file__) for m in (feature_detail,fighter_scopes,uv_preview,color_trial)]
        receipt=dict(schema=1,fighter=row['label'],source_id=row['source_id'],parent=row['parent']['id'],parent_sha256=sha(parentpath),baseline_sha256=sha(refpath),original_sha256=sha(row['original']['path']),geometry_sha256=sha(gp),plan_sha256=sha(args.experiment/'plan-with-prompts.json'),input_pins=row['input_pins'],raw_sha256=sha(rawpath),raw_size=list(raw.size),output_sha256=sha(dest/'atlas.png'),regions=checks,assembly=report,unmapped_tile_padding_source_pixels=padding,alpha_exact=True,outside_feature_exact=True,approved=False,selected=False,game_verified=False,processor_hashes={p.name:sha(p) for p in processors})
        (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(dict(fighter=row['label'],changed=int(changed.sum()),sha256=receipt['output_sha256'],regions=checks)))

if __name__=='__main__':main()
