import contextlib,io,runpy,json,struct,re
from pathlib import Path
import numpy as np
from PIL import Image
with contextlib.redirect_stdout(io.StringIO()): d=runpy.run_path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py')
a=d['apt']; h=d['hd_assets']; root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
assets=json.loads((root/'corpus.json').read_text())['assets']
result={}
for movie in ['mainMenu','support/mainMenuLogosIcons']:
 base=movie.split('/')[-1]; inner=dict(h.archive_entries(h.unpack_refpack(d['outer']['screens/intMain/'+movie+'.big'])))
 data,symbols,rels,_=d['object_info'](inner[base+'.o']); b,k,m,c,_=a.load_movie('screens/screens.viv','screens/intMain/'+movie+'.big')
 byname={int(x['name']):asset for asset in assets for x in asset['aliases'] if ('intMain/'+movie+'.big::') in x['source']}
 output={'object_sha256':d['digest'](inner[base+'.o']), 'apt_sha256':d['digest'](b), 'sprites':{},'shapes':[]}
 for i,cr in enumerate(c):
  if cr and cr['type']=='Sprite':
   if movie=='mainMenu' and i!=50:continue
   output['sprites'][i]=cr['frames']
 for shape in ([24,28,32,35,38,41,45,49] if movie=='mainMenu' else [i for i,cr in enumerate(c) if cr and cr['type']=='Shape']):
  bounds=struct.unpack_from('<4f',b,c[shape]['offset']+8)
  model=symbols.get('__Model:::'+str(shape));sc=struct.unpack_from('<4f',data,model['offset']+92) if model else None
  out={'shape':shape,'bounds':bounds,'parts':[]}
  for name,s in symbols.items():
   match=re.fullmatch('__RM:::__GP_RM_'+str(shape)+'_(\\d+)',name)
   if not match:continue
   part=int(match[1]);rm=s['offset'];ts=rels.get(rm+0x48,'')
   if 'SHAPENAME=' not in ts: continue
   im=int(re.search(r'SHAPENAME=(\d+),',ts)[1]);asset=byname[im]
   mat=struct.unpack_from('<16f',data,struct.unpack_from('<I',data,rm+0x58)[0]); vb=symbols[f'__VB:::__GPvb_9_{part}_{shape}']['offset'];ptr,count,stride,flags,off=struct.unpack_from('<5I',data,vb)
   enc=[struct.unpack_from('<3h',data,off+i*stride) for i in range(count//stride)]
   pos=[[(q[j]+16384)*sc[j]/16384 for j in range(3)] for q in enc];uv=[[p[0]+mat[12],p[1]+mat[13]] for p in pos]
   px=np.array(Image.open(root/asset['original']).convert('RGBA'));alp=px[:,:,3];rgb=px[:,:,:3]; non=alp>0
   out['parts'].append({'part':part,'image':im,'id':asset['id'],'original':str(root/asset['original']),'size':[asset['width'],asset['height']],'matrix':mat,'positions':pos,'uv':uv,'alpha_range':[int(alp.min()),int(alp.max())],'alpha_counts':[int((alp==0).sum()),int(((alp>0)&(alp<255)).sum()),int((alp==255).sum())],'unique_rgb':np.unique(rgb.reshape(-1,3),axis=0).tolist() if len(np.unique(rgb.reshape(-1,3),axis=0))<12 else 'many','rgb_at_nonzero_alpha_range':[[int(rgb[:,:,j][non].min()),int(rgb[:,:,j][non].max())] for j in range(3)]})
  output['shapes'].append(out)
 result[movie]=output
Path('/private/tmp/emblem_metadata.json').write_text(json.dumps(result,indent=2))
for movie,out in result.items():
 print(movie,out['object_sha256'],out['apt_sha256'])
 for s in out['shapes']:
  print('SHAPE',s['shape'],'bounds',s['bounds'])
  for p in s['parts']:
   print(' ',p['part'],'img',p['image'],p['size'],'xy',[[round(min(q[j] for q in p['positions']),4),round(max(q[j] for q in p['positions']),4)] for j in range(2)],'UV',[[round(min(q[j] for q in p['uv']),4),round(max(q[j] for q in p['uv']),4)] for j in range(2)],'tr',p['matrix'][12:14],'alpha',p['alpha_range'],p['alpha_counts'],'RGB',p['unique_rgb'],'nonzero',p['rgb_at_nonzero_alpha_range'])
 print('SPRITES',json.dumps(out['sprites']) if movie!='mainMenu' else '50 done')
