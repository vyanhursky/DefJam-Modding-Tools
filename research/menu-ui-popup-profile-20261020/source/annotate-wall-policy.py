"""Record the zero-adoption native wall core honestly; widened scenery remains a new draft."""
from pathlib import Path
import json
p=Path(__file__).resolve().parent;f=p/'review-items.json';d=json.loads(f.read_text());it=next(x for x in d if x['key']=='profile-wall');it['method']='Faithful HD original core · new widescreen wall scenery';it['placement']+=' Native core uses zero generated pixels; new wall is only outside4:3.';f.write_text(json.dumps(d,indent=2)+'\n');v=json.loads((p/'verification.json').read_text());v.update(native_paper_restorations=10,new_wide_scene_studies=1,wall_core_faithful_exact=True);(p/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
