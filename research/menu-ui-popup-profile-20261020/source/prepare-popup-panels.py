"""Prepare source-geometry-led popup/profile/autosave edit inputs without modifying originals.

Integer used-texel mosaics are review/authoring references. Exact fractional UVs,
APT transforms, clip order and platform/language selection remain in audit JSON.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json
p=Path('logs/ui-restoration-20261017/pilot-v1/popup-profile-v1-20261020');src=json.loads((p/'survey-sources.json').read_text());byname={(a['source'].split('::')[1],int(a['name'])):a for a in src};groups=[]
def group(key,label,movie,parts,size,kind='paper',note='',preview=None):
 out=Image.new('RGBA',size);refs=[]
 for name,box,xy in parts:
  a=byname[(movie,name)];im=Image.open(p/a['source_file']).convert('RGBA');out.paste(im.crop(box),xy);refs.append(dict(source_id=a['id'],source_key=a['key'],name=name,source_file=a['source_file'],stored_size=list(im.size),crop=list(box),offset=list(xy)))
 out.save(p/(key+'-source.png'));g=dict(key=key,label=label,parts=refs,texel_size=list(size),native_size=preview or list(size),kind=kind,note=note,source_file=key+'-source.png',preview_transform='Headerleft256texels→343nativepx;right77unchanged' if preview else 'Integer used-texel mosaic,notfullscreenruntimecapture');groups.append(g)
 if kind=='paper':
  # Use a padded square edit target for thin strips, never stretch the target graphics.
  if size[0]/size[1]>3:
   scale=3;im=out.resize((size[0]*scale,size[1]*scale),Image.Resampling.LANCZOS);cw=1024;ch=512;xy=((cw-im.width)//2,(ch-im.height)//2);assert xy[0]>=0 and xy[1]>=0;tar=Image.new('RGBA',(cw,ch));tar.paste(im,xy);g['edit_crop']=[xy[0],xy[1],xy[0]+im.width,xy[1]+im.height];g['edit_target_size']=[cw,ch]
  else:tar=out;g['edit_crop']=None;g['edit_target_size']=list(out.size)
  tar.save(p/(key+'-edit-target.png'));g['edit_file']=key+'-edit-target.png'
 return g
m='screens/options/userID.big'
group('profile-wall','Profile · brick wall and paper',m,[(87,(0,0,640,480),(0,0))],(640,480),'wall','Native full-stage source; baked paper/emblem protected; source storage1024x512padding stays exact.')
group('profile-list','Profile · list paper and red selector',m,[(91,(0,0,187,256),(0,0)),(90,(0,0,187,72),(0,256))],(187,328),'paper','Shape92used187x328; nativeorigin17,7; live profile text/scroll remains separate.')
group('profile-shadow','Profile · two-part soft backing',m,[(127,(0,0,256,256),(0,0)),(125,(0,0,256,116),(0,256))],(256,372),'faithful','Shape128two-part black alpha backing; APTwidth292vsrendered256; preserve soft silhouette.')
group('profile-radial','Profile · radial overlay',m,[(120,(0,0,256,256),(0,0))],(256,256),'faithful','Source256squareeffect sampled across640x480; isolated source preview only,actualscalingunverified.')
group('profile-noids-fr','Profile · AUCUNE IDENTITE',m,[(2,(0,0,256,97),(0,0))],(256,97),'faithful','Exact French stamp paths and alpha; nativebboxoverhang retainedinaudit.')
group('profile-noids-en','Profile · NO USER IDs',m,[(6,(0,0,256,109),(0,0))],(256,109),'faithful','Exact English stamp paths and alpha; nativepositionretainedinaudit.')
group('shared-popup','Shared popup · torn paper', 'screens/beloader.big',[(127,(0,0,256,256),(0,0)),(126,(0,0,151,256),(256,0))],(407,256),'paper','Shared feloader/beloader/intMainmessage IDs; texelquadsheight256,APT310isnotfilled.')
group('shared-header','Shared popup · header and control strip','screens/feloader.big',[(30,(0,0,256,96),(0,0)),(31,(0,0,77,96),(256,0))],(333,96),'paper','Shape32: leftUV256→geometry343,right77; exact fractional sampling retained. Nativeboundy-23..73.',[420,96])
for key,label,name,w,h in [('platform-card','Shared popup · card diagram',220,118,128),('platform-cube','Shared popup · GameCube card',236,118,128),('platform-paper','Shared popup · layered note',244,128,112)]:group(key,label,'screens/beloader.big',[(name,(0,0,w,h),(0,0))],(w,h),'paper','Live text/control overlays stay separate; source graphic paths protected.')
m='screens/memoryCard/autosaveMessage.big'
group('autosave-ps2-en','Autosave · PS2 English',m,[(42,(0,0,512,256),(0,0)),(41,(0,0,511,144),(1,256))],(512,400),'paper','Shape43 inPS2bkg50frame0; lowerquadstartsx1.029,UVx.029..511.011. IntegerpreviewcropsretainedseparatefromexactnativeUV.')
group('autosave-ps2-fr','Autosave · PS2 French',m,[(47,(0,0,512,256),(0,0)),(46,(0,0,512,144),(0,256))],(512,400),'paper','Shape48 inPS2bkg50languageframe2; pairFrenchwithFrench. Runtimeplatform/language unverified.')
group('autosave-gc','Autosave · GameCube A/B',m,[(60,(0,0,512,256),(0,0)),(59,(0,0,512,119),(0,256))],(512,375),'paper','GCbkg64Shape61, rootScale1.021484; languageonlyswitcheslivetext; exact nativeUVretained.')
group('autosave-xbox','Autosave · Xbox console',m,[(67,(0,0,467,256),(0,0))],(467,256),'paper','Xboxbkg70Shape68; texturequadheight256vsAPT313, noinventedfill; sourceconsoleiconexact.')
(p/'panel-groups.json').write_text(json.dumps(groups,indent=2)+'\n')
# Wall inputs: exact640x480core plus534nativepx on bothsides for32:9.
wall=Image.open(p/'profile-wall-source.png').convert('RGBA');wall.save(p/'profile-wall-edit-target.png');spec=[]
for side in ['left','right']:
 target=Image.new('RGBA',(790,480),(128,128,128,255));target.paste(wall.crop((0,0,256,480) if side=='left' else (384,0,640,480)),(534,0) if side=='left' else (0,0));target.save(p/f'profile-wall-{side}-edit-target.png');spec.append(dict(side=side,size=[790,480],gap=[0,0,534,480] if side=='left' else [256,0,790,480],fixed_context=[534,0,790,480] if side=='left' else [0,0,256,480]))
(p/'wide-inputs.json').write_text(json.dumps(spec,indent=2)+'\n');print('15studies,22sources;11paper/wall candidates+4Faithfuleffects/stamps;wall640x480cropprotected')
