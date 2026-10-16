#!/usr/bin/env python3
"""Local texture review with durable notes, regions, candidate revisions and export.

Requires Pillow; reuses an existing hd_corpus corpus read-only. All review data
and imported artwork live in --workspace, outside tracked source. Example:
  defjam-tools serve --corpus LOCAL_CORPUS --workspace LOCAL_WORK
  defjam-tools workshop import --corpus LOCAL_CORPUS --workspace LOCAL_WORK \
      --asset ORIGINAL_SOURCE_ID --image candidate.png --style faithful
This tool does not call a generation API, install packs, or modify the game.
"""
import argparse
import base64
import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import threading
import time
from urllib.parse import parse_qs, urlparse
import uuid
from urllib.request import Request, urlopen

from PIL import Image

HERE = Path(__file__).resolve().parent / "resources"
MAX_UPLOAD = 24 * 1024 * 1024
STYLES = {"faithful": "Rich original detail", "remaster": "Stylized remaster"}
PILOT = {
    "v2ip_113a.xsh": ("Blaze", "Battle", True),
    "v2ip_113b.xsh": ("Blaze", "Story variant", False),
    "v2ip_113c.xsh": ("Blaze", "Bloody Blaze", False),
    "v2ip_009a.xsh": ("Nyne", "Main", True),
    "v2ip_112a.xsh": ("Trejo", "Main", True),
}


class Invalid(ValueError):
    pass


class Conflict(Invalid):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def inside(root, relative):
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()):
        raise Invalid("Image path leaves its data folder")
    return p


