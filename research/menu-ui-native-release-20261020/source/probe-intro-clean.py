"""Run the calibrated new-ID route against a nested, disposable save fixture.

Remove only the pre-existing AAA profile inside a full outer save guard, so the normal
harness's AAA keyboard input cannot collide. Neither the normal save nor base fixture changes.
"""
from pathlib import Path
import os,importlib.util,shutil,json
from PIL import Image
spec=importlib.util.spec_from_file_location('h','scripts/harness.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
root='/Users/vlad/Code/defjam-data/playtest-menu-ui-v1-rc1';os.environ['DEFJAM_DATA']=root
with h.SaveGuard(root) as outer:
 profile=Path(root)/'save/UserData/45410049/004100410041'
 assert (profile/'AAA').is_file()
 shutil.rmtree(profile)
 route=h.ROUTES['intro'];name='menu-rc2-intro-clean-32x9-all'
 r=h.run_game(name,stages=route['stages'],shots=route['shots'],secs=route['secs'],until=route['until'],after=route['after'],env=dict(RECOMP_TEXTURE_PACKS='faithful-hd-a512d2429f11-opacity;faithful-hd-a512d2429f11-channels;menu-ui-hd-wide-v1-rc2',RECOMP_WS_ASPECT='3.555555556',RECOMP_TRANS_SHOT_NATIVE='1',RECOMP_TEXTURE_TRACE='1'),inherit_recomp=False)
 if not h.reached(r.summary,route['until']):r.missing_anchor=route['until']
 shots=r.shots()
 for name in shots:
  image=Image.open(name);image.load();image.save(Path(name).with_suffix('.png'));Path(name).unlink()
 receipt=dict(route='intro-clean',aspect='32x9',mode='all',log=r.log,save_ok=r.save_ok,identity=r.identity,summary=r.summary,shots=shots,faults=h.run_faults(r))
receipt['outer_save_restored']=outer.restored_equal
Path('logs/menu-ui-v1-rc/menu-rc2-intro-clean-32x9-all-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('outer save restored:',outer.restored_equal,'faults:',receipt['faults'])
