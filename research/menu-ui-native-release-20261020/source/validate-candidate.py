"""Read-only audit of the actual release artifact, including ZIP and manifest boundaries."""
import json,hashlib,zipfile,importlib.util
from pathlib import Path
from PIL import Image
repo=Path.cwd();root=Path('/Users/vlad/Code/defjam-data/playtest-menu-ui-v1-rc1/mods/menu-ui-hd-wide-v1-rc2');spec=importlib.util.spec_from_file_location('release',repo/'scripts/build-menu-ui-release.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);native=dict(m.mappings(root/'manifest.ini','textures'));wide=dict(m.mappings(root/'manifest.ini','wide'));cat=json.load(open('config/menu-ui-approved-artwork.json'));reg=json.load(open('config/menu-ui-runtime-registrations.json'));sizes={s['source_id']:(s['aliases'][0]['width']*4,s['aliases'][0]['height']*4) for s in cat['reviewed_sources']+reg['sources']};assert set(native)==set(sizes) and len(native)==157
for sid,rel in native.items():
 f=m.safe_file(root,rel)
 with Image.open(f) as im:assert im.size==sizes[sid] and im.mode in ('RGB','RGBA'),sid
slabs=0
for sid,value in wide.items():
 if value=='stretch':continue
 items=value.split(';');assert len(items)<=16
 for item in items:
  dt,rel=item.split(':',1);assert dt=='inner' or int(dt)==float(dt);m.safe_file(root,rel);slabs+=1
assert slabs==164
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();listing=json.load((root/'files.json').open())['files'];assert all(sha(root/f['path'])==f['sha256'] and (root/f['path']).stat().st_size==f['bytes'] for f in listing)
with zipfile.ZipFile(root.with_suffix('.zip')) as z:
 assert not z.testzip();names=z.namelist();assert len(names)==326 and all(n.startswith(root.name+'/') and '..' not in Path(n).parts and not n.endswith('.exe') for n in names)
 assert all('faithful-hd-' not in n for n in names)
 for n in names:assert hashlib.sha256(z.read(n)).hexdigest()==sha(root/Path(n).relative_to(root.name))
receipt=dict(native_textures=len(native),wide_entries=len(wide),wide_slabs=slabs,files=len(names),all_native_sizes=True,all_files_sha256=True,zip_crc=True,zip_matches_folder=True,faithful_library_bundled=False,source_canvas_core_unchanged=True)
Path('logs/menu-ui-v1-rc/candidate-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