def atomic_json(path, data):
    pending = path.with_name(path.name + "." + uuid.uuid4().hex + ".pending")
    try:
        with pending.open("x", encoding="utf8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def brief(asset, style, note="", regions=(), parent=None):
    direction = ("Restore richer fine detail while closely preserving original shapes, palette, painted shading and grit."
                 if style == "faithful" else
                 "Create a stronger modern stylized remaster of materials and linework, retaining the original game's cartoonish character and grit.")
    return ("Use case: precise-object-edit\nAsset: " + asset["label"] + "\n"
            + ("Input: selected candidate revision "+parent["id"]+" as edit target; original atlas and faithful HD as references.\nParent SHA-256: "+parent["sha256"]+"\n" if parent else
               "Input: original texture atlas as edit target; faithful HD as comparison.\n") + direction + "\n"
            "Preserve every UV island, orientation, mirrored/split lettering, borders and atlas proportions. "
            "Preserve faces and likeness; do not beautify or redesign faces. Apparent low-resolution face damage needs a separate reviewed request. "
            "Use references for tattoos, logos and clothing words. Flag uncertain details for Vlad instead of inventing inscriptions. "
            "Keep original alpha/material channels separately; do not reinterpret their meaning. "
            "No additional logos, objects, lighting or perspective.\n"
            + ("Regional notes: " + json.dumps(regions, ensure_ascii=False) + "\n" if regions else "")
            + ("Requested revision: " + note + "\n" if note else ""))


def classify(asset):
    categories = set(asset.get("categories", [asset.get("category", "Other textures")]))
    for alias in asset.get("aliases", []):
        s = alias["source"].lower()
        if "::screens/portrait/" in s: categories.add("Portraits and selection art")
        if "::screens/shopthumbs/" in s: categories.add("Customization thumbnails")
        if "::screens/venuethumbs/" in s: categories.add("Venue previews")
    return sorted(categories)


def metadata(asset):
    result = dict(fighter="", variant="", pilot=False, featured=False, role="Texture")
    for alias in asset.get("aliases", []):
        member = alias["source"].rsplit("::", 1)[-1].lower()
        if member in PILOT:
            fighter, variant, primary = PILOT[member]
            main = alias.get("index") == 0
            result.update(fighter=fighter, variant=variant, pilot=True,
                          featured=primary and main, role="Primary atlas" if main else "Secondary map · purpose unverified")
            break
    result["label"] = (result["fighter"] + " · " + result["variant"] + " · " + result["role"]
                       if result["pilot"] else asset.get("label", asset["id"][:12]))
    return result


def empty_review():
    return dict(version=0, flag=False, status="unreviewed", notes="", tags=[], regions=[],
                face_reviewed=False, channels_reviewed=False, game_verified=False, selected=False,
                mip_policy="channels")


def region_boxes(regions, target):
    if not isinstance(regions,list) or len(regions)>100: raise Invalid("Invalid assembly regions")
    boxes=[]
    for rect in regions:
        if not isinstance(rect,list) or len(rect)!=4 or any(type(n) not in (int,float) or not math.isfinite(n) or n<0 or n>1 for n in rect): raise Invalid("Invalid assembly coordinates")
        x,y,width,height=rect
        if width<=0 or height<=0 or x+width>1.000001 or y+height>1.000001: raise Invalid("Assembly region outside texture")
        box=(round(x*target[0]),round(y*target[1]),round((x+width)*target[0]),round((y+height)*target[1]))
        if box[2]<=box[0] or box[3]<=box[1]: raise Invalid("Assembly region contains no pixels")
        boxes.append(box)
    return boxes


def assemble_generated(raw, baseline_path, asset, options, parent=None):
    """Technical atlas assembly after imagegen; retain raw output for provenance.

    Resize only an identical aspect ratio. Copy protected areas and alpha from
    the accepted baseline exactly; prompts alone cannot enforce pixel locks.
    Regional revisions retain parent pixels outside explicit edit boxes.
    """
    if set(options)-{"scale","preserve_alpha","protected_regions","edited_regions"}: raise Invalid("Unknown assembly option")
    scale=options.get("scale",4)
    if type(scale)!=int or not 1<=scale<=8: raise Invalid("Assembly scale must be integer 1–8")
    regions=options.get("protected_regions",[])
    target=(asset["width"]*scale,asset["height"]*scale)
    if max(target)>16384: raise Invalid("Assembled atlas is too large")
    boxes=region_boxes(regions,target)
    edits=options.get("edited_regions",[]);edit_boxes=region_boxes(edits,target)
    parent_raw=None
    if edit_boxes:
        if not parent: raise Invalid("Edited regions require a parent revision")
        parent_raw=parent["path"].read_bytes()
        if sha(parent_raw)!=parent["sha256"]: raise Invalid("Parent candidate checksum changed")
    baseline_raw=baseline_path.read_bytes()
    if asset.get("upscaled_hash") and sha(baseline_raw)!=asset["upscaled_hash"]: raise Invalid("Faithful baseline checksum changed")
    with Image.open(io.BytesIO(raw)) as generated, Image.open(io.BytesIO(baseline_raw)) as baseline:
        if generated.format!="PNG" or getattr(generated,"n_frames",1)!=1 or generated.mode not in ("RGB","RGBA"): raise Invalid("Use a single RGB/RGBA PNG draft")
        if generated.width*asset["height"]!=generated.height*asset["width"]: raise Invalid("Generated aspect ratio changed; atlas cannot be stretched into alignment")
        if max(generated.size)>16384: raise Invalid("Generated draft is too large")
        # Atlas RGB can carry data even where alpha is tiny; avoid Pillow's
        # premultiplied RGBA resize destroying those independent channels.
        image=generated.convert("RGB").resize(target,Image.Resampling.LANCZOS).convert("RGBA")
        image.putalpha(generated.convert("RGBA").getchannel("A").resize(target,Image.Resampling.LANCZOS))
        base=baseline.convert("RGBA")
        if base.size!=target:
            resized=base.convert("RGB").resize(target,Image.Resampling.LANCZOS).convert("RGBA")
            resized.putalpha(base.getchannel("A").resize(target,Image.Resampling.LANCZOS));base=resized
        if edit_boxes:
            with Image.open(io.BytesIO(parent_raw)) as prior:
                if prior.size!=target: raise Invalid("Regional revision must use its parent's exact resolution")
                assembled=prior.convert("RGBA")
                for box in edit_boxes: assembled.paste(image.crop(box),box)
                image=assembled
        if options.get("preserve_alpha",True): image.putalpha(base.getchannel("A"))
        for box in boxes: image.paste(base.crop(box),box)
        out=io.BytesIO();image.save(out,format="PNG",compress_level=3)
        return out.getvalue(),dict(raw_sha256=sha(raw),raw_size=list(generated.size),scale=scale,
             baseline_sha256=sha(baseline_raw),preserve_alpha=bool(options.get("preserve_alpha",True)),
             protected_regions=regions,protected_pixel_boxes=[list(b) for b in boxes],
             edited_regions=edits,edited_pixel_boxes=[list(b) for b in edit_boxes],
             parent_sha256=sha(parent_raw) if parent_raw else "")


class WorkspaceLock:
    """One writer process; threads share Workshop.lock, CLI can use --server."""
    def __init__(self, root):
        self.root=Path(root); self.file=None

    def __enter__(self):
        self.root.mkdir(parents=True,exist_ok=True)
        path=self.root/".workshop.lock"
        if path.is_symlink(): raise Invalid("Workspace lock must not be a symlink")
        self.file=path.open("a+b")
        try:
            if os.name=="nt":
                import msvcrt
                self.file.seek(0); self.file.write(b"\0"); self.file.flush(); self.file.seek(0)
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise Invalid("Workshop already open. Use its browser or import with --server http://127.0.0.1:PORT")
        return self

    def __exit__(self,*args):
        self.file.close()


class Workshop:
    def __init__(self, corpus, workspace, aliases=None):
        self.corpus_root = Path(corpus).resolve()
        from .paths import require_private_output
        self.root = require_private_output(workspace)
        if self.root == self.corpus_root or self.root.is_relative_to(self.corpus_root):
            raise Invalid("Choose a separate workspace; the accepted corpus stays read-only")
        self.root.mkdir(parents=True, exist_ok=True)
        self.file = self.root / "workshop.json"
        if self.file.is_symlink(): raise Invalid("Review store must not be a symlink")
        self.lock = threading.RLock()
        raw = json.loads((self.corpus_root / "corpus.json").read_text())
        self.corpus_id = raw["corpus_id"]
        self.assets = {a["id"]: dict(a, **metadata(a), browse_categories=classify(a))
                       for a in raw["assets"] if not a.get("error")}
        self.categories = sorted({c for a in self.assets.values() for c in a["browse_categories"]})
        self.aliases = aliases or {}
        self.data = (json.loads(self.file.read_text()) if self.file.exists() else
                     dict(schema=1, corpus_id=self.corpus_id, reviews={}, candidates={}, requests=[], session={}))
        if self.data.get("schema") != 1 or self.data.get("corpus_id") != self.corpus_id:
            raise Invalid("This workspace belongs to another corpus. Preserve it and choose a separate workspace")
        if not self.file.exists(): atomic_json(self.file, self.data)

    def asset(self, ident):
        try: return self.assets[ident]
        except KeyError: raise Invalid("Unknown texture")

    def candidate(self, ident, revision):
        return next((c for c in self.data["candidates"].get(ident, []) if c["id"] == revision), None)

    def review(self, ident, revision="asset"):
        return copy.deepcopy(self.data["reviews"].get(ident + ":" + revision, empty_review()))

    def summary(self, a):
        r = self.review(a["id"])
        candidates = self.data["candidates"].get(a["id"], [])
        reviews=[r]+[self.review(a["id"],c["id"]) for c in candidates]
        return {**{k: a[k] for k in ("id", "label", "fighter", "variant", "pilot", "featured", "role", "width", "height", "browse_categories")},
                "flag": any(v["flag"] for v in reviews), "status": r["status"], "tags": r["tags"], "notes": any(v["notes"] or v["regions"] for v in reviews),
                "candidates": len(candidates), "selected": any(self.review(a["id"], c["id"])["selected"] for c in candidates),
                "thumbnail": "/api/image/" + a["id"] + "/thumb"}

    def catalog(self, params):
        def value(k, default=""): return params.get(k, [default])[0]
        scope, fighter, category, status, query = (value(k) for k in ("scope", "fighter", "category", "status", "q"))
        query = query.casefold().strip(); found = []
        with self.lock:
            for a in self.assets.values():
                if scope == "featured" and not a["featured"]: continue
                if scope == "pilot" and not a["pilot"]: continue
                if fighter and fighter != a["fighter"]: continue
                if category and category not in a["browse_categories"]: continue
                r = self.review(a["id"])
                reviews=[r]+[self.review(a["id"],c["id"]) for c in self.data["candidates"].get(a["id"],[])]
                if status == "flagged" and not any(v["flag"] for v in reviews): continue
                if status == "noted" and not any(v["notes"] or v["regions"] for v in reviews): continue
                if status == "candidates" and not self.data["candidates"].get(a["id"]): continue
                if status == "selected" and not any(self.review(a["id"], c["id"])["selected"] for c in self.data["candidates"].get(a["id"], [])): continue
                haystack = " ".join([a["label"], a["id"], *[text for v in reviews for text in [v["notes"],*v["tags"],*[region["note"] for region in v["regions"]]]], *[v["source"] for v in a.get("aliases", [])]])
                if query and query not in haystack.casefold(): continue
                found.append(a)
            found.sort(key=lambda a: (not a["featured"], a["fighter"], a["variant"], a["label"], a["id"]))
            page = max(0, int(value("page", "0")))
            return dict(total=len(found), page=page, page_size=30,
                        assets=[self.summary(a) for a in found[page*30:(page+1)*30]])

    def detail(self, ident):
        with self.lock:
            a = self.asset(ident)
            return dict(self.summary(a), aliases=a.get("aliases", []), source_id=ident,
                        decoded_id=a.get("decoded_id"), review=self.review(ident),
                        original="/api/image/"+ident+"/original", faithful="/api/image/"+ident+"/faithful",
                        candidates=[dict(c, review=self.review(ident, c["id"]),
                                         image="/api/image/"+ident+"/"+c["id"]) for c in self.data["candidates"].get(ident, [])],
                        briefs={s: brief(a, s) for s in STYLES})

    def transaction(self, mutate):
        with self.lock:
            before = copy.deepcopy(self.data)
            try:
                result = mutate()
                atomic_json(self.file, self.data)
                return result
            except Exception:
                self.data = before
                raise

    def save_review(self, ident, revision, request):
        self.asset(ident)
        def update():
            candidate = None if revision == "asset" else self.candidate(ident, revision)
            if revision != "asset" and not candidate: raise Invalid("Unknown candidate")
            current = self.review(ident, revision)
            if request.get("version") != current["version"]:
                raise Conflict("Review changed in another tab. Your draft is retained; reload before merging it")
            result = empty_review()
            for key in ("flag", "face_reviewed", "channels_reviewed", "game_verified", "selected"):
                if not isinstance(request.get(key, False), bool): raise Invalid("Invalid review flag")
                result[key] = request.get(key, False)
            result["status"] = request.get("status", "unreviewed")
            if result["status"] not in ("unreviewed", "needs_revision", "approved", "rejected"): raise Invalid("Invalid status")
            result["notes"] = request.get("notes", "")
            if not isinstance(result["notes"], str) or len(result["notes"]) > 20000: raise Invalid("Notes are too long")
            tags = request.get("tags", [])
            if not isinstance(tags, list) or len(tags) > 30 or any(not isinstance(t,str) or len(t)>80 for t in tags): raise Invalid("Invalid tags")
            result["tags"] = list(dict.fromkeys(t.strip() for t in tags if t.strip()))
            result["mip_policy"] = request.get("mip_policy", "channels")
            if result["mip_policy"] not in ("channels", "opacity"): raise Invalid("Unknown channel policy")
            regions = request.get("regions", [])
            if not isinstance(regions, list) or len(regions)>100: raise Invalid("Too many regions")
            for region in regions:
                if not isinstance(region,dict) or set(region) != {"id","rect","note","kind"}: raise Invalid("Invalid region")
                if not isinstance(region["id"],str) or len(region["id"])>80 or not isinstance(region["note"],str) or len(region["note"])>4000: raise Invalid("Invalid regional note")
                rect=region["rect"]
                if not isinstance(rect,list) or len(rect)!=4 or any(type(n) not in (int,float) or not math.isfinite(n) or n<0 or n>1 for n in rect): raise Invalid("Invalid region coordinates")
                if rect[2]<=0 or rect[3]<=0 or rect[0]+rect[2]>1.000001 or rect[1]+rect[3]>1.000001: raise Invalid("Region outside texture")
                if region["kind"] not in ("revise","protect","reference"): raise Invalid("Invalid region type")
            result["regions"] = copy.deepcopy(regions)
            if result["selected"]:
                if not candidate or result["status"] != "approved" or not result["face_reviewed"] or not result["channels_reviewed"]:
                    raise Invalid("Select an atlas-approved candidate after checking face preservation and texture channels")
                for other in self.data["candidates"].get(ident, []):
                    if other["id"] != revision:
                        key=ident+":"+other["id"]
                        if key in self.data["reviews"] and self.data["reviews"][key].get("selected"):
                            self.data["reviews"][key]["selected"]=False
                            self.data["reviews"][key]["version"]+=1
            result.update(version=current["version"]+1, updated=stamp())
            if candidate: result["output_sha256"]=candidate["sha256"]
            self.data["reviews"][ident+":"+revision]=result
            return copy.deepcopy(result)
        return self.transaction(update)

    def save_session(self, session):
        if not isinstance(session,dict) or len(json.dumps(session))>16000: raise Invalid("Invalid session")
        return self.transaction(lambda: self.data.update(session=copy.deepcopy(session)) or session)

    def import_candidate(self, ident, raw, label, style, parent="", prompt="", assembly=None, request_id=""):
        a=self.asset(ident)
        if style not in STYLES or not isinstance(label,str) or not label.strip() or len(label)>140: raise Invalid("Choose a label and style")
        if len(raw)>MAX_UPLOAD: raise Invalid("PNG exceeds the 24 MiB import limit")
        if len(prompt)>20000: raise Invalid("Prompt is too long")
        raw_generated=raw
        assembled=None
        if assembly is not None:
            if not isinstance(assembly,dict): raise Invalid("Invalid assembly options")
            prior=self.candidate(ident,parent) if parent else None
            parent_input=dict(path=inside(self.root,prior["path"]),sha256=prior["sha256"]) if prior else None
            raw,assembled=assemble_generated(raw,inside(self.corpus_root,a["upscaled"]),a,assembly,parent_input)
        with Image.open(io.BytesIO(raw)) as im:
            if im.format != "PNG" or getattr(im,"n_frames",1)!=1: raise Invalid("Import a single PNG texture")
            width,height=im.size
            scale=width//a["width"]
            if not 1<=scale<=8 or width!=a["width"]*scale or height!=a["height"]*scale or max(width,height)>16384:
                raise Invalid("PNG must preserve the full atlas at uniform integer scale 1–8×")
            if im.mode not in ("RGB","RGBA"): raise Invalid("Use an RGB or RGBA PNG")
            im.load(); pixel_hash=sha(im.convert("RGBA").tobytes()); mode=im.mode
        revision="r-"+uuid.uuid4().hex[:16]
        digest=sha(raw); relative="candidates/"+ident+"/"+revision+".png"
        def update():
            if parent and not self.candidate(ident,parent): raise Invalid("Unknown parent revision")
            job=None
            if request_id:
                job=next((q for q in self.data["requests"] if q["id"]==request_id),None)
                if not job or job["asset"]!=ident or job["style"]!=style: raise Invalid("Request does not match candidate asset/style")
            path=inside(self.root,relative); path.parent.mkdir(parents=True,exist_ok=True)
            with path.open("xb") as f: f.write(raw); f.flush(); os.fsync(f.fileno())
            candidate=dict(id=revision,label=label.strip(),style=style,parent=parent,sha256=digest,
                           pixel_sha256=pixel_hash,width=width,height=height,scale=scale,mode=mode,
                           path=relative,prompt=prompt,created=stamp())
            if assembled:
                raw_path="raw/"+ident+"/"+revision+".png";target=inside(self.root,raw_path);target.parent.mkdir(parents=True,exist_ok=True)
                with target.open("xb") as f: f.write(raw_generated);f.flush();os.fsync(f.fileno())
                candidate["assembly"]=dict(assembled,raw_path=raw_path)
            if job:
                job.update(status="generated",output_revision=revision,output_sha256=digest)
                candidate["request_id"]=request_id
            self.data["candidates"].setdefault(ident,[]).append(candidate)
            return copy.deepcopy(candidate)
        return self.transaction(update)

    def queue_request(self, ident, style, revision, note):
        a=self.asset(ident)
        if style not in STYLES or not isinstance(note,str) or len(note)>12000: raise Invalid("Invalid revision brief")
        def update():
            parent=None if revision=="asset" else self.candidate(ident,revision)
            if revision != "asset" and not parent: raise Invalid("Unknown parent candidate")
            for path_key,hash_key in (("original","original_hash"),("upscaled","upscaled_hash")):
                if a.get(hash_key) and sha(inside(self.corpus_root,a[path_key]).read_bytes())!=a[hash_key]:
                    raise Invalid("Source or faithful image changed; verify the retained corpus before generation")
            if parent and sha(inside(self.root,parent["path"]).read_bytes())!=parent["sha256"]:
                raise Invalid("Parent candidate changed; import it as a new revision")
            review=self.review(ident,revision)
            item=dict(id="q-"+uuid.uuid4().hex[:16],asset=ident,label=a["label"],style=style,
                      parent="" if revision=="asset" else revision,status="queued",created=stamp(),
                      prompt=brief(a,style,note or review["notes"],review["regions"],parent),
                      original=str(inside(self.corpus_root,a["original"])),
                      faithful=str(inside(self.corpus_root,a["upscaled"])))
            if parent:
                item.update(parent_image=str(inside(self.root,parent["path"])),parent_sha256=parent["sha256"])
            self.data["requests"].append(item)
            return copy.deepcopy(item)
        return self.transaction(update)

    def image_path(self, ident, revision):
        a=self.asset(ident)
        if revision in ("original","faithful","thumb"):
            return inside(self.corpus_root,a[{"original":"original","faithful":"upscaled","thumb":"thumbnail"}[revision]])
        c=self.candidate(ident,revision)
        if not c: raise Invalid("Unknown candidate image")
        return inside(self.root,c["path"])

    def export_pack(self):
        with self.lock:
            chosen=[]
            for ident,candidates in self.data["candidates"].items():
                for c in candidates:
                    r=self.review(ident,c["id"])
                    if r["selected"]:
                        if r["status"]!="approved" or not r["face_reviewed"] or not r["channels_reviewed"] or r.get("output_sha256")!=c["sha256"]:
                            raise Invalid("Selected candidate needs renewed approval")
                        raw=self.image_path(ident,c["id"]).read_bytes()
                        if sha(raw)!=c["sha256"]: raise Invalid("Candidate file changed; import it as a new revision")
                        chosen.append((ident,c,r,raw))
            if not chosen: raise Invalid("No approved candidates selected. Review a candidate before exporting")
            release="restored-"+time.strftime("%Y%m%d-%H%M%S",time.gmtime())+"-"+secrets.token_hex(2)
            output=self.root/"exports"/release; output.mkdir(parents=True)
            receipt=dict(schema=1,corpus_id=self.corpus_id,created=stamp(),packs=[],assets=[])
            try:
                for policy in ("opacity","channels"):
                    rows=[v for v in chosen if v[2]["mip_policy"]==policy]
                    if not rows: continue
                    name=release+("-o" if policy=="opacity" else "-c")
                    pack=output/name; (pack/"textures").mkdir(parents=True)
                    entries={}
                    for ident,c,r,raw in rows:
                        filename="textures/"+ident+".png"
                        (pack/filename).write_bytes(raw)
                        entries[ident]=filename
                        for runtime,source in self.aliases.items():
                            if source==ident: entries[runtime]=filename
                        receipt["assets"].append(dict(source_id=ident,revision=c["id"],sha256=c["sha256"],
                                                      png_mips=policy,game_verified=r["game_verified"]))
                    (pack/"manifest.ini").write_text("[pack]\nschema=1\nname=Restored fighter pilot\npng_mips="+policy+
                        "\n[textures]\n"+"".join(k+"="+v+"\n" for k,v in sorted(entries.items())),encoding="ascii")
                    receipt["packs"].append(name)
                atomic_json(output/"export.json",receipt)
                (output/"INSTALL.txt").write_text("Local test pack; not installed automatically.\nCopy the pack folders into your data mods folder.\nList faithful HD first and these components last; restart the game.\nMissing keys inherit the baseline. A rejected winning image uses the game original.\nRuntime aliases are bounded; confirm each replacement in game.\n",encoding="utf8")
            except Exception:
                shutil.rmtree(output); raise
            return dict(path=str(output),packs=receipt["packs"],assets=len(chosen))


def handler_for(store, token):
    class Handler(BaseHTTPRequestHandler):
        server_version="TextureWorkshop/1"
        def reply(self, status, data, mime="application/json"):
            if mime=="application/json": data=json.dumps(data,ensure_ascii=False).encode()
            self.send_response(status); self.send_header("Content-Type",mime)
            self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; connect-src 'self' blob:; frame-ancestors 'none'")
            self.end_headers()
            try: self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError): pass

        def route(self):
            u=urlparse(self.path); return u.path.strip("/").split("/"),parse_qs(u.query)

        def do_GET(self):
            try:
                if self.headers.get("Host") not in ("127.0.0.1:"+str(self.server.server_port),"localhost:"+str(self.server.server_port)):
                    return self.reply(403,dict(error="Use the loopback workshop address"))
                parts,q=self.route()
                from . import model_workshop
                model_static=model_workshop.static_file(parts,HERE)
                if model_static: return self.reply(200,*model_static)
                if parts==["api","models"]: return self.reply(200,model_workshop.catalog(store))
                if len(parts)==4 and parts[:2]==["api","model"] and parts[3]=="model.glb":
                    return self.reply(200,model_workshop.model_glb(store,parts[2],q.get("revision",["original"])[0]),"model/gltf-binary")
                if parts==[""]:
                    return self.reply(200,(HERE/"texture_workshop.html").read_bytes(),"text/html; charset=utf-8")
                static={"workshop.js":("texture_workshop.js","text/javascript; charset=utf-8"),
                        "workshop.css":("texture_workshop.css","text/css; charset=utf-8")}
                if len(parts)==1 and parts[0] in static:
                    file,mime=static[parts[0]]; return self.reply(200,(HERE/file).read_bytes(),mime)
                if parts==["api","config"]:
                    with store.lock:
                        return self.reply(200,dict(token=token,corpus_id=store.corpus_id,total=len(store.assets),
                            categories=store.categories,styles=STYLES,session=store.data["session"],
                            queued=sum(q["status"]=="queued" for q in store.data["requests"]),workspace=str(store.root)))
                if parts==["api","catalog"]: return self.reply(200,store.catalog(q))
                if len(parts)==3 and parts[:2]==["api","asset"]: return self.reply(200,store.detail(parts[2]))
                if parts==["api","export-review"]:
                    with store.lock: return self.reply(200,store.data)
                if len(parts)==4 and parts[:2]==["api","image"]:
                    with store.lock: path=store.image_path(parts[2],parts[3])
                    channel=q.get("channel",["rgba"])[0]
                    if channel not in ("rgba","rgb","alpha"): raise Invalid("Unknown image channel")
                    if channel=="rgba":
                        return self.reply(200,path.read_bytes(),"image/jpeg" if path.suffix.lower() in (".jpg",".jpeg") else "image/png")
                    with Image.open(path) as im:
                        im=im.convert("RGBA"); out=io.BytesIO()
                        (im.convert("RGB") if channel=="rgb" else im.getchannel("A")).save(out,format="PNG")
                    return self.reply(200,out.getvalue(),"image/png")
                return self.reply(404,dict(error="Not found"))
            except (Invalid,ValueError,OSError,KeyError) as e: self.reply(400,dict(error=str(e)))

        def do_POST(self):
            try:
                if self.headers.get("Host") not in ("127.0.0.1:"+str(self.server.server_port),"localhost:"+str(self.server.server_port)):
                    return self.reply(403,dict(error="Use the loopback workshop address"))
                expected="http://"+self.headers.get("Host","")
                if self.headers.get("Origin") not in (None,expected) or self.headers.get("X-Workshop-Token")!=token:
                    return self.reply(403,dict(error="Use this workshop's local browser page"))
                length=int(self.headers.get("Content-Length","0"))
                if not 0<length<MAX_UPLOAD*2: raise Invalid("Request too large")
                req=json.loads(self.rfile.read(length)); parts,_=self.route()
                if parts==["api","model-view"]:
                    from .model_workshop import save_view
                    return self.reply(200,save_view(store,req,atomic_json))
                if len(parts)==4 and parts[:2]==["api","review"]:
                    return self.reply(200,store.save_review(parts[2],parts[3],req))
                if parts==["api","session"]: return self.reply(200,store.save_session(req))
                if parts==["api","import"]:
                    raw=base64.b64decode(req["image"],validate=True)
                    c=store.import_candidate(req["asset"],raw,req["label"],req["style"],req.get("parent",""),req.get("prompt",""),req.get("assembly"),req.get("request_id",""))
                    return self.reply(200,c)
                if parts==["api","request"]:
                    return self.reply(200,store.queue_request(req["asset"],req["style"],req.get("revision","asset"),req.get("note","")))
                if parts==["api","export-pack"]: return self.reply(200,store.export_pack())
                return self.reply(404,dict(error="Not found"))
            except Conflict as e: self.reply(409,dict(error=str(e)))
            except (Invalid,ValueError,OSError,KeyError,TypeError) as e: self.reply(400,dict(error=str(e)))

        def log_message(self,*args): pass
    return Handler


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action",choices=("serve","import","export"))
    ap.add_argument("--corpus",type=Path); ap.add_argument("--workspace",type=Path)
    ap.add_argument("--server",help="Import/export through an already running loopback workshop")
    ap.add_argument("--port",type=int,default=8768)
    ap.add_argument("--asset"); ap.add_argument("--image",type=Path); ap.add_argument("--label",default="Imported candidate")
    ap.add_argument("--style",choices=STYLES,default="faithful"); ap.add_argument("--parent",default="")
    ap.add_argument("--prompt-file",type=Path)
    ap.add_argument("--assemble-scale",type=int,help="Normalize a same-aspect draft; copy baseline alpha and protected regions")
    ap.add_argument("--protect-region",action="append",default=[],help="Normalized x,y,width,height copied exactly from faithful HD")
    ap.add_argument("--edit-region",action="append",default=[],help="Only these normalized regions may change; other pixels come from --parent")
    ap.add_argument("--request-id",default="")
    args=ap.parse_args()
    assembly=None
    if args.assemble_scale is not None:
        assembly=dict(scale=args.assemble_scale,preserve_alpha=True,
            protected_regions=[[float(n) for n in text.split(',')] for text in args.protect_region],
            edited_regions=[[float(n) for n in text.split(',')] for text in args.edit_region])
    elif args.protect_region or args.edit_region: ap.error("Region assembly requires --assemble-scale")
    if args.edit_region and not args.parent: ap.error("--edit-region requires --parent")
    if args.action=="import" and (not args.asset or not args.image): ap.error("import requires --asset and --image")
    if args.server:
        u=urlparse(args.server)
        if args.action=="serve" or u.scheme!="http" or u.hostname not in ("127.0.0.1","localhost") or not u.port or u.path not in ("", "/") or u.username or u.password:
            ap.error("--server must name a local http://127.0.0.1:PORT workshop for import/export")
        base=args.server.rstrip("/")
        with urlopen(base+"/api/config",timeout=10) as response: config=json.load(response)
        payload=({"asset":args.asset,"image":base64.b64encode(args.image.read_bytes()).decode(),
                  "label":args.label,"style":args.style,"parent":args.parent,
                  "assembly":assembly,"request_id":args.request_id,
                  "prompt":args.prompt_file.read_text() if args.prompt_file else ""} if args.action=="import" else {})
        request=Request(base+("/api/import" if args.action=="import" else "/api/export-pack"),
                        data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","X-Workshop-Token":config["token"]})
        with urlopen(request,timeout=60) as response: print(response.read().decode())
        return
    if not args.corpus or not args.workspace: ap.error("--corpus and --workspace are required without --server")
    aliases=json.loads((HERE/"profiles/hd-runtime-aliases.json").read_text())["aliases"]
    with WorkspaceLock(args.workspace):
        store=Workshop(args.corpus,args.workspace,aliases)
        if args.action=="import":
            print(json.dumps(store.import_candidate(args.asset,args.image.read_bytes(),args.label,args.style,args.parent,
                args.prompt_file.read_text() if args.prompt_file else "",assembly,args.request_id),indent=2)); return
        if args.action=="export": print(json.dumps(store.export_pack(),indent=2)); return
        if not 1024<=args.port<=65535: ap.error("Choose a port from 1024 through 65535")
        server=ThreadingHTTPServer(("127.0.0.1",args.port),handler_for(store,secrets.token_urlsafe(32)))
        print("Texture workshop: http://127.0.0.1:"+str(args.port),flush=True)
        print("Saved reviews: "+str(store.file),flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: server.server_close()


if __name__=="__main__": main()
