"""Full-left native material harmonization of a source-only AI outpaint.

Same original center/right. Smooth overlapping native-lightness quantile and
chroma transfer on added pixels; no reflection/edge-hold strips or row warps.
"""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,shutil,importlib.util,numpy as np
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',r/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams)
j=json.loads((p/'generation-result.json').read_text());shutil.copy2(j['path'],p/'raw.png');raw=Image.open(p/'raw.png').convert('RGB');assert abs(raw.width/raw.height-1808/1440)<.006;im=raw.resize((1808,1440),Image.Resampling.LANCZOS);im.save(p/'normalized.png');j['raw_size']=list(raw.size);j['raw_sha256']=sha(p/'raw.png');j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='Only new left brickwork,full1600px width. Native material tone/chroma/softness calibrated. Originalcenter/right discarded from model output and retained exactly.';(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=1,pilot_total_calls=83,calls=[j]),indent=2)+'\n')
base=Image.open(r/'battle-setup-v2/cmtype-wide-v2.png').convert('RGB');before=np.array(base);source=base.crop((1600,0,1808,1440));src=np.array(source);source_lab=rgb_to_lab(src)
def rms(im):
 a=np.array(im).astype(float);b=np.array(im.filter(ImageFilter.GaussianBlur(3))).astype(float);return float(np.sqrt(np.mean((a-b)**2)))
# Compare actual generated brick region, not the generated copy of fixed context.
ref_rms=rms(source.crop((0,90,200,1320)));trials=[]
for rad in [0,.5,.75,1,1.25,1.5,2,2.5,3]:
 filtered=im if rad==0 else im.filter(ImageFilter.GaussianBlur(rad));trials.append((abs(rms(filtered.crop((1360,90,1560,1320)))-ref_rms),rad))
radius=min(trials)[1];filtered=im if radius==0 else im.filter(ImageFilter.GaussianBlur(radius));gen=np.array(filtered.crop((0,0,1600,1440)));lab=rgb_to_lab(gen);outlab=lab.copy();quantiles=np.linspace(0,1,65);nodes=[78,270,462,654,846,1038,1230,1374];maps=[];parameters=[]
for y in nodes:
 lo=max(78,y-192);hi=min(1344,y+192);hi=max(hi,lo+1);g=lab[lo:hi];s=source_lab[lo:hi];gq=np.quantile(g[:,:,0],quantiles);sq=np.quantile(s[:,:,0],quantiles);gx,ix=np.unique(gq,return_index=True);sx=sq[ix];gmean=g[:,:,1:].mean((0,1));smean=s[:,:,1:].mean((0,1));scale=np.clip(s[:,:,1:].std((0,1))/np.maximum(g[:,:,1:].std((0,1)),.1),.5,1.5);maps.append((gx,sx,gmean,smean,scale));parameters.append(dict(y=y,sample=[lo,hi],gen_L_quantiles=gq.tolist(),source_L_quantiles=sq.tolist(),gen_ab_mean=gmean.tolist(),source_ab_mean=smean.tolist(),ab_scale=scale.tolist()))
for y in range(78,1440):
 i=max(0,min(len(nodes)-2,int(np.searchsorted(nodes,y)-1)));t=np.clip((y-nodes[i])/(nodes[i+1]-nodes[i]),0,1);t=t*t*(3-2*t);results=[]
 for k in [i,i+1]:
  gx,sx,gmean,smean,scale=maps[k];v=lab[y].copy();v[:,0]=np.interp(v[:,0],gx,sx);v[:,1:]=(v[:,1:]-gmean)*scale+smean;results.append(v)
 outlab[y]=results[0]*(1-t)+results[1]*t
matched,_=lab_to_rgb(outlab);Image.fromarray(matched).save(p/'native-material-calibrated.png');a=before.copy();a[78:,:1600]=matched[78:]
# Smallest one-sided boundary correction; whole-side material is already calibrated.
x0,x1,y0,y1=1088,1600,78,1440;band=a[y0:y1,x0:x1].astype(float);fixed=band.copy();fixed[:,-1]=before[y0:y1,1600];t=np.linspace(0,1,512)[:,None]
for y in [0,-1]:fixed[y]=band[y]+(fixed[y,0]-band[y,0])*(1-t)+(fixed[y,-1]-band[y,-1])*t
reconciled,res=seams.boundary_match(band,fixed);a[y0:y1,x0:x1]=np.rint(reconciled).clip(0,255).astype('uint8')
# Beam retained; gently meet it in generated brick's first16rows only.
t=np.linspace(0,1,16);weight=t*t*(3-2*t);a[78:94,:1600]=np.rint(before[78:94,:1600]*(1-weight[:,None,None])+a[78:94,:1600]*weight[:,None,None]).astype('uint8')
assert np.array_equal(a[:,1600:],before[:,1600:]);assert np.array_equal(a[:78],before[:78]);master=Image.fromarray(a);master.save(p/'cmtype-wide-v3.png')
for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 x=(5120-w)//2;out=master.crop((x,0,x+w,1440));out.save(p/('cmtype-'+ratio+'-v3.png'));assert np.array_equal(np.array(out)[:,(w-1920)//2:(w+1920)//2],before[:,1600:3520])
for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/('cmtype-'+side+'-join.png'))
for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
 layer=Image.new('RGBA',(5120,1440));layer.paste(master.crop((x0,0,x1,1440)),(x0,0));layer.save(p/('cmtype-'+side+'-extension-v3.png'))
base.crop((1216,0,1984,1440)).save(p/'left-before.png');master.crop((1216,0,1984,1440)).save(p/'left-current.png');master.crop((0,0,1856,1440)).save(p/'full-left-proof.png')
receipt=dict(domain=[0,78,1600,1362],strategy='Replace entire AI leftbrick material using only nativecontext,then smoothly transfer sourceLab lightness distribution and chroma in overlapping384px-high windows. No narrow mixed-material gap.',source_reference=[1600,0,208,1440],source_detail_rms=ref_rms,generated_gaussian_radius=radius,quantile_parameters=parameters,interpolation='smoothstep between8height nodes;65lightness quantiles;sourceab mean/std transfer',boundary_band=[1088,78,512,1362],harmonic_residual=res,original_center_and_entire_right_exact=True,top78_exact=True,no_source_copy_strip=True,no_row_warp=True,new_calls=1,pilot_total_calls=83,master_sha256=sha(p/'cmtype-wide-v3.png'),processor_sha256=sha(Path(__file__)));(p/'assembly-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==h for f,h in prev.items());ap=json.loads((r/'battle-fighter-approval-20261019.json').read_text());assert all(sha(r/f['path'])==f['sha256'] for f in ap['files']);(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_fighter_pins_exact=39,entire_right_v2_exact=True,original_center_exact=True,five_aspect_centers_exact=True,top78_exact=True,new_builtin_calls=1,pilot_total_calls=83),indent=2)+'\n');print('PASS',len(prev),'priorPNGs/39fighterpins/5centers/entireright/top78 exact;generated softness radius',radius)
