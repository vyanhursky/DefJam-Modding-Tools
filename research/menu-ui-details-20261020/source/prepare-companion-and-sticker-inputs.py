"""Historical preparation of proven venue companions and four tile-grouped sticker edit inputs.

Run only on a COPY after prepare-large-menu-batch.py and static mapping audits.
Retain fullsourcecanvases; fractional native transforms stay in auditmetadata.
"""
from pathlib import Path
from PIL import Image
import json,shutil,hashlib
p=Path('logs/ui-restoration-20261017/pilot-v1/menu-details-v1-20261020');data=json.loads((p/'shortlist-sources.json').read_text());root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');assets=json.loads((root/'corpus.json').read_text())['assets']
for name in ['152','157']:
 matches=[(a,z) for a in assets for z in a['aliases'] if '/chsVenue.big::' in z['source'] and str(z['name']).strip()==name];assert len(matches)==1;a,z=matches[0];key='asset-'+a['id'][:12];shutil.copy2(root/a['original'],p/(key+'-source.png'));data.append(dict(priority_group='Venue frame/mask pieces identified',id=a['id'],source=z['source'],index=str(z['index']),name=name,width=str(a['width']),height=str(a['height']),original=a['original'],key=key,source_size=[a['width'],a['height']],source_sha256=hashlib.sha256((root/a['original']).read_bytes()).hexdigest(),source_file=key+'-source.png'))
(p/'sources.json').write_text(json.dumps(data,indent=2)+'\n');byname={(a['source'].split('::')[1],int(a['name'])):a for a in data};refs=[]
for key,label,shape,group,width,overhang in [('start-short','Press START',29,[(28,0,128),(27,128,6)],134,0),('start-french-short','Appuie sur START',32,[(31,0,128),(30,128,39)],167,-12),('start-button','Press START button',36,[(35,0,128),(34,128,55)],183,0),('start-french-long','Appuie sur la touche START',38,[(37,0,244)],244,-29)]:
 out=Image.new('RGBA',(width,40));parts=[]
 for name,x,w in group:
  a=byname[('screens/intMain/prestart.big',name)];im=Image.open(p/a['source_file']).convert('RGBA');out.paste(im.crop((0,0,w,40)),(x,0));parts.append(dict(source_id=a['id'],name=name,key=a['key'],x=x,width=w,active_height=40))
 out.save(p/(key+'-source.png'));wide=out.resize((width*4,160),Image.Resampling.LANCZOS);target=Image.new('RGBA',(1024,512));xy=((1024-wide.width)//2,176);target.paste(wide,xy);target.save(p/(key+'-edit-target.png'));refs.append(dict(key=key,label=label,shape=shape,parts=parts,native_size=[width,40],local_overhang_x=overhang,preview_policy='Integertexelassembly;fractionalUV/Apttransformsretainedinaudit,notroundedatgameexport',edit_target_size=[1024,512],edit_crop=[xy[0],xy[1],xy[0]+wide.width,xy[1]+160]))
(p/'sticker-groups.json').write_text(json.dumps(refs,indent=2)+'\n')
