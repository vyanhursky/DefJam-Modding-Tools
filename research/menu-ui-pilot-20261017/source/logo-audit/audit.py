from pathlib import Path
import json,struct,re,hashlib,collections
from PIL import Image
ns={};exec(Path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py').read_text().split('results = []')[0],ns)
hd=ns['hd_assets'];apt=ns['apt'];inner=dict(hd.archive_entries(hd.unpack_refpack(ns['outer']['screens/intMain/prestart.big'])));data,syms,rels,_=ns['object_info'](inner['prestart.o'])
buf,consts,movie,chars,_=apt.load_movie('screens/screens.viv','screens/intMain/prestart.big')
root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0'); corpus=json.loads((root/'corpus.json').read_text())
wanted={19,27,28,30,31,34,35,37}; assets={}
for a in corpus['assets']:
 for alias in a['aliases']:
  if alias['source']=='screens/screens.viv::screens/intMain/prestart.big::prestart.xsh' and int(alias['name'].strip()) in wanted: assets[int(alias['name'].strip())]=(a,alias)
raw={r['index']:(r,im) for r,im in hd.shpx_images(inner['prestart.xsh'],indices={x[1]['index'] for x in assets.values()})}
out={'hashes':{n:hd.digest(inner[n]) for n in inner},'assets':[],'shapes':[],'timeline':[],'characters':[{'id':i,**{k:v for k,v in c.items() if k!='frames'},'frame_count':len(c.get('frames',[]))} for i,c in enumerate(chars)]}
for name,(a,alias) in sorted(assets.items()):
 path=root/a['original']; assert hd.digest(path.read_bytes())==a['original_hash'];im=Image.open(path).convert('RGBA');r,ri=raw[alias['index']];assert ri.tobytes()==im.tobytes()
 pix=list(im.get_flattened_data()); alpha=im.getchannel('A');rgb=collections.Counter(p[:3] for p in pix);hist=alpha.histogram();visible=collections.Counter(p[:3] for p in pix if p[3]);
 out['assets'].append({'name':name,'index':alias['index'],'dimensions':im.size,'id':a['id'],'original_hash':a['original_hash'],'raw_record':r,'alpha_bbox':alpha.getbbox(),'alpha_extrema':alpha.getextrema(),'alpha_levels':sum(x>0 for x in hist),'alpha_zero':hist[0],'alpha_opaque':hist[255],'alpha_partial':sum(hist[1:255]),'rgb_unique':len(rgb),'rgb_top':rgb.most_common(4),'visible_rgb_unique':len(visible),'visible_rgb_top':visible.most_common(4)})
for shape,c in enumerate(chars):
 if c['type']!='Shape':continue
 parts=[]
 for part in range(10):
  key=f'__RM:::__GP_RM_{shape}_{part}'
  if key not in syms:break
  rm=syms[key]['offset'];texture=rels.get(rm+72,'');match=re.search(r'SHAPENAME=(\d+),',texture)
  if not match or int(match.group(1)) not in wanted: continue
  model=syms[f'__Model:::{shape}']['offset'];scale=struct.unpack_from('<4f',data,model+92)
  matoff=struct.unpack_from('<I',data,rm+88)[0];mat=struct.unpack_from('<16f',data,matoff)
  vb=syms[f'__VB:::__GPvb_9_{part}_{shape}']['offset'];ptr,count,stride,flags,vtx=struct.unpack_from('<5I',data,vb)
  xyz=[[ (q[j]+16384)*scale[j]/16384 for j in range(3)] for q in [struct.unpack_from('<3h',data,vtx+i*stride) for i in range(count//stride)]]
  uv=[[q[0]+mat[12],q[1]+mat[13]] for q in xyz]
  parts.append({'part':part,'image_name':int(match.group(1)),'material_offset':rm,'matrix':mat,'vertex_count':count//stride,'stride':stride,'xyz':xyz,'uv_pixels':uv})
 if parts:out['shapes'].append({'id':shape,'apt_bbox':struct.unpack_from('<4f',buf,c['offset']+8),'object_bbox':struct.unpack_from('<6f',data,syms[f'__BBOX:::{shape}']['offset']),'parts':parts})
for cid,c in [(0,movie)]+[(i,c) for i,c in enumerate(chars) if i and c['type']=='Sprite']:
 frames=c.get('frames',[])
 if cid not in [0,21,22,29,32,33,36,38,39,40,41]:continue
 for fi,items in enumerate(frames):
  for kind,ev in items:
   if kind=='PlaceObject' and (ev.get('character') in [20,21,22,29,32,33,36,38,39,40,41] or (cid==0 and ev['depth'] in [11,15])):out['timeline'].append({'parent_sprite':cid,'frame0':fi,'event':kind,**ev})
   if kind=='FrameLabel':out['timeline'].append({'parent_sprite':cid,'frame0':fi,'event':kind,**ev})
Path('logs/ui-restoration-20261017/logo-audit/metadata.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=1))
