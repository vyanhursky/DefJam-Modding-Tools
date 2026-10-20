"""Coordinates-only audit of the three shared popup movies; no images emitted."""
import contextlib, csv, hashlib, importlib.util, io, json, os, re, runpy, struct
from pathlib import Path
from PIL import Image
import numpy as np

repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
with contextlib.redirect_stdout(io.StringIO()): d=runpy.run_path(str(repo/'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
h,apt,outer=d['hd_assets'],d['apt'],d['outer']
corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
assets=json.loads((corpus/'corpus.json').read_text())['assets']
byname={}
for a in assets:
 for z in a.get('aliases',[]):
  try: byname[int(z['name'])]=a
  except (TypeError,ValueError): pass
def objinfo(obj):
 shoff=struct.unpack_from('<I',obj,32)[0]; es,n,ni=struct.unpack_from('<HHH',obj,46)
 secs=[struct.unpack_from('<10I',obj,shoff+i*es) for i in range(n)]; namesec=secs[ni]; names=obj[namesec[4]:namesec[4]+namesec[5]]
 sn={names[s[0]:].split(b'\0')[0].decode():s for s in secs}; ds=sn['.data']; data=obj[ds[4]:ds[4]+ds[5]]
 sy=sn['.symtab']; st=secs[sy[6]]; strings=obj[st[4]:st[4]+st[5]]; symbols=[]
 for p in range(sy[4],sy[4]+sy[5],16):
  nm,val,size,info,other,sec=struct.unpack_from('<IIIBBH',obj,p); symbols.append(dict(name=strings[nm:].split(b'\0')[0].decode(),offset=val,size=size))
 rel=sn['.rel.data']; rels={}
 for p in range(rel[4],rel[4]+rel[5],8):
  off,info=struct.unpack_from('<II',obj,p); rels[off]=symbols[info>>8]['name']
 return data,{s['name']:s for s in symbols if s['name']},rels
movies=[('feloader','screens/feloader.big','feloader'),('beloader','screens/beloader.big','beloader'),('message','screens/intMain/message.big','message')]
out={'schema':1,'scope':'all material references with corpus canvases >=128x128 in named movies','movies':[]}
for mov,entry,base in movies:
 inner=dict(h.archive_entries(h.unpack_refpack(outer[entry]))); obj=inner[base+'.o']; data,symbols,rels=objinfo(obj)
 b,k,root,chars,_=apt.load_movie('screens/screens.viv',entry)
 aliases={}
 for a in assets:
  for z in a.get('aliases',[]):
   if f'/{base}.big::' in z['source']:
    try: aliases[int(z['name'])]=a
    except (TypeError,ValueError): pass
 mo={'movie':mov,'archive_entry':entry,'object_sha256':hashlib.sha256(obj).hexdigest(),'apt_sha256':hashlib.sha256(b).hexdigest(),'root':root,'uses':[]}
 for sname,sym in symbols.items():
  m=re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)',sname)
  if not m: continue
  shape,part=map(int,m.groups()); texsym=rels.get(sym['offset']+0x48,''); im=re.search(r'SHAPENAME=(\d+),',texsym)
  if not im: continue
  image=int(im[1]); a=aliases.get(image) or byname.get(image)
  if not a or a['width']<128 or a['height']<128: continue
  mat=struct.unpack_from('<16f',data,struct.unpack_from('<I',data,sym['offset']+0x58)[0])
  vbo=symbols.get(f'__VB:::__GPvb_9_{part}_{shape}')
  if not vbo: continue
  ptr,count,stride,flags,off=struct.unpack_from('<5I',data,vbo['offset']); enc=[struct.unpack_from('<3h',data,off+i*stride) for i in range(count//stride)]
  scale=struct.unpack_from('<4f',data,symbols[f'__Model:::{shape}']['offset']+92)
  pos=[tuple((q[j]+16384)*scale[j]/16384 for j in range(3)) for q in enc]
  uv=[(p[0]*mat[0]+p[1]*mat[4]+mat[12],p[0]*mat[1]+p[1]*mat[5]+mat[13]) for p in pos]
  png=corpus/a['original']; alpha=np.array(Image.open(png).convert('RGBA'))[:,:,3]
  alias=next((z for z in a.get('aliases',[]) if f'/{base}.big::' in z['source'] and z.get('name','').strip().isdigit()),None)
  mo['uses'].append({'shape':shape,'part':part,'image':image,'source_id':a['id'],'source':alias['source'] if alias else None,'texture_alias_name':alias['name'].strip() if alias else None,'canvas':[a['width'],a['height']],'alpha_range':[int(alpha.min()),int(alpha.max())],'alpha_counts':[int((alpha==0).sum()),int(((alpha>0)&(alpha<255)).sum()),int((alpha==255).sum())],'shape_bounds':struct.unpack_from('<4f',b,chars[shape]['offset']+8),'material_symbol':sname,'texture_symbol':texsym,'matrix':mat,'encoded_xyz':enc,'positions':pos,'uv':uv,'uv_bounds':[[min(p[j] for p in uv),max(p[j] for p in uv)] for j in (0,1)],'tiles_outside_canvas':any(min(p[j] for p in uv)<0 or max(p[j] for p in uv)>[a['width'],a['height']][j] for j in (0,1))})
 # Include ancestry of every textured character by following placements from root.
 wanted={u['shape'] for u in mo['uses']}; relevant=set(wanted)
 while True:
  new={idx for idx,ch in enumerate(chars) if ch and idx not in relevant and any(kind=='PlaceObject' and item.get('character') in relevant for f in ch.get('frames',[]) for kind,item in f)}
  if not new: break
  relevant|=new
 mo['hierarchy']={str(i):chars[i] for i in sorted(relevant)}
 labels=[]
 for parent,ch in enumerate(chars):
  if ch:
   for fi,frame in enumerate(ch.get('frames',[])):
    for kind,item in frame:
     if kind=='PlaceObject' and item.get('name') in ('titleBacker','noteBacker','messageBacker','buttonBacker','paper'):
      child=item.get('character'); c=chars[child] if child is not None else None
      labels.append({'parent':parent,'frame':fi,'name':item['name'],'character':child,'type':c['type'] if c else None,'frames':len(c.get('frames',[])) if c else 0})
 mo['named_placements']=labels
 mo['named_symbols']=[n for n in symbols if any(x.lower() in n.lower() for x in ('backer','note','message','button','title'))]
 out['movies'].append(mo)
Path('logs/ui-restoration-20261020/shared-popup-metadata-20261020.json').write_text(json.dumps(out,indent=2))
for mo in out['movies']:
 print(mo['movie'],'uses',len(mo['uses']),'named_symbols',mo['named_symbols'])
 for u in mo['uses']:
  print(u['shape'],u['part'],u['image'],u['source_id'][:16],u['canvas'],'UV',u['uv_bounds'],'outside',u['tiles_outside_canvas'],'alpha',u['alpha_range'],u['alpha_counts'])
