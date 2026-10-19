from pathlib import Path
from PIL import Image
import json,struct,re,collections
n={};exec(Path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py').read_text().split('results = []')[0],n);hd=n['hd_assets'];apt=n['apt']
root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');corpus=json.loads((root/'corpus.json').read_text());out={'schema':1,'note':'Source metadata only; packed vertex coordinates follow earlier inferred formula. No runtime timing claimed.','resources':[]}
for resource,wanted in [('screens/options/options.big',{71,70,8,7,4}),('screens/jukebox/beatbox.big',{20,19})]:
 base=Path(resource).stem;inn=dict(hd.archive_entries(hd.unpack_refpack(n['outer'][resource])));data,syms,rels,_=n['object_info'](inn[base+'.o']);buf,co,mo,ch,_=apt.load_movie('screens/screens.viv',resource)
 res={'resource':resource,'members_sha256':{k:hd.digest(v) for k,v in inn.items()},'stage':[mo['screen_width'],mo['screen_height']],'assets':[],'shapes':[],'ancestor_events':[],'root_events':mo['frames'],'character_counts':dict(collections.Counter(x['type'] for x in ch if x))}
 assets={}
 for a in corpus['assets']:
  for al in a['aliases']:
   if al['source']=='screens/screens.viv::'+resource+'::'+base+'.xsh' and int(al['name'].strip()) in wanted:assets[int(al['name'].strip())]=(a,al)
 raw={r['index']:(r,im) for r,im in hd.shpx_images(inn[base+'.xsh'],indices={al['index'] for a,al in assets.values()})}
 for name,(a,al) in sorted(assets.items()):
  p=root/a['original'];assert hd.digest(p.read_bytes())==a['original_hash'];im=Image.open(p).convert('RGBA');r,ri=raw[al['index']];assert ri.tobytes()==im.tobytes();alpha=im.getchannel('A');hist=alpha.histogram()
  res['assets'].append({'name':name,'id':a['id'],'original_hash':a['original_hash'],'dimensions':im.size,'alpha_bbox':alpha.getbbox(),'alpha_extrema':alpha.getextrema(),'alpha_counts':{'zero':hist[0],'opaque':hist[255],'partial':sum(hist[1:255])},'rgba_extrema':im.getextrema(),'aliases':a['aliases'],'shpx_record':r})
 for shape,c in enumerate(ch):
  if not c or c['type']!='Shape':continue
  parts=[]
  for part in range(20):
   key=f'__RM:::__GP_RM_{shape}_{part}'
   if key not in syms:break
   rm=syms[key]['offset'];m=re.search(r'SHAPENAME=(\d+),',rels.get(rm+72,''))
   if not m or int(m[1]) not in wanted:continue
   sc=struct.unpack_from('<4f',data,syms[f'__Model:::{shape}']['offset']+92);mp=struct.unpack_from('<I',data,rm+88)[0];mat=struct.unpack_from('<16f',data,mp);vb=syms[f'__VB:::__GPvb_9_{part}_{shape}']['offset'];ptr,ct,stride,flags,vtx=struct.unpack_from('<5I',data,vb)
   xyz=[[(q[j]+16384)*sc[j]/16384 for j in range(3)] for q in [struct.unpack_from('<3h',data,vtx+i*stride) for i in range(ct//stride)]];uv=[[q[0]*mat[0]+q[1]*mat[4]+mat[12],q[0]*mat[1]+q[1]*mat[5]+mat[13]] for q in xyz]
   parts.append({'part':part,'image_name':int(m[1]),'matrix':mat,'vertex_count':ct//stride,'stride':stride,'xyz':xyz,'uv_pixels':uv})
  if parts:res['shapes'].append({'id':shape,'apt_bbox':struct.unpack_from('<4f',buf,c['offset']+8),'object_bbox':struct.unpack_from('<6f',data,syms[f'__BBOX:::{shape}']['offset']),'parts':parts})
 targets={s['id'] for s in res['shapes']};ancestors=set(targets)
 while True:
  prev=set(ancestors)
  for cid,c in enumerate(ch):
   if c and any(ev.get('character') in ancestors for fr in c.get('frames',[]) for kind,ev in fr if kind=='PlaceObject'):ancestors.add(cid)
  if prev==ancestors:break
 for cid in sorted(ancestors):
  c=ch[cid]
  if 'frames' not in c:continue
  evs=[]
  for fi,items in enumerate(c['frames']):
   for kind,ev in items:
    entry={'frame0':fi,'kind':kind,**ev}
    if kind=='Action':entry['disassembly']=[{'offset':x.offset,'name':x.name,'operands':x.operands,'note':x.note} for x in apt.disassemble_block(buf,ev['instructions_at'],co)]
    evs.append(entry)
  res['ancestor_events'].append({'id':cid,'type':c['type'],'frame_count':len(c['frames']),'events':evs})
 res['overlay_context']={'shape_bounds':{},'sprite92_frames':ch[92].get('frames',[]),'source_metadata':[]}
 for sid in ([91] if base=='options' else [43,89,91]):res['overlay_context']['shape_bounds'][str(sid)]=struct.unpack_from('<4f',buf,ch[sid]['offset']+8)
 res['overlay_context']['source_metadata']=[r for r,im in hd.shpx_images(inn[base+'.xsh'],decode=False) if r['name'].strip() in ['87','88','90']]
 if base=='options':
  from PIL import ImageChops
  im8=raw[assets[8][1]['index']][1].convert('RGBA');im71=raw[assets[71][1]['index']][1].convert('RGBA');diff=ImageChops.difference(im8,im71)
  res['platform_background_comparison']={'same_source_id':assets[8][0]['id']==assets[71][0]['id'],'rgb_difference_bbox':diff.convert('RGB').getbbox(),'differing_rgba_texels':sum(x!=y for x,y in zip(im8.get_flattened_data(),im71.get_flattened_data()))}
 out['resources'].append(res)
Path('logs/ui-restoration-20261017/next-scope/options-jukebox-geometry.json').write_text(json.dumps(out,indent=2))
for r in out['resources']:
 print(r['resource']);print('ASSETS',json.dumps([{k:a[k] for k in ['name','id','dimensions','alpha_bbox','alpha_counts']} for a in r['assets']]))
 print('SHAPES',json.dumps(r['shapes'],indent=1));print('ANCESTORS',json.dumps(r['ancestor_events'],indent=1))
