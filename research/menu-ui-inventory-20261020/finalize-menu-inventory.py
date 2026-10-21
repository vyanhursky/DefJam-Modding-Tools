"""Enrich gallery scope/gap metadata; emit downloadable source index; sync serving source."""
from pathlib import Path
import csv,json,shutil,hashlib
r=Path('logs/ui-restoration-20261017/pilot-v1');d=Path('logs/ui-restoration-20261020');f=r/'menu-inventory-data.json';m=json.loads(f.read_text());m['registered_screens']=[x['screen'] for x in csv.DictReader((r.parent/'registered-screens.csv').open())];approved={x['source_id'] for x in json.loads(Path('config/menu-ui-approved-artwork.json').read_text())['reviewed_sources']};gapmeta=json.loads((d/'menu-widescreen-background-gaps-metadata.json').read_text());gaps={a['source_id'] for group in gapmeta['resources'] if group['label']!='story/tournament' for a in group['assets'] if a['source_id'] not in approved};assert len(gaps)==10
for a in m['assets']:a['background_gap']=a['id'] in gaps
f.write_text(json.dumps(m,indent=2)+'\n');assert len(m['assets'])==1834 and sum(a['registered'] for a in m['assets'])==1323
for name,assets in [('menu-inventory-index.csv',[a for a in m['assets'] if a['registered']]),('menu-inventory-core-index.csv',m['assets'])]:
 with (r/name).open('w',newline='') as out:
  w=csv.DictWriter(out,fieldnames=['id','screen','texture_name','native_width','native_height','review_state','treatment','widescreen_candidate','original','faithful','custom']);w.writeheader()
  for a in assets:w.writerow(dict(id=a['id'],screen=';'.join(a['screens']),texture_name=';'.join(x['name'] for x in a['aliases']),native_width=a['width'],native_height=a['height'],review_state=a['review_state'],treatment=a['treatment_label'],widescreen_candidate=a['background_gap'],original=a['original'],faithful=a['faithful'],custom=a['custom'] or ''))
for a in m['assets']:
 for key in ['original','faithful','original_thumbnail','faithful_thumbnail','custom','custom_thumbnail']:
  if a[key]:assert (r/a[key]).is_file(),(a['id'],key)
for n in ['menu_inventory.html','menu_inventory.css','menu_inventory.mjs','review_sequence.mjs','review_navigation.css','review_navigation.mjs']:shutil.copy2(d/n,r/('inventory.html' if n.endswith('.html') else n))
receipt=dict(registered=m['scopes']['registered'],core=m['scopes']['core'],unrestored_background_source_tiles=10,all_1834_original_and_faithful_files_exist=True,local_image_files=len(list((r/'menu-inventory').rglob('*.png')))+len(list((r/'menu-inventory').rglob('*.jpg'))));(r/'menu-inventory/build-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
