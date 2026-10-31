"""Retain existing JSON formatting while appending new metadata records."""
from pathlib import Path
import json,re,subprocess
for name in ['config/menu-ui-approved-artwork.json','config/menu-ui-source-shaped-exports.json']:
 f=Path(name);new=json.loads(f.read_text());base=subprocess.check_output(['git','show','HEAD:'+name],text=True);old=json.loads(base)
 if 'approved-artwork' in name:
  new['restoration_status']=new['restoration_status'].replace('studies19sources','studies22sources');new['runtime_status']='Earlier HD/wide menus owner-playtested. Extras, Phone and Popup/Profile22tile approved source4xexports ready/uninstalled. New Gym/controls and prior16batch pending; transition native pan acceptance pending.'
 text=base
 for key,value in new.items():
  if old.get(key)==value:continue
  m=re.search(r'^  "'+re.escape(key)+r'": ',text,re.M);assert m,key;start=m.end();_,length=json.JSONDecoder().raw_decode(text[start:]);segment=text[start:start+length]
  if isinstance(value,list) and value[:len(old[key])]==old[key]:
   addition=',\n'+',\n'.join('    '+json.dumps(v,indent=2).replace('\n','\n    ') for v in value[len(old[key]):]);replacement=segment.rstrip()[:-1].rstrip()+addition+'\n  ]'
  elif isinstance(value,dict) and key=='components':
   additions={k:v for k,v in value.items() if k not in old[key]};assert all(value[k]==v for k,v in old[key].items());addition=',\n'+',\n'.join('    '+json.dumps(k)+': '+json.dumps(v,indent=2).replace('\n','\n    ') for k,v in additions.items());replacement=segment.rstrip()[:-1].rstrip()+addition+'\n  }'
  else:replacement=json.dumps(value,indent=2).replace('\n','\n  ')
  text=text[:start]+replacement+text[start+length:]
 assert json.loads(text)==new;f.write_text(text)
