"""Collect actual native captures; never synthesize an uncaptured runtime result."""
from pathlib import Path
import json,shutil
repo=Path.cwd();art=repo/'logs/ui-restoration-20261017/pilot-v1';out=art/'native-playtest-rc2';out.mkdir(exist_ok=True);rows=[]
def add(label,receipt,route,aspect,mode,revision):
 r=json.loads(receipt.read_text());imgs=[]
 for name in r['shots']:
  f=Path(name).with_suffix('.png')
  if not f.exists():continue
  dst=out/f.name;shutil.copy2(f,dst);imgs.append(dict(path='native-playtest-rc2/'+f.name,label=f.stem.split('-')[-1]))
 imgs.sort(key=lambda image:float(image['label'].removesuffix('s')))
 if imgs:rows.append(dict(label=label,route=route,aspect=aspect,mode=mode,revision=revision,save_ok=r['save_ok'],faults=r['faults'],log=Path(r['log']).name,images=imgs))
for p in sorted((repo/'logs/menu-ui-v1-rc').glob('menu-rc1-pan-*-all-receipt.json')):
 r=json.loads(p.read_text());add('Transition / Main Menu · '+r['aspect'],p,'pan',r['aspect'],'with Faithful','RC1; transition files identical to RC2')
for p in sorted((repo/'logs/menu-ui-v1-rc').glob('menu-rc2-*-receipt.json')):
 r=json.loads(p.read_text());add({'pan':'Start → Main transition','pan-sync':'Transition · synchronous control','loading':'One-on-one loading','ffa':'Four-player FFA loading','tour2':'Options · incomplete navigation','tour3':'Options / Jukebox / High Scores','intro-clean':'Story character creation'}.get(r['route'],r['route'])+' · '+r['aspect']+' · '+{'all':'Menu + Faithful','menu-only':'Menu only','baseline':'Faithful control','original':'Original control'}.get(r['mode'],r['mode']),p,r['route'],r['aspect'],r['mode'],'RC2')
for p,label,route in [(repo/'logs/ui-restoration-20261020/transition-pan-receipt.json','Previous menu packs · transition 32:9','pan'),(repo/'logs/menu-ui-v1-rc/loading-baseline-receipt.json','Previous menu packs · loading 32:9','loading')]:
 add(label,p,route,'32x9','before','previous menu packs; no new transition/loading extension')
data=dict(schema=1,title='Separate menu pack · native Mac playtest',pack='menu-ui-hd-wide-v1-rc2',archive_bytes=421563157,installed_bytes=423392524,notes='Actual native captures from serial save-guarded runs. Transition black rectangle also reproduced with Faithful alone; not release accepted. Story GF/partner scenes need later-story fixtures. Animation timestamps are relative to screen calls; separate runs are not frame synchronized.',runs=rows)
(out/'data.json').write_text(json.dumps(data,indent=2)+'\n');print(len(rows),'native runs in gallery')
