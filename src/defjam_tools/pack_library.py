"""Read immutable published texture archives and keep a separate revision pass.

A private schema-1 config pins each ZIP's SHA-256 and size. No extraction,
installation, selection or mutation of the corpus/workshop is performed.
"""
from collections import Counter
import configparser
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
import re
import threading
import zipfile

from PIL import Image

from .paths import require_private_output
from .texture_workshop import Invalid, Conflict, atomic_json, inside, stamp

HASH = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,79}\Z")
STATUSES = ("unreviewed", "looks_good", "needs_revision", "question")
MAX_IMAGE = 64 * 1024 * 1024
MAX_PIXELS = 64 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(value):
    p = PurePosixPath(value)
    if not value or "\\" in value or p.is_absolute() or any(x in ("", ".", "..") for x in value.split("/")) or ":" in value:
        raise Invalid("Unsafe archive path")
    return value


def png_info(data):
    with Image.open(io.BytesIO(data)) as im:
        if im.format != "PNG" or im.width * im.height > MAX_PIXELS:
            raise Invalid("Expected a bounded PNG image")
        return [im.width, im.height]


class PackLibrary:
    def __init__(self, config, store):
        self.store = store
        self.config_path = Path(config).resolve()
        cfg = json.loads(self.config_path.read_text(encoding="utf8"))
        if cfg.get("schema") != 1:
            raise Invalid("Unsupported pack library config schema")
        self.root = require_private_output(cfg["review_root"])
        if any(self.root == p or self.root.is_relative_to(p) or p.is_relative_to(self.root)
               for p in (store.root.resolve(), store.corpus_root.resolve())):
            raise Invalid("Pack review storage must be separate from corpus and workshop")
        self.file = self.root / "pack-reviews.json"
        self.lock = threading.RLock()
        self.packs = {}
        self.entries = {}
        self.local_images = {}
        for spec in cfg["packs"]:
            self._load(spec)
        if not self.packs:
            raise Invalid("Configure at least one published pack")
        self.data = json.loads(self.file.read_text(encoding="utf8")) if self.file.exists() else dict(schema=1, reviews={})
        if self.data.get("schema") != 1 or not isinstance(self.data.get("reviews"), dict):
            raise Invalid("Unsupported pack review schema; retain the old file")

    def _local(self, path, expected=None):
        path = Path(path).resolve()
        # Only explicit config/corpus references are exposed, never URL paths.
        if not path.is_file() or path.stat().st_size > MAX_IMAGE:
            raise Invalid("Missing or oversized baseline: " + str(path))
        raw = path.read_bytes()
        if expected and digest(raw) != expected:
            raise Invalid("Baseline hash mismatch: " + str(path))
        return dict(path=path, size=png_info(raw), sha256=digest(raw))

    def _load(self, spec):
        key = spec["id"]
        if not SLUG.fullmatch(key) or key in self.packs or not HASH.fullmatch(spec["sha256"]):
            raise Invalid("Invalid/duplicate pack ID or SHA-256")
        path = Path(spec["archive"]).resolve()
        if path.stat().st_size != spec["size"]:
            raise Invalid("Published archive size mismatch: " + key)
        h = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
        if h.hexdigest() != spec["sha256"]:
            raise Invalid("Published archive SHA-256 mismatch: " + key)
        labels = {}
        if spec.get("metadata"):
            labels = json.loads(Path(spec["metadata"]).read_text(encoding="utf8"))
            if labels.get("schema") != 1:
                raise Invalid("Unsupported pack metadata schema")
            labels = labels["sources"]
        pack = dict(id=key, name=spec["name"], version=spec["version"], sha256=spec["sha256"],
                    bytes=spec["size"], archive=path, native=0, wide=0, supporting=0, pngs=0)
        rows = []
        with zipfile.ZipFile(path) as z:
            members = {}
            casefolded = set()
            for info in z.infolist():
                if info.is_dir():
                    safe_name(info.filename.rstrip("/")); continue
                safe_name(info.filename)
                if info.filename.casefold() in casefolded or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise Invalid("Duplicate archive path or symlink")
                casefolded.add(info.filename.casefold()); members[info.filename] = info
            manifests = [n for n in members if n.endswith("manifest.ini")]
            if len(manifests) != 1 or members[manifests[0]].file_size > 4 * 1024 * 1024:
                raise Invalid("Expected exactly one bounded manifest.ini")
            prefix = manifests[0][:-len("manifest.ini")]
            ini = configparser.ConfigParser(interpolation=None, strict=True)
            ini.read_string(z.read(manifests[0]).decode("utf8"))
            if ini.get("pack", "schema") != "1":
                raise Invalid("Unsupported pack manifest schema")
            used = set()

            def add(sid, relative, kind, offset=""):
                full = prefix + safe_name(relative)
                if full not in members or not full.lower().endswith(".png") or members[full].file_size > MAX_IMAGE:
                    raise Invalid("Missing/oversized manifest PNG: " + relative)
                raw = z.read(full)
                size = png_info(raw)
                eid = digest((sid + "\n" + kind + "\n" + str(offset) + "\n" + full).encode())[:24]
                meta = labels.get(sid, {})
                asset = self.store.assets.get(sid)
                # Only exact source IDs (or an explicit metadata corpus_id) match.
                if not asset and meta.get("corpus_id"):
                    asset = self.store.assets.get(meta["corpus_id"])
                label = meta.get("label") or (asset or {}).get("label") or relative.rsplit("/", 1)[-1]
                category = meta.get("family") or meta.get("category") or (asset or {}).get("category") or "Other pack textures"
                row = dict(id=eid, pack=key, source_id=sid, label=label, category=category,
                           kind=kind, offset=str(offset), path=relative, member=full, size=size,
                           sha256=digest(raw), crop=meta.get("crop") if kind == "native" else None, context=meta.get("context", ""),
                           backdrop=meta.get("backdrop", "checker"), aliases=meta.get("aliases") or (asset or {}).get("aliases", []),
                           baseline={}, corpus_id=(asset or {}).get("id"), provenance=meta.get("provenance", ""))
                # Wide slabs are deliberately not registered against a whole original.
                if kind == "native":
                    for name, field in (("original", "original"), ("faithful", "upscaled")):
                        override = meta.get(name)
                        if override:
                            info = self._local(override["path"], override["sha256"])
                        elif asset and asset.get(field):
                            info = self._local(inside(self.store.corpus_root, asset[field]), asset.get(field + "_hash"))
                        else:
                            continue
                        self.local_images[(key, eid, name)] = info
                        row["baseline"][name] = dict(size=info["size"], sha256=info["sha256"])
                # Crops are normalized canvas coordinates, never a replacement image.
                crop = row["crop"]
                if crop is not None and (not isinstance(crop, list) or len(crop) != 4 or
                        not all(isinstance(n, (float, int)) and 0 <= n <= 1 for n in crop) or
                        crop[0] >= crop[2] or crop[1] >= crop[3]):
                    raise Invalid("Invalid normalized comparison crop")
                used.add(full); rows.append(row); self.entries[(key, eid)] = row
                pack[kind] += 1
            for sid, relative in ini.items("textures"):
                if not HASH.fullmatch(sid):
                    raise Invalid("Expected full source IDs in manifest")
                add(sid, relative, "native")
            if ini.has_section("wide"):
                for sid, value in ini.items("wide"):
                    if not HASH.fullmatch(sid):
                        raise Invalid("Invalid wide source ID")
                    if value.strip() == "stretch":
                        for row in rows:
                            if row["source_id"] == sid: row["context"] += " · runtime stretch"
                        continue
                    for part in value.split(";"):
                        offset, relative = part.split(":", 1)
                        if offset != "inner": int(offset)
                        add(sid, relative, "wide", offset)
            pngs = [n for n in members if n.lower().endswith(".png")]
            for full in pngs:
                if not full.startswith(prefix):
                    raise Invalid("PNG outside pack root")
                if full not in used:
                    sid = PurePosixPath(full).stem
                    add(sid, full[len(prefix):], "supporting")
            pack["pngs"] = len(pngs)
            pack["png_mips"] = ini.get("pack", "png_mips", fallback="opacity")
        pack["rows"] = sorted(rows, key=lambda r: (r["label"].casefold(), r["kind"], r["offset"], r["id"]))
        self.packs[key] = pack

    def review_key(self, row):
        return self.packs[row["pack"]]["sha256"] + ":" + row["id"] + ":" + row["sha256"]

    def review(self, row):
        return deepcopy(self.data["reviews"].get(self.review_key(row), dict(version=0, status="unreviewed", notes="")))

    def save(self, key, ident, req):
        with self.lock:
            row = self.entries[(key, ident)]
            old = self.review(row)
            if req.get("version") != old["version"]:
                raise Conflict("This texture was reviewed in another tab; reload before saving")
            if req.get("status") not in STATUSES or not isinstance(req.get("notes"), str) or len(req["notes"]) > 12000:
                raise Invalid("Invalid review status or notes")
            saved = dict(version=old["version"] + 1, status=req["status"], notes=req["notes"], updated=stamp(),
                         pack=key, pack_sha256=self.packs[key]["sha256"], image_sha256=row["sha256"],
                         entry=ident, source_id=row["source_id"], label=row["label"], path=row["path"])
            updated = deepcopy(self.data); updated["reviews"][self.review_key(row)] = saved
            self.root.mkdir(parents=True, exist_ok=True)
            atomic_json(self.file, updated)
            self.data = updated
            return saved

    def config(self, token):
        return dict(token=token, packs=[{k: v for k, v in p.items() if k not in ("archive", "rows")} for p in self.packs.values()])

    def catalog(self, q):
        with self.lock:
            pack = self.packs[q.get("pack", [next(iter(self.packs))])[0]]
            rows = pack["rows"]
            counts = Counter(self.review(r)["status"] for r in rows)
            categories = sorted({r["category"] for r in rows})
            def matches(r):
                hay = " ".join((r["label"], r["source_id"], r["path"], r["context"], json.dumps(r["aliases"], ensure_ascii=False))).casefold()
                return (q.get("q", [""])[0].casefold() in hay and
                        q.get("category", [""])[0] in ("", r["category"]) and
                        q.get("kind", [""])[0] in ("", r["kind"]) and
                        q.get("status", [""])[0] in ("", self.review(r)["status"]))
            matched = [r for r in rows if matches(r)]
            offset = max(0, int(q.get("offset", [0])[0])); limit = min(100, max(1, int(q.get("limit", [60])[0])))
            return dict(total=len(matched), all=len(rows), offset=offset, categories=categories, counts=counts,
                        items=[dict(id=r["id"], label=r["label"], category=r["category"], kind=r["kind"],
                                    size=r["size"], backdrop=r["backdrop"], baseline=list(r["baseline"]), source_id=r["source_id"], status=self.review(r)["status"]) for r in matched[offset:offset+limit]])

    def detail(self, key, ident):
        with self.lock:
            row = self.entries[(key, ident)]
            out = {k: v for k, v in row.items() if k != "member"}
            out["review"] = self.review(row)
            out["alternatives"] = []
            for p in self.packs.values():
                for r in p["rows"]:
                    if r["source_id"] == row["source_id"] and r["kind"] == row["kind"] and r["offset"] == row["offset"] and p["id"] != key:
                        out["alternatives"].append(dict(id=p["id"] + "/" + r["id"], label=p["name"] + " " + p["version"]))
            cid = row["corpus_id"]
            if cid and row["kind"] == "native":
                for c in self.store.data.get("candidates", {}).get(cid, []):
                    out["alternatives"].append(dict(id="candidate/" + c["id"], label="Workshop · " + c["label"], size=[c["width"], c["height"]]))
            return out

    def image(self, key, ident, variant, channel="rgba", crop=False, thumb=False):
        row = self.entries[(key, ident)]
        if channel not in ("rgb", "rgba", "alpha"):
            raise Invalid("Unknown image channel")
        if variant == "published":
            with zipfile.ZipFile(self.packs[key]["archive"]) as z:
                raw = z.read(row["member"])
            if digest(raw) != row["sha256"]:
                raise Invalid("Published image changed; restart with a verified archive")
        elif variant in ("original", "faithful"):
            info = self.local_images[(key, ident, variant)]; raw = info["path"].read_bytes()
            if digest(raw) != info["sha256"]:
                raise Invalid("Baseline changed since library opened")
        elif variant.startswith("candidate:") and row["corpus_id"] and row["kind"] == "native":
            revision = variant.split(":", 1)[1]
            with self.store.lock:
                candidates = self.store.data.get("candidates", {}).get(row["corpus_id"], [])
                c = next((c for c in candidates if c["id"] == revision), None)
                if c is None: raise Invalid("Unknown workshop revision")
                raw = self.store.image_path(row["corpus_id"], revision).read_bytes()
            if digest(raw) != c["sha256"]:
                raise Invalid("Candidate hash mismatch")
        else:
            raise Invalid("Unknown image variant")
        if channel == "rgba" and not crop and not thumb:
            return raw
        with Image.open(io.BytesIO(raw)) as im:
            im = im.convert("RGBA")
            if crop and row["crop"]:
                box = row["crop"]; im = im.crop(tuple(round(n * (im.width if i % 2 == 0 else im.height)) for i, n in enumerate(box)))
            if thumb: im.thumbnail((220, 120), Image.Resampling.LANCZOS)
            if channel == "rgb": im = im.convert("RGB")
            elif channel == "alpha": im = im.getchannel("A")
            out = io.BytesIO(); im.save(out, format="PNG"); return out.getvalue()

    def export(self):
        with self.lock:
            return dict(schema=1, exported=stamp(), packs=self.config("")["packs"],
                        reviews=[dict(self.review(r), entry=r["id"], pack=r["pack"], source_id=r["source_id"], path=r["path"], label=r["label"])
                                 for r in self.entries.values() if self.review(r)["status"] != "unreviewed" or self.review(r)["notes"]])


