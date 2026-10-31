"""Serial save-guarded native route/aspect tests of the isolated menu-only pack."""
from pathlib import Path
import importlib.util,os,json,sys
repo=Path.cwd();spec=importlib.util.spec_from_file_location('h',repo/'scripts/harness.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);os.environ['DEFJAM_DATA']='/Users/vlad/Code/defjam-data/playtest-menu-ui-v1-rc1';route=sys.argv[1];aspect=sys.argv[2] if len(sys.argv)>2 else '32x9';ratio={'4x3':'1.333333333','16x10':'1.6','16x9':'1.777777778','21x9':'2.333333333','32x9':'3.555555556'}[aspect];mode=sys.argv[3] if len(sys.argv)>3 else 'all';pack='menu-ui-hd-wide-v1-rc2';packs=('faithful-hd-a512d2429f11-opacity;faithful-hd-a512d2429f11-channels;' if mode in ('all','baseline') else '')+(pack if mode not in ('baseline','original') else '')
env={'RECOMP_TEXTURE_PACKS':packs,'RECOMP_WS_ASPECT':ratio,'RECOMP_TRANS_SHOT_NATIVE':'1','RECOMP_WS_WIDE_TRACE':'1','RECOMP_TEXTURE_TRACE':'1'}
if route in ('pan','pan-sync'):stages=h.ROUTES['boot']['stages'];shots='@getscreeninfo(intmain/mainmenu,0,0.15,0.3,0.4,0.5,0.65,0.8,1,1.2,2,3';until=h.ROUTES['boot']['until'];after=5;secs=100
elif route=='loading':stages=h.ROUTES['fight']['stages'];shots='@getscreeninfo(battle/cmtype,2.5,@getscreeninfo(battle/choosef2,4,@getscreeninfo(battle/oldmload,0.1,0.4,0.8,1.5,2.3,@game.startgame(,0.3';until='game.startgame(';after=3;secs=230
elif route in ('ffa','team','ffa3'):
 stages=h.ROUTES['ffa']['stages'] if route=='ffa' else h.ROUTES['fight']['stages'];shots='@getscreeninfo(battle/oldmload,0.1,0.4,0.8,1.5,2.3,@game.startgame(,0.3';until='game.startgame(';after=3;secs=250
elif route in ('tour','tour2','tour3'):
 stages=['getscreeninfo(intmain/mainmenu=down@4;a@7','getscreeninfo(options/options=b@8','getscreeninfo(intmain/mainmenu#2=down@4;right@5;a@8','getscreeninfo(jukebox/beatbox=b@8','getscreeninfo(intmain/mainmenu#3=right@4;down@5;down@6;a@9','getscreeninfo(hiscores/hiscores=b@8'];shots='@getscreeninfo(options/options,3,@getscreeninfo(jukebox/beatbox,3.1,@getscreeninfo(hiscores/hiscores,3.2';until='getscreeninfo(hiscores/hiscores';after=6;secs=170
elif route in ('intro','intro2'):stages=[line.replace('a@5;a@7;', 'a@5;right@6;right@6.5;a@7;') for line in h.ROUTES['intro']['stages']];shots=h.ROUTES['intro']['shots'];until=h.ROUTES['intro']['until'];after=10;secs=330
elif route=='crib':stages=h.ROUTES['crib']['stages']+['getscreeninfo(story/crib#2=start@5'];shots='@getscreeninfo(story/crib,7,12,@getscreeninfo(options/criboptions,4';until='getscreeninfo(options/criboptions';after=7;secs=150
else:raise SystemExit(route)
if route=='pan-sync':env.update(RECOMP_TEXTURE_SYNC='1',RECOMP_PB_BATCH_DUMP='shot')
name=f'menu-rc2-{route}-{aspect}-{mode}';r=h.run_game(name,stages=stages,shots=shots,secs=secs,until=until,after=after,env=env,inherit_recomp=False)
if not h.reached(r.summary,until):r.missing_anchor=until
from PIL import Image
shotfiles=r.shots()
for f in shotfiles:
 image=Image.open(f);image.load();image.save(str(Path(f).with_suffix('.png')));Path(f).unlink()
receipt=dict(route=route,aspect=aspect,mode=mode,log=r.log,save_ok=r.save_ok,identity=r.identity,summary=r.summary,shots=shotfiles,faults=h.run_faults(r));Path('logs/menu-ui-v1-rc/'+name+'-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
