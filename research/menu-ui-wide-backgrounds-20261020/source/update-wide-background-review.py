"""Build the local seven-scene review without changing approvals or active game packs."""
from pathlib import Path
from PIL import Image
import json
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'wide-backgrounds-v1-20261020';g=json.loads((p/'groups.json').read_text());scenes=[]
for x in g:
 key=x['key'];note='Only new scenery uses imggen; the unlit Faithful HD 4:3 scene core is unchanged.'
 if key=='cribOptions':note='New left wall extension only. Right door scenery reuses the already-approved Options door; the original translucent paper-wall tail remains a separate layer.'
 if key=='matchLoa':note+=' Portraits, venue text, logos and the separate translucent lighting layer stay live in-game.'
 if key=='tips':note+=' Tips text and animated sticker stay live in-game; this preview shows the background plate.'
 for mode in ['original','faithful']:
  im=Image.open(p/f'{key}-32x9-{mode}.png')
  for side,px in [('left',1600),('right',3520)]:im.crop((px-384,0,px+384,1440)).save(p/f'{key}-{side}-join-{mode}.png')
 scenes.append(dict(key=key,label=x['label'],note=note,source_ids=[y['id'] for y in x['parts']],revision='v3' if key=='tips' else 'v1',geometry_note='Authored APT root/parent placements audited offline. Native geometry, clips, lighting, fades and active loading route still require in-game checks. Centered native stage640x480; master5120x1440; corex1600..3520; five aspect ratios.'))
(p/'review-data.json').write_text(json.dumps(dict(schema=1,status='unapproved artwork; uninstalled',scenes=scenes),indent=2)+'\n')
for name in ['review.html','inventory.html']:
 f=r/name;s=f.read_text();banner='<aside style="padding:12px;background:#28331d;border:1px solid #6b7f4e;margin:12px"><a href="wide-backgrounds.html">New: seven widescreen background candidates · Story, Crib Options and pre-fight loading</a></aside>'
 if 'New: seven widescreen background candidates' not in s:
  if '<body>' in s:s=s.replace('<body>','<body>'+banner,1)
  else:
   import re
   s=re.sub(r'(<body[^>]*>)',lambda m:m[1]+banner,s,count=1)
  f.write_text(s)
inventory=r/'menu-inventory-data.json';data=json.loads(inventory.read_text());links={sid:'wide-backgrounds.html?scene='+x['key'] for x in scenes for sid in x['source_ids']}
for asset in data['assets']:
 if asset['id'] in links:asset['wide_review_url']=links[asset['id']]
inventory.write_text(json.dumps(data,indent=1)+'\n')
print('Seven scene review and additive links ready; approval ledgers unchanged')
