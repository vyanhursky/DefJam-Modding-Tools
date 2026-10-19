"""Pin the owner-approved skyline and join remaining pilot references."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw

pilot=Path(__file__).resolve().parent
root=pilot/'batch2'
root.mkdir(exist_ok=True)
corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
tiles=json.loads((pilot.parent/'pilot-tiles.json').read_text())
lookup={(t['menu'],t['name']):t for t in tiles}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
approved=pilot/'seam-v3/title-skyline-wide-master-v3.png'
receipt=json.loads((pilot/'seam-v3/receipt.json').read_text())
assert sha(approved)==receipt['current_master_sha256']
records=[]
for ratio,row in receipt['outputs'].items():
    p=pilot/'seam-v3'/row['path']
    assert sha(p)==row['sha256']
    records.append(dict(aspect=ratio,path=str(p),sha256=sha(p)))
approval=dict(schema=1,asset='retail prestart isolated skyline scenery',
    version='seam-v3/full-height-right-repair',status='owner-approved artwork',
    owner_request="It's looking better. Let's take this one as approved and move on to the others. Make sure the prompts and everything you used are documented so we don't have the same issues again",
    date='2026-10-17',master=dict(path=str(approved),sha256=sha(approved)),
    aspect_previews=records,source_ids=[lookup[('prestart',n)]['id'] for n in ['2','1']],
    scope='Exact isolated skyline master and derived aspect crops; no whole title/runtime acceptance or approval of separate restoration trials',
    provenance=['generations.json','wide-assembly-receipt.json','seam-v2/generations.json','seam-v2/assemble-bridges.py','seam-v2/assembly-receipt.json','seam-v3/right-full-height-prompt.txt','seam-v3/assemble.py','seam-v3/receipt.json'])
(pilot/'skyline-approval.json').write_text(json.dumps(approval,indent=2))
definitions=[('title-middle','prestart',['6','5'],'x'),('title-tower','prestart',['11','10'],'x'),
             ('mode-wall-lit','mainMenu',['14','13'],'x'),('mode-shutter','mainMenu',['18','17'],'y'),
             ('mode-surround','mainMenu',['53','52'],'x')]
refs=[]
for label,menu,names,axis in definitions:
    row=dict(label=label,menu=menu,names=names,axis=axis,variants={})
    for kind in ['source','faithful']:
        field='original' if kind=='source' else 'faithful'
        parts=[]
        for n in names:
            tile=lookup[(menu,n)]
            p=corpus/tile[field]
            assert sha(p)==tile['original_hash' if kind=='source' else 'faithful_hash']
            parts.append(Image.open(p).convert('RGBA'))
        w=sum(p.width for p in parts) if axis=='x' else max(p.width for p in parts)
        h=max(p.height for p in parts) if axis=='x' else sum(p.height for p in parts)
        joined=Image.new('RGBA',(w,h))
        offset=0
        for image in parts:
            joined.paste(image,(offset,0) if axis=='x' else (0,offset))
            offset+=image.width if axis=='x' else image.height
        p=root/(label+'-'+kind+'.png')
        joined.save(p)
        # Neutral checker reference displays alpha without inventing scenery.
        checker=Image.new('RGB',(w,h),'#151515')
        d=ImageDraw.Draw(checker)
        step=max(16,w//32)
        for y in range(0,h,step):
            for x in range(0,w,step):
                if (x//step+y//step)%2:
                    d.rectangle((x,y,x+step-1,y+step-1),fill='#343434')
        checker.paste(joined,mask=joined.getchannel('A'))
        checker.save(root/(label+'-'+kind+'-checker.png'))
        row['variants'][kind]=dict(path=p.name,size=[w,h],sha256=sha(p))
    refs.append(row)
(root/'references.json').write_text(json.dumps(dict(schema=1,joins='Authoring canvas; geometry audit controls rendered preview',records=refs),indent=2))
print(json.dumps({'approval_hash':sha(approved),'reference_sets':len(refs),'approval':str(pilot/'skyline-approval.json')},indent=2))
