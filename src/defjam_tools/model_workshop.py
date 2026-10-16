"""Private model artifact and view-state endpoints for the texture workshop."""
import copy
import json
import math
from pathlib import Path

from .defjam_model import FIGHTERS, make_glb, sha


def receipt(store, fighter):
    if fighter not in FIGHTERS:
        raise ValueError("Unknown preview fighter")
    root = store.root / "models" / fighter
    data = json.loads((root / "index.json").read_text(encoding="utf8"))
    if data.get("schema") != 1 or data.get("decoder") != 1 or data.get("source_id") != FIGHTERS[fighter][2]:
        raise ValueError("Incompatible model preview; rebuild it with defjam-tools model")
    return root, data


def catalog(store):
    models = []
    for fighter in FIGHTERS:
        if not (store.root / "models" / fighter / "index.json").exists():
            continue
        _, data = receipt(store, fighter)
        models.append(dict(id=fighter, **data))
    file = store.root / "model-viewer.json"
    with store.lock:
        state = json.loads(file.read_text(encoding="utf8")) if file.exists() else dict(schema=1, views={})
    return dict(models=models, state=state)


def save_view(store, req, atomic_json):
    fighter, view = req.get("fighter"), req.get("view")
    _, model = receipt(store, fighter)
    if not isinstance(view, dict) or set(view) - {"position", "target", "left", "right", "lighting", "wireframe", "groups"}:
        raise ValueError("Invalid model view state")
    for key in ("position", "target"):
        xyz = view.get(key)
        if not isinstance(xyz, list) or len(xyz) != 3 or any(type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 10000 for n in xyz):
            raise ValueError("Invalid camera coordinates")
    for key in ("left", "right"):
        if view.get(key) not in ("original", "faithful") and not store.candidate(model["source_id"], view.get(key)):
            raise ValueError("Unknown model texture revision")
    if view.get("lighting") not in ("unlit", "studio") or type(view.get("wireframe")) != bool:
        raise ValueError("Invalid rendering preference")
    groups = view.get("groups")
    if not isinstance(groups, list) or any(g not in model["groups"] for g in groups):
        raise ValueError("Unknown material group")
    with store.lock:
        file = store.root / "model-viewer.json"
        data = json.loads(file.read_text(encoding="utf8")) if file.exists() else dict(schema=1, views={})
        data["views"][fighter] = copy.deepcopy(view)
        data["fighter"] = fighter
        atomic_json(file, data)
    return dict(saved=True)


def model_glb(store, fighter, revision="original"):
    root, index = receipt(store, fighter)
    if revision not in ("original", "faithful") and not store.candidate(index["source_id"], revision):
        raise ValueError("Unknown model texture revision")
    raw = (root / "geometry.json").read_bytes()
    if sha(raw) != index["geometry_sha256"]:
        raise ValueError("Private geometry cache checksum changed; rebuild the preview")
    with store.lock:
        path = store.image_path(index["source_id"], revision)
        image = path.read_bytes()
        asset = store.asset(index["source_id"])
        candidate = store.candidate(index["source_id"], revision)
        expected = (candidate["sha256"] if candidate else
                    asset.get("original_hash" if revision == "original" else "upscaled_hash"))
        if expected and sha(image) != expected:
            raise ValueError("Texture checksum changed; import a new revision before exporting")
    return make_glb(json.loads(raw), image, revision)


def static_file(parts, here):
    """Exact allowlist only; no user-selected paths or CDN requests."""
    files = {
        ("model-viewer",): (here / "model_viewer.html", "text/html; charset=utf-8"),
        ("model-viewer.js",): (here / "model_viewer.js", "text/javascript; charset=utf-8"),
        ("model-viewer.css",): (here / "model_viewer.css", "text/css; charset=utf-8"),
    }
    for route, file in (("three.module.min.js", "three.module.min.js"), ("three.core.min.js", "three.core.min.js"),
                        ("controls/OrbitControls.js", "OrbitControls.js"), ("loaders/GLTFLoader.js", "GLTFLoader.js"),
                        ("utils/BufferGeometryUtils.js", "BufferGeometryUtils.js")):
        files[tuple(("vendor/" + route).split("/"))] = (here / "vendor/three" / file, "text/javascript; charset=utf-8")
    item = files.get(tuple(parts))
    if not item:
        return None
    path, mime = item
    raw = path.read_bytes()
    if parts[0] == "vendor":
        # Upstream bytes remain pinned on disk. Resolve their bare module import
        # locally without inline scripts/import maps or weakening the page CSP.
        raw = raw.replace(b"from 'three'", b"from '/vendor/three.module.min.js'")
    return raw, mime
