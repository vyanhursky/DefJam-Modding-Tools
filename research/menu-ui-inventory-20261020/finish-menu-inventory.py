"""Preserve source-only inventory tooling and a new immutable private overlay."""
from pathlib import Path
import json,hashlib,shutil,subprocess
repo=Path.cwd();r=repo/'logs/ui-restoration-20261017/pilot-v1';d=repo/'logs/ui-restoration-20261020';tools=Path('/Users/vlad/Code/DefJam-Modding-Tools');b=tools/'research/menu-ui-inventory-20261020';b.mkdir(exist_ok=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
sourcefiles=[d/n for n in ['approve-controls.py','build-menu-inventory.py','finalize-menu-inventory.py','menu-ui-remaining-census.py','audit-menu-widescreen-background-gaps-20261020.py','map-story-shop-paper-shapes.py','prepare-story-shop.py','survey-story-support.py','survey-story-more.py','finish-menu-inventory.py']]+[repo/'docs/research'/n for n in ['menu-inventory-browser-2026-10-20.md','menu-ui-remaining-census-2026-10-20.md','menu-widescreen-background-gaps-2026-10-20.md','menu-story-shop-mapping-2026-10-20.md']]
for f in sourcefiles:shutil.copy2(f,b/f.name)
paused=json.loads((r/'story-shop-v1-20261020/generations-paused.json').read_text());lines=['# Three in-flight proposals retained without adoption','Owner changed scope: do not continue routine panel/button generations. Historical total147; no final assembly or approval.']
for item in paused['items']:lines+=['',item['key'],'transparent_background: true','reference: '+item['reference'],'reference_sha256: '+sha(r/'story-shop-v1-20261020'/item['reference']),'raw: '+item['raw_file'],'raw_sha256: '+item['raw_sha256'],item['prompt']]
(b/'paused-prompts.txt').write_text('\n'.join(lines)+'\n');(b/'README.md').write_text('''# Full menu image inventory and widescreen focus

Source only. PNGs, galleryindexJSON/CSV, owner reviews and raw proposals stay
private. Serving origin remains127.0.0.1:51738;8768writer is untouched.
Packaged UI resources: menu_inventory.html/css/mjs,review_sequence.mjs and
review_navigation.mjs/css. Staticgalleryserver uses a private metadata manifest.
Build with build-menu-inventory.py then finalize-menu-inventory.py against
private sources. Metadata-onlycensus andbackground audits reproduce counts.
Do not re-run finish-menu-inventory.py against an existing immutablearchive.

Gym/control15/22approvedD175/UI; earlier16/19stillpending. Routine panels/buttons
restoration stoppedD177/UI. Only3newshopcallsalreadyinflightfinished; rawoutputs
held without adoption. No other imagegen before owner shortlist selections.
Focus widescreen backgrounds with exact source palette/nativecenter/bothjoins.

Gallerydefault1323registered IDs/115reviewed/1208outsideapproval; optional1834
core/132reviewed/1702outsideapproval. Scopes overlap; counts do not mean
individual paintings. Faithfulexistsforall; reviewedFaithfulkept explicitly
labeled. Fiveknownwidecandidate groups,10unreviewedtiles; activegameuse/clip
unverified. Exactreport hasgeometry/caveats. Leave running game unchanged.

Tests: node --test tests/review-navigation.test.mjs tests/menu-inventory.test.mjs
Browserproof/privatearchive: <data>/scratch/menu-ui-inventory-widescreen-focus-20261020/.
Source publication blocked by GitHub sign-in; commits saved locally.
''');(b/'SOURCE_SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(b.iterdir()) if f.is_file() and f.name!='SOURCE_SHA256SUMS'))
status='''- 2026-10-20 D175/UI–D178/UI — Scope changes to widescreen backgrounds and
  owner-selected exceptions; stop routinepanel/button imagegen. Gym15/22
  approved127newpins/600total/136IDs,22tile4xexport exact/uninstalled. Prior16/19
  pending. Prepared30studies57sources deferred;3inflight rawshopproposals held,
  noassembly/adoption,147historicalcalls. Sevenotherplannedcalls notstarted.
  Fullimagebrowser51738/inventory.html:1323registered(115reviewed/1208outside),
  optional1834core(132reviewed/1702outside). Original/Faithful/status/customwhere
  available, search/screen/size/backgroundfilter, zoom/pan, Prev/Next/keys,
  localshortlistnotes/download. Fiveknownwidegroups10tiles; nativeuse/clipunknown.
  All1323IDs paginatedonce/28pages; comparison/mouse/arrow/shortlistreload pass,
  zerooverflow/errors.8Node+22gamefocusedtests/600pins pass. Game/packs/saves/
  8768writer/17workshop/Trejo untouched. Source research/menu-ui-inventory-20261020/,
  privateoverlay <data>/scratch/menu-ui-inventory-widescreen-focus-20261020/.
  Preserve browser selections, previousimmutablearchives and conditionalpan/Mode
  checks. No moregenerationbeforeownerchoices. GitHubauthstillblocks publishing.

'''
f=tools/'PROGRESS.md';s=f.read_text();i=s.index('- 2026-10-20 D172/UI');f.write_text(s[:i]+status+s[i:]);f=tools/'docs/menu-art-workflow.md';f.write_text(f.read_text()+'\n\n## Full image inventory and owner-selected widescreen work\n\n'+status+'\nShortlist keydefjam-menu-inventory-shortlist-v1 at51738. Do not clear owner selections. The gallery is static; notes stay local and may be downloaded. Backgroundfilter includesunregisteredStoryassets throughcore scope. No art/reviewJSON/CSV entersGit.\n');f=tools/'.local-handoff.md';f.write_text(status+(f.read_text() if f.exists() else ''))
# Prior artwork preservation before creating the additive snapshot.
before=json.loads((r/'story-shop-v1-20261020/before-hashes.json').read_text());assert all(sha(r/n)==h for n,h in before.items());cat=json.loads((repo/'config/menu-ui-approved-artwork.json').read_text());pins={f['path']:f['sha256'] for ap in cat['approval_records'] for f in ap['files']};assert len(pins)==600 and all(sha(r/n)==h for n,h in pins.items())
a=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-inventory-widescreen-focus-20261020');a.mkdir(exist_ok=False);target=a/'session/pilot-v1';target.mkdir(parents=True)
for folder in ['menu-inventory','story-shop-v1-20261020']:shutil.copytree(r/folder,target/folder)
for n in ['inventory.html','menu_inventory.css','menu_inventory.mjs','menu-inventory-data.json','menu-inventory-index.csv','menu-inventory-core-index.csv','review.html','review_sequence.mjs','review_navigation.mjs','review_navigation.css','controls-approval-20261020.json']:shutil.copy2(r/n,target/n)
shutil.copytree(d/'approved-pack-exports/menu-ui-gym-controls-test-v1',a/'exports/menu-ui-gym-controls-test-v1');shutil.copytree(b,a/'source')
for n in ['config/menu-ui-approved-artwork.json','config/menu-ui-source-shaped-exports.json']:dst=a/'metadata'/Path(n).name;dst.parent.mkdir(exist_ok=True);shutil.copy2(repo/n,dst)
(a/'README.md').write_text('''Immutable additive overlay: fullmenuinventory+source+Gymapproval/export+
threeunadoptedrawshopproposals. Requirespreviouscontrols/popup/earlierartarchive
chain for remainingapprovedart. No runtime game/build/save/pack change. Preserve
ownerbrowserlocalshortlist at51738 separately; exportedshortlists remainlocal.
''');manifest={str(f.relative_to(a)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in sorted(a.rglob('*')) if f.is_file()};(a/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');receipt=dict(archive=str(a),files=len(manifest),bytes=sum(x['bytes'] for x in manifest.values()),manifest_sha256=sha(a/'manifest.json'),prior_pins_exact=600,prior_pngs_exact=len(before));(r/'menu-inventory/archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
