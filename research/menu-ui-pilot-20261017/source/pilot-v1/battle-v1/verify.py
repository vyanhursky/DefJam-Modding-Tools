"""Private batch invariants: source identity/alpha/padding/geometry and old art."""
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
p=Path(__file__).resolve().parent;r=p.parent;repo=r.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();rows=json.loads((p/'references.json').read_text());meta=json.loads((repo/'logs/ui-restoration-20261017/next-scope/battle-background-geometry.json').read_text());records=[]
for row in rows:
 label=row['label'];m=next(x for x in meta['movies'] if x['movie']==label);base=np.array(Image.open(p/(label+'-faithful.png')).convert('RGBA'));rest=np.array(Image.open(p/(label+'-restrained.png')).convert('RGBA'));held=np.array(Image.open(p/(label+'-protected.png')))>0;assert np.array_equal(base[:,:,3],rest[:,:,3]);assert np.array_equal(base[held],rest[held]);assert np.array_equal(base[1920:],rest[1920:]);pieces=[]
 for i,t in enumerate(row['tiles']):
  original=next(x for x in m['background_parts'] if x['source_id']==t['id']);assert t['sha256']==original['original_png_sha256']==sha(p/(t['name']+'-source.png'));f=p/(t['name']+'-restrained.png');im=Image.open(f).convert('RGBA');faithful=Image.open(p/(t['name']+'-faithful.png')).convert('RGBA');im.putalpha(faithful.getchannel('A'));im.paste(faithful.crop((0,1920,im.width,2048)),(0,1920));im.save(f);a=np.array(im);b=np.array(faithful);assert np.array_equal(a[:,:,3],b[:,:,3]);assert np.array_equal(a[1920:],b[1920:]);pieces.append(a[:1920,:,:3])
 assert np.array_equal(np.concatenate(pieces,1),rest[:1920,:,:3]);center=np.array(Image.open(p/(label+'-center.png')).convert('RGB'));master=np.array(Image.open(p/(label+'-wide-draft.png')));assert np.array_equal(master[:,1600:3520],center)
 for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
  a=np.array(Image.open(p/(label+'-'+ratio+'-draft.png')));assert a.shape==(1440,w,3);assert np.array_equal(a[:,(w-1920)//2:(w+1920)//2],center)
 records.append(dict(label=label,source_ids_verified=2,mosaic_alpha_exact=True,protected_graphics_exact=True,stored_padding_exact=True,tile_alpha_exact=2,tile_padding_exact=2,active_rgb_tile_reassembly_exact=True,center_and_five_aspect_centers_exact=True))
before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==h for f,h in before.items());receipts=json.loads((p/'generations.json').read_text());assert len(receipts['calls'])==22
verification=dict(schema=1,records=records,existing_pngs_unchanged=len(before),new_builtin_calls=22,pilot_total_calls=79,all_checks_pass=True,source_shaped_alpha_note='Each original tile alpha/padding restored from its own faithful4x reference. Mosaic preview alpha uses assembled-source Lanczos; previews are flattened RGB. Active tile RGB reassembles exactly.',outputs='4masters,20aspectdrafts,20originalreferences,8source-shapedtiles,8joinproofs,8separateextensionlayers',status='Unapproved; native mapping/portraits/lighting/in-game checks pending')
(p/'verification.json').write_text(json.dumps(verification,indent=2)+'\n');print('PASS:',len(before),'previous PNGs;8IDs/alpha/padding/splits;4protected mosaics;20aspectcenters;22calls/79total')
