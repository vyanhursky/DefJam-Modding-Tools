"""Session-local, read-only menu metadata census; all outputs remain ignored."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import json
import re
import sys

REPO = Path(__file__).resolve().parents[2]
DATA = Path('/Users/vlad/Code/defjam-data/extracted')
CORPUS = Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hd_assets', REPO / 'scripts/hd_assets.py')
hd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hd)
corpus = json.loads((CORPUS / 'corpus.json').read_text())
assets = corpus['assets']
byid = {a['id']: a for a in assets}
ui = [a for a in assets if 'UI and menus' in a.get('categories', [])]
groups = defaultdict(set)
containers = defaultdict(set)
rows = []
screen_ids = set()
for a in assets:
    for alias in a['aliases']:
        source = alias['source']
        if source.startswith('screens/screens.viv::'):
            member = source.split('::')[1]
            p = member.split('/')
            group = p[1] if len(p) > 2 else '_shared'
            groups[group].add(a['id'])
            containers[group].add(member)
            screen_ids.add(a['id'])
        if 'UI and menus' in a.get('categories', []) or source.startswith('screens/'):
            rows.append(dict(id=a['id'], source=source, index=alias['index'], name=alias['name'],
                             width=a.get('width'), height=a.get('height'), alpha=a.get('alpha'),
                             original=a.get('original'), faithful=a.get('upscaled')))
with (OUT / 'all-menu-texture-aliases.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

# Freshly validate screens.viv metadata against the retained corpus, without
# decoding or writing original archive payloads.
blob = (DATA / 'screens/screens.viv').read_bytes()
fresh = []
apt = []
leaf_types = Counter()
for label, leaf in hd.walk(blob, 'screens/screens.viv'):
    leaf_types[Path(label.split('::')[-1]).suffix.lower()] += 1
    if leaf[:4] == b'SHPX':
        for record, _ in hd.shpx_images(leaf, decode=False):
            fresh.append(dict(source=label, **record))
    elif label.lower().endswith('.apt'):
        apt.append(dict(source=label, size=len(leaf), sha256=hd.digest(leaf)))
fresh_ids = {x['source_id'] for x in fresh if 'source_id' in x}
errors = [x for x in fresh if 'error' in x]
(OUT / 'fresh-screens-metadata.json').write_text(json.dumps(dict(records=fresh, apt=apt, errors=errors), indent=2))
flow = (DATA / 'screens/feflow.xml').read_text()
flow_names = re.findall(r'<screen>\s*<name>(.*?)</name>', flow, re.S)
registered = set()
for name in flow_names:
    target = 'screens/screens.viv::screens/' + name.lower() + '.big::'
    for a in assets:
        if any(z['source'].lower().startswith(target) for z in a['aliases']):
            registered.add(a['id'])
core_groups = ['_shared','intMain','battle','options','memoryCard','story','extras','hiScores','jukebox','trans','chyron','_art']
core_ids = set().union(*(groups[g] for g in core_groups))
catalog_groups = ['portrait','shopThumbs','sketchAssets','thumbs','venuethumbs','match']
catalog_ids = set().union(*(groups[g] for g in catalog_groups))
large_core = [a for a in assets if a['id'] in core_ids and a.get('width',0)>=256 and a.get('height',0)>=128]
summary = dict(corpus_id=corpus['corpus_id'], corpus_file_sha256=hd.digest((CORPUS/'corpus.json').read_bytes()),
               totals=corpus['totals'], ui_category_unique=len(ui), screens_unique=len(screen_ids),
               groups={g:dict(unique=len(groups[g]), containers=len(containers[g])) for g in sorted(groups)},
               screen_aliases=len(fresh), fresh_unique=len(fresh_ids), fresh_errors=errors,
               missing_from_corpus=sorted(fresh_ids-set(byid)), corpus_screens_not_in_fresh=sorted(screen_ids-fresh_ids),
               apt_movies=len(apt), leaf_types=dict(leaf_types),
               feflow_registered_screens=len(flow_names),feflow_unique_screen_names=len(set(flow_names)),
               registered_screen_texture_union=len(registered),
               core_texture_union=len(core_ids),catalog_texture_union=len(catalog_ids),
               large_core_candidates=len(large_core),
               notes=['Group counts overlap by shared texture ID.', 'Large core is dimension-filtered, not a verified background count.',
                      'UI category includes inventory/portrait/loading components, not 11261 background paintings.'])
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
(OUT / 'large-core-candidates.json').write_text(json.dumps(large_core,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='groups'},indent=2))
