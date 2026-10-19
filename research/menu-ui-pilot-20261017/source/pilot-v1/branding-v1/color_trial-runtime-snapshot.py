"""Deterministic, private skin-color trials. Never imports, approves or installs art.

Geometry defines skin coverage and protected-to-body UV seams. Original RGB is
palette authority; source alpha, protected pixels and other materials stay exact.
Outputs are immutable trial files with input/recipe/mask hashes for later import.
"""
import argparse
from collections import defaultdict, deque
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .paths import require_private_output

VERSION = 1
XYZ = np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])
WHITE = np.array([.95047,1,1.08883])
VARIANTS = {"gentle": dict(chroma=.75,luminance=0,spatial=False),
            "source-palette": dict(chroma=1.,luminance=.5,spatial=True)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rgb_to_lab(rgb):
    v = np.asarray(rgb,dtype=np.float64)/255
    v = np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
    xyz = (v @ XYZ.T)/WHITE
    d = 6/29
    f = np.where(xyz>d**3,np.cbrt(xyz),xyz/(3*d*d)+4/29)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],axis=-1)


def lab_to_rgb(lab):
    v = np.asarray(lab,dtype=np.float64)
    y = (v[...,0]+16)/116
    f = np.stack([y+v[...,1]/500,y,y-v[...,2]/200],axis=-1)
    d = 6/29
    xyz = np.where(f>d,f**3,3*d*d*(f-4/29))*WHITE
    linear = xyz @ np.linalg.inv(XYZ).T
    encoded = np.where(linear<=.0031308,12.92*linear,1.055*np.maximum(linear,0)**(1/2.4)-.055)
    clipped = np.any((encoded<-.5/255)|(encoded>1+.5/255),axis=-1)
    return np.rint(np.clip(encoded,0,1)*255).astype(np.uint8), clipped


def protected(uv, boxes):
    return any(x<=uv[0]<=x+w and y<=uv[1]<=y+h for x,y,w,h in boxes)


def geometry_masks(geometry, size, protected_regions, seam_height_range=None, seam_half_width=None):
    """Skin/other material masks and paired UV seam edges, in source coordinates.

    Only paired edges crossing a protected/unprotected skin region are guarded.
    Position weld tolerance is 1e-4 game units; ambiguous or absent matches never
    trigger a guessed seam. Transparent other materials are conservatively held.
    """
    if not isinstance(size,int) or not 8<=size<=2048:
        raise ValueError("Analysis size must be 8..2048")
    if geometry.get("schema")!=1 or not geometry.get("meshes"):
        raise ValueError("Expected decoded schema-1 geometry")
    for box in protected_regions:
        if len(box)!=4 or any(not math.isfinite(v) or v<0 for v in box) or box[2]<=0 or box[3]<=0 or box[0]+box[2]>1 or box[1]+box[3]>1:
            raise ValueError("Invalid protected region")
    skin = Image.new("L",(size,size)); other = Image.new("L",(size,size))
    edges = defaultdict(list)
    for mesh in geometry["meshes"]:
        is_skin = mesh["group"].startswith("emc2_skin")
        draw = ImageDraw.Draw(skin if is_skin else other)
        pos,uv,indices = mesh["positions"],mesh["uv"],mesh["indices"]
        if len(indices)%3 or len(pos)!=len(uv):
            raise ValueError("Invalid triangle arrays")
        for at in range(0,len(indices),3):
            ids = indices[at:at+3]
            if any(type(i)!=int or i<0 or i>=len(uv) for i in ids):
                raise ValueError("Invalid triangle index")
            points = [uv[i] for i in ids]
            if any(len(p)!=2 or not all(math.isfinite(v) and 0<=v<=1 for v in p) for p in points):
                raise ValueError("UV outside atlas")
            draw.polygon([(u*size,v*size) for u,v in points],fill=255)
            if not is_skin: continue
            centroid = np.mean(points,axis=0).tolist()
            for a,b in zip(ids,ids[1:]+ids[:1]):
                pair = tuple(tuple(round(float(v),4) for v in pos[i]) for i in (a,b))
                tex = (uv[a],uv[b])
                if pair[0]==pair[1]: continue
                if pair[1]<pair[0]: pair=pair[::-1];tex=tex[::-1]
                edges[pair].append(dict(uv=tex,centroid=centroid,held=all(protected(p,protected_regions) for p in tex),editable=all(not protected(p,protected_regions) for p in tex)))
    held = Image.new("L",(size,size)); draw = ImageDraw.Draw(held)
    for x,y,w,h in protected_regions:
        draw.rectangle((round(x*size),round(y*size),round((x+w)*size)-1,round((y+h)*size)-1),fill=255)
    if seam_height_range is not None:
        if len(seam_height_range)!=2 or not 0<=seam_height_range[0]<seam_height_range[1]<=1:
            raise ValueError("Invalid seam height range")
        bounds=geometry["bounds"];low=bounds[0][1];height=bounds[1][1]-low
        center=(bounds[0][0]+bounds[1][0])/2
        if seam_half_width is not None and (not math.isfinite(seam_half_width) or not 0<seam_half_width<1):
            raise ValueError("Invalid seam half width")
        if height<=0:raise ValueError("Invalid model height")
    seams=[]; seen=set()
    for pair,items in edges.items():
        if seam_height_range is not None and not all(low+height*seam_height_range[0]<=p[1]<=low+height*seam_height_range[1] for p in pair):
            continue
        if seam_half_width is not None and seam_height_range is not None and any(abs(p[0]-center)>height*seam_half_width for p in pair):
            continue
        locked=[row for row in items if row["held"]]
        for row in items:
            key=tuple(tuple(p) for p in row["uv"])
            if locked and row["editable"] and key not in seen:
                seen.add(key);seams.append(dict(body=row["uv"],face=locked[0]["uv"],body_centroid=row["centroid"],face_centroid=locked[0]["centroid"]))
    editable = (np.asarray(skin)>0)&~(np.asarray(other)>0)&~(np.asarray(held)>0)
    # Padding may extend only into unused atlas pixels, never another material.
    padded = (np.asarray(skin.filter(ImageFilter.MaxFilter(3)))>0)&~(np.asarray(other)>0)&~(np.asarray(held)>0)
    return editable, padded, seams, np.asarray(other)>0, np.asarray(held)>0


