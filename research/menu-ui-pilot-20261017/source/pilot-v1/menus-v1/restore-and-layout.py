"""Restrained source-shaped color/alpha assembly and independent menu layers.

Uses the same accepted fine-lightness policy as the earlier background batch.
Everything generated remains a review draft; no workshop/runtime write.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb,box_blur
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();records=[]
configs={'options-panel':dict(active=[574,480],seams=[512],boxes=[[65,106,340,145],[70,250,465,135],[55,350,320,75],[390,100,165,160]]),'options-wall':dict(active=[171,487],seams=[],boxes=[[0,85,60,330],[130,300,126,55]]),'jukebox-background':dict(active=[640,480],seams=[512],boxes=[[30,85,570,360]])}
for label,cfg in configs.items():
 base=Image.open(p/(label+'-faithful.png')).convert('RGBA');a=np.array(base);rgb=a[:,:,:3];lab=rgb_to_lab(rgb);raw=Image.open(p/(label+'-raw.png')).convert('RGBA');rl=rgb_to_lab(np.array(raw.convert('RGB').resize(base.size,Image.Resampling.LANCZOS)))[:,:,0];L=lab[:,:,0];detail=np.clip(.25*((rl-box_blur(rl,8))-(L-box_blur(L,8))),-1,1)
 h,w=a.shape[:2];held=np.zeros((h,w),bool);held[:16]=held[-16:]=True;held[:,:16]=held[:,-16:]=True;aw,ah=cfg['active'];held[ah*4:]=True;held[:,aw*4:]=True
 for x in cfg['seams']:held[:,(x-4)*4:(x+4)*4]=True
 for x,y,bw,bh in cfg['boxes']:held[y*4:(y+bh)*4,x*4:(x+bw)*4]=True
 held|=(box_blur((a[:,:,3]==255).astype(float),4)<.999999)|(rgb.max(2)<=16)
 allowed=box_blur((~held).astype(float),4)*(~held);nl=lab.copy();nl[:,:,0]+=detail*allowed;new,clip=lab_to_rgb(nl);new[held|clip]=rgb[held|clip];out=np.dstack([new,a[:,:,3]])
 assert np.array_equal(out[:,:,3],a[:,:,3]);assert np.array_equal(out[held],a[held]);Image.fromarray(out).save(p/(label+'-restrained.png'));Image.fromarray(held.astype('uint8')*255).save(p/(label+'-protected.png'));delta=rgb_to_lab(new)-lab
 records.append(dict(label=label,source_size=[base.width//4,base.height//4],raw_size=list(raw.size),raw_normalization='full returned canvas to faithful4x; surface proposal only, geometry and alpha rejected',size=list(base.size),raw_sha256=sha(p/(label+'-raw.png')),baseline_sha256=sha(p/(label+'-faithful.png')),output_sha256=sha(p/(label+'-restrained.png')),alpha_exact=True,protected_exact=True,changed_rgb_pixels=int(np.any(rgb!=new,2).sum()),median_Lab=np.median(delta[a[:,:,3]>0],axis=0).tolist(),active=cfg['active'],boxes=cfg['boxes'],max_fine_L=1,strength=.25))
(p/'restoration-receipt.json').write_text(json.dumps(dict(records=records,processor_sha256=sha(Path(__file__))),indent=2)+'\n')
# Preserve original stored texture IDs/canvases, including unused texels.
splits=[]
for label,names in [('options-panel',['options-71','options-70']),('jukebox-background',['beatbox-20','beatbox-19'])]:
 im=Image.open(p/(label+'-restrained.png'))
 for i,name in enumerate(names):
  base=Image.open(p/(name+'-faithful.png')).convert('RGBA');out=base.copy();w=base.width;x=i*2048;out.paste(im.crop((x,0,x+w,base.height)),(0,0));out.paste(base.crop((0,1920,base.width,base.height)),(0,1920));out.save(p/(name+'-restrained.png'));splits.append(dict(name=name,parent=label,sha256=sha(p/(name+'-restrained.png'))))
(p/'splits.json').write_text(json.dumps(splits,indent=2)+'\n')
# Approximate authored top-state layout: wall moves separately in game. Clip
# panel to574x480 and wall to171x487 for original; full256 wall stored columns
# can supply the next85 columns of scenery in widened review/integration.
def layout(variant,known=False):
 def im(label):
  if variant=='source':return Image.open(p/(label+'-source.png')).convert('RGBA')
  return Image.open(p/(label+'-'+variant+'.png')).convert('RGBA')
 def scaled(label,rect):return im(label).crop(rect).resize((int((rect[2]-rect[0])*(3 if variant=='source' else .75)),int((rect[3]-rect[1])*(3 if variant=='source' else .75))),Image.Resampling.BILINEAR if variant=='source' else Image.Resampling.LANCZOS)
 k=1 if variant=='source' else 4
 # Keep stored sampling support beyond the geometry edge; cropping at171
 # before filtering creates a false translucent last column in the4:3view.
 wall=scaled('options-wall',(0,0,256*k,487*k));panel=scaled('options-panel',(0,0,574*k,480*k));canvas=Image.new('RGBA',(2176 if known else 1920,1440),(0,0,0,255));plane=wall.transform(canvas.size,Image.Transform.AFFINE,(1,0,-469.4*3,0,1,0),Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));canvas.alpha_composite(plane);canvas.alpha_composite(panel,(0,0));return canvas
layout('source').save(p/'options-original-layout.png');layout('restrained').save(p/'options-center.png');layout('restrained',True).save(p/'options-known.png')
for variant in ['source','restrained']:
 im=Image.open(p/('jukebox-background-'+variant+'.png')).convert('RGBA');factor=1 if variant=='source' else 4;im=im.crop((0,0,640*factor,480*factor)).resize((1920,1440),Image.Resampling.BILINEAR if variant=='source' else Image.Resampling.LANCZOS);im.save(p/('jukebox-original-layout.png' if variant=='source' else 'jukebox-center.png'))
# Independent bottom strip remains a source reference; not baked into backdrop.
wide=[]
for label in ['options','jukebox']:
 known=Image.open(p/(label+'-known.png' if label=='options' else label+'-center.png')).convert('RGBA');target=Image.new('RGBA',(3072,1024),(0,0,0,255));size=(round(known.width*.6),864);small=known.resize(size,Image.Resampling.LANCZOS);target.paste(small,(960,0));target.save(p/(label+'-outpaint-target.png'));guide=target.copy();d=ImageDraw.Draw(guide);d.rectangle((960,0,960+size[0]-1,863),outline='#55eaff',width=5);d.line((0,864,3071,864),fill='#ff65c0',width=4);guide.save(p/(label+'-outpaint-guide.png'))
 wide.append(dict(label=label,target=[3072,1024],protected=[960,0,size[0],864],active_height=864,final_canvas=[5120,1440],known_context_width=known.width,original_stage=[1600,0,1920,1440],options_wall_x=469.4 if label=='options' else None,options_wall_extra_stored_columns_reused=85 if label=='options' else 0,source_layers='independent options panel/wall; no live UI/lighting baked' if label=='options' else 'backdrop only; bottom strip, list mask, lighting and text remain separate'))
(p/'outpaint-layout.json').write_text(json.dumps(wide,indent=2)+'\n');print('3 restrained layers;4source-shaped splits;2source layouts and widened targets')
