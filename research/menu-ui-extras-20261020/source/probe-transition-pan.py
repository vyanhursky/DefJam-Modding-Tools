"""One serial guarded baseline run of the reported transition; no pack/settings writes."""
from pathlib import Path
import importlib.util,os,subprocess,json
repo=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('harness',repo/'scripts/harness.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
check=subprocess.run(['pgrep','-x','defjam_recomp'],capture_output=True,text=True)
if check.returncode==0:raise SystemExit('A game process is already running;baselineprobe did not start or stop it.')
if check.returncode not in (0,1):raise SystemExit('Cannot verify no active game process: '+check.stderr)
os.environ['DEFJAM_DATA']='/Users/vlad/Code/defjam-data/playtest-menu-ui'
packs='faithful-hd-a512d2429f11-opacity;faithful-hd-a512d2429f11-channels;menu-ui-restored-test-v1;menu-ui-branding-registered-test-v1;menu-ui-mode-conditional-test-v1;menu-ui-wide-test-v1'
shots='@getscreeninfo(intmain/mainmenu,0,0.1,0.2,0.3,0.4,0.6,0.8,1,1.2,1.4,1.6,2,3'
r=h.run_game('menu-transition-pan-32x9-20261020',stages=h.ROUTES['boot']['stages'],shots=shots,secs=100,until=h.ROUTES['boot']['until'],after=5,env={'RECOMP_TEXTURE_PACKS':packs,'RECOMP_WS_ASPECT':'3.555555556','RECOMP_TRANS_SHOT_NATIVE':'1','RECOMP_WS_WIDE_TRACE':'1','RECOMP_PB_BATCH_DUMP':'shot'},inherit_recomp=False,quiet=True)
h.print_run(r)
for f in r.shots():h.bmp_to_png(f)
receipt=dict(log=r.log,save_ok=r.save_ok,identity=r.identity,summary=r.summary,shots=r.shots(),faults=h.run_faults(r));(Path(__file__).resolve().parent/'transition-pan-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');raise SystemExit(bool(h.run_faults(r)))
