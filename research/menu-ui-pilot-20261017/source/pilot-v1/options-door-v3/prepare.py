from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();shutil.copy2(root/'review.html',p/'review-before.html');shutil.copy2('/var/folders/fm/_69514_113d4bgm8lqlf9tk80000gn/T/codex-clipboard-562a149b-03ed-4d9c-b3fe-a2719ef53962.png',p/'owner-door-reference.png')
files=[root/'menus-seams-v2'/('jukebox-'+s) for s in ['wide-v2.png','4x3-v2.png','16x10-v2.png','16x9-v2.png','21x9-v2.png','32x9-v2.png','left-join.png','right-join.png']]+[root/'menus-v1'/f for f in ['jukebox-background-restrained.png','beatbox-20-restrained.png','beatbox-19-restrained.png']];approval=dict(schema=1,decision='D140',date='2026-10-18',owner_words='The jukebox is good - I approve that.',scope='Current Jukebox v2 backdrop artwork,center restoration/splits and five aspect crops; no live strip/mask/lighting/runtime acceptance.',files=[dict(path=str(f.relative_to(root)),sha256=sha(f),size=list(Image.open(f).size)) for f in files]);a=root/'jukebox-approval-20261018.json';assert not a.exists();a.write_text(json.dumps(approval,indent=2)+'\n')
(root/'batch2/mode-environment-lit-known3x.png')
ref=Image.open(root/'batch2/mode-environment-lit-known3x.png').convert('RGB');ref.crop((1020,270,1750,1380)).save(p/'source-proportioned-door.png')
# A layout scaffold fixes requested narrow proportions before image generation.
# Target crop is master x2800..5120; original4:3 ends at local720.
old=Image.open(root/'menus-seams-v2/options-wide-v2.png').convert('RGB');im=old.crop((2800,0,5120,1440));im.paste((20,23,14),(720,0,2320,1440))
# Reuse the real mode doorway as editable layout context at uniform scale1x.
# Full framed door x~570..1300,y265..1375 => width/height~.66.
seed=Image.open(p/'source-proportioned-door.png');im.paste(seed,(570,265));im.paste(old.crop((2800,0,3520,1440)),(0,0));im.save(p/'door-target.png');guide=im.copy();d=ImageDraw.Draw(guide);d.line((720,0,720,1439),fill='cyan',width=5);d.rectangle((720,0,2319,1439),outline='#ff55dd',width=5);d.line((1280,265,1280,1375),fill='#ff55dd',width=4);guide.save(p/'door-guide.png')
(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(root)):sha(f) for d in ['menus-v1','menus-seams-v2','transparency-v2','batch2'] for f in (root/d).glob('*.png')},indent=2)+'\n');(p/'layout.json').write_text(json.dumps(dict(master=[5120,1440],target=[2320,1440],crop=[2800,0,5120,1440],source_bound_local=720,allowed_master=[3520,0,1600,1440],reference_frame=[570,265,730,1110],desired_right_jamb_local_approx=1280,door_width_height_ratio_approx=.65),indent=2)+'\n')