def seam_guard(size, seams, inner=3., outer=12.):
    if not 0<=inner<outer:
        raise ValueError("Seam radii must satisfy 0 <= inner < outer")
    # Pixel coordinates are source texels; radii stay stable across HD scales.
    guard=np.zeros((size,size),dtype=np.float64)
    for seam in seams:
        a,b=np.asarray(seam["body"])*size
        lo=np.maximum(np.floor(np.minimum(a,b)-outer-1).astype(int),0)
        hi=np.minimum(np.ceil(np.maximum(a,b)+outer+1).astype(int),size)
        if np.any(hi<=lo):continue
        yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]]
        points=np.stack([xx+.5,yy+.5],axis=-1)
        v=b-a;length=float(v@v)
        if not length:continue
        t=np.clip(((points-a)@v)/length,0,1)
        distance=np.linalg.norm(points-(a+t[...,None]*v),axis=-1)
        t=np.clip((distance-inner)/(outer-inner),0,1)
        value=1-t*t*(3-2*t)
        patch=guard[lo[1]:hi[1],lo[0]:hi[0]]
        np.maximum(patch,value,out=patch)
    return guard


def box_blur(array, radius):
    result=np.asarray(array,dtype=np.float64)
    for axis in (0,1):
        pads=[(0,0)]*result.ndim;pads[axis]=(radius,radius)
        p=np.pad(result,pads)
        sums=np.cumsum(p,axis=axis)
        shape=list(sums.shape);shape[axis]=1
        sums=np.concatenate([np.zeros(shape),sums],axis=axis)
        low=[slice(None)]*result.ndim;high=list(low)
        low[axis]=slice(0,-(2*radius+1));high[axis]=slice(2*radius+1,None)
        result=(sums[tuple(high)]-sums[tuple(low)])/(2*radius+1)
    return result


def components(mask):
    remaining=mask.copy();height,width=mask.shape
    for y,x in zip(*np.nonzero(mask)):
        if not remaining[y,x]:continue
        q=deque([(int(y),int(x))]);remaining[y,x]=False;points=[]
        while q:
            yy,xx=q.popleft();points.append((yy,xx))
            for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                if 0<=ny<height and 0<=nx<width and remaining[ny,nx]:
                    remaining[ny,nx]=False;q.append((ny,nx))
        yield np.array(points,dtype=int)


