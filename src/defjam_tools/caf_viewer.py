"""CAF inspection service. Reads workshop revisions; writes only its own state."""
import argparse
from collections import OrderedDict
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import parse_qs, urlparse

import numpy as np
from PIL import Image

from .caf_assets import BUILDS, VERSION, build_catalog, fit_build, palette_images, sha, with_palette
from .paths import require_private_output
from .texture_workshop import Conflict, Invalid, WorkspaceLock, atomic_json, inside

HERE = Path(__file__).resolve().parent / "resources"
MAX_REQUEST = 128 * 1024


def rgba_resize(image, size, sampling=Image.Resampling.LANCZOS):
    image = image.convert("RGBA")
    if image.size == size:
        return image
    rgb = image.convert("RGB").resize(size, sampling).convert("RGBA")
    rgb.putalpha(image.getchannel("A").resize(size, sampling))
    return rgb


def composite(canvas, image, origin, mode):
    """Source FSH copy or RGB alpha blend; keep max material alpha.

    The game's 8-bit RGB blend divides by 256 with rounding; endpoints are
    handled explicitly. This is a texture composition, not a game shader.
    """
    x, y = origin
    if min(x, y) < 0 or x + image.width > canvas.width or y + image.height > canvas.height:
        raise Invalid("Texture leaves the composed CAF atlas")
    if mode == "c":
        canvas.paste(image, (x, y))
        return
    if mode != "b":
        raise Invalid("Unknown CAF composite mode")
    target = (x, y, x + image.width, y + image.height)
    dst = np.array(canvas.crop(target), dtype=np.uint32)
    src = np.array(image, dtype=np.uint32)
    alpha = src[:, :, 3:4]
    rgb = (src[:, :, :3] * alpha + dst[:, :, :3] * (255 - alpha) + 128) >> 8
    rgb = np.where(alpha == 255, src[:, :, :3], np.where(alpha == 0, dst[:, :, :3], rgb))
    out = np.concatenate((rgb, np.maximum(src[:, :, 3:4], dst[:, :, 3:4])), axis=2)
    canvas.paste(Image.fromarray(out.astype(np.uint8)), (x, y))


class SourceReader:
    """No Workshop constructor or workspace lock: production stays read-only."""
    def __init__(self, corpus, workspace):
        self.corpus_root = Path(corpus).resolve()
        self.root = Path(workspace).resolve()
        raw = json.loads((self.corpus_root / "corpus.json").read_text(encoding="utf8"))
        self.corpus_id = raw["corpus_id"]
        self.assets = {a["id"]: a for a in raw["assets"] if not a.get("error")}

    def snapshot(self):
        file = self.root / "workshop.json"
        if file.is_symlink():
            raise Invalid("Workshop metadata must not be a symlink")
        data = json.loads(file.read_text(encoding="utf8")) if file.exists() else dict(schema=1, corpus_id=self.corpus_id, candidates={})
        if data.get("schema") != 1 or data.get("corpus_id") != self.corpus_id:
            raise Invalid("Workshop belongs to a different corpus")
        return data

    def revisions(self, ident, snapshot=None):
        if ident not in self.assets:
            raise Invalid("Unknown CAF texture")
        data = snapshot if snapshot is not None else self.snapshot()
        return [dict(id="original", label="Original"), dict(id="faithful", label="Lanczos 4×")] + [
            dict(id=c["id"], label=c["label"], sha256=c["sha256"], parent=c.get("parent", ""))
            for c in data["candidates"].get(ident, [])]

    def image(self, ident, revision, snapshot=None):
        if ident not in self.assets:
            raise Invalid("Unknown CAF texture")
        asset = self.assets[ident]
        if revision in ("original", "faithful"):
            key = "original" if revision == "original" else "upscaled"
            file = inside(self.corpus_root, asset[key])
            expected = asset[key + "_hash"]
        else:
            data = snapshot if snapshot is not None else self.snapshot()
            candidate = next((c for c in data["candidates"].get(ident, []) if c["id"] == revision), None)
            if not candidate:
                raise Invalid("Unknown CAF texture revision")
            file, expected = inside(self.root, candidate["path"]), candidate["sha256"]
        raw = file.read_bytes()
        if sha(raw) != expected:
            raise Invalid("Texture checksum changed; import a new immutable revision")
        return raw


