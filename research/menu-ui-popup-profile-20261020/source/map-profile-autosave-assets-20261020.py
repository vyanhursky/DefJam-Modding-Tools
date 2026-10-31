"""Reconstruction of the inline decoder used for the 2026-10-20 mapping.

The decoder was executed inline and was not saved as a file at the time. This
script was transcribed from that successful command for provenance; it is a
faithful reconstruction, not the original saved source file. It reads the
user's local dump/corpus and writes coordinates, aliases, alpha ranges, hashes
and APT root frames to the private metadata JSON. It does not edit source
assets, application code, generated art, or game files.

The approved-ID filtering, classification notes, and nested autosave-sprite
timeline enrichment were applied to that JSON in separate inline commands;
this file records the decoder phase only.
"""

import contextlib
import io
import json
import os
import re
import runpy
import struct
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import hd_assets

root = Path(
    "/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/"
    "b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0"
)
os.environ["DEFJAM_DATA"] = "/Users/vlad/Code/defjam-data"
outer = dict(
    hd_assets.archive_entries(
        Path("/Users/vlad/Code/defjam-data/extracted/screens/screens.viv").read_bytes()
    )
)
assets = json.loads((root / "corpus.json").read_text())["assets"]
with contextlib.redirect_stdout(io.StringIO()):
    decoder = runpy.run_path("logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py")

approved = {
    item["source_id"]
    for item in json.loads(Path("config/menu-ui-approved-artwork.json").read_text())["reviewed_sources"]
}
pending = {
    source_id
    for item in json.loads(
        Path("logs/ui-restoration-20261017/pilot-v1/menu-details-v1-20261020/review-items.json").read_text()
    )
    for source_id in item["source_ids"]
}
results = []

for entry, base in [
    ("screens/options/userID.big", "userID"),
    ("screens/memoryCard/autosaveMessage.big", "autosaveMessage"),
]:
    inner = dict(hd_assets.archive_entries(hd_assets.unpack_refpack(outer[entry])))
    obj = inner[base + ".o"]
    data, symbols, relocations, _ = decoder["object_info"](obj)
    apt_data, _, movie, characters, _ = decoder["apt"].load_movie("screens/screens.viv", entry)

    image_by_name = {}
    for asset in assets:
        for alias in asset["aliases"]:
            if "::" + entry + "::" in alias["source"] and alias["source"].endswith("::" + base + ".xsh"):
                try:
                    image_name = int(alias["name"].strip())
                except ValueError:
                    continue
                image_by_name[image_name] = asset

    uses = []
    for symbol_name, symbol in symbols.items():
        match = re.fullmatch(r"__RM:::__GP_RM_(\d+)_(\d+)", symbol_name)
        if not match:
            continue
        shape, part = map(int, match.groups())
        texture_symbol = relocations.get(symbol["offset"] + 0x48, "")
        image_match = re.search(r"SHAPENAME=(\d+),", texture_symbol)
        if not image_match:
            continue
        image_name = int(image_match.group(1))
        asset = image_by_name.get(image_name)
        if not asset or asset["width"] < 128 or asset["height"] < 128:
            continue

        material = struct.unpack_from(
            "<16f", data, struct.unpack_from("<I", data, symbol["offset"] + 0x58)[0]
        )
        model = symbols.get("__Model:::" + str(shape))
        scale = struct.unpack_from("<4f", data, model["offset"] + 92) if model else (1, 1, 1, 1)
        vertex_symbol = symbols.get(f"__VB:::__GPvb_9_{part}_{shape}")
        if not vertex_symbol:
            continue
        _, byte_count, stride, _, vertex_offset = struct.unpack_from("<5I", data, vertex_symbol["offset"])
        encoded = [
            struct.unpack_from("<3h", data, vertex_offset + index * stride)
            for index in range(byte_count // stride)
        ]
        positions = [
            [(vertex[axis] + 16384) * scale[axis] / 16384 for axis in range(3)]
            for vertex in encoded
        ]
        uv_points = [
            [
                point[0] * material[0] + point[1] * material[4] + material[12],
                point[0] * material[1] + point[1] * material[5] + material[13],
            ]
            for point in positions
        ]
        apt_bounds = struct.unpack_from("<4f", apt_data, characters[shape]["offset"] + 8)
        uses.append(
            {
                "image_name": image_name,
                "source_id": asset["id"],
                "shape": shape,
                "part": part,
                "apt_shape_bounds": list(apt_bounds),
                "vertex_positions": positions,
                "uv_points": uv_points,
                "uv_bounds": [
                    [min(point[axis] for point in uv_points), max(point[axis] for point in uv_points)]
                    for axis in range(2)
                ],
                "material_matrix": list(material),
                "model_scale": list(scale),
            }
        )

    root_items = []
    for frame_index, frame in enumerate(movie.get("frames", [])):
        for kind, item in frame:
            if kind in ("PlaceObject", "FrameLabel", "RemoveObject"):
                root_items.append({"frame": frame_index, "kind": kind, "item": item})

    image_rows = []
    for image_name, asset in sorted(image_by_name.items()):
        if asset["width"] < 128 or asset["height"] < 128:
            continue
        aliases = [alias for alias in asset["aliases"] if "::" + entry + "::" in alias["source"]]
        if not aliases:
            continue
        source_id = asset["id"]
        image_rows.append(
            {
                "image_name": image_name,
                "source_id": source_id,
                "width": asset["width"],
                "height": asset["height"],
                "original_hash": asset["original_hash"],
                "alpha_range": asset["alpha"],
                "alias": aliases[0]["source"],
                "classification_status": (
                    "excluded-approved"
                    if source_id in approved
                    else ("excluded-pending16" if source_id in pending else "unapproved-mapped")
                ),
                "uses": [use for use in uses if use["image_name"] == image_name],
            }
        )

    results.append(
        {
            "movie": entry,
            "apt_root_frames": len(movie.get("frames", [])),
            "apt_root_labels": [
                {"frame": item["frame"], "label": item["item"].get("name")}
                for item in root_items
                if item["kind"] == "FrameLabel"
            ],
            "root_items": root_items,
            "images_ge_128": image_rows,
            "source_asset_uses": uses,
            "approved_intersection": [item["source_id"] for item in image_rows if item["source_id"] in approved],
            "pending16_intersection": [item["source_id"] for item in image_rows if item["source_id"] in pending],
        }
    )

output = {
    "schema": 1,
    "created": "2026-10-20",
    "scope": "Static source geometry and alpha range only; no builds/game runs/art generation. Coordinates use the same compressed-vertex formula and material matrices as audit-phone.py / audit-venue-frame-20261020.py.",
    "corpus": str(root),
    "assets": results,
}
Path("logs/ui-restoration-20261020/profile-autosave-metadata-20261020.json").write_text(
    json.dumps(output, indent=2)
)
