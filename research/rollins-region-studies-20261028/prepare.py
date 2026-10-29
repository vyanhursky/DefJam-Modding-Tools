#!/usr/bin/env python3
"""Prepare two immutable, unapproved Rollins body studies; no live mutations."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from defjam_tools import region_detail,color_trial


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for arg in ['root','workspace','corpus']:ap.add_argument('--'+arg,type=Path,required=True)
    ap.add_argument('--output-name',default='assembled-v2')
    args=ap.parse_args();root=args.root;plan=json.loads((root/'plan.json').read_text(encoding='utf8'))
    outdir=root/args.output_name;outdir.mkdir(exist_ok=False)
    aid=plan['source_id'];parent_path=args.workspace/plan['parent']['path'];assert sha(parent_path)==plan['parent']['sha256']
    refpath=args.corpus/'textures'/f'{aid}.png';assert sha(refpath)==plan['source_sha256']
    parent=Image.open(parent_path).convert('RGBA');ref=Image.open(refpath).convert('RGBA');before=np.asarray(parent)
    geometry_path=args.workspace/'models/rollins/geometry.json';g=json.loads(geometry_path.read_text(encoding='utf8'))
    index=json.loads(geometry_path.with_name('index.json').read_text(encoding='utf8'))
    assert sha(geometry_path)==index['geometry_sha256'] and g['source_id']==aid
    mask,_,seams,other,held=color_trial.geometry_masks(g,512,[[.5,0,.5,.5]])
    assert len(seams)==16
    mask=np.repeat(np.repeat(mask,4,axis=0),4,axis=1)
    guard=color_trial.seam_guard(2048,seams,inner=12,outer=48)
    Image.fromarray(mask.astype(np.uint8)*255).save(outdir/'body-skin-mask.png')
    Image.fromarray(np.rint(guard*255).astype(np.uint8)).save(outdir/'head-body-seam-guard.png')
    # Atlas coordinates, audited against source. Keep uncertain tiny arm and
    # emblem lettering exact, not the words guessed by the generative study.
    arm_text=[(150,80,350,116),(170,150,340,207),(155,264,360,300),
              (695,70,850,108),(705,118,850,169),(685,220,855,275),(650,460,830,500)]
    letters=[(x+1024,y+1280,a+1024,b+1280) for x,y,a,b in arm_text]
    letters += [(768,512,1024,610),(768,748,1024,832)]
    sun_text=(576,512,712,1176)
    boxes=dict(sun=tuple(plan['boxes']['sun']),arms=tuple(plan['boxes']['arms']),emblem=(768,512,1024,832))
    raws={name:root/'raw'/file for name,file in [('sun','sun-direct.png'),('arms','arms-direct.png'),('emblem','small-emblem.png'),('skin','skin-material.png'),('decal','sun-decal.png')]}
    records=[]
    for method,label in [('source-locked','B · Source contours + generated skin/ink grain'),('direct','A · Localized tattoo restoration + generated skin detail')]:
        holds=letters+([sun_text] if method=='source-locked' else [])
        result,grain_report=region_detail.grain(parent,Image.open(raws['skin']),mask,guard,held_boxes=holds,amplitude=.8)
        reports=[]
        for name,box in boxes.items():
            # The direct emblem redraw changes its loops. Hard text holds also
            # cut across those changed curves. Keep that raw as a study only;
            # use source contours for this component in both model variants.
            component_method='source-locked' if name=='emblem' else method
            result,report=region_detail.patch(ref,result,Image.open(raws[name]),box,mask,guard,
                                              held_boxes=holds,method=component_method,strength=.8)
            reports.append(dict(region=name,report=report))
        out=np.asarray(result);assert np.array_equal(out[...,3],before[...,3])
        assert np.array_equal(out[~mask],before[~mask]) and np.array_equal(out[guard>=1],before[guard>=1])
        for x0,y0,x1,y1 in holds:assert np.array_equal(out[y0:y1,x0:x1],before[y0:y1,x0:x1])
        path=outdir/f'rollins-v5-{method}.png'
        if path.exists():raise ValueError('Use a new output directory, do not overwrite drafts')
        result.save(path,compress_level=3)
        # Local low-frequency diagnostics: not a universal appearance threshold.
        lowref=color_trial.rgb_to_lab(np.asarray(ref.convert('RGB').resize((512,512))))
        lowout=color_trial.rgb_to_lab(np.asarray(result.convert('RGB').resize((512,512))))
        lowmask=mask[::4,::4]
        records.append(dict(method=method,label=label,asset=aid,parent=plan['parent']['id'],
            parent_sha256=sha(parent_path),reference_sha256=sha(refpath),geometry_sha256=sha(geometry_path),
            raw_sha256={k:sha(p) for k,p in raws.items()},output=str(path),output_sha256=sha(path),
            processor_sha256=sha(Path(region_detail.__file__)),held_letter_boxes=holds,paired_head_body_seams=16,
            alpha_exact=True,head_and_all_other_materials_exact=True,seam_core_exact=True,
            changed_pixels=int(np.any(out!=before,axis=-1).sum()),
            median_body_Lab_distance_to_source=float(np.median(np.linalg.norm(lowout[lowmask]-lowref[lowmask],axis=-1))),
            grain=grain_report,patches=reports,approved=False))
        print(method,records[-1]['changed_pixels'],'changed; Lab distance',round(records[-1]['median_body_Lab_distance_to_source'],3),flush=True)
    (outdir/'receipt.json').write_text(json.dumps(dict(schema=1,records=records,decal_adopted=False,
        direct_emblem_adopted=False,emblem_reason='direct interpretation changes contours; held text bands interrupt the redrawn motif',
        decal_reason='standalone graphic study; cleaned/changed line shapes and residual background fill, not a UV-ready faithful repair'),indent=2)+'\n',encoding='utf8')
    for name,box in boxes.items():
        w,h=box[2]-box[0],box[3]-box[1];scale=512/w;tileh=round(h*scale)
        sheet=Image.new('RGB',(1536,tileh+45),'#1b211c');draw=ImageDraw.Draw(sheet)
        choices=[('Current v4 / source artwork',parent),('B · Source contours',Image.open(outdir/'rollins-v5-source-locked.png')),('A · Localized restoration',Image.open(outdir/'rollins-v5-direct.png'))]
        for i,(caption,im) in enumerate(choices):
            draw.text((i*512+10,12),caption,fill='white');sheet.paste(im.crop(box).convert('RGB').resize((512,tileh)),(i*512,40))
        sheet.save(outdir/f'{name}-v4-B-A.png')


if __name__=='__main__':main()
