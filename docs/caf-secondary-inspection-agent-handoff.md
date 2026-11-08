# CAF secondary inspection: handoff for an upscaling agent

Send finished customization textures into the existing CAF inspector for a second,
on-model review. This workflow imports immutable workshop revisions and queues
their exact PNG hashes. It does not approve artwork, select a release revision,
install a pack or mark anything verified in the game.

## Services and ownership

- Texture workshop: `http://127.0.0.1:8768/` — owns candidate imports and art reviews.
- CAF inspector: `http://127.0.0.1:8780/caf-viewer` — reads workshop candidates;
  owns separate outfits, secondary-inspection status and notes.
- Check both services are using the same `corpus_id` before importing/queueing.
  Use workshop `GET /api/config` and CAF `GET /api/caf/catalog`.
- Keep the active writer running. Use `workshop import --server` while it runs;
  do not open a second CLI writer on its workspace. Do not directly edit either
  service's JSON state. Refreshing CAF revisions does not require restarting 8768.
- Keep source IDs, parent IDs, prompts, raw outputs and existing batch ledgers.
  A thumbnail filename, runtime texture ID or garment model name is not sufficient
  to identify the corpus asset. Resolve the exact 64-character source asset ID.

## 1. Resolve each texture and import only when necessary

Use the batch's existing source IDs. Verify against workshop
`GET /api/asset/ASSET_ID`: `source_id`, aliases, original dimensions and candidates.
The CAF catalogue maps `resources[resource_name].records[].asset` to these same
IDs; `groups[].items[].styles[].variants` maps model/style/color to that resource.
A resource can contain several maps. Retain the exact record/asset relationship.
Do not guess a source from a similar-looking garment or a shortened hash.

If the PNG was already imported, reuse its candidate `id` and `sha256` from that
asset response. Confirm its bytes match the batch output; do not reimport a whole
batch just to send it to CAF. Every import makes a new revision, even for identical
bytes. A timed-out import may have succeeded: check the asset's candidates before
retrying, using hash, label, parent and request ID to identify the result.

For a finished, full-atlas PNG that has not been imported:

```sh
python -m defjam_tools workshop import \
  --server http://127.0.0.1:8768 \
  --asset FULL_SOURCE_ASSET_ID \
  --image /private/batch/finished.png \
  --label "Batch name · item · upscale v2" \
  --style faithful \
  --prompt-file /private/batch/exact-prompt.txt
```

Use the configured tools Python/environment. `faithful` means Rich Original
Detail, not a claim that generated art is the Lanczos baseline. Add `--parent
r-EXACT_PARENT_ID` for a revision of an imported candidate, and `--request-id
q-EXACT_REQUEST_ID` only when completing that matching workshop generation request.
Store the import's returned JSON in the private batch receipt.

Import accepts a single RGB/RGBA PNG, at most 24 MiB, preserving the **entire source
atlas** at uniform integer scale 1–8× (maximum edge 16,384 pixels). A crop, mockup,
contact sheet or differently proportioned generation is not an importable atlas.
Do any required protected-region/alpha assembly through the established authoring
workflow first. Preserve the submitted finished bytes and raw generation separately.
Do not overwrite candidate PNGs or inherit a parent's approval.

## 2. Prepare a pinned batch manifest

Save this outside the source repository, replacing every placeholder. `sha256` is
the SHA-256 of the **PNG file bytes**, as returned by import, not `pixel_sha256`.
Use exact imported `r-...` IDs for generated upscales, not `original` or `faithful`.

```json
{
  "batch": "customization-finished-batch",
  "corpus_id": "FULL_CORPUS_ID",
  "items": [
    {"asset": "FULL_SOURCE_ASSET_ID", "revision": "r-EXACT_REVISION_ID", "sha256": "FULL_PNG_SHA256"}
  ]
}
```

Include one entry per source/revision. Keep detailed provenance in the existing
batch ledger; this manifest is a handoff index, not a replacement for that ledger.

## 3. Preflight, then enqueue serially

Save the following Python block as a private `send-caf-batch.py`. It uses only the
standard library. It preflights the whole manifest, matching the corpus and exact
revision/hash, reading each PNG through CAF's hash-checked endpoint, and checking
the source participates in an equipped resource's atlas composition. Unknown or
auxiliary-only maps stop the batch for manual investigation.

Without `--queue`, it makes **GET requests only**. With `--queue`, it adds pending
entries using the CAF token and current optimistic state version. It never writes
outfits, notes or approval fields. Queueing an existing source/revision reuses its
entry and preserves its notes/status. Do not parallelize state writes.

