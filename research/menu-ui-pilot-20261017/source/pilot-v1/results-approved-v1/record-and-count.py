"""Freeze owner-approved result paper art; reconcile source IDs against retained menu census."""
from pathlib import Path
from PIL import Image
import csv,json,hashlib,re
r=Path(__file__).resolve().parent.parent;p=Path(__file__).resolve().parent;base=r.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not (r/'results-approval-20261019.json').exists()
(p/'review-before.html').write_bytes((r/'review.html').read_bytes())
prior={str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents};(p/'before-hashes.json').write_text(json.dumps(prior,indent=2)+'\n')
refs=json.loads((r/'results-v1/references.json').read_text());files=[]
for a in refs['panels']:
 label=a['label'];files += [f'results-v1/{label}-restrained.png',f'results-v1/{label}-restrained-alpha.png']+[f'results-v1/{x["name"]}-restrained.png' for x in a['parts']]+[f'results-v1/{label}-{ratio}-draft.png' for ratio in ['4x3','16x10','16x9','21x9','32x9']]
assert len(files)==60 and len(set(files))==60
approval=dict(schema=1,decision='D156',date='2026-10-19',owner_words='Approved all of these. How many more textures left to do for Menu/UI?',status='owner-approved artwork',scope='All6result/rematch/reward-earned panel layouts,18source-shaped tiles,6alpha proofs and30aspect-placement drafts. Excludes raw proposals,originals,masks and native game integration/acceptance.',files=[dict(path=f,sha256=sha(r/f),size=list(Image.open(r/f).size)) for f in files]);(r/'results-approval-20261019.json').write_text(json.dumps(approval,indent=2)+'\n')
s=(r/'review.html').read_text();s=s.replace('Results &amp; Rematch · six paper-panel drafts','Results &amp; Rematch · six approved paper panels',1).replace('New drafts await your feedback.','All six paper layouts are owner-approved artwork; native game validation remains pending.',1).replace('Restrained v1 · awaiting feedback','Restrained v1 · approved artwork',1).replace("+' · source alpha and graphics protected · unapproved artwork'","+' · source alpha and graphics protected · approved artwork · game validation pending'",1)
i=s.index('<details id="paper-stage">');s=s[:i]+'<p><a href="results-approval-20261019.json">Six paper layouts approval and exact artwork hashes</a></p>\n'+s[i:];assert 'paper-panel drafts' not in s;(r/'review.html').write_text(s)
rows=list(csv.DictReader((base/'all-menu-texture-aliases.csv').open()));byid={x['id']:x for x in rows};covered={};lookup=lambda movie,names:[x for x in rows if ('::screens/'+movie+'.big::').lower() in x['source'].lower() and x['name'].strip() in set(map(str,names))]
def add(group,items,status='approved-artwork'):
 for x in items:
  assert x['id'] in byid
  assert x['id'] not in covered,(group,x['id'])
  covered[x['id']]=dict(group=group,status=status)
add('title-scenery',lookup('intMain/prestart',[1,2,5,6,10,11]))
add('mode-scenery',lookup('intMain/mainMenu',[4,5,13,14,17,18,52,53]),'conditional-artwork-native-lighting-check')
brand=json.loads((r/'branding-v1/references.json').read_text());add('title-logo-menu-emblems',[dict(id=x['source_id']) for x in brand if x['label']=='title-logo' or x['label'].startswith('door-')])
add('options-jukebox',lookup('options/options',[71,70,4])+lookup('jukebox/beatbox',[20,19]))
add('battle-backgrounds',[x for a in json.loads((r/'battle-v1/references.json').read_text()) for x in a['tiles']])
add('rewards-shared-wall',json.loads((r/'rewards-v1/references.json').read_text())['parts'])
h=json.loads((r/'hiscores-v1/references.json').read_text());print('HighScoresrefs type',type(h).__name__)
# High Scores sources are the two original wall/board tiles, not its glow.
add('high-scores',lookup('hiScores/hiScores',[1,2]))
add('result-papers',[x for a in refs['panels'] for x in a['parts']])
flow=[x['screen'] for x in csv.DictReader((base/'registered-screens.csv').open())];registered={x['id'] for x in rows if any(x['source'].lower().startswith('screens/screens.viv::screens/'+n.lower()+'.big::') for n in flow)}
core_groups={'_shared','intMain','battle','options','memoryCard','story','extras','hiScores','jukebox','trans','chyron','_art'}
core=set()
for x in rows:
 if x['source'].startswith('screens/screens.viv::'):
  bits=x['source'].split('::')[1].split('/');group=bits[1] if len(bits)>2 else '_shared'
  if group in core_groups:core.add(x['id'])
assert len(registered)==1323 and len(core)==1834 and len(byid)==11261
assert set(covered)<=registered
priority=[]
for label,movie,names in [('Extras main note sheets','extras/extras',[37,42,48,52]),('Story phone shell','story/msgCentr',[110,111]),('Venue frame/mask pieces identified','battle/chsVenue',[143,145,150]),('Title shield and localized Press Start fragments','intMain/prestart',[16,27,28,30,31,34,35,37])]:
 for x in lookup(movie,names):priority.append(dict(priority_group=label,**x))
for x in brand:
 if x['label'].startswith('support-'):priority.append(dict(priority_group='Separate menu support emblems',**byid[x['source_id']]))
assert len(priority)==23 and len({x['id'] for x in priority})==23 and not set(x['id'] for x in priority)&set(covered)
counts=dict(covered_by_artwork_review=len(covered),unconditionally_approved_source_ids=sum(x['status']=='approved-artwork' for x in covered.values()),conditionally_reviewed_mode_source_ids=8,registered_flows=dict(total=len(registered),covered=len(registered&set(covered)),not_custom_restored=len(registered-set(covered))),core_families=dict(total=len(core),covered=len(core&set(covered)),not_custom_restored=len(core-set(covered))),broad_ui_category=dict(total=len(byid),covered=len(covered),not_custom_restored=len(set(byid)-set(covered))),confirmed_priority_shortlist=23)
summary=dict(counts=counts,covered_sources=[dict(id=k,**v,aliases=[x for x in rows if x['id']==k]) for k,v in covered.items()],priority_shortlist=priority,notes=['Not-custom-restored means not covered by this custom artwork review,not missing from FaithfulHD.','23is a confirmed next-art shortlist,not a complete remaining background/job count. Frame,popup,Story UI,small text/icons and other support art need classification.','One source ID counts once; aspectexports/joins/raws do not count. Mode8counted as reviewedconditionally,not fullyaccepted.','Registeredflow/core/broad scopes overlap;do not add. No background-only workload estimate from staticimagecounts.'])
(p/'remaining-inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
with (p/'remaining-registered-source-textures.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(byid[k] for k in sorted(registered-set(covered)))
assert all(sha(r/f)==h for f,h in prior.items());assert all(sha(r/f['path'])==f['sha256'] for f in approval['files'])
(p/'verification.json').write_text(json.dumps(dict(approved_files=60,approved_panel_layouts=6,approved_source_tiles=18,prior_pngs_unchanged=len(prior),counts=counts),indent=2)+'\n');print(json.dumps(counts,indent=2))
