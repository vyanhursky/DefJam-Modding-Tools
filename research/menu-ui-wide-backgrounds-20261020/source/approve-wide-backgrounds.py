"""Freeze explicit approval of seven wide scenes; leave native acceptance and held batches separate."""
from pathlib import Path
import json,csv,hashlib,collections
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'wide-backgrounds-v1-20261020';f=Path('config/menu-ui-approved-artwork.json');cat=json.loads(f.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();prior={x['path']:x['sha256'] for rec in cat['approval_records'] for x in rec['files']};assert len(prior)==600;assert all(sha(r/n)==h for n,h in prior.items());data=json.loads((p/'review-data.json').read_text());names=set()
for scene in data['scenes']:
 k=scene['key'];v='-v3' if k=='tips' else '';names.add(f'{k}-wide'+('-v3.png' if k=='tips' else '-v1.png'));names.add(f'{k}-core-hd.png')
 for a in ['4x3','16x10','16x9','21x9','32x9']:names.add(f'{k}-{a}-draft{v}.png')
 for side in ['left','right']:names.add(f'{k}-{side}-join{v}.png')
names.update(['cribOptions-composite-wide.png','cribOptions-composite-core-faithful.png'])
for a in ['4x3','16x10','16x9','21x9','32x9']:names.add(f'matchLoa-{a}-draft-lighting.png')
files=[dict(path=str(Path(p.name)/n),sha256=sha(p/n)) for n in sorted(names)];record=dict(schema=1,decision='D181/UI',date='2026-10-20',owner_words="OK - I approve them all. Does this mean we've finished the modpack? Or anything else left to review?",status='owner-approved artwork',scope='All seven wide-background scenes currently shown atwide-backgrounds.html; tipsv3, othersv1, Criblayer/composite reuse and proposed loader-lighting previews. Original/Faithful4:3cores retained. Excludes raw/history, held detail/shop candidates, active loading-route coverage, native registration and runtime acceptance.',files=files)
(r/'wide-backgrounds-approval-20261020.json').write_text(json.dumps(record,indent=2)+'\n');cat['approval_records'].append({k:record[k] for k in ['decision','status','scope','files']}|dict(record='wide-backgrounds-approval-20261020.json'))
rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));old={s['source_id'] for s in cat['reviewed_sources']};new={sid for s in data['scenes'] for sid in s['source_ids']}-old;assert len(new)==13
for sid in sorted(new):
 aliases=[dict(source=x['source'],name=x['name'].strip(),index=int(x['index']),width=int(x['width']),height=int(x['height'])) for x in rows if x['id']==sid];assert aliases;cat['reviewed_sources'].append(dict(source_id=sid,family='wide-menu-loading-backgrounds',status='approved-artwork',aliases=aliases,treatment='Faithful source core retained; approved imggen exterior scenery'))
cat['unique_pinned_files']=len(prior)+len(files);cat['pilot_imagegen_calls']=162;cat['restoration_status']='First-release artwork scope approved D181/UI: seven finalwide scenes/13newsourceIDs. No further routine panels/buttons/shop generations; held16study/19sourcebatch deferred. Pack integration/native release acceptance pending.';cat['runtime_status']='Earlier HD/wide menus owner-playtested. New approved wide masters/Profile need registration; approved component exports require isolatedRC integration. Actual loading routes/live layers, fullfire-escape pan, Mode specificlighting and native derivative checks remain pending. Game/activepacks untouched.'
ids={s['source_id'] for s in cat['reviewed_sources']};counts=cat['source_counts'];counts['covered_by_artwork_review']=len(ids);counts['unconditionally_approved_source_ids']=sum(s['status']=='approved-artwork' for s in cat['reviewed_sources']);inventory=r/'menu-inventory-data.json';inv=json.loads(inventory.read_text())
for key,predicate in [('registered_flows',lambda a:a['registered']),('core_families',lambda a:True)]:
 covered=sum(a['id'] in ids and predicate(a) for a in inv['assets']);counts[key]['covered']=covered;counts[key]['not_custom_restored']=counts[key]['total']-covered
counts['broad_ui_category']['covered']=len(ids);counts['broad_ui_category']['not_custom_restored']=counts['broad_ui_category']['total']-len(ids);f.write_text(json.dumps(cat,indent=2)+'\n')
data['status']='owner-approved artwork D181/UI; uninstalled; native acceptance pending'
for scene in data['scenes']:scene['status']='approved-artwork'
(p/'review-data.json').write_text(json.dumps(data,indent=2)+'\n')
for asset in inv['assets']:
 if asset['id'] in new:
  asset.update(review_state='approved',treatment='faithful-retained',treatment_label='Faithful HD center retained · widescreen scenery approved',family='wide-menu-loading-backgrounds',background_gap=False,wide_approved=True)
for scope,predicate in [('registered',lambda a:a['registered']),('core',lambda a:True)]:
 assets=[a for a in inv['assets'] if predicate(a)];c=inv['scopes'][scope];c['covered']=sum(a['id'] in ids for a in assets);c['remaining']=c['total']-c['covered'];c['states']=dict(collections.Counter(a['review_state'] for a in assets));c['treatments']=dict(collections.Counter(a['treatment'] for a in assets))
# Keep original shape of global summary; default registered scope drives its counts.
for key in ['covered','remaining']:
 if key in inv['counts']:inv['counts'][key]=inv['scopes']['registered'][key]
inventory.write_text(json.dumps(inv,indent=1)+'\n');print(json.dumps(dict(new_pins=len(files),total_pins=cat['unique_pinned_files'],reviewed=len(ids),unconditional=counts['unconditionally_approved_source_ids'],registered=counts['registered_flows']['covered'],core=counts['core_families']['covered'])))
