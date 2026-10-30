#!/usr/bin/env python3
"""Assemble private whole-atlas drafts with measured material masks and source color.

Reads a private plan/raw PNG directory; never approves, imports or edits reviews.
Run with PYTHONPATH=src. Exact prompts/raw art remain private. Existing output
folders are immutable. Geometry-specific UV seam pairs are measured, not copied
from any pilot fighter. No animation/game shader parity is implied.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from defjam_tools import region_detail, material_palette, uv_preview, fighter_scopes, face_detail, color_trial
from defjam_tools.fighter_scopes import scopes,feature_coverage,include_unmapped_features
from defjam_tools.color_trial import components, rgb_to_lab, seam_guard
from defjam_tools.paths import require_private_output


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()




def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--fighter',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=require_private_output(args.output)
    if out.exists():ap.error('Output already exists; use a new immutable stage')
    plan=json.loads(args.plan.read_text());row=next(r for r in plan['fighters'] if r['slug']==args.fighter)
    original=Path(row['corpus_files']['original']['path']);baseline=Path(row['corpus_files']['upscaled']['path']);raw=args.plan.parent/'raw'/(args.fighter+'.png')
    assert sha(original)==row['corpus_files']['original']['sha256'] and sha(baseline)==row['corpus_files']['upscaled']['sha256']
    geompath=args.workspace/'models'/args.fighter/'geometry.json';geometry=json.loads(geompath.read_text());index=json.loads(geompath.with_name('index.json').read_text())
    assert sha(geompath)==index['geometry_sha256'] and geometry['source_id']==row['source_id']
    source=Image.open(original);reference=Image.open(baseline).convert('RGBA');generated=Image.open(raw);source_size=source.width
    if source.size!=(512,512) or reference.size!=(2048,2048):raise ValueError('This audited batch requires512square source and2048square Faithful')
    if abs(generated.width/generated.height-1)>.005:raise ValueError('Generated full atlas must remain square')
    if reference.width%source_size:raise ValueError('Noninteger HD scale')
    scale=reference.width//source_size
    allowed,masks,seams=scopes(geometry,source_size,row.get('editable_alpha_groups',()),row.get('editable_extra_groups',()),row.get('editable_alpha_regions',()))
    allowed=include_unmapped_features(allowed,masks,row.get('unmapped_rgb_features',[]))
    for x0,y0,x1,y1 in row['held_source_boxes']:allowed[y0:y1,x0:x1]=False
    allowedhd=np.repeat(np.repeat(allowed,scale,0),scale,1)
    guard=seam_guard(reference.width,seams,inner=scale*.75,outer=scale*3)
    restored,report=region_detail.patch(reference,reference,generated,(0,0,*reference.size),allowedhd,guard,method='direct',strength=.9)
    result,cloth,clothmask=material_palette.match(reference,restored,geometry,source_size=source_size)
    a=np.asarray(reference);b=np.asarray(result).copy()
    # The last cloth calibration must respect the same immutable source holds.
    b[~allowedhd]=a[~allowedhd];b[guard>=1]=a[guard>=1];b[...,3]=a[...,3]
    contour_reports=[]
    for feature in row.get('source_contour_features',[]):
        box=[v*scale for v in feature['source_box']];x0,y0,x1,y1=box
        tilemask=np.zeros_like(allowedhd);tilemask[y0:y1,x0:x1]=True;tilemask&=allowedhd
        # Uncertain source tattoo paths control the design. Do not adopt raw
        # guessed words/portrait contours; add residual only inside original ink.
        b[tilemask]=a[tilemask]
        rawbox=[round(v/source_size*generated.width) for v in feature['source_box']]
        locked,detail=region_detail.patch(reference,Image.fromarray(b),generated.crop(rawbox),box,tilemask,guard,method='source-locked',strength=.9)
        b=np.asarray(locked).copy();contour_reports.append(dict(name=feature['name'],source_box=feature['source_box'],detail=detail))
    result=Image.fromarray(b)
    assert np.array_equal(b[...,3],a[...,3]) and np.array_equal(b[~allowedhd],a[~allowedhd]) and np.array_equal(b[guard>=1],a[guard>=1])
    changed=np.any(b!=a,axis=-1)
    if not changed.any():raise ValueError('No restored pixels')
    lowref=rgb_to_lab(np.asarray(reference.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    lowraw=rgb_to_lab(np.asarray(generated.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    lowout=rgb_to_lab(np.asarray(result.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    coverage=[]
    for group,mask in masks.items():
        editable=mask&allowed
        if not editable.any():coverage.append(dict(group=group,status='held',reason='eye/mouth/alpha/unknown or shared coverage'));continue
        comps=[]
        for pts in components(editable):
            if len(pts)<4:continue
            yy,xx=pts.T;local=np.zeros_like(editable);local[yy,xx]=True;hd=np.repeat(np.repeat(local,scale,0),scale,1)
            count=int(changed[hd].sum());comps.append(dict(source_pixels=len(pts),bounds=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],changed_HD_pixels=count,coverage_fraction=float(count/hd.sum())))
        coverage.append(dict(group=group,components=comps,median_Lab_before=float(np.median(np.linalg.norm(lowraw[editable]-lowref[editable],axis=-1))),median_Lab_after=float(np.median(np.linalg.norm(lowout[editable]-lowref[editable],axis=-1)))))
    named_features=feature_coverage(a,b,row.get('features',[]),scale)
    out.mkdir(parents=True)
    result.save(out/'atlas.png',compress_level=3);Image.fromarray(allowedhd.astype('uint8')*255).save(out/'allowed.png');clothmask.save(out/'cloth-mask.png')
    # Readable comparison at native512 display scale; original/Faithful/new remain
    # separately available in the live gallery at 25/50/100/200%.
    sheet=Image.new('RGB',(1536,536),'#171717');draw=ImageDraw.Draw(sheet)
    for i,(title,im) in enumerate((('Original',Image.open(original)),('Faithful HD',reference),('Rich Original Detail draft',result))):
        draw.text((i*512+8,5),title,fill='white');sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(i*512,24))
    sheet.save(out/'comparison.png')
    for view in ('front','back'):
        preview=uv_preview.render(geometry,result,view=view,size=(512,768))
        preview.save(out/(view+'-UV-diagnostic.png'))
    for n,feature in enumerate(row.get('features',[])):
        box=[v*scale for v in feature['source_box']];w,h=box[2]-box[0],box[3]-box[1]
        target=(max(64,round(w*min(512/w,512/h))),max(64,round(h*min(512/w,512/h))))
        compare=Image.new('RGB',(target[0]*2,target[1]+24),'#171717');draw=ImageDraw.Draw(compare)
        for i,(title,im) in enumerate((('Source',reference),('Final',result))):
            compare.paste(im.convert('RGB').crop(box).resize(target,Image.Resampling.LANCZOS),(i*target[0],24));draw.text((i*target[0]+4,5),title,fill='white')
        compare.save(out/('feature-'+str(n)+'.png'))
    processors=[Path(__file__)]+[Path(m.__file__) for m in (region_detail,material_palette,uv_preview,fighter_scopes,face_detail,color_trial)]
    receipt=dict(schema=1,fighter=row['label'],source_id=row['source_id'],parent='faithful',plan_sha256=sha(args.plan),original_sha256=sha(original),baseline_sha256=sha(baseline),raw_sha256=sha(raw),raw_size=list(generated.size),geometry_sha256=sha(geompath),output_sha256=sha(out/'atlas.png'),source_size=source_size,scale=scale,held_source_boxes=row['held_source_boxes'],source_seam_edge_count=len(seams),changed_pixels=int(changed.sum()),region_assembly=report,cloth_palette=cloth,material_coverage=coverage,named_features=named_features,editable_alpha_groups=row.get('editable_alpha_groups',[]),editable_extra_groups=row.get('editable_extra_groups',[]),unmapped_rgb_features=row.get('unmapped_rgb_features',[]),alpha_exact=True,source_holds_exact=True,seam_cores_exact=True,approved=False,selected=False,game_verified=False,processor_hashes={p.name:sha(p) for p in processors})
    receipt.update(editable_alpha_regions=row.get('editable_alpha_regions',[]),source_contour_features=contour_reports,preview_omissions=geometry.get('skipped',[]))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(fighter=row['label'],changed=receipt['changed_pixels'],seams=len(seams),sha256=receipt['output_sha256'],output=str(out))))

if __name__=='__main__':main()
