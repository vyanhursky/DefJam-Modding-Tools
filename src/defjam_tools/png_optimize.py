"""Copy-only PNG optimization with exact RGBA and PNG metadata verification."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import tempfile
import time
import zlib

from PIL import Image
from .paths import require_private_output

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def chunks(data):
    """Validate chunk boundaries/CRCs; retain every non-IDAT payload exactly."""
    if not data.startswith(SIGNATURE):
        raise ValueError("Not a PNG")
    pos = 8
    result = []
    while pos < len(data):
        if len(data) - pos < 12:
            raise ValueError("Truncated PNG chunk")
        size = struct.unpack_from(">I", data, pos)[0]
        end = pos + 12 + size
        if end > len(data):
            raise ValueError("PNG chunk exceeds input")
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + size]
        crc = struct.unpack_from(">I", data, pos + 8 + size)[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError("PNG chunk CRC mismatch")
        result.append((kind, payload))
        pos = end
        if kind == b"IEND":
            if size or pos != len(data):
                raise ValueError("Invalid IEND or trailing bytes")
            break
    if not result or result[0][0] != b"IHDR" or len(result[0][1]) != 13:
        raise ValueError("Missing PNG IHDR")
    if result[-1][0] != b"IEND" or not any(k == b"IDAT" for k, _ in result):
        raise ValueError("Incomplete PNG")
    return result


def verify_pixels(before, after):
    old = chunks(before)
    new = chunks(after)
    # Conservative profile: preserve format, palette, colour metadata, text and
    # private chunks. Even metadata that is safe to strip is left untouched.
    if [(k, v) for k, v in old if k != b"IDAT"] != [(k, v) for k, v in new if k != b"IDAT"]:
        raise ValueError("PNG header/metadata/palette changed")
    with Image.open(io.BytesIO(before)) as a, Image.open(io.BytesIO(after)) as b:
        aa = a.convert("RGBA")
        bb = b.convert("RGBA")
        pixels = aa.tobytes()
        if aa.size != bb.size or pixels != bb.tobytes():
            raise ValueError("Decoded RGBA changed, including hidden RGB")
        return {"dimensions": list(aa.size), "decoded_rgba_sha256": digest(pixels),
                "rgba_exact": True, "non_idat_chunks_exact": True}


def encode_copy(data, executable, level=4):
    """Feed a frozen byte snapshot to Oxipng; never give it the source path."""
    with tempfile.TemporaryDirectory(prefix="defjam-png-") as temp:
        target = Path(temp) / "candidate.png"
        command = [executable, "-o", str(level), "--nx", "--interlace", "keep",
                   "--threads", "1", "--timeout", "60", "--out", str(target), "-"]
        result = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=180, check=False)
        if result.returncode:
            raise ValueError("Oxipng failed: " + result.stderr.decode("utf8", "replace")[-2000:])
        # Some versions skip writing when no improvement is found.
        return target.read_bytes() if target.exists() else data


def optimize_bytes(data, executable, level=4, encoder=None):
    original_chunks = chunks(data)
    depth = original_chunks[0][1][8]
    if depth > 8 or any(k in (b"acTL", b"fcTL", b"fdAT") for k, _ in original_chunks):
        return data, {"status": "retained_unsupported", "reason": "Static PNG at <=8-bit depth required"}
    start = time.perf_counter()
    try:
        candidate = (encoder or encode_copy)(data, executable, level)
        proof = verify_pixels(data, candidate)
        selected = candidate if len(candidate) < len(data) else data
        return selected, {"status": "optimized" if selected is candidate and selected != data else "retained_not_smaller",
                          "candidate_bytes": len(candidate), **proof,
                          "seconds": round(time.perf_counter() - start, 4)}
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        # Preserve a usable exact original and surface the failed experiment.
        return data, {"status": "retained_verification_failed", "reason": str(error),
                      "seconds": round(time.perf_counter() - start, 4)}


def relative_png(value):
    if not isinstance(value, str) or "\\" in value:
        raise ValueError("Output must be a forward-slash relative PNG path")
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(v in ("..", ".", "") for v in value.split("/")) or ":" in value or p.suffix.lower() != ".png":
        raise ValueError("Unsafe output PNG path")
    return p


def plan_entries(source=None, manifest=None):
    if (source is None) == (manifest is None):
        raise ValueError("Choose exactly one input directory or manifest")
    if source is not None:
        source = Path(source)
        if source.is_symlink() or not source.is_dir():
            raise ValueError("Input must be a real directory")
        source = source.resolve()
        entries = [{"input": str(p), "output": p.relative_to(source).as_posix()}
                   for p in sorted(source.rglob("*")) if p.is_file() and p.suffix.lower() == ".png"]
        # Reject links even if they are directory links containing no PNGs.
        if any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError("Input tree contains a symlink")
    else:
        entries = json.loads(Path(manifest).read_text(encoding="utf8"))
        if not isinstance(entries, list):
            raise ValueError("Manifest must be a list of input/output PNG pairs")
    if not entries:
        raise ValueError("No PNG inputs")
    result = []
    used = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"input", "output"}:
            raise ValueError("Each entry needs exactly input and output")
        p = Path(entry["input"])
        if not p.is_absolute() and manifest is not None:
            p = Path(manifest).resolve().parent / p
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents) or not p.is_file():
            raise ValueError("Input must be a regular file without symlink parents")
        p = p.resolve()
        if p.suffix.lower() != ".png":
            raise ValueError("Only PNG inputs are accepted")
        rel = relative_png(entry["output"])
        collision = str(rel).casefold()
        if collision in used:
            raise ValueError("Duplicate output name, including case-insensitive collisions")
        used.add(collision)
        result.append((p, rel))
    return result


def optimize_batch(output, *, source=None, manifest=None, executable="oxipng", level=4, jobs=4, progress=False):
    if level not in range(7) or jobs not in range(1, 33):
        raise ValueError("Level must be 0..6; jobs must be 1..32")
    entries = plan_entries(source, manifest)
    output = require_private_output(output)
    if output.exists():
        raise ValueError("Output must not already exist; choose a new staging directory")
    if source is not None:
        source_path = Path(source).resolve()
        if output.is_relative_to(source_path) or source_path.is_relative_to(output):
            raise ValueError("Input and output trees must be disjoint")
    if any(p.is_relative_to(output) or output == p for p, _ in entries):
        raise ValueError("Output would contain an input")
    exe = shutil.which(str(executable))
    if not exe:
        raise ValueError("Oxipng is not installed; install it separately or pass --oxipng")
    version = subprocess.run([exe, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    # Validate every PNG before creating output or invoking any optimization.
    for p, _ in entries:
        chunks(p.read_bytes())
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()

    def process(item):
        p, rel = item
        data = p.read_bytes()
        selected, proof = optimize_bytes(data, exe, level)
        if digest(p.read_bytes()) != digest(data):
            raise ValueError("Input changed during optimization: " + str(p))
        target = output.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(selected)
        if target.read_bytes() != selected:
            raise ValueError("Output write verification failed")
        return {"input": str(p), "output": str(rel), "input_sha256": digest(data),
                "output_sha256": digest(selected), "before_bytes": len(data),
                "after_bytes": len(selected), **proof}

    records = []
    try:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            for record in pool.map(process, entries):
                records.append(record)
                if progress and (len(records) % 50 == 0 or len(records) == len(entries)):
                    print(f"Verified {len(records)}/{len(entries)} PNGs", flush=True)
    finally:
        before = sum(x["before_bytes"] for x in records)
        after = sum(x["after_bytes"] for x in records)
        receipt = {"schema": 1, "tool": "defjam_tools.png_optimize", "optimizer": version,
                   "module_sha256": digest(Path(__file__).read_bytes()),
                   "profile": ["-o", str(level), "--nx", "--interlace", "keep", "--threads", "1", "--timeout", "60"],
                   "policy": "Copy only. No alpha optimization, quantization, colour-type/depth reduction or metadata stripping. All non-IDAT chunks and decoded RGBA exact. Keep smaller only. APNG/16-bit retained unchanged. Not an installable/signed release.",
                   "complete": len(records) == len(entries), "planned_files": len(entries),
                   "files": len(records), "before_bytes": before, "after_bytes": after,
                   "saved_bytes": before-after, "saved_percent": round(100*(before-after)/before, 4) if before else 0,
                   "failures": sum(x["status"] == "retained_verification_failed" for x in records),
                   "skipped": sum(x["status"] == "retained_unsupported" for x in records),
                   "seconds": round(time.perf_counter()-started, 3), "records": records}
        (output / "optimization-receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf8")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--input", type=Path, help="Recursively read PNGs; preserve relative paths")
    inputs.add_argument("--manifest", type=Path, help="JSON list of input/output pairs, for selected files")
    parser.add_argument("--out", type=Path, required=True, help="NEW private staging directory; never in-place")
    parser.add_argument("--oxipng", default="oxipng", help="Installed optimizer path")
    parser.add_argument("--level", type=int, choices=range(7), default=4)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        result = optimize_batch(args.out, source=args.input, manifest=args.manifest,
                                executable=args.oxipng, level=args.level, jobs=args.jobs, progress=True)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    print(json.dumps({k:v for k,v in result.items() if k != "records"}, indent=2))
    return int(bool(result["failures"] or not result["complete"]))


if __name__ == "__main__":
    raise SystemExit(main())
