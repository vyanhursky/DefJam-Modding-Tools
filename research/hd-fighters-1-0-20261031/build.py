#!/usr/bin/env python3
"""Build immutable HD Fighters1.0 assets from an explicit owner-approved hash list.

No generation, review updates, active installation, settings changes or uploads.
All inputs/outputs containing artwork must remain outside the source repository.
"""
import argparse,hashlib,importlib.util,json,shutil,stat,sys,zipfile
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
sys.path.insert(0,str(REPO/'src'))
from defjam_tools.paths import require_private_output
from defjam_tools.hd_assets import archive_entries,unpack_refpack,shpx_images
PUBLIC='https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def module(name,path):
 sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for x in ['workspace','dump','corpus','helper','catalogue','output']:ap.add_argument('--'+x,type=Path,required=True)
 args=ap.parse_args();out=require_private_output(args.output)
 if out.exists():ap.error('Use a new immutable output directory')
 recipe=json.loads((HERE/'selection.json').read_text());assert recipe['version']=='1.0.0' and recipe['channel']=='stable'
 state=json.loads((args.workspace/'workshop.json').read_text());corpus=json.loads((args.corpus/'corpus.json').read_text());assert corpus['corpus_id']==recipe['corpus_id'];assets={a['id']:a for a in corpus['assets']};archive_cache={};leaf_cache={};verified=[];source_records=[]
 def resolve(alias):
  route=alias['source'].split('::');root=route[0]
  if root not in archive_cache:archive_cache[root]=dict(archive_entries((args.dump/root).read_bytes()))
  entries=archive_cache[root]
  for i,name in enumerate(route[1:]):
   matches=[(n,b) for n,b in entries.items() if n.lower()==name.lower()];assert len(matches)==1,'Ambiguous source member';raw=matches[0][1]
   if i<len(route[1:])-1:
    key='::'.join(route[:i+2])
    if key not in archive_cache:archive_cache[key]=dict(archive_entries(raw if raw[:4] in (b'BIG4',b'BIGF') else unpack_refpack(raw)))
    entries=archive_cache[key]
  return raw if raw[:4]==b'SHPX' else unpack_refpack(raw)
 for number,row in enumerate(recipe['selections']):
  aid=row['source_id'];a=assets[aid];original=args.corpus/a['original'];faithful=args.corpus/a['upscaled'];assert sha(original)==row['original_sha256']==a['original_hash'];assert sha(faithful)==row['faithful_sha256']==a['upscaled_hash'];assert row['source_dimensions']==[a['width'],a['height']]
  if row['revision']:
   c=next(x for x in state['candidates'][aid] if x['id']==row['revision']);assert c['sha256']==row['sha256'];assert 'Local RealESRNet' not in c['label'];assert 'local-upscale-comparison' not in state['reviews'].get(aid+':'+c['id'],{}).get('tags',[]);source=args.workspace/c['path'];assert source.resolve().is_relative_to(args.workspace.resolve())
  else:source=original if row['method']=='original-native' else faithful
  assert sha(source)==row['sha256']
  key=row['source_alias']['source'];index=row['source_alias']['index'];cache_key=(key,index)
  if cache_key not in leaf_cache:
   decoded=list(shpx_images(resolve(row['source_alias']),indices={index}));assert len(decoded)==1;leaf_cache[cache_key]=decoded[0]
  descriptor,decoded=leaf_cache[cache_key];assert descriptor.get('source_id')==aid and decoded is not None,'Dump source identity mismatch'
  with Image.open(original) as own,Image.open(faithful) as base,Image.open(source) as final:
   assert np.array_equal(np.asarray(own.convert('RGBA')),np.asarray(decoded.convert('RGBA'))),'Source PNG differs from decoded own dump'
   assert final.format=='PNG' and final.mode=='RGBA' and getattr(final,'n_frames',1)==1
   assert final.size==(a['width']*row['output_scale'],a['height']*row['output_scale'])
   reference=own if row['output_scale']==1 else base
   assert final.size==reference.size and np.array_equal(np.asarray(final)[...,3],np.asarray(reference.convert('RGBA'))[...,3]),'Own material alpha changed'
  verified.append((row,source));source_records.append(dict(source_id=aid,source_identity_verified=True,alpha_exact=True,output_size=[a['width']*row['output_scale'],a['height']*row['output_scale']]))
  if number%25==0:print('Validated own source/PNG/alpha',number+1,'/',len(recipe['selections']),flush=True)
 assert len(verified)==218 and len({r['source_id'] for r,_ in verified})==218
 out.mkdir(parents=True);root='hd-fighters-v1-0-0';pack=out/root;(pack/'textures').mkdir(parents=True)
 manifest='[pack]\nschema=1\nname=HD Fighters 1.0\npng_mips=channels\n[textures]\n'
 for row,source in verified:
  aid=row['source_id'];shutil.copyfile(source,pack/'textures'/(aid+'.png'));manifest+=aid+'=textures/'+aid+'.png\n'
 (pack/'manifest.ini').write_text(manifest,encoding='ascii')
 notes='''HD Fighters 1.0 / 1.0.0

218 source-ID texture entries:80 fixed-fighter main/outfit/Story atlases,
133 fixed-fighter secondary/injury maps and5 shared sparkle/tape inputs.
200 Rich Original Detail restorations preserve the illustrated game style while
restoring faces/hair, skin/tattoos, clothes/headwear/footwear and accessories.
Original-palette matching and own material alpha are retained.

Explicit unchanged fallbacks: David Banner and11 injury maps use Lanczos4x;
Carmen B uses the original native512 texture with no upscale. Five small shared
sparkle/tape inputs retain original native pixels for shader/blend fidelity.
No local-neural comparison trials are included. Baselines are supplied explicitly
even when the global HD Textures setup option is disabled. All original Banner
artwork is unchanged; no proposed replacement flag was produced or included.

Install: Def Jam Recompiled0.12.1 or later > Mods > Refresh catalogue > HD Fighters
Install/Update. Show testing versions is not required. Enable HD Fighters and
place it AFTER optional Faithful HD in Load Order, then restart the game.
Faithful HD is optional. HD Widescreen Menus is separate. No auto-enable.
Disable/remove the mod to return to original textures. Earlier versions retained.

Scope: fixed roster and identified in-engine Story state source IDs. Created-player
customization, portraits/menus and prerecorded MAD video are separate workstreams.
Unmapped shader/specular/shadow symbolic inputs are not speculative replacements.
No meshes, rigs, animations, executable or gameplay changes. Static review cannot
prove runtime injury switching, Story routing, material alpha or mip behavior.
Those still need native playtesting; unknown small tattoo words remain uncertain.

PLAYTEST: Bonecrusher is specifically queued for this test pack. Also check
Xzibit face/body transitions, injury br01/br02 changes, Story state transitions,
transparent hair/jewelry/tape and distant mip levels. Native verification pending.

Credits: vyanhursky; AI-assisted restoration of the user's own game textures.
Derived game artwork; original rights remain with their respective owners.
The source MIT licence does not cover artwork. No game executable or disc archive.
'''
 (pack/'README.txt').write_text(notes,encoding='utf8')
 receipt=dict(schema=1,id='hd-fighters',version='1.0.0',channel='stable',scope=recipe['scope'],textures=recipe['selections'],png_mips='channels',selection_sha256=sha(HERE/'selection.json'),builder_sha256=sha(Path(__file__)),owner_packaging_and_publication_authorized='2026-10-31',native_verified=False,art_review_state_modified=False,limitations=recipe['limitations'])
 (pack/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 archive=out/'hd-fighters-v1.0.0.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as bundle:
  for p in sorted(p for p in pack.rglob('*') if p.is_file()):
   zi=zipfile.ZipInfo(root+'/'+p.relative_to(pack).as_posix(),date_time=(2026,10,31,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.create_system=3;zi.external_attr=(stat.S_IFREG|0o644)<<16;bundle.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None;files=z.infolist()
 digest=sha(archive);descriptor=dict(size=archive.stat().st_size,unpacked_size=sum(i.file_size for i in files),file_count=len(files),sha256=digest,root=root,urls=[PUBLIC+'/hd-fighters/1.0.0/'+digest+'/'+archive.name])
 helper=module('released_fighters1_mods',args.helper/'setup/mods.py');catalogue=module('catalogue_fighters1_check',args.catalogue/'tools/package_check.py')
 installed=helper.unpack_archive(archive,descriptor,out/'released-installer-validation');checked=catalogue.unpack_archive(archive,descriptor,out/'catalogue-installer-validation');expected={r['source_id'] for r,_ in verified}
 assert set(installed['texture_ids'])==set(checked['texture_ids'])==expected;assert installed['files']==checked['files'];assert len(installed['files'])==221;assert installed['capabilities']==checked['capabilities']==['textures-v1']
 current=json.loads((args.workspace/'workshop.json').read_text());assert all(next(c for c in current['candidates'][r['source_id']] if c['id']==r['revision'])==next(c for c in state['candidates'][r['source_id']] if c['id']==r['revision']) for r,_ in verified if r['revision'])
 artifact=dict(id='hd-fighters',version='1.0.0',archive=descriptor,textures=218,scope=recipe['scope'],source_identities_verified=source_records,installed_file_hashes=installed['files'],released_installer_validated=True,catalogue_validator_validated=True,selected_candidate_metadata_unchanged=True,native_acceptance_pending=True)
 (out/'artifact.json').write_text(json.dumps(artifact,indent=2)+'\n');(out/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n');(out/'RELEASE-NOTES.txt').write_text(notes)
 (out/'upload-plan.json').write_text(json.dumps(dict(profile='defjam-r2',endpoint='https://01e722513e8a17b02561c12731a3e4cb.r2.cloudflarestorage.com',bucket='defjam-ffny-mods',public_base=PUBLIC,prefix='hd-fighters/1.0.0/'+digest,filename=archive.name,local_zip=str(archive),sha256=digest,size=descriptor['size']),indent=2)+'\n')
 print(json.dumps(dict(archive=descriptor,scope=recipe['scope'],validators='both passed'),indent=2))
if __name__=='__main__':main()