def color_field(reference, parent, sample_mask, padded, spatial):
    ref=rgb_to_lab(reference);draft=rgb_to_lab(parent)
    chroma=np.linalg.norm(draft[...,1:],axis=-1)
    valid=sample_mask&(ref[...,0]>32)&(ref[...,0]<90)&(draft[...,0]>32)&(draft[...,0]<90)&(chroma>8)&(chroma<65)
    if np.count_nonzero(valid)<32:
        raise ValueError("Too few stable skin pixels for calibration")
    delta=ref-draft
    median=np.median(delta[valid],axis=0)
    # Avoid pulling tattoo redesign differences into the color/shading field.
    delta=np.clip(delta,median-np.array([8,6,6]),median+np.array([8,6,6]))
    field=np.zeros_like(delta)
    for points in components(padded):
        ys,xs=points.T
        y0,y1=int(ys.min()),int(ys.max())+1;x0,x1=int(xs.min()),int(xs.max())+1
        component=np.zeros((y1-y0,x1-x0),dtype=bool);component[ys-y0,xs-x0]=True
        weights=valid[y0:y1,x0:x1]&component
        local=delta[y0:y1,x0:x1]
        anchor=np.median(local[weights],axis=0) if np.count_nonzero(weights)>=32 else median
        if spatial:
            numerator=local*weights[...,None];denominator=weights.astype(float)
            for _ in range(3):
                numerator=box_blur(numerator,6);denominator=box_blur(denominator,6)
            values=np.divide(numerator,denominator[...,None],out=np.broadcast_to(anchor,local.shape).copy(),where=denominator[...,None]>.02)
        else: values=np.broadcast_to(anchor,local.shape)
        field[ys,xs]=values[ys-y0,xs-x0]
    return np.clip(field,[-8,-15,-15],[8,15,15]),dict(sample_count=int(valid.sum()),median_reference_minus_parent_Lab=median.tolist())


def resize_float(array, size, resample=Image.Resampling.BILINEAR):
    if array.ndim==2:
        return np.asarray(Image.fromarray(array.astype(np.float32)).resize(size,resample),dtype=np.float64)
    return np.stack([resize_float(array[...,i],size,resample) for i in range(array.shape[-1])],axis=-1)


