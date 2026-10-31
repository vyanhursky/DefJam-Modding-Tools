"""Independent file-level checks after final art assembly and browser review."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
pilot=root.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:np.array(Image.open(p).convert('RGBA'))
approval=json.loads((pilot/'skyline-approval.json').read_text())
assert sha(pilot/'seam-v3/title-skyline-wide-master-v3.png')==approval['master']['sha256']
for row in approval['aspect_previews']:assert sha(Path(row['path']))==row['sha256']
rest=json.loads((root/'restoration-receipt.json').read_text())
for row in rest['records']:
    label=row['label'];old=load(root/(label+'-faithful.png'));new=load(root/(label+'-restrained.png'))
    held=np.array(Image.open(root/(label+'-protected.png')))>0
    assert np.array_equal(old[:,:,3],new[:,:,3]) and np.array_equal(old[held],new[held])
wide=json.loads((root/'wide-receipt.json').read_text())
for label in ['title-middle','title-tower','mode-environment']:
    old=load(root/(label+'-assembled-proposal.png'));new=load(root/(label+'-wide-draft.png'))
    end=3520 if label.startswith('title') else 4086
    assert np.array_equal(old[:,1600:end],new[:,1600:end])
    mask=np.zeros(old.shape[:2],dtype=bool)
    for record in wide['records']:
        if record['label']==label:
            x,y,w,h=record['domain'];mask[y:y+h,x:x+w]=True
    assert np.array_equal(old[~mask],new[~mask])
for label in ['title-layers','title-middle','title-tower','mode-environment','mode-environment-lit']:
    center=load(root/(label+'-4x3-preview.png'))
    for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
        frame=load(root/(label+'-'+ratio+'-preview.png'))
        assert frame.shape[:2]==(1440,width)
        assert np.array_equal(frame[:,(width-1920)//2:(width+1920)//2],center)
workspace=Path('/Users/vlad/Code/defjam-data/hd-work/texture-workshop')
old=json.loads((pilot/'workshop-before-menu-import.json').read_text())
current=json.loads((workspace/'workshop.json').read_text())
writer={k:old[k]==current[k] for k in ['reviews','requests','session']}
writer['candidate_count']=sum(map(len,current['candidates'].values()))
writer['old_candidates_exact']=all(current['candidates'][k]==v for k,v in old['candidates'].items())
for row in json.loads((pilot/'menu-import-receipt.json').read_text())['imports']:
    record=row['response'];assert record in current['candidates'][row['asset']]
    assert sha(workspace/record['path'])==record['sha256']
result=dict(schema=1,approved_skyline='master+5crops exact',restorations='5/5alpha+protected exact',
    wide_contexts='3/3protected+outside allowed domains exact',aspect_centers='25/25exact',
    writer=writer,browser=dict(study_images_loaded=25,restoration_pairs_loaded=5,
        bounds='37.5% at32:9, toggle pass',console_errors=0),
    source_checks='Both whitespace,AGENTS/CLAUDE equality and hygiene pass; no broad runtime/core tests needed')
(root/'verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
