from pathlib import Path
import contextlib,io,runpy,json,struct,re,hashlib,csv
root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
with contextlib.redirect_stdout(io.StringIO()): d=runpy.run_path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py')
h=d['hd_assets']; apt=d['apt']; outer=d['outer']; digest=d['digest']; object_info=d['object_info']
assets=json.loads((root/'corpus.json').read_text())['assets']
entry='screens/battle/chsVenue.big'; movie='chsVenue'
inner=dict(h.archive_entries(h.unpack_refpack(outer[entry])))
obj=inner[movie+'.o']; data,symbols,rels,_=object_info(obj); b,k,m,c,_=apt.load_movie('screens/screens.viv',entry)
byname={int(z['name']):a for a in assets for z in a['aliases'] if '/'+movie+'.big::' in z['source']}
results=[]
for name in [143,145,150,152,157]:
 candidates=[]
 for symname,sym in symbols.items():
  mt=re.fullmatch(r'__RM:::__GP_RM_(\d+)_(\d+)',symname)
  if not mt: continue
  ts=rels.get(sym['offset']+0x48,''); im=re.search(r'SHAPENAME=(\d+),',ts)
  if im and int(im[1])==name: candidates.append((int(mt[1]),int(mt[2]),sym['offset'],ts))
 results.append({'image_name':name,'uses':[]})
 for shape,part,rm,ts in candidates:
  sc=struct.unpack_from('<4f',data,symbols['__Model:::'+str(shape)]['offset']+92)
  mat=struct.unpack_from('<16f',data,struct.unpack_from('<I',data,rm+0x58)[0])
  vbo=symbols[f'__VB:::__GPvb_9_{part}_{shape}']['offset']; ptr,count,stride,flags,off=struct.unpack_from('<5I',data,vbo)
  enc=[struct.unpack_from('<3h',data,off+i*stride) for i in range(count//stride)]
  pos=[[(q[j]+16384)*sc[j]/16384 for j in range(3)] for q in enc]
  uv=[[p[0]*mat[0]+p[1]*mat[4]+mat[12],p[0]*mat[1]+p[1]*mat[5]+mat[13]] for p in pos]
  a=byname[name];
  results[-1]['uses'].append({'shape':shape,'part':part,'apt_bounds':struct.unpack_from('<4f',b,c[shape]['offset']+8),'rm_symbol':f'__GP_RM_{shape}_{part}','material_symbol':ts,'matrix':mat,'encoded_xyz':enc,'positions':pos,'uv_pixels':uv,'source_id':a['id'],'original':str(root/a['original']),'size':[a['width'],a['height']],'sha256':hashlib.sha256((root/a['original']).read_bytes()).hexdigest(),'alpha_range':a.get('alpha'),'alpha_counts':'read from corpus; inspect source stats via existing row'})
out={'movie':'chsVenue','apt_sha256':digest(b),'object_sha256':digest(obj),'apt_root':m,'images':results}
Path('logs/ui-restoration-20261020/venue-frame-metadata-20261020.json').write_text(json.dumps(out,indent=2))
print('APT root frames',len(m.get('frames',[])))
print('Shape summaries:')
for x in results:
 print('image',x['image_name'],'uses',len(x['uses']))
 for u in x['uses']:
  print(' shape',u['shape'],'part',u['part'],'bbox',u['apt_bounds'],'size',u['size'],'id',u['source_id'][:16],'uv',[[round(min(p[j] for p in u['uv_pixels']),4),round(max(p[j] for p in u['uv_pixels']),4)] for j in range(2)],'uvpoints',[[round(a,3),round(b,3)] for a,b in u['uv_pixels']],'matrix',u['matrix'],'alpha',u['alpha_range'],u['alpha_counts'])
