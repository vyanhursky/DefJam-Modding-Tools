#!/usr/bin/env python3
"""Prepare head-detail and whole-clothing-palette drafts without a live mutation.

Every output directory is new. Existing candidates/source PNGs remain untouched.
Exact raw generation prompts are supplied in the private root, not regenerated.
"""
import argparse,hashlib,json,io
from pathlib import Path
import numpy as np
from PIL import Image
from defjam_tools import face_detail,color_trial,material_palette


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['root','corpus','workspace','output']:ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();out=args.output;out.mkdir(exist_ok=False)
    state=json.loads((args.root/'before-workshop.json').read_text())
    jobs={j['name']:j for j in json.loads((args.root/'prompts.json').read_text())}
    held={'blaze':[(200,700,620,1024)],'nyne':[(0,840,1024,1024)],'trejo':[(0,850,600,1024),(0,680,110,800)],
          'redman':[(0,850,1024,1024),(800,380,980,560),(700,750,850,850)],
          'rollins':[(0,850,600,1024),(850,480,1024,620),(0,760,120,860)]}
    protect={'blaze':[[.5,0,.5,.5]],'nyne':[[.5,0,.5,.51]],'trejo':[[.49,0,.51,.51]],'redman':[[.49,0,.51,.5]],'rollins':[[.49,0,.51,.5]]}
    records=[]
    for plan in json.loads((args.root/'plan.json').read_text()):
        name,aid,parentid=plan['name'],plan['source_id'],plan['parent'];baseline=args.corpus/'textures'/f'{aid}.png'
        parentpath=args.workspace/next(c['path'] for c in state['candidates'][aid] if c['id']==parentid) if parentid else baseline
        if sha(parentpath)!=plan['parent_sha256']:raise ValueError('Parent pin changed')
        parent=Image.open(parentpath).convert('RGBA');ref=Image.open(baseline).convert('RGBA')
        geometry_path=args.workspace/'models'/name/'geometry.json';geometry=json.loads(geometry_path.read_text());index=json.loads(geometry_path.with_name('index.json').read_text())
        assert sha(geometry_path)==index['geometry_sha256'] and geometry['source_id']==aid
        _,_,seams,_,_=color_trial.geometry_masks(geometry,512,protect[name])
        guard=color_trial.seam_guard(2048,[{'body':s['face']} for s in seams],inner=12,outer=48)
        raw=args.root/'raw'/f'{name}-head-v3.png'
        head,headreport=face_detail.merge(ref,parent,Image.open(raw),(1024,0,2048,1024),held[name],guard,strength=.8)
        head.save(out/f'{name}-head-before-cloth.png',compress_level=3)
        final,clothreport,mask=material_palette.match(ref,head,geometry)
        finalpath=out/f'{name}-restoration-v3.png';final.save(finalpath,compress_level=3);mask.save(out/f'{name}-clothing-mask.png')
        original=np.asarray(parent);result=np.asarray(final)
        allowed=np.asarray(mask)>0;allowed[:1024,1024:]=True
        assert np.array_equal(original[~allowed],result[~allowed])
        assert np.array_equal(original[...,3],result[...,3])
        before,after=clothreport['median_Lab_distance_before'],clothreport['median_Lab_distance_after']
        if before>.5 and after>=before*.8:raise ValueError('Clothing palette did not improve: '+name)
        core=guard>=1;core[:,:1024]=False;core[1024:]=False
        assert np.array_equal(result[core],original[core])
        row=dict(plan,output=str(finalpath),output_sha256=sha(finalpath),raw_sha256=sha(raw),reference_sha256=sha(baseline),geometry_sha256=sha(geometry_path),
                 head_report=headreport,clothing_report=clothreport,paired_head_edges=len(seams),alpha_exact=True,outside_head_and_cloth_exact=True,
                 prompt=jobs[name]['prompt'],processors={'face_detail':sha(Path(face_detail.__file__)),'material_palette':sha(Path(material_palette.__file__))})
        records.append(row)
        print(name,'cloth Lab distance',round(before,2),'->',round(after,2),'head seam pairs',len(seams),flush=True)
    (out/'receipt.json').write_text(json.dumps({'schema':1,'records':records,'live_workspace_modified':False},indent=2)+'\n')


if __name__=='__main__':main()