def route_get(handler, library, token, parts, q, resources):
    if parts == ["packs"]:
        handler.reply(200, (resources / "pack_library.html").read_bytes(), "text/html; charset=utf-8"); return True
    static = {"packs.js": ("pack_library.js", "text/javascript; charset=utf-8"), "packs.css": ("pack_library.css", "text/css; charset=utf-8")}
    if len(parts) == 1 and parts[0] in static:
        file, mime = static[parts[0]]; handler.reply(200, (resources / file).read_bytes(), mime); return True
    if parts[:2] != ["api", "packs"]: return False
    if library is None:
        handler.reply(503, dict(error="No published packs configured. Start serve with --pack-library PRIVATE_CONFIG.json.")); return True
    if parts == ["api", "packs", "config"]: handler.reply(200, library.config(token))
    elif parts == ["api", "packs", "catalog"]: handler.reply(200, library.catalog(q))
    elif parts == ["api", "packs", "export"]: handler.reply(200, library.export())
    elif len(parts) == 4: handler.reply(200, library.detail(parts[2], parts[3]))
    elif len(parts) == 6 and parts[4] == "image":
        handler.reply(200, library.image(parts[2], parts[3], unquote(parts[5]), q.get("channel", ["rgba"])[0], q.get("crop", [""])[0] == "1", q.get("thumb", [""])[0] == "1"), "image/png")
    else: handler.reply(404, dict(error="Unknown pack route"))
    return True


def route_post(handler, library, parts, req):
    if parts[:2] != ["api", "packs"]: return False
    if library is None: raise Invalid("No published packs configured")
    if len(parts) == 5 and parts[4] == "review": handler.reply(200, library.save(parts[2], parts[3], req))
    else: handler.reply(404, dict(error="Unknown pack route"))
    return True
