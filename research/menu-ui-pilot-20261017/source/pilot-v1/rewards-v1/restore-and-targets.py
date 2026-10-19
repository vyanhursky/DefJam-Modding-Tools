"""Restrained source-aligned detail and blank full-height side targets."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib,shutil
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;src=Image.open(p/'wall-source.png').convert('RGBA');faith=src.resize((2796,2048),Image.Resampling.LANCZOS);a=np.array(faith);b=a.copy();raw=Image.open(p/'restoration-raw.png').convert('RGB');assert abs(raw.width/raw.height-699/480)<.008;raw=raw.resize((2796,1920),Image.Resampling.LANCZOS);raw.save(p/'restoration-normalized.png');v=np.asarray(raw,dtype=float);low=np.asarray(raw.filter(ImageFilter.GaussianBlur(4)),dtype=float);lum=(v-low)@np.array([.2126,.7152,.0722]);lab=rgb_to_lab(b[:1920,:,:3]);lab[:,:,0]+=np.clip(lum/255*100,-1.5,1.5)*.35;rgb,_=lab_to_rgb(lab);a[:1920,:,:3]=rgb
# Retain edge vignettes, tile seam and all padding exactly in source-shaped assets.
a[:,:160]=b[:,:160];a[:,2636:]=b[:,2636:];a[:,1996:2092]=b[:,1996:2092];a[1920:]=b[1920:];a[:,:,3]=b[:,:,3];Image.fromarray(a).save(p/'wall-restrained.png');Image.fromarray(a).getchannel('A').save(p/'wall-restrained-alpha.png')
# Every original tile keeps its own complete canvas, including unused columns.
refs=json.loads((p/'references.json').read_text())
for part in refs['parts']:
 n=part['part'];original=Image.open(p/f'wall-{n}-source.png').convert('RGBA');out=np.array(original.resize((original.width*4,2048),Image.Resampling.LANCZOS));x=0 if n==0 else 2044;used=512 if n==0 else 188;out[:,:used*4,:3]=a[:,x:x+used*4,:3];base=np.array(original.resize((original.width*4,2048),Image.Resampling.LANCZOS));out[:,:12*4]=base[:,:12*4];out[:,(used-12)*4:]=base[:,(used-12)*4:];out[1920:]=base[1920:];out[:,:,3]=base[:,:,3];Image.fromarray(out).save(p/f'wall-{n}-restrained.png');assert np.array_equal(out[:,:,3],base[:,:,3]);assert np.array_equal(out[1920:],base[1920:])
core=Image.fromarray(a).convert('RGB').crop((0,0,2796,1920)).resize((2097,1440),Image.Resampling.LANCZOS);core.save(p/'wall-restored-rgb.png');sourcecore=core.crop((120,0,1977,1440));sourcecore.save(p/'wall-interior.png')
# Common world -512..1240; trusted native interior40..659 (619px).
for side in ['left','right']:
 if side=='left':w=2040;im=Image.new('RGB',(w,1440));im.paste(sourcecore.crop((0,0,384,1440)),(1656,0));context=[1656,2040];gap=[0,1656]
 else:w=2127;im=Image.new('RGB',(w,1440));im.paste(sourcecore.crop((1857-384,0,1857,1440)),(0,0));context=[0,384];gap=[384,w]
 im.save(p/f'{side}-target.png')
(p/'restoration-receipt.json').write_text(json.dumps(dict(source_shaped_size=[2796,2048],alpha_exact=True,padding_rows=[1920,2048],edge_vignette_columns_preserved=[0,160,2636,2796],tile_seam_guard=[1996,2092],detail='Lab L only, raw highpass Gaussian4,clamp1.5L,strength.35',native_layouts=dict(buyrewards_crop=29,unlock_crop=50.4),wide_coverage_exception='Native4:3 vignette remains; widescreen exposes new continuous wall beyond trustedinterior40..659 and relocates vignette to outerviewedges. Source-shaped alpha is never replaced.'),indent=2)+'\n');print('Source-shaped alpha/padding/seam protected; two nativeinterior-only targets ready')
