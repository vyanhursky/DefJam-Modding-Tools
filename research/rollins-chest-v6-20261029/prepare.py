#!/usr/bin/env python3
"""Prepare a v5A child limited to anatomical chest skin and its tattoo island."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
from defjam_tools import skin_scope,color_trial,region_detail


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['root','workspace','corpus']:ap.add_argument('--'+k,type=Path,required=True)
    ap.add_argument('--output-name',default='assembled-v3')
    args=ap.parse_args();root=args.root;out=root/args.output_name;out.mkdir(exist_ok=False)
    plan=json.loads((root/'plan.json').read_text(encoding='utf8'));aid=plan['source_id'];pp=args.workspace/plan['parent']['path']
    assert sha(pp)==plan['parent']['sha256']
    rp=args.corpus/'textures'/f'{aid}.png';assert sha(rp)==plan['source_sha256']
    parent=Image.open(pp).convert('RGBA');reference=Image.open(rp).convert('RGBA')
    gp=args.workspace/'models/rollins/geometry.json';g=json.loads(gp.read_text(encoding='utf8'))
    assert sha(gp)==json.loads(gp.with_name('index.json').read_text(encoding='utf8'))['geometry_sha256']
    planes=[(1,16,True),(2,.3,True),(0,-3,True),(0,3,False),(3,0,True),(3,.375,False),(4,0,True),(4,.25,False)]
    extras={11:[549,550],16:list(range(79,91))}
    front,parts=skin_scope.rasterize(g,512,planes)
    emblem,emblem_parts=skin_scope.rasterize(g,512,[(1,100,True)],extras)
    safe,_,seams,_,_=color_trial.geometry_masks(g,512,[[.5,0,.5,.5]])
    front &= safe;emblem &= safe;scope=front|emblem
    assert len(seams)==16 and int(front.sum())==5819 and int(emblem.sum())==3141
    def hd(mask):return np.repeat(np.repeat(mask,4,axis=0),4,axis=1)
    mask=hd(scope);front_hd=hd(front);emblem_hd=hd(emblem)
    seam=color_trial.seam_guard(2048,seams,inner=12,outer=48)
    # Fade inside exact anatomical/material coverage; never blur edits beyond it.
    eroded=Image.fromarray(scope.astype(np.uint8)*255);feather=np.zeros((512,512),float)
    for _ in range(4):eroded=eroded.filter(ImageFilter.MinFilter(3));feather+=(np.asarray(eroded)>0)/4
    weight=color_trial.resize_float(feather,(2048,2048))*mask
    guard=np.maximum(seam,1-weight)
    for name,m in [('chest-scope',mask),('front-chest',front_hd),('chest-tattoo',emblem_hd)]:Image.fromarray(m.astype(np.uint8)*255).save(out/(name+'-mask.png'))
    Image.fromarray(np.rint(weight*255).astype(np.uint8)).save(out/'chest-feather.png')
    swatch=root.parent/'rollins-region-studies-20261028/raw/skin-material.png'
    # Calibrate the material's spatial scale before transfer: enlarging the
    # entire swatch to2048 makes its pores too broad. Use a512px fine-detail
    # tile with bounded luminance RMS, keeping original chest shading/color.
    tile=np.asarray(Image.open(swatch).convert('RGB').resize((512,512),Image.Resampling.LANCZOS))
    sample=color_trial.rgb_to_lab(np.tile(tile,(4,4,1)))[...,0]
    residual=sample-color_trial.box_blur(color_trial.box_blur(sample,2),2)
    residual-=residual.mean();rms=float(residual.std())
    residual=np.clip(residual*(1.2/max(rms,1e-8)),-3,3)
    lab=color_trial.rgb_to_lab(np.asarray(reference)[...,:3]);low=color_trial.box_blur(lab[...,0],8)
    lab[...,0]+=residual+.15*np.clip(lab[...,0]-low,-2,2)
    rgb,_=color_trial.lab_to_rgb(lab);prior=np.asarray(parent)
    blend=(1-guard)*front_hd;pixels=prior.copy()
    pixels[...,:3]=np.rint(prior[...,:3]*(1-blend[...,None])+rgb*blend[...,None]).astype(np.uint8)
    grain_report=dict(method='frequency-calibrated generated material over original diffuse',tile_hd=512,
        highpass_radius_hd=2,highpass_passes=2,target_L_rms=1.2,max_L_residual=3,
        raw_material_residual_rms=rms,source_sharpening_strength=.15,source_sharpening_radius_hd=8)
    tattoo=root/'raw/chest-tattoo.png'
    result,tattoo_report=region_detail.patch(reference,Image.fromarray(pixels),Image.open(tattoo),
        (768,512,1024,832),emblem_hd,guard,method='direct',strength=.9)
    prior=np.asarray(parent);final=np.asarray(result);changed=np.any(final!=prior,axis=-1)
    assert np.array_equal(final[...,3],prior[...,3]) and np.array_equal(final[~mask],prior[~mask])
    assert np.array_equal(final[seam>=1],prior[seam>=1]) and np.array_equal(final[:1024,1024:],prior[:1024,1024:])
    output=out/'rollins-v6-chest.png';result.save(output,compress_level=3)
    report=dict(schema=1,asset=aid,parent=plan['parent']['id'],parent_sha256=sha(pp),reference_sha256=sha(rp),
        geometry_sha256=sha(gp),output=str(output),output_sha256=sha(output),raw_tattoo_sha256=sha(tattoo),
        reused_material_path=str(swatch),reused_material_sha256=sha(swatch),chest_skin_method='existing successful generated material + source luminance sharpening; direct crop blocked',
        main_front_native_pixels=int(front.sum()),emblem_native_pixels=int(emblem.sum()),scope_hd_pixels=int(mask.sum()),
        changed_front_pixels=int((changed&front_hd).sum()),changed_tattoo_pixels=int((changed&emblem_hd).sum()),
        clipping_planes=planes,contributors=parts,emblem_contributors=emblem_parts,paired_seams=16,
        alpha_exact=True,outside_chest_exact=True,head_arms_back_clothes_boots_exact=True,seam_core_exact=True,
        grain=grain_report,tattoo=tattoo_report,
        processors={k:sha(Path(v.__file__)) for k,v in [('skin_scope',skin_scope),('region_detail',region_detail),('color_trial',color_trial)]})
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    for name,box in [('tattoo',(768,512,1024,832)),('front-skin',(320,0,720,512))]:
        width=480;height=round((box[3]-box[1])*width/(box[2]-box[0]));sheet=Image.new('RGB',(width*3,height+40),'#1b211c');d=ImageDraw.Draw(sheet)
        for n,(label,im) in enumerate([('Original',reference),('v5A',parent),('v6 chest',result)]):
            d.text((n*width+10,12),label,fill='white');sheet.paste(im.crop(box).convert('RGB').resize((width,height)),(n*width,40))
        sheet.save(out/(name+'-comparison.png'))
    print(json.dumps({k:report[k] for k in ['scope_hd_pixels','changed_front_pixels','changed_tattoo_pixels','output_sha256']},indent=2))


if __name__=='__main__':main()
