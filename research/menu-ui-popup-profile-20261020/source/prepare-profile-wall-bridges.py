"""Target only128nativepx outside each original boundary; fix original/outercontext."""
from pathlib import Path
from PIL import Image
import json
p=Path('logs/ui-restoration-20261017/pilot-v1/popup-profile-v1-20261020');core=Image.open(p/'profile-wall-source.png').convert('RGB');rows=[]
for side in ['left','right']:
 ext=Image.open(p/f'profile-wall-{side}-extension.png').convert('RGB').resize((534,480),Image.Resampling.LANCZOS);out=Image.new('RGB',(384,480),(128,128,128))
 if side=='left':out.paste(ext.crop((278,0,406,480)),(0,0));out.paste(core.crop((0,0,128,480)),(256,0));order='outerwall128 / editablegap128 / original128'
 else:out.paste(core.crop((512,0,640,480)),(0,0));out.paste(ext.crop((128,0,256,480)),(256,0));order='original128 / editablegap128 / outerwall128'
 out.save(p/f'profile-wall-{side}-bridge-target.png');rows.append(dict(side=side,size=[384,480],gap=[128,0,256,480],layout=order,adoption='Only128nativecolumnsoutsidenativecore;fixedcontextdiscarded'))
(p/'bridge-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
