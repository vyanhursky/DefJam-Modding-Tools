#!/usr/bin/env python3
"""Metadata-only Menu/UI census against retained source-ID inventories."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / "logs/ui-restoration-20261017"
read_csv = lambda path: list(csv.DictReader((ROOT / path).open(newline="")))
aliases = read_csv("logs/ui-restoration-20261017/all-menu-texture-aliases.csv")
by_id = {}
for row in aliases:
    by_id.setdefault(row["id"], row)
all_ids = set(by_id)
flows = [r["screen"] for r in read_csv("logs/ui-restoration-20261017/registered-screens.csv")]
registered = {
    r["id"] for r in aliases
    if any(r["source"].lower().startswith(
        f"screens/screens.viv::screens/{name.lower()}.big::") for name in flows)
}
core_groups = {"_shared", "intMain", "battle", "options", "memoryCard", "story",
               "extras", "hiScores", "jukebox", "trans", "chyron", "_art"}
core = set()
for row in aliases:
    if row["source"].startswith("screens/screens.viv::"):
        parts = row["source"].split("::")[1].split("/")
        group = parts[1] if len(parts) > 2 else "_shared"
        if group in core_groups:
            core.add(row["id"])

config = json.loads((ROOT / "config/menu-ui-approved-artwork.json").read_text())
config_reviewed = {r["source_id"] for r in config["reviewed_sources"]}
controls = {r["id"] for r in json.loads(
    (LOGS / "pilot-v1/controls-v1-20261020/sources.json").read_text())}
pending = {r["id"] for r in json.loads(
    (LOGS / "pilot-v1/menu-details-v1-20261020/references.json").read_text())["sources"]}
old_inventory = json.loads((LOGS / "pilot-v1/results-approved-v1/remaining-inventory.json").read_text())
draft_ready = {r["id"] for r in old_inventory["priority_shortlist"]}
approved = config_reviewed | controls
dimension = {r["id"]: (int(r["width"]), int(r["height"])) for r in aliases}

screen_ids = defaultdict(set)
for row in aliases:
    if row["id"] in registered:
        for name in flows:
            prefix = f"screens/screens.viv::screens/{name.lower()}.big::"
            if row["source"].lower().startswith(prefix):
                screen_ids[name].add(row["id"])
families = []
for name in flows:
    ids = screen_ids[name]
    families.append({
        "screen": name,
        "source_ids": len(ids),
        "approved_ids": len(ids & approved),
        "remaining_ids": len(ids - approved),
        "status": "no approved source ID in this screen family" if ids and not ids & approved
                  else "partly covered; remaining IDs" if ids - approved
                  else "all registered IDs covered" if ids else "no source IDs matched",
    })

def scope(total, source_set):
    cov = len(source_set & approved)
    remaining = source_set - approved
    pending_ids = remaining & pending
    ready_ids = remaining & draft_ready - pending_ids
    untouched = remaining - pending_ids - ready_ids
    at_least_128_square = {i for i in remaining if dimension[i][0] >= 128 and dimension[i][1] >= 128}
    at_least_256_by_128 = {i for i in remaining if dimension[i][0] >= 256 and dimension[i][1] >= 128}
    return {
        "total": len(source_set), "approved_reviewed_ids": cov,
        "pending_batch_ids": len(pending_ids), "other_prior_shortlist_ids": len(ready_ids),
        "untouched_after_pending_and_shortlist": len(untouched),
        "remaining_without_custom_art_review": len(remaining),
        "remaining_ids_at_least_128x128": len(at_least_128_square),
        "remaining_ids_at_least_256x128": len(at_least_256_by_128),
    }

result = {
    "schema": 1,
    "method": "Distinct source texture IDs; retained CSVs and approval/reference JSON only.",
    "inputs": {
        "alias_rows": len(aliases), "broad_unique_ids": len(all_ids),
        "registered_screen_rows": len(flows), "config_reviewed_ids": len(config_reviewed),
        "controls_source_rows": len(json.loads((LOGS / "pilot-v1/controls-v1-20261020/sources.json").read_text())),
        "controls_unique_ids": len(controls), "pending_menu_details_unique_ids": len(pending),
    },
    "reconciliation": {
        "config_ids_outside_broad_inventory": len(config_reviewed - all_ids),
        "controls_ids_outside_broad_inventory": len(controls - all_ids),
        "controls_ids_missing_from_config": len(controls - config_reviewed),
        "controls_overlap_config": len(controls & config_reviewed),
        "controls_overlap_pending_details": len(controls & pending),
        "pending_details_overlap_approved_union": len(pending & approved),
        "pending_details_overlap_prior_shortlist": len(pending & draft_ready),
        "prior_shortlist_overlap_approved": len(draft_ready & approved),
        "prior_shortlist_remaining_after_approved_and_pending": len(draft_ready - approved - pending),
        "approved_union_ids": len(approved),
    },
    "scopes": {
        "registered_flows": scope(1323, registered),
        "core_families": scope(1834, core),
        "broad_ui_category": scope(11261, all_ids),
    },
    "bounded_registered_screen_families": {
        "listed": len(flows),
        "with_source_ids": sum(bool(screen_ids[n]) for n in flows),
        "with_no_source_id_match": sum(not screen_ids[n] for n in flows),
        "with_zero_approved_ids": sum(bool(screen_ids[n]) and not screen_ids[n] & approved for n in flows),
        "with_remaining_ids": sum(bool(screen_ids[n] - approved) for n in flows),
        "rows": families,
    },
    "disposition_note": "Pending and prior-shortlist counts are reported within each scope after removing approved IDs. The pending menu-details batch contains 19 IDs; it intersects the registered boundary by 13, core by 19, broad by 19. The 23-item prior confirmed shortlist is historical: 6 are now approved and 17 are in the pending batch, leaving no extra IDs outside those sets.",
    "classification_limit": "No pixel inspection or XSH/APT draw-shape analysis was performed. The census does not count actionable paintings or classify all residual IDs as backgrounds; fonts, glyphs, photos, masks, effects, widgets and small UI pieces are mixed in the broad scopes.",
}
(ROOT / "logs/ui-restoration-20261020/menu-ui-remaining-census.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("inputs", "reconciliation", "scopes", "bounded_registered_screen_families")}, indent=2))
