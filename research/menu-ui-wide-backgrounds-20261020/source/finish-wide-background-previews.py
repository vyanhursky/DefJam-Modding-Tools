"""Add correctly layered Crib door reuse and review-only original loader-lighting previews."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,csv,numpy as np
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'wide-backgrounds-v1-20261020';widths={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120};c=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows={x['id']:x for x in csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open())}
sid='1c2de449c28536a5491ef5828f81d171544917f2238a18c8a1474ea8685edbae';wall=Image.open(p/'cribOptions-wide-v1.png').convert('RGBA');approved=Image.open(r/'options-softness-v4/options-wide-v4.png').convert('RGBA');assert approved.size==(5120,1440),approved.size
# Layer recipe: root depth1 door translated469.4, root depth3 paper wall/tail over it.
core_modes={}
for mode in ['faithful','original']:
 door=Image.open(c/rows[sid][mode]).convert('RGBA');scale=4 if mode=='faithful' else 1;door=door.crop((0,0,171*scale,487*scale)).resize((513,1461),Image.Resampling.LANCZOS if mode=='faithful' else Image.Resampling.NEAREST);core=Image.new('RGBA',(1920,1440));core.paste(door,(round(469.3999938964844*3),0));layer=Image.open(p/f'cribOptions-core-{ "hd" if mode=="faithful" else "original-hd"}.png').convert('RGBA');core.alpha_composite(layer);core_modes[mode]=core;core.save(p/f'cribOptions-composite-core-{mode}.png')
master=Image.new('RGBA',(5120,1440));master.paste(approved.crop((3520,0,5120,1440)),(3520,0));master.paste(core_modes['faithful'],(1600,0));master.alpha_composite(wall);master.paste(core_modes['faithful'],(1600,0));master.save(p/'cribOptions-composite-wide.png')
for aspect,w in widths.items():
 left=(5120-w)//2;draft=master.crop((left,0,left+w,1440));draft.save(p/f'cribOptions-{aspect}-draft.png');assert np.array_equal(np.array(draft)[:,(w-1920)//2:(w+1920)//2],np.array(core_modes['faithful']))
 for mode in core_modes:
  b=Image.new('RGBA',(w,1440));b.paste(core_modes[mode],((w-1920)//2,0));b.save(p/f'cribOptions-{aspect}-{mode}.png')
for side,x in [('left',1600),('right',3520)]:master.crop((x-384,0,x+384,1440)).save(p/f'cribOptions-{side}-join.png')
# Loading vignette: preview proposed full-stage stretch; no source alpha edits or runtime installation.
sid='11b71080a3890bb179763083899791bd5ad7537e73a4f9d6f79a3c18979fae91';overlay=Image.open(c/rows[sid]['faithful']).convert('RGBA').crop((0,0,2560,1920))
for aspect,w in widths.items():
 for mode in ['draft','faithful','original']:
  base=Image.open(p/f'matchLoa-{aspect}-{mode}.png').convert('RGBA')
  if mode=='draft':light=overlay.resize((w,1440),Image.Resampling.LANCZOS);base.alpha_composite(light)
  else:light=overlay.resize((1920,1440),Image.Resampling.LANCZOS);base.alpha_composite(light,((w-1920)//2,0))
  base.save(p/f'matchLoa-{aspect}-{mode}-lighting.png')
(p/'composition-notes.json').write_text(json.dumps(dict(crib_door_source_id='1c2de449c28536a5491ef5828f81d171544917f2238a18c8a1474ea8685edbae',door_x=469.3999938964844,door_layer='under paper wall/tail',right_extension='already approved options-softness-v4/options-wide-v4.png',crib_composite_center_exact=True,loading_overlay_source_id=sid,loading_overlay_policy='proposed native stretch; review-only preview; runtime route/alpha/mask checks pending',runtime_installed=False),indent=2)+'\n');print('Crib composition/source order exact; loader overlay preview only')