def correct(reference, parent, geometry, protected_regions, variant, source_size=512, seam_height_range=None, seam_half_width=None):
    if variant not in VARIANTS:raise ValueError("Unknown trial variant")
    if reference.size!=parent.size or reference.width!=reference.height or reference.width%source_size or reference.width>4096:
        raise ValueError("Use equal square images at integer source scale, at most 4096")
    config=VARIANTS[variant]
    ref=np.asarray(reference.convert("RGBA"));raw=np.asarray(parent.convert("RGBA"))
    if not np.array_equal(ref[...,3],raw[...,3]):raise ValueError("Parent alpha differs from baseline")
    mask,padded,seams,other,held=geometry_masks(geometry,source_size,protected_regions,seam_height_range,seam_half_width)
    if not seams:raise ValueError("No proven protected/body UV seam; supply verified geometry and protected regions")
    low_ref=np.asarray(reference.convert("RGB").resize((source_size,source_size),Image.Resampling.LANCZOS))
    low_raw=np.asarray(parent.convert("RGB").resize((source_size,source_size),Image.Resampling.LANCZOS))
    field,report=color_field(low_ref,low_raw,mask,padded,config["spatial"])
    size=parent.size
    editable=resize_float(padded.astype(float),size,Image.Resampling.NEAREST)>0
    # Repeat exact integer source masks so neither protected faces nor another
    # material can be recolored by interpolation at the mask boundary.
    held_hd=resize_float(held.astype(float),size,Image.Resampling.NEAREST)>0
    other_hd=resize_float(other.astype(float),size,Image.Resampling.NEAREST)>0
    field=resize_float(field,size)
    lab=rgb_to_lab(raw[...,:3])
    # Keep dark/neutral tattoo ink from acquiring a compensating blue cast.
    t=np.clip((lab[...,0]-18)/20,0,1);weight=t*t*(3-2*t)
    c=np.clip((np.linalg.norm(lab[...,1:],axis=-1)-3)/10,0,1);weight*=c*c*(3-2*c)
    shift=field*weight[...,None]*np.array([config["luminance"],config["chroma"],config["chroma"]])
    corrected,clipped=lab_to_rgb(lab+shift)
    scale=parent.width/source_size
    guard=seam_guard(parent.width,seams,inner=3*scale,outer=12*scale)*editable
    mixed=np.rint(corrected*(1-guard[...,None])+ref[...,:3]*guard[...,None]).astype(np.uint8)
    out=raw.copy();out[editable,:3]=mixed[editable]
    out[held_hd|other_hd]=raw[held_hd|other_hd]
    # Protected input must already be baseline-identical; do not silently fix a
    # different identity and call it a color correction.
    if not np.array_equal(raw[held_hd],ref[held_hd]):raise ValueError("Protected parent pixels differ from faithful baseline")
    checks=dict(alpha_exact=bool(np.array_equal(out[...,3],raw[...,3])),protected_exact=bool(np.array_equal(out[held_hd],raw[held_hd])),other_materials_exact=bool(np.array_equal(out[other_hd],raw[other_hd])),outside_mask_exact=bool(np.array_equal(out[~editable],raw[~editable])),seam_core_exact=bool(np.array_equal(out[guard>=1],ref[guard>=1])))
    if not all(checks.values()):raise ValueError("Color trial invariant failed")
    report.update(variant=variant,parameters=config,version=VERSION,source_size=source_size,blur_radius_source=6,blur_passes=3,seam_inner_source=3,seam_outer_source=12,seam_edges=len(seams),seam_height_range=seam_height_range,seam_half_width=seam_half_width,edited_pixels=int(np.count_nonzero(np.any(out!=raw,axis=-1))),gamut_clipped_pixels=int(np.count_nonzero(clipped&editable)),checks=checks)
    masks=dict(editable=Image.fromarray(editable.astype(np.uint8)*255),seam_guard=Image.fromarray(np.rint(guard*255).astype(np.uint8)))
    return Image.fromarray(out),report,masks,seams


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference",type=Path,required=True)
    ap.add_argument("--parent-image",type=Path,required=True)
    ap.add_argument("--geometry",type=Path,required=True)
    for name in ("reference","parent","geometry"):
        ap.add_argument("--"+name+"-sha256",required=True,help="Expected source/parent/geometry pin")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--parent-id",required=True)
    ap.add_argument("--asset-id",required=True)
    ap.add_argument("--source-size",type=int,default=512)
    ap.add_argument("--seam-height-range",help="Restrict proven seam edges to normalized model height min,max")
    ap.add_argument("--protect-region",action="append",required=True,help="Normalized x,y,width,height")
    ap.add_argument("--seam-half-width",type=float,help="Limit seam to +/- this fraction of model height about model center X")
    args=ap.parse_args()
    if args.seam_half_width is not None and not args.seam_height_range:
        ap.error("Seam half width requires a height range")
    output=require_private_output(args.output)
    if output.exists():ap.error("Trial output must be a new directory; old recipes stay immutable")
    raw={name:path.read_bytes() for name,path in (("reference",args.reference),("parent",args.parent_image),("geometry",args.geometry))}
    for name,data in raw.items():
        if sha(data)!=getattr(args,name+"_sha256"):
            ap.error(name+" input checksum changed")
    geometry=json.loads(raw["geometry"])
    if geometry.get("source_id")!=args.asset_id:
        ap.error("Geometry source ID does not match atlas")
    boxes=[[float(v) for v in text.split(",")] for text in args.protect_region]
    seam_height_range=[float(v) for v in args.seam_height_range.split(",")] if args.seam_height_range else None
    results=[]
    for variant in VARIANTS:
        with Image.open(io.BytesIO(raw["reference"])) as ref,Image.open(io.BytesIO(raw["parent"])) as parent:
            for image in (ref,parent):
                if image.format!="PNG" or image.mode not in ("RGB","RGBA") or getattr(image,"n_frames",1)!=1:
                    ap.error("Use single RGB/RGBA PNG inputs")
            image,report,masks,seams=correct(ref,parent,geometry,boxes,variant,args.source_size,seam_height_range,args.seam_half_width)
        results.append((variant,image,report,masks,seams))
    output.mkdir(parents=True)
    receipt=dict(schema=1,processor="defjam_tools.color_trial",processor_sha256=sha(Path(__file__).read_bytes()),parent_id=args.parent_id,asset_id=args.asset_id,inputs={name:dict(path=str(path.resolve()),sha256=sha(raw[name])) for name,path in (("reference",args.reference),("parent",args.parent_image),("geometry",args.geometry))},protected_regions=boxes,outputs=[])
    for variant,image,report,masks,seams in results:
        file=output/(variant+".png");image.save(file,compress_level=3)
        report.update(file=file.name,sha256=sha(file.read_bytes()),masks={})
        for name,mask in masks.items():
            path=output/(variant+"-"+name+".png");mask.save(path)
            report["masks"][name]=dict(file=path.name,sha256=sha(path.read_bytes()))
        report["seams"]=seams
        receipt["outputs"].append(report)
        brief=dict(type="deterministic-color-trial",parent=args.parent_id,asset=args.asset_id,inputs=receipt["inputs"],recipe={k:v for k,v in report.items() if k!="seams"},processor_sha256=receipt["processor_sha256"],protected_regions=boxes,receipt=str(output/"receipt.json"),note="Color-only postprocess of existing imagegen v4. No redraw/warp/resampling of parent pixels. Protected face, alpha, other materials and outside mask exact; UV seam core restores faithful original. New unapproved review draft, not installed/game verified.")
        (output/(variant+"-recipe.txt")).write_text(json.dumps(brief,indent=2)+"\n",encoding="utf8")
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf8")
    print(json.dumps(dict(output=str(output),variants=[dict(variant=r[2]["variant"],checks=r[2]["checks"],seams=r[2]["seam_edges"]) for r in results]),indent=2))


if __name__=="__main__":main()
