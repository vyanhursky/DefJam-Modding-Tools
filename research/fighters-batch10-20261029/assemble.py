#!/usr/bin/env python3
"""Assemble private whole-atlas drafts with measured material masks and source color.

Reads a private plan/raw PNG directory; never approves, imports or edits reviews.
Run with PYTHONPATH=src. Exact prompts/raw art remain private. Existing output
folders are immutable. Geometry-specific UV seam pairs are measured, not copied
from any pilot fighter. No animation/game shader parity is implied.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from defjam_tools import region_detail, material_palette
from defjam_tools.color_trial import components, rgb_to_lab, seam_guard
from defjam_tools.paths import require_private_output


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scopes(geometry, size):
    groups={}
    edges=defaultdict(list)
    for mesh in geometry['meshes']:
        group=mesh['group'];canvas=groups.setdefault(group,Image.new('L',(size,size)))
        draw=ImageDraw.Draw(canvas);uv=mesh['uv'];pos=mesh['positions'];indices=mesh['indices']
        for at in range(0,len(indices),3):
            ids=indices[at:at+3]
            points=np.asarray([uv[i] for i in ids])
            if len(ids)!=3 or np.any(~np.isfinite(points)) or np.any((points<0)|(points>1)):
                raise ValueError('Invalid triangle UVs')
            draw.polygon([tuple(p*size) for p in points],fill=255)
            if not group.startswith('emc2_skin'):continue
            for a,b in zip(ids,ids[1:]+ids[:1]):
                pair=tuple(tuple(round(float(v),4) for v in pos[i]) for i in (a,b))
                tex=(uv[a],uv[b])
                if pair[0]==pair[1]:continue
                if pair[1]<pair[0]:pair=pair[::-1];tex=tex[::-1]
                edges[pair].append(tex)
    allowed=Image.new('L',(size,size));held=Image.new('L',(size,size));masks={}
    for group,canvas in groups.items():
        masks[group]=np.asarray(canvas)>0
        known=group.startswith(('emc2_skin','emc4_cloth','emc3_jewelry','nospec'))
        target=allowed if known and 'ALPHA' not in group.upper() and 'MATALPH' not in group.upper() else held
        target.paste(255,mask=canvas)
    # Material boundaries/eye-mouth-alpha tiles retain their source plus one
    # native texel. All unknown materials remain explicitly held.
    mask=(np.asarray(allowed)>0)&~(np.asarray(held.filter(ImageFilter.MaxFilter(3)))>0)
    seams=[];seen=set()
    for pair,items in edges.items():
        distinct=[]
        for tex in items:
            if not any(np.max(np.abs(np.asarray(tex)-old))*size<=1 for old in distinct):distinct.append(np.asarray(tex))
        if len(distinct)!=2:continue # absent/ambiguous weld is no seam guarantee
        for tex in distinct:
            key=tuple(map(tuple,tex))
            if key not in seen:seen.add(key);seams.append(dict(body=tex.tolist(),world_edge=pair))
    return mask,masks,seams


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--fighter',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=require_private_output(args.output)
    if out.exists():ap.error('Output already exists; use a new immutable stage')
    plan=json.loads(args.plan.read_text());row=next(r for r in plan['fighters'] if r['slug']==args.fighter)
    original=Path(row['corpus_files']['original']['path']);baseline=Path(row['corpus_files']['upscaled']['path']);raw=args.plan.parent/'raw'/(args.fighter+'.png')
    assert sha(original)==row['corpus_files']['original']['sha256'] and sha(baseline)==row['corpus_files']['upscaled']['sha256']
    geompath=args.workspace/'models'/args.fighter/'geometry.json';geometry=json.loads(geompath.read_text());index=json.loads(geompath.with_name('index.json').read_text())
    assert sha(geompath)==index['geometry_sha256'] and geometry['source_id']==row['source_id']
    reference=Image.open(baseline).convert('RGBA');generated=Image.open(raw);source_size=Image.open(original).width
    if reference.width%source_size:raise ValueError('Noninteger HD scale')
    scale=reference.width//source_size
    allowed,masks,seams=scopes(geometry,source_size)
    for x0,y0,x1,y1 in row['held_source_boxes']:allowed[y0:y1,x0:x1]=False
    allowedhd=np.repeat(np.repeat(allowed,scale,0),scale,1)
    guard=seam_guard(reference.width,seams,inner=scale*.75,outer=scale*3)
    restored,report=region_detail.patch(reference,reference,generated,(0,0,*reference.size),allowedhd,guard,method='direct',strength=.9)
    result,cloth,clothmask=material_palette.match(reference,restored,geometry,source_size=source_size)
    a=np.asarray(reference);b=np.asarray(result).copy()
    # The last cloth calibration must respect the same immutable source holds.
    b[~allowedhd]=a[~allowedhd];b[guard>=1]=a[guard>=1];b[...,3]=a[...,3]
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
    out.mkdir(parents=True)
    result.save(out/'atlas.png',compress_level=3);Image.fromarray(allowedhd.astype('uint8')*255).save(out/'allowed.png');clothmask.save(out/'cloth-mask.png')
    # Readable comparison at native512 display scale; original/Faithful/new remain
    # separately available in the live gallery at 25/50/100/200%.
    sheet=Image.new('RGB',(1536,536),'#171717');draw=ImageDraw.Draw(sheet)
    for i,(title,im) in enumerate((('Original',Image.open(original)),('Faithful HD',reference),('Rich Original Detail draft',result))):
        draw.text((i*512+8,5),title,fill='white');sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(i*512,24))
    sheet.save(out/'comparison.png')
    receipt=dict(schema=1,fighter=row['label'],source_id=row['source_id'],parent='faithful',original_sha256=sha(original),baseline_sha256=sha(baseline),raw_sha256=sha(raw),raw_size=list(generated.size),geometry_sha256=sha(geompath),output_sha256=sha(out/'atlas.png'),source_size=source_size,scale=scale,held_source_boxes=row['held_source_boxes'],source_seam_edge_count=len(seams),changed_pixels=int(changed.sum()),region_assembly=report,cloth_palette=cloth,material_coverage=coverage,alpha_exact=True,source_holds_exact=True,seam_cores_exact=True,approved=False,selected=False,game_verified=False,processor_hashes={p.name:sha(p) for p in [Path(__file__),Path(region_detail.__file__),Path(material_palette.__file__)]})
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(fighter=row['label'],changed=receipt['changed_pixels'],seams=len(seams),sha256=receipt['output_sha256'],output=str(out))))

if __name__=='__main__':main()
