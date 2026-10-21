"""Build all1,323 registered-menu source IDs into a private original/Faithful gallery.

No review state or runtime pack is changed; approved status, native preview
availability and chosen treatment are recorded separately. All image bytes local.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import csv,json,hashlib,shutil,collections
repo=Path.cwd();r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'menu-inventory';p.mkdir(exist_ok=True);corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));flows=[x['screen'] for x in csv.DictReader((r.parent/'registered-screens.csv').open())];byid=collections.defaultdict(list);screenids=collections.defaultdict(set)
for x in rows:
 for screen in flows:
  if x['source'].lower().startswith('screens/screens.viv::screens/'+screen.lower()+'.big::'):byid[x['id']].append(x);screenids[x['id']].add(screen)
assert len(byid)==1323
registered_ids=set(byid)
core_groups={'_shared','intMain','battle','options','memoryCard','story','extras','hiScores','jukebox','trans','chyron','_art'}
for x in rows:
 if not x['source'].startswith('screens/screens.viv::'):continue
 entry=x['source'].split('::')[1];parts=entry.split('/');group=parts[1] if len(parts)>2 else '_shared'
 if group not in core_groups:continue
 if x not in byid[x['id']]:byid[x['id']].append(x)
 if not screenids[x['id']]:screenids[x['id']].add(entry.removeprefix('screens/').removesuffix('.big'))
assert len(byid)==1834
cat=json.loads((repo/'config/menu-ui-approved-artwork.json').read_text());approved={x['source_id']:x for x in cat['reviewed_sources']};assert len(approved)==136
native={e['source_id']:dict(path=e['art'],crop=e.get('crop'),state='conditional' if 'conditional' in c['status'] else 'approved') for c in json.loads((repo/'config/menu-ui-source-shaped-exports.json').read_text())['components'].values() for e in c['entries']};treatment={};pending={}
for folder in ['controls-v1-20261020','popup-profile-v1-20261020','menu-details-v1-20261020']:
 items=json.loads((r/folder/'review-items.json').read_text());refs=json.loads((r/folder/'references.json').read_text())
 for item in items:
  for sid in item['source_ids']:treatment[sid]='faithful-retained' if (item.get('kind')=='faithful' or item.get('method','').startswith('Faithful')) or item['key']=='profile-wall' else 'restored'
 if folder.startswith('menu-details'):
  for t in refs['source_tiles']:pending[t['source_id']]=dict(path=folder+'/'+t['draft'],state='pending')
gapmeta=json.loads((repo/'logs/ui-restoration-20261020/menu-widescreen-background-gaps-metadata.json').read_text());gapids={a['source_id'] for group in gapmeta['resources'] if group['label']!='story/tournament' for a in group['assets'] if a['source_id'] not in approved}
assert len(gapids)==10
assets=[]
for sub in ['originals','faithful','custom','thumb-original','thumb-faithful','thumb-custom']:(p/sub).mkdir(exist_ok=True)
def thumb(im,path):
 im=im.convert('RGBA');im.thumbnail((300,190),Image.Resampling.LANCZOS);out=Image.new('RGB',(300,190));d=ImageDraw.Draw(out)
 for y in range(0,190,12):
  for x in range(0,300,12):d.rectangle((x,y,x+11,y+11),fill=(57,57,57) if (x//12+y//12)%2 else (77,77,77))
 out.paste(im,((300-im.width)//2,(190-im.height)//2),im);out.save(path,quality=85)
for sid,aliases in sorted(byid.items(),key=lambda kv:(sorted(screenids[kv[0]])[0],int(kv[1][0]['index']),kv[0])):
 x=aliases[0];w,h=int(x['width']),int(x['height']);a=approved.get(sid);state=('conditional' if 'conditional' in a['status'] else 'approved') if a else 'pending' if sid in pending else 'unreviewed';family=a['family'] if a else '';method=treatment.get(sid,'restored' if a else 'not-custom-reviewed')
 if family=='fire-escape-transition' and any(z['name'].strip()=='9' for z in aliases):method='faithful-retained'
 label=sorted(screenids[sid])[0]+' · #'+x['name'].strip();asset=dict(id=sid,background_gap=sid in gapids,registered=sid in registered_ids,label=label,width=w,height=h,screens=sorted(screenids[sid]),aliases=[dict(source=z['source'],name=z['name'].strip(),index=int(z['index'])) for z in aliases],review_state=state,treatment=method,treatment_label='Reviewed · Faithful HD retained' if method=='faithful-retained' and a else 'Draft · Faithful HD retained' if method=='faithful-retained' else 'Reviewed custom artwork' if a else 'Custom draft available' if sid in pending else 'Faithful HD · no individual custom review',family=family,custom=None,custom_thumbnail=None)
 for kind in ['original','faithful']:
  sub='originals' if kind=='original' else 'faithful';src=corpus/x[kind];dest=p/sub/(sid+'.png');shutil.copy2(src,dest);im=Image.open(dest);assert im.size==(w,h) if kind=='original' else im.size==(w*4,h*4);th=p/('thumb-'+kind)/(sid+'.jpg');thumb(im,th);asset[kind]=str(dest.relative_to(r));asset[kind+'_thumbnail']=str(th.relative_to(r))
 custom=pending.get(sid) if not a else native.get(sid)
 if custom:
  src=r/custom['path'];im=Image.open(src).convert('RGBA');im=im.crop(custom['crop']) if custom.get('crop') else im;assert im.size==(w*4,h*4),(sid,im.size,(w,h));dest=p/'custom'/(sid+'.png');im.save(dest);th=p/'thumb-custom'/(sid+'.jpg');thumb(im,th);asset['custom']=str(dest.relative_to(r));asset['custom_thumbnail']=str(th.relative_to(r))
 asset['search']=' '.join([sid,label,*asset['screens'],*[z['source']+' '+z['name'] for z in asset['aliases']]]).lower();assets.append(asset)
def count(items):
 covered=sum(a['review_state'] in ['approved','conditional'] for a in items)
 return dict(total=len(items),covered=covered,remaining=len(items)-covered,pending=sum(a['review_state']=='pending' for a in items),states=dict(collections.Counter(a['review_state'] for a in items)),treatments=dict(collections.Counter(a['treatment'] for a in items)),custom_previews=sum(bool(a['custom']) for a in items))
scopes=dict(registered=count([a for a in assets if a['registered']]),core=count(assets));assert scopes['registered']['covered']==115 and scopes['registered']['pending']==13;assert scopes['core']['covered']==132 and scopes['core']['pending']==19
counts=scopes['registered'];manifest=dict(schema=1,scope='Registered menu flows plus optional core menu/support resources; distinct original source IDs',counts=counts,scopes=scopes,registered_screens=flows,screens=sorted({screen for a in assets for screen in a['screens']}),assets=assets);(r/'menu-inventory-data.json').write_text(json.dumps(manifest,indent=2)+'\n')
for n in ['menu_inventory.html','menu_inventory.css','menu_inventory.mjs','review_sequence.mjs','review_navigation.css','review_navigation.mjs']:shutil.copy2(repo/'logs/ui-restoration-20261020'/n,r/('inventory.html' if n.endswith('.html') else n))
f=r/'review.html';s=f.read_text();i=s.index('<h1>');s=s if 'href="inventory.html"' in s else s[:i]+'<p><a href="inventory.html">Browse all 1,323 menu textures · Original / Faithful HD / custom status</a></p>\n'+s[i:];f.write_text(s)
counts['local_image_files']=len(list(p.rglob('*.png')))+len(list(p.rglob('*.jpg')));(p/'build-verification.json').write_text(json.dumps(counts,indent=2)+'\n');print(json.dumps(counts))
