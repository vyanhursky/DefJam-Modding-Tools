"""One-shot import through the existing writer; preserve all prior art/reviews."""
from pathlib import Path
from PIL import Image
import json
import hashlib
import subprocess

p = Path(__file__).resolve().parent
workspace = Path('/Users/vlad/Code/defjam-data/hd-work/texture-workshop')
receipt = p/'menu-import-receipt.json'
if receipt.exists():
    raise SystemExit('Import receipt exists; do not duplicate revisions')
old = json.loads((p/'workshop-before-menu-import.json').read_text())
assert json.loads((workspace/'workshop.json').read_text()) == old
tiles = json.loads((p.parent/'pilot-tiles.json').read_text())
rows = []
for label, menu, names, seam in [('title-skyline','prestart',['2','1'],512),
                                  ('mode-wall-dark','mainMenu',['5','4'],256)]:
    im = Image.open(p/(label+'-palette-constrained-trial.png'))
    for i, name in enumerate(names):
        tile = next(x for x in tiles if x['menu']==menu and x['name']==name)
        left = 0 if i==0 else seam*4
        right = seam*4 if i==0 else im.width
        piece = im.crop((left,0,right,im.height))
        assert piece.size == (tile['width']*4,tile['height']*4)
        filename = label+'-tile-'+name+'-palette-trial.png'
        piece.save(p/filename)
        prompt = ('Menu/UI palette-preserving technical trial1; owner direction D124: restrained cleanup, original color/no warmer or yellower grade, centered composition, wide scenery through32:9.\n'
                  +'Source '+tile['id']+'; '+menu+' XSH name'+name+' index'+str(tile['index'])+'.\n'
                  +'Creative source: built-in image_gen, raw-v2 joined draft '+str(p/(label+'-raw-v2.png'))
                  +' (SHA256 '+hashlib.sha256((p/(label+'-raw-v2.png')).read_bytes()).hexdigest()+').\n'
                  +'Technical assembly: '+str(p/'palette-proof.py')+'; receipt '+str(p/'palette-proof-receipt.json')+'.\n'
                  +'Original per-pixel Lab chroma and lighting control; detail L bounded1; protected graphics/seams/alpha/padding exact. Full exact prompts/inputs/raw history: '+str(p/'generations.json')+'.\n'
                  +'The imported image is a derived tile, not the raw imagegen canvas. Raw model output had a slight aspect mismatch; explicit trial normalization and cropping are retained in the receipt. No approval, selection or game verification.\n\n'
                  +'Original generation prompt:\n'+(p/('title-restoration-prompt.txt' if menu=='prestart' else 'mode-wall-restoration-prompt.txt')).read_text()
                  +'\nColor-only revision prompt:\n'+(p/(label+'-color-revision-prompt.txt')).read_text())
        promptfile = p/(label+'-tile-'+name+'-import-provenance.txt')
        promptfile.write_text(prompt)
        title = ('Title skyline' if menu=='prestart' else 'Mode wall')+' · tile'+name+' · source palette trial1'
        command = ['/Users/vlad/Code/DefJam-Modding-Tools/.venv/bin/defjam-tools','workshop','import',
                   '--server','http://127.0.0.1:8768','--asset',tile['id'],'--image',str(p/filename),
                   '--label',title,'--style','faithful','--prompt-file',str(promptfile)]
        result = subprocess.run(command,capture_output=True,text=True)
        if result.returncode:
            (p/'partial-import-receipt.json').write_text(json.dumps(rows,indent=2))
            raise SystemExit('Import failed: '+result.stderr)
        rows.append(dict(asset=tile['id'],menu=menu,name=name,file=filename,response=json.loads(result.stdout)))
        print(menu,name,'imported',flush=True)
new = json.loads((workspace/'workshop.json').read_text())
assert old['reviews'] == new['reviews']
assert old['requests'] == new['requests']
assert old['session'] == new['session']
for key,value in old['candidates'].items():
    assert new['candidates'][key] == value
assert sum(map(len,new['candidates'].values())) == sum(map(len,old['candidates'].values()))+4
receipt.write_text(json.dumps(dict(imports=rows,
    preservation=dict(reviews='unchanged',requests='unchanged',session='unchanged',old_candidates='unchanged'),
    before_candidates=sum(map(len,old['candidates'].values())),after_candidates=sum(map(len,new['candidates'].values()))),indent=2))
print('PASS old reviews/requests/session/candidates preserved; four new unapproved menu drafts')