class CafViewer:
    def __init__(self, catalog, reader, state_dir):
        self.root = Path(catalog).resolve()
        self.reader = reader
        self.state_root = require_private_output(state_dir)
        if (self.state_root == reader.root or self.state_root.is_relative_to(reader.root)
                or self.state_root == reader.corpus_root or self.state_root.is_relative_to(reader.corpus_root)
                or self.state_root == self.root or self.state_root.is_relative_to(self.root)):
            raise Invalid("Use a separate CAF state folder outside the workshop, corpus and immutable cache")
        self.catalog = json.loads((self.root / "catalog.json").read_text(encoding="utf8"))
        if self.catalog.get("schema") != 1 or self.catalog.get("decoder") not in (1, VERSION) or self.catalog.get("corpus_id") != reader.corpus_id:
            raise Invalid("Incompatible CAF cache/corpus; rebuild into a new private folder")
        self.groups = {g["id"]: g for g in self.catalog["groups"]}
        self.items = {item["id"]: (g, item) for g in self.groups.values() for item in g["items"]}
        self.assets = {r["asset"] for res in self.catalog["resources"].values() for r in res["records"] if r.get("asset")}
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.file = self.state_root / "caf-state.json"
        if self.file.is_symlink():
            raise Invalid("CAF state must not be a symlink")
        self.state = (json.loads(self.file.read_text(encoding="utf8")) if self.file.exists() else
                      dict(schema=1, corpus_id=reader.corpus_id, version=0, outfits={}, queue=[], session={}))
        if self.state.get("schema") != 1 or self.state.get("corpus_id") != reader.corpus_id:
            raise Invalid("Incompatible CAF inspection state; preserve it and choose another folder")
        self.lock = threading.RLock()
        self.render_lock = threading.Lock()
        self.renders = OrderedDict()
        self.geometry_cache = {}

    def verified(self, record):
        path = inside(self.root, record["path"])
        raw = path.read_bytes()
        if sha(raw) != record["sha256"]:
            raise Invalid("CAF cache checksum changed; rebuild it")
        return raw

    def default_outfit(self):
        slots = {}
        for slot in (2, 3, 5, 12, 13, 14, 18):
            group = self.groups.get(str(slot))
            if group:
                item = next((i for i in group["items"] if i.get("geometry")), None)
                if item:
                    slots[str(slot)] = dict(item=item["id"], style=0, color=0, palette="default")
        return dict(build="C", skin="pl05", slots=slots, revisions={})

    def validate_outfit(self, value):
        if not isinstance(value, dict) or set(value) - {"build", "skin", "slots", "revisions"}:
            raise Invalid("Invalid CAF outfit")
        if value.get("build") not in BUILDS or not re.fullmatch(r"pl0[1-8]", value.get("skin", "")):
            raise Invalid("Unknown CAF build or skin palette")
        slots, revisions = value.get("slots"), value.get("revisions")
        if not isinstance(slots, dict) or len(slots) > 38 or not isinstance(revisions, dict) or len(revisions) > 150:
            raise Invalid("Invalid CAF selections")
        for slot, selected in slots.items():
            if not isinstance(selected, dict) or set(selected) != {"item", "style", "color", "palette"}:
                raise Invalid("Invalid equipped CAF part")
            group, item = self.items.get(selected["item"], (None, None))
            if group is None or group["id"] != slot or group["kind"] in ("Template", "Palette", "BlendShape"):
                raise Invalid("This CAF part cannot be equipped")
            if not item.get("geometry") and item["model"] != "NON_GEOM":
                raise Invalid("This CAF mesh layout is not supported")
            for key in ("style", "color"):
                if type(selected[key]) != int or selected[key] < 0:
                    raise Invalid("Invalid CAF style or color index")
            if item["styles"]:
                if selected["style"] >= len(item["styles"]) or selected["color"] >= len(item["styles"][selected["style"]]["variants"]):
                    raise Invalid("CAF style/color does not belong to this item")
            elif selected["style"] or selected["color"]:
                raise Invalid("CAF base part has no texture variants")
            palette = selected["palette"]
            if not isinstance(palette, str) or not (palette == "default" or re.fullmatch(r"pl\d{2}", palette)):
                raise Invalid("Invalid CAF named palette")
        snapshot = self.reader.snapshot()
        for ident, revision in revisions.items():
            if ident not in self.assets or revision not in {r["id"] for r in self.reader.revisions(ident, snapshot)}:
                raise Invalid("Unknown CAF per-item revision")
        return copy.deepcopy(value)

    def selection_resource(self, item, selected):
        if not item["styles"]:
            return None
        name = item["styles"][selected["style"]]["variants"][selected["color"]]
        if name.lower() not in self.catalog["resources"]:
            raise Invalid("Missing CAF source texture: " + name)
        return self.catalog["resources"][name.lower()]

    def public_catalog(self):
        # Paths and private decoded vertex arrays are never needed by the sidebar.
        result = {k: self.catalog[k] for k in ("builds", "groups", "limitations", "errors")}
        result = copy.deepcopy(result)
        result["shop"] = copy.deepcopy(self.catalog.get("shop", dict(groups={}, unresolved=[])))
        snapshot = self.reader.snapshot()
        public_resources = {}
        for name, resource in self.catalog["resources"].items():
            if re.fullmatch(r"v2cp_[a-d]_[a-f]", name):
                continue
            records = [dict(asset=r.get("asset"), name=r["name"], placement=r["placement"],
                            width=r["width"], height=r["height"], index=r["index"])
                       for r in resource["records"]]
            public_resources[name] = dict(name=resource["name"], records=records, palettes=resource.get("palettes", []))
        result.update(resources=public_resources, default=self.default_outfit(),
                      revisions={ident: self.reader.revisions(ident, snapshot) for ident in sorted(self.assets)},
                      corpus_id=self.reader.corpus_id)
        with self.lock:
            result["state"] = copy.deepcopy(self.state)
        return result

    def geometry(self, name, build, slot):
        # Retail accessories have fewer distinct fits; use the game's remap.
        build = fit_build(slot, build)
        variants = self.catalog["geometry"][name]
        if build not in variants:
            build = "C"
        record = variants[build]
        key = record["sha256"]
        if key not in self.geometry_cache:
            model = json.loads(self.verified(record))
            self.geometry_cache[key] = {k: model[k] for k in ("meshes", "bounds", "skipped")}
            self.geometry_cache[key]["notices"] = model.get("caf_omissions", [])
        return self.geometry_cache[key], key

    def scene(self, req):
        outfit = self.validate_outfit(req.get("outfit"))
        focus = req.get("compare")
        if focus is not None:
            if not isinstance(focus, dict) or set(focus) != {"asset", "a", "b"} or focus["asset"] not in self.assets:
                raise Invalid("Invalid CAF comparison")
            choices = {r["id"] for r in self.reader.revisions(focus["asset"])}
            if focus["a"] not in choices or focus["b"] not in choices:
                raise Invalid("Unknown CAF A/B revision")
        scale = req.get("scale", 4)
        if type(scale) != int or scale not in (1, 2, 4):
            raise Invalid("CAF inspection scale must be 1, 2 or 4")
        with self.render_lock:
            snapshot = self.reader.snapshot()
            meshes, geometry_pins, selections, notices = [], [], [], []
            for slot, selected in outfit["slots"].items():
                group, item = self.items[selected["item"]]
                if item.get("geometry"):
                    model, pin = self.geometry(item["geometry"], outfit["build"], slot)
                    notices.extend(model.get("notices", []))
                    for failure in self.catalog["errors"]:
                        if failure.get("model") == item["geometry"] and failure.get("build") == fit_build(slot, outfit["build"]):
                            notices.append(item["model"] + ": this build's shape is unsupported; source C geometry is shown")
                    geometry_pins.append(pin)
                    for mesh in model["meshes"]:
                        ref = mesh.get("texture_ref", "").split(",")[0]
                        if ref not in ("cp_a", "cp_b", "cp_c", "cp_d"):
                            notices.append(item["model"] + ": unsupported material binding " + ref)
                            continue
                        meshes.append(dict(mesh, slot=slot, item=item["id"], atlas=ref[-1]))
                resource = self.selection_resource(item, selected)
                if resource:
                    selections.append((group, selected, resource))
            if not meshes:
                raise Invalid("Equip at least one supported CAF mesh")
            selections.sort(key=lambda x: (x[0]["stage"], int(x[0]["id"])))
            layers, source_pins = [], []
            for group, selected, res in selections:
                first = res["records"][0] if res["records"] else None
                companions = first["placement"]["parameters"][0] if first and first["placement"] else 0
                eligible = {first["name"]} if first else set()
                eligible.update(f"al{i:02d}" for i in range(1, companions + 1))
                for record in res["records"]:
                    if record["name"] not in eligible:
                        continue
                    instruction = record["placement"]
                    if not instruction:
                        notices.append(res["name"] + ": auxiliary map omitted (no atlas instruction)")
                        continue
                    ident = record.get("asset")
                    if not ident:
                        raise Invalid("Source texture is missing from the accepted corpus: " + res["name"])
                    versions = [outfit["revisions"].get(ident, "original")] * 2
                    if focus and focus["asset"] == ident:
                        versions = [focus["a"], focus["b"]]
                    images = []
                    for revision in versions:
                        raw = self.reader.image(ident, revision, snapshot)
                        image = Image.open(io.BytesIO(raw)).convert("RGBA")
                        palette = selected["palette"]
                        if palette != "default":
                            if palette not in res.get("palettes", []):
                                raise Invalid("Named palette does not belong to this CAF resource")
                            if revision in ("original", "faithful"):
                                pal_raw = inside(self.root, res["palette_path"]).read_bytes()
                                if sha(pal_raw) != res["sha256"]:
                                    raise Invalid("CAF palette source checksum changed")
                                image = with_palette(pal_raw, record, palette_images(pal_raw)[palette])
                            else:
                                notices.append(res["name"] + ": " + revision + " keeps authored RGB; " + palette + " applies only to Original/Lanczos")
                        source_pins.append(sha(raw))
                        if image.width * record["height"] != image.height * record["width"]:
                            raise Invalid("CAF revision changed its source aspect ratio")
                        # Reconstruct source bilinear sampling inside the shared
                        # HD atlas. Do not silently turn Original into Lanczos.
                        sampling = Image.Resampling.BILINEAR if revision == "original" else Image.Resampling.LANCZOS
                        images.append(rgba_resize(image, (record["width"] * scale, record["height"] * scale), sampling))
                    layers.append((instruction, images, ident))
            recipe = dict(outfit=outfit, compare=focus, scale=scale, sources=source_pins, geometry=geometry_pins)
            key = sha(json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode())
            if key in self.renders:
                self.renders.move_to_end(key)
                return self.renders[key]["scene"]
            images, urls = {}, {}
            for side in ("a", "b"):
                urls[side] = {}
                for atlas in "abcd":
                    base_name = f"v2cp_{atlas}_{outfit['build'].lower()}"
                    base = self.catalog["resources"][base_name]["images"][outfit["skin"]]
                    canvas = rgba_resize(Image.open(io.BytesIO(self.verified(base))), (256 * scale, 256 * scale))
                    for instruction, pair, _ in layers:
                        if instruction["atlas"] == atlas:
                            composite(canvas, pair[0 if side == "a" else 1], [v * scale for v in instruction["origin"]], instruction["mode"])
                    stream = io.BytesIO()
                    canvas.save(stream, format="PNG", compress_level=1)
                    name = side + atlas + ".png"
                    images[name] = stream.getvalue()
                    urls[side][atlas] = f"/api/caf/render/{key}/{name}"
            positions = [p for m in meshes for p in m["positions"]]
            scene = dict(key=key, meshes=meshes, textures=urls,
                         bounds=[[min(p[i] for p in positions) for i in range(3)],
                                 [max(p[i] for p in positions) for i in range(3)]],
                         notices=sorted(set(notices)), compared_asset=focus["asset"] if focus else None,
                         compared_on_model=bool(focus and any(ident == focus["asset"] for _, _, ident in layers)),
                         vertices=len(positions), triangles=sum(len(m["indices"]) // 3 for m in meshes))
            self.renders[key] = dict(scene=scene, images=images)
            while len(self.renders) > 8:
                self.renders.popitem(last=False)
            return scene

    def image(self, ident, revision):
        if ident not in self.assets:
            raise Invalid("This source is not a CAF texture")
        return self.reader.image(ident, revision)

    def save(self, req):
        with self.lock:
            if type(req.get("version")) != int or req["version"] != self.state["version"]:
                raise Conflict("CAF state changed in another tab. Reload before saving; your draft is retained.")
            data = copy.deepcopy(self.state)
            action = req.get("action")
            if action == "outfit":
                name = req.get("name", "")
                if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
                    raise Invalid("Name this outfit (1–100 characters)")
                if name not in data["outfits"] and len(data["outfits"]) >= 100:
                    raise Invalid("The CAF library holds at most 100 saved outfits")
                data["outfits"][name] = self.validate_outfit(req.get("outfit"))
            elif action == "session":
                value = req.get("session")
                if not isinstance(value, dict) or set(value) - {"outfit", "camera", "compare", "lighting", "mode", "focus"}:
                    raise Invalid("Invalid CAF session")
                self.validate_outfit(value.get("outfit"))
                if value.get("lighting", "unlit") not in ("unlit", "studio") or value.get("mode", "split") not in ("single", "split"):
                    raise Invalid("Invalid CAF display preference")
                if value.get("focus") is not None and value["focus"] not in value["outfit"]["slots"]:
                    raise Invalid("CAF focus must be an equipped slot")
                comparison = value.get("compare")
                if comparison is not None:
                    if not isinstance(comparison, dict) or set(comparison) != {"asset", "a", "b"} or comparison["asset"] not in self.assets:
                        raise Invalid("Invalid saved CAF comparison")
                    revisions = {r["id"] for r in self.reader.revisions(comparison["asset"])}
                    if comparison["a"] not in revisions or comparison["b"] not in revisions:
                        raise Invalid("Unknown saved CAF revision")
                camera = value.get("camera")
                if camera is not None:
                    if not isinstance(camera, dict) or set(camera) != {"position", "target"}:
                        raise Invalid("Invalid CAF camera")
                    for xyz in camera.values():
                        if not isinstance(xyz, list) or len(xyz) != 3 or any(type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 10000 for n in xyz):
                            raise Invalid("Invalid CAF camera coordinates")
                data["session"] = copy.deepcopy(value)
            elif action == "queue":
                ident, revision = req.get("asset"), req.get("revision")
                raw = self.image(ident, revision)
                pin = sha(raw)
                entry = next((r for r in data["queue"] if r["asset"] == ident and r["revision"] == revision), None)
                if entry is None:
                    if len(data["queue"]) >= 2000:
                        raise Invalid("The CAF inspection queue holds at most 2,000 revisions")
                    entry = dict(id=sha((ident + ":" + revision + ":" + pin).encode())[:24], asset=ident,
                                 revision=revision, sha256=pin, status="pending", notes="")
                    data["queue"].append(entry)
            elif action == "inspection":
                entry = next((r for r in data["queue"] if r["id"] == req.get("id")), None)
                if entry is None or req.get("status") not in ("pending", "inspected", "needs_work") or not isinstance(req.get("notes"), str) or len(req["notes"]) > 20000:
                    raise Invalid("Invalid CAF inspection note")
                if sha(self.image(entry["asset"], entry["revision"])) != entry["sha256"]:
                    raise Invalid("Queued revision checksum changed")
                entry.update(status=req["status"], notes=req["notes"])
            else:
                raise Invalid("Unknown CAF state operation")
            data["version"] += 1
            atomic_json(self.file, data)
            self.state = data
            return copy.deepcopy(data)


def route_get(handler, viewer, token, parts, query):
    static = {"caf-viewer": ("caf_viewer.html", "text/html; charset=utf-8"),
              "caf-viewer.js": ("caf_viewer.js", "text/javascript; charset=utf-8"),
              "caf-wardrobe.js": ("caf_wardrobe.js", "text/javascript; charset=utf-8"),
              "caf-viewer.css": ("caf_viewer.css", "text/css; charset=utf-8")}
    if len(parts) == 1 and parts[0] in static:
        file, mime = static[parts[0]]
        handler.reply(200, (HERE / file).read_bytes(), mime)
        return True
    if parts[:2] != ["api", "caf"]:
        return False
    if viewer is None:
        handler.reply(400, dict(error="Start the CAF service with a built private catalogue; see the CAF viewer guide"))
        return True
    if parts == ["api", "caf", "catalog"]:
        handler.reply(200, dict(viewer.public_catalog(), token=token))
    elif len(parts) == 5 and parts[2] == "image":
        handler.reply(200, viewer.image(parts[3], parts[4]), "image/png")
    elif len(parts) == 5 and parts[2] == "render":
        with viewer.render_lock:
            handler.reply(200, viewer.renders[parts[3]]["images"][parts[4]], "image/png")
    else:
        handler.reply(404, dict(error="Unknown CAF route"))
    return True


def route_post(handler, viewer, parts, req):
    if parts[:2] != ["api", "caf"]:
        return False
    if viewer is None:
        raise Invalid("CAF service is not configured")
    if parts == ["api", "caf", "scene"]:
        handler.reply(200, viewer.scene(req))
    elif parts == ["api", "caf", "state"]:
        handler.reply(200, viewer.save(req))
    else:
        handler.reply(404, dict(error="Unknown CAF route"))
    return True


def handler_for(viewer, token):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, data, mime="application/json"):
            if mime == "application/json":
                data = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            for key, value in (("Content-Type", mime), ("Content-Length", str(len(data))), ("Cache-Control", "no-store"),
                               ("X-Content-Type-Options", "nosniff"),
                               ("Content-Security-Policy", "default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; connect-src 'self' blob:; frame-ancestors 'none'")):
                self.send_header(key, value)
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def allowed(self, write=False):
            host = self.headers.get("Host")
            valid = host in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")
            return valid and (not write or (self.headers.get("Origin") in (None, "http://" + host)
                                            and self.headers.get("X-Workshop-Token") == token))

        def do_GET(self):
            if not self.allowed():
                return self.reply(403, dict(error="Use this viewer's loopback address"))
            try:
                parsed = urlparse(self.path)
                parts = parsed.path.strip("/").split("/")
                if parts == [""]:
                    parts = ["caf-viewer"]
                if route_get(self, viewer, token, parts, parse_qs(parsed.query)):
                    return
                from .model_workshop import static_file
                item = static_file(parts, HERE)
                if item and parts[0] == "vendor":
                    return self.reply(200, *item)
                self.reply(404, dict(error="Not found"))
            except (ValueError, OSError, KeyError, TypeError) as ex:
                self.reply(400, dict(error=str(ex)))

        def do_POST(self):
            if not self.allowed(True):
                return self.reply(403, dict(error="Use this viewer's local browser page"))
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_REQUEST:
                    raise Invalid("CAF request is too large")
                req = json.loads(self.rfile.read(length))
                if not isinstance(req, dict):
                    raise Invalid("Expected a CAF JSON object")
                parts = urlparse(self.path).path.strip("/").split("/")
                if not route_post(self, viewer, parts, req):
                    self.reply(404, dict(error="Not found"))
            except Conflict as ex:
                self.reply(409, dict(error=str(ex)))
            except (ValueError, OSError, KeyError, TypeError) as ex:
                self.reply(400, dict(error=str(ex)))

        def log_message(self, *args):
            pass
    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("build", "serve"))
    ap.add_argument("--dump", type=Path)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--workspace", type=Path)
    ap.add_argument("--catalog", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--state-dir", type=Path)
    ap.add_argument("--port", type=int, default=8780)
    args = ap.parse_args()
    if args.action == "build":
        if not args.dump or not args.output:
            ap.error("build requires --dump and a new private --output directory")
        print(json.dumps(build_catalog(args.dump, args.corpus, args.output), indent=2))
        return
    if not args.workspace or not args.catalog or not args.state_dir:
        ap.error("serve requires --workspace (read-only), --catalog and a separate --state-dir")
    if not 1024 <= args.port <= 65535:
        ap.error("Choose a port from 1024 through 65535")
    viewer = CafViewer(args.catalog, SourceReader(args.corpus, args.workspace), args.state_dir)
    with WorkspaceLock(args.state_dir):
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(viewer, secrets.token_urlsafe(32)))
        print(f"Create-a-Fighter inspector: http://127.0.0.1:{args.port}/caf-viewer", flush=True)
        print("Production workshop is read-only; inspection state: " + str(viewer.file), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
