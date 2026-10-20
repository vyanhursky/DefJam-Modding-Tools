"""Freeze explicit owner approval of current15popup/profile studies, not prior16."""
from pathlib import Path
import json,hashlib,csv,importlib.util
from PIL import Image
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'popup-profile-v1-20261020';catpath=Path('config/menu-ui-approved-artwork.json');cat=json.loads(catpath.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
prior={x['path']:x['sha256'] for s in cat['approval_records'] for x in s['files']};assert len(prior)==343;assert all(sha(r/n)==h for n,h in prior.items())
items=json.loads((p/'review-items.json').read_text());tiles=json.loads((p/'assembly-receipt.json').read_text())['source_tiles'];assert len(tiles)==22
names={t['art'] for t in tiles}
for i in items:
 names.update([i['draft_file'],i['alpha_draft_file']]);names.update(f'{i["key"]}-{a}'+('-draft-v3.png' if i['key']=='profile-wall' else '-draft.png') for a in ['4x3','16x10','16x9','21x9','32x9'])
names.update(['profile-wall-wide-v3.png','profile-wall-left-join-v3.png','profile-wall-right-join-v3.png'])
files=[dict(path=str(Path(p.name)/n),sha256=sha(p/n)) for n in sorted(names)]
ap=dict(schema=1,decision='D172/UI',date='2026-10-20',owner_words='Looks good - I approve this batch. You can start the next batch.',status='owner-approved artwork',scope='Current15popup/profile/autosave studies over22sourceIDs; fullsource4xtiles, sourceprotected papers, Faithful stamps/effects/nativewallcore, currentv3widewall and fiveaspectstudies. Raw/history, previous16itembatch and native runtime acceptance excluded.',files=files)
(r/'popup-profile-approval-20261020.json').write_text(json.dumps(ap,indent=2)+'\n');cat['approval_records'].append({k:ap[k] for k in ['decision','status','scope']}|dict(record='popup-profile-approval-20261020.json',files=files));rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));entries=[]
for t in tiles:
 sid=t['source_id'];assert sid not in {s['source_id'] for s in cat['reviewed_sources']};aliases=[dict(source=x['source'],name=x['name'].strip(),index=int(x['index']),width=int(x['width']),height=int(x['height'])) for x in rows if x['id']==sid];cat['reviewed_sources'].append(dict(source_id=sid,family='popup-profile-autosave',status='approved-artwork',aliases=aliases));entries.append(dict(source_id=sid,label='Popup/Profile '+aliases[0]['name'],art=str(Path(p.name)/t['art']),crop=None,size=[v*4 for v in t['native_size']]))
c=cat['source_counts'];c['covered_by_artwork_review']=114;c['unconditionally_approved_source_ids']=96
for k in ['registered_flows','core_families','broad_ui_category']:c[k]['covered']=114;c[k]['not_custom_restored']=c[k]['total']-114
cat['unique_pinned_files']=len(prior)+len(files);cat['restoration_status']='RESUMED;15popup/profile studies22sources approved D172/UI. Earlier16item19sourcebatch remains pending D170/UI. Next batch preparation and linked review navigation.';catpath.write_text(json.dumps(cat,indent=2)+'\n')
f=Path('config/menu-ui-source-shaped-exports.json');ex=json.loads(f.read_text());component=dict(name='Menu UI Popup Profile approved art test v1',png_mips='opacity',status='owner-approved artwork D172/UI; native game validation pending; wide wall not registered',entries=entries);ex['components']['menu-ui-popup-profile-test-v1']=component;f.write_text(json.dumps(ex,indent=2)+'\n');spec=importlib.util.spec_from_file_location('exporter','scripts/export-menu-ui-pack.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);dest=Path('logs/ui-restoration-20261020/approved-pack-exports');mod.export(dict(schema=1,components={'menu-ui-popup-profile-test-v1':component}),cat,r,dest)
for e in entries:assert Image.open(dest/'menu-ui-popup-profile-test-v1/textures'/f'{e["source_id"]}.png').tobytes()==Image.open(r/e['art']).tobytes()
s=(r/'review.html').read_text();start=s.index('<section id="popup-batch-panel">');end=s.index('<section id="detail-batch-panel">');block=s[start:end].replace('This new batch is unapproved.','This batch is owner-approved; native game validation remains pending.').replace('Current candidate · awaiting feedback','Current candidate · approved artwork').replace('Overview of sixteen menu detail candidates','Overview of fifteen popup and profile candidates');s=s[:start]+block+s[end:];# replace status only in popup script
idx=s.index('<script>(()=>{const items=[{"key": "profile-wall"');s=s[:idx]+s[idx:].replace(' · UNAPPROVED · ',' · APPROVED ARTWORK · ',1);(r/'review.html').write_text(s)
print(json.dumps(dict(new_pins=len(files),total_pins=cat['unique_pinned_files'],reviewed=114,unconditional=96,export_tiles=22)))
