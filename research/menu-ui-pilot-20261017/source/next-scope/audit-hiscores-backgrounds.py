import contextlib,io,runpy,json,struct,re
from pathlib import Path
import numpy as np
from PIL import Image
with contextlib.redirect_stdout(io.StringIO()):d=runpy.run_path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py')
h=d['hd_assets'];apt=d['apt'];root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');assets=json.loads((root/'corpus.json').read_text())['assets'];results=[]
for movie,names in [('hiScores',[2,1])]:
 entry='screens/hiScores/'+movie+'.big';inner=dict(h.archive_entries(h.unpack_refpack(d['outer'][entry])));data,symbols,rels,_=d['object_info'](inner[movie+'.o']);b,k,m,c,_=apt.load_movie('screens/screens.viv',entry)
 byname={int(z['name']):a for a in assets for z in a['aliases'] if '/'+movie+'.big::' in z['source']}
 matchshapes=set()
 for name,sym in symbols.items():
  mt=re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)',name)
  if mt:
   ts=rels.get(sym['offset']+0x48,'');im=re.search(r'SHAPENAME=(\d+),',ts)
   if im and int(im[1]) in names:matchshapes.add(int(mt[1]))
 out={'movie':movie,'apt_sha256':d['digest'](b),'object_sha256':d['digest'](inner[movie+'.o']),'root':m,'shapes':[],'ancestors':{},'image_ids':{str(n):byname[n]['id'] for n in names}}
 for shape in sorted(matchshapes):
  bbox=struct.unpack_from('<4f',b,c[shape]['offset']+8);sc=struct.unpack_from('<4f',data,symbols['__Model:::'+str(shape)]['offset']+92);outshape={'shape':shape,'bbox':bbox,'parts':[]}
  for name,sym in symbols.items():
   mt=re.fullmatch('__RM:::__GP_RM_'+str(shape)+r'_(\d+)',name)
   if not mt:continue
   part=int(mt[1]);rm=sym['offset'];ts=rels.get(rm+0x48,'');im=int(re.search(r'SHAPENAME=(\d+),',ts)[1]);a=byname[im];mat=struct.unpack_from('<16f',data,struct.unpack_from('<I',data,rm+0x58)[0]);vbo=symbols[f'__VB:::__GPvb_9_{part}_{shape}']['offset'];ptr,count,stride,flags,off=struct.unpack_from('<5I',data,vbo);enc=[struct.unpack_from('<3h',data,off+i*stride) for i in range(count//stride)];pos=[[(q[j]+16384)*sc[j]/16384 for j in range(3)] for q in enc];uv=[[p[0]*mat[0]+p[1]*mat[4]+mat[12],p[0]*mat[1]+p[1]*mat[5]+mat[13]] for p in pos]
   px=np.array(Image.open(root/a['original']).convert('RGBA'));al=px[:,:,3]
   outshape['parts'].append({'part':part,'image':im,'source_id':a['id'],'original':str(root/a['original']),'size':[a['width'],a['height']],'material_matrix':mat,'quantized_positions':pos,'quantized_uv':uv,'alpha_range':[int(al.min()),int(al.max())],'alpha_counts':[int((al==0).sum()),int(((al>0)&(al<255)).sum()),int((al==255).sum())]})
  out['shapes'].append(outshape)
 relevant=set(matchshapes)
 while True:
  added=[]
  for idx,ch in enumerate(c):
   if ch and idx not in relevant and any(item.get('character') in relevant for f in ch.get('frames',[]) for kind,item in f if kind=='PlaceObject'):added.append(idx)
  if not added:break
  relevant.update(added)
 for idx in sorted(relevant-set(matchshapes)):out['ancestors'][idx]=c[idx]
 out['relevant_character_ids']=sorted(relevant);results.append(out)
Path('logs/ui-restoration-20261017/next-scope/hiscores-background-metadata.json').write_text(json.dumps(results,indent=2))
for o in results:
 print('MOVIE',o['movie'],'rootframes',len(o['root']['frames']),'shapes',[s['shape'] for s in o['shapes']],'ancestors',[(i,v['type'],len(v.get('frames',[]))) for i,v in o['ancestors'].items()])
 for s in o['shapes']:
  print(' shape',s['shape'],'bbox',s['bbox'])
  for p in sorted(s['parts'],key=lambda p:p['part']):print('  part',p['part'],'img',p['image'],p['size'],'UV',[[round(min(q[j] for q in p['quantized_uv']),4),round(max(q[j] for q in p['quantized_uv']),4)] for j in range(2)],'tr',p['material_matrix'][12:14],'alpha',p['alpha_range'])
 for idx,ch in o['ancestors'].items():
  print(' ancestor',idx)
  for fi,f in enumerate(ch.get('frames',[])):
   ff=[(kind,item) for kind,item in f if kind in ['FrameLabel','RemoveObject'] or kind=='PlaceObject' and item.get('character') in o['relevant_character_ids']]
   if ff:print('   frame',fi,ff)
 print(' ROOT relevant placements')
 for fi,f in enumerate(o['root']['frames']):
  ff=[(kind,item) for kind,item in f if kind in ['FrameLabel','RemoveObject'] or kind=='PlaceObject' and item.get('character') in o['relevant_character_ids']]
  if ff:print(' frame',fi,ff)