```python
import hashlib
import json
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8780"

def get(path):
    with urlopen(BASE + path, timeout=60) as response:
        return response.read()

def catalog():
    return json.loads(get("/api/caf/catalog"))

if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--queue"):
    raise SystemExit("Usage: send-caf-batch.py manifest.json [--queue]")
with open(sys.argv[1], encoding="utf8") as source:
    batch = json.load(source)
c = catalog()
assert batch["corpus_id"] == c["corpus_id"], "Wrong corpus"
assert batch["items"], "Empty batch"
mapped = set()
for group in c["groups"]:
    for item in group["items"]:
        if item.get("limitation"):
            continue
        for style in item["styles"]:
            for name in style["variants"]:
                records = c["resources"].get(name.lower(), {}).get("records", [])
                if not records:
                    continue
                first = records[0]
                placement = first.get("placement")
                count = placement["parameters"][0] if placement else 0
                eligible = {first["name"], *(f"al{i:02d}" for i in range(1, count + 1))}
                mapped.update(r["asset"] for r in records
                              if r.get("placement") and r["name"] in eligible and r.get("asset"))
seen = set()
rows = []
for item in batch["items"]:
    asset, revision, digest = (item[k] for k in ("asset", "revision", "sha256"))
    assert re.fullmatch(r"[0-9a-f]{64}", asset), "Invalid source ID"
    assert re.fullmatch(r"r-[0-9a-f]{16}", revision), "Use an imported revision ID"
    assert re.fullmatch(r"[0-9a-f]{64}", digest), "Invalid PNG hash"
    assert (asset, revision) not in seen, "Duplicate manifest entry"
    seen.add((asset, revision))
    assert asset in mapped, f"No composed CAF mapping: {asset}"
    candidate = next((r for r in c["revisions"].get(asset, []) if r["id"] == revision), None)
    assert candidate and candidate.get("sha256") == digest, f"Revision/hash mismatch: {asset}"
    assert hashlib.sha256(get(f"/api/caf/image/{asset}/{revision}")).hexdigest() == digest
    rows.append(dict(item, url=BASE + "/caf-viewer?" + urlencode(dict(asset=asset, revision=revision))))
if len(sys.argv) == 3:
    for row in rows:
        for attempt in range(3):
            c = catalog()  # get the current token and optimistic version
            payload = dict(action="queue", version=c["state"]["version"],
                           asset=row["asset"], revision=row["revision"])
            request = Request(BASE + "/api/caf/state", data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json", "X-Workshop-Token": c["token"]})
            try:
                with urlopen(request, timeout=60) as response:
                    state = json.load(response)
                break
            except HTTPError as error:
                if error.code != 409 or attempt == 2:
                    raise
        entry = next(q for q in state["queue"]
                     if (q["asset"], q["revision"]) == (row["asset"], row["revision"]))
        assert entry["sha256"] == row["sha256"], "Existing queue pin differs; investigate"
        row.update(queue_id=entry["id"], status=entry["status"])
        print(json.dumps(dict(queued=row)), file=sys.stderr, flush=True)
print(json.dumps(dict(batch=batch["batch"], corpus_id=batch["corpus_id"],
                      queued=len(sys.argv) == 3, items=rows), indent=2))
```

Run normally, without Python's `-O` option (the checks above use assertions):

```sh
python3 /private/batch/send-caf-batch.py /private/batch/caf-batch.json
python3 /private/batch/send-caf-batch.py /private/batch/caf-batch.json --queue > /private/batch/caf-receipt.json
```

Use a new receipt filename per attempt. On failure, retain stderr and completed
queue IDs; this is a serial, resumable submission, not an atomic batch transaction.
Rerunning the same manifest safely reuses completed queue entries. If an import
or PNG changed, stop and resolve identity rather than rewriting a hash to fit.
The queue holds at most 2,000 revisions. A persistent 409 means another client is
saving: save its notes and coordinate a quiet moment, then rerun.

## 4. Verify in the viewer and report to Vlad

Save any current inspection notes, then click **Refresh texture revisions** in the
existing CAF tab. Open **Inspection queue** and select the submitted entry. It
equips a matching source model/style/color and selects the exact candidate as B.
Keep or select the desired body build, skin, other clothing, hair and accessories.
Opening a queued item can replace that slot; save a named outfit first if needed.

The receipt's exact link also opens and queues that revision:
`http://127.0.0.1:8780/caf-viewer?asset=ASSET_ID&revision=REVISION_ID`.
**Opening this link is a queue write**, not a read-only preview. It does not mark
the entry inspected. Do not open many browser tabs against the same state writer.

Compare A = Original or Lanczos 4× against B = the exact imported revision. Use
Single view → toggle A/B / Hold A, or Side by side; inspect front, back, close-ups,
UV seams, hems, logos, tattoo alpha, hair silhouette and jewelry as relevant.
Texture RGB lighting helps judge authored pixels; Studio is a supplementary view.
Check that the source is actually composed on the model; auxiliary-map omissions
or a missing relationship are not a successful secondary inspection.

**Hair color** selects indexed Original/Lanczos palettes. Restored RGB hair keeps
its authored color, with a scene notice; the inspector does not recolor generated
RGB art. Atlas thumbnails likewise show authored image bytes.

Record feedback in **Inspection notes**, set **Inspected** or **Needs work**, and
click **Save inspection**. Those states apply only to the exact queued revision;
neither is artwork approval or game verification. Return the manifest, receipt,
queue IDs, direct links, rejected/unmapped entries and any review findings to Vlad.
For the first existing batch, preflight everything, queue one representative item,
verify its model and B revision, then submit the full manifest (the first entry is
reused). Leave aesthetic decisions pending until actually reviewed.

## Recovery and boundaries

If CAF is offline, use the owner's existing CAF restart command/configuration.
Preserve its cache and separate state folder; do not rebuild accepted caches or
start two writers. Do not restart the texture workshop to fix CAF. Never restore
an old JSON backup over newer reviews. A browser refresh or external submission
can make another tab's state version stale: save drafts, refresh revisions and
retry the intended operation, preserving the newest notes.

CAF is a static inspection preview. Body labels remain source A–F; hat/hair
compatibility, animation, game lighting/shaders and exhaustive native outfit parity
are not claimed. Keep native acceptance and release decisions in their existing
separate workflows. See [the CAF guide](create-a-fighter-viewer.md) for assembly
limits and saved-outfit controls.
