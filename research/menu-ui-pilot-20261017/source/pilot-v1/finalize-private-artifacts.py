"""Archive this private pilot and update the authoring project's handoff only."""
from pathlib import Path
import hashlib
import shutil

source = Path(__file__).resolve().parent
destination = Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-pilot-20261017-v1')
if destination.exists():
    raise SystemExit('Stable experiment already exists; do not overwrite it')
shutil.copytree(source, destination)
count = 0
for path in source.rglob('*'):
    if path.is_file():
        copy = destination/path.relative_to(source)
        assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(copy.read_bytes()).digest()
        count += 1
progress = Path('/Users/vlad/Code/DefJam-Modding-Tools/PROGRESS.md')
text = progress.read_text()
marker = '- 2026-10-17: menu/UI source-palette pilot'
if marker in text:
    raise SystemExit('Authoring handoff already has this pilot; inspect before repeating')
entry = '''- 2026-10-17: menu/UI source-palette pilot added four unapproved Rich Original
  Detail revisions through the existing writer8768: prestart skyline names2/1
  r-79d5b7230a144039 / r-a0377c04607f46ab and mainMenu wall names5/4
  r-3403319ed9c449ad / r-2aec9aa2ab7b4144. Total candidates13→17; all prior
  candidate records, reviews, requests and saved session verified unchanged.
  Old13request records/zero queued remain; six new built-in imagegen calls are
  retained in the private pilot provenance, not invented queue requests.
  Owner chose restrained cleanup/original color (no warmer/yellower), centered
  composition/controls, and21:9/32:9 scenery in first pass. Raw prompt-only drafts
  drifted; scratch technical derivatives retain faithful spatial chroma/lighting,
  protected graphics/seams/alpha/padding and bounded fine luminance (medianLab0).
  Palette assembler remains a private experiment, not adopted authoring-core code.
  Isolated skyline wide previews keep faithful center exact at all5ratios;
  new-side seams/brightness and other layers remain unfinished. No approval,
  selection, export, installation or game run. No authoring-core source change.
  Existing67tests were not rerun or claimed for this scratch experiment.
  Stable private experiment: <data>/scratch/menu-ui-pilot-20261017-v1/; read-only
  preview http://127.0.0.1:51738/review.html, existing workshop8768 unchanged.
  Recomp report: docs/research/menu-ui-pilot-results-2026-10-17.md. Inspect initial
  cleanup vs faithful and added scenery before further art/runtime integration.
  Fighter/Trejo review below remains active and intact; no server cutover occurred.

'''
text = text.replace('## Current status\n\n','## Current status\n\n'+entry,1)
progress.write_text(text)
handoff = Path('/Users/vlad/Code/DefJam-Modding-Tools/.local-handoff.md')
old = handoff.read_text()
handoff.write_text('## Menu/UI pilot2026-10-17\n\nStable private archive: '+str(destination)
    +'\nRead-only preview: http://127.0.0.1:51738/review.html (server exec54187 in coordinating recomp chat).\n'
    +'Existing8768writer/session preserved. Four new unapproved menu trials;17total candidates.\n'
    +'Exact prompts, raw model outputs, processor/mask/input/output hashes, original review backup and import/center-check receipts are archived.\n'
    +'No art approval, selection, export or game installation. Trejo session below remains active.\n\n'+old)
print('Stable private archive:',destination)
print('Verified identical files:',count)
print('Updated authoring PROGRESS.md and ignored local handoff; no core source changes')
