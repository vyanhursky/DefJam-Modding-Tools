#!/usr/bin/env python3
"""Repair both split back-crest UV fragments, retaining all other parent pixels."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from defjam_tools import feature_detail,material_palette,uv_preview,color_trial,skin_scope
from defjam_tools.skin_scope import clip
from defjam_tools.paths import require_private_output


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--experiment',type=Path,required=True);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();out=require_private_output(args.output)
    if out.exists():ap.error('Use a fresh immutable assembly stage')
    p=json.loads((args.experiment/'plan-with-prompts.json').read_text());aid=p['source_id'];gpath=args.workspace/'models/warren-g/geometry.json';assert sha(gpath)==p['geometry_sha256'];g=json.loads(gpath.read_text());parentpath=args.workspace/p['parent']['path'];assert sha(parentpath)==p['parent']['sha256'];corpus=Path(p['corpus']);baseline=corpus/'textures'/(aid+'.png');original=corpus/'originals'/(aid+'.png')
    parent=Image.open(parentpath).convert('RGBA');ref=Image.open(baseline).convert('RGBA');generated=Image.open(args.experiment/'raw/edit.png')
    cloth,_,_=material_palette.clothing_mask(g,512);back=np.asarray(Image.open(args.experiment/'inputs/back-UV-scope.png'))>0;mask=np.zeros((512,512),bool)
    for x0,y0,x1,y1 in p['source_regions']:mask[y0:y1,x0:x1]=True
    mask&=cloth&back;hd=np.repeat(np.repeat(mask,4,0),4,1)
    result,report=feature_detail.restore(ref,parent,generated,[v*4 for v in p['box']],hd,source_size=512,radius_source=8,feather_source=1.5,strength=1.)
    a=np.asarray(parent);b=np.asarray(result);changed=np.any(a!=b,axis=-1);fragments=[];world=[]
    for n,(x0,y0,x1,y1) in enumerate(p['source_regions']):
        scope=hd[y0*4:y1*4,x0*4:x1*4];cc=changed[y0*4:y1*4,x0*4:x1*4];fraction=float(cc[scope].mean());assert fraction>.7
        fragments.append(dict(fragment=n,source_box=[x0,y0,x1,y1],safe_pixels=int(scope.sum()),changed_pixels=int(cc[scope].sum()),changed_fraction=fraction))
        for m in g['meshes']:
            if not m['group'].startswith('emc4_cloth'):continue
            for at in range(0,len(m['indices']),3):
                poly=[np.array([*m['positions'][i],*m['uv'][i]],float) for i in m['indices'][at:at+3]]
                for axis,limit,above in [(3,x0/512,True),(3,x1/512,False),(4,y0/512,True),(4,y1/512,False),(2,-.5,False)]:poly=clip(poly,axis,limit,above)
                if len(poly)>=3:world.extend(poly)
    pts=np.array(world);lo=pts[:,:2].min(0)-.35;hi=pts[:,:2].max(0)+.35;bounds=[float(lo[0]),float(lo[1]),float(hi[0]),float(hi[1])];size=(768,min(1200,max(256,round(768*(hi[1]-lo[1])/(hi[0]-lo[0])))))
    out.mkdir(parents=True);result.save(out/'atlas.png',compress_level=3);Image.fromarray(hd.astype('uint8')*255).save(out/'mask.png')
    sheet=Image.new('RGB',(size[0]*3,size[1]+24),'#171717');draw=ImageDraw.Draw(sheet)
    for n,(name,im) in enumerate([('Original',ref),('Previous',parent),('Both fragments restored',result)]):
        preview=uv_preview.render(g,im,view='back',bounds=bounds,size=size,groups=('emc4_cloth',));preview.save(out/('back-'+str(n)+'.png'));sheet.paste(preview,(n*size[0],24));draw.text((n*size[0]+5,5),name+' · RGB UV diagnostic',fill='white')
    sheet.save(out/'back-comparison.png')
    checks=dict(alpha_exact=bool(np.array_equal(a[...,3],b[...,3])),outside_back_crest_exact=bool(np.array_equal(a[~hd],b[~hd])))
    processors=[Path(__file__)]+[Path(m.__file__) for m in (feature_detail,material_palette,uv_preview,color_trial,skin_scope)]
    assert all(checks.values());receipt=dict(schema=1,parent=p['parent']['id'],parent_sha256=sha(parentpath),plan_sha256=sha(args.experiment/'plan-with-prompts.json'),source_id=aid,geometry_sha256=sha(gpath),baseline_sha256=sha(baseline),original_sha256=sha(original),raw_sha256=sha(args.experiment/'raw/edit.png'),output_sha256=sha(out/'atlas.png'),fragments=fragments,checks=checks,assembly=report,back_projection_bounds=bounds,back_projection_size=size,approved=False,processor_hashes={x.name:sha(x) for x in processors});(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
