"""Stable entry points over the extracted authoring modules."""
import argparse
import importlib
import json
import os
from pathlib import Path
import sys

COMMANDS = {
    "serve": "texture_workshop",
    "workshop": "texture_workshop",
    "model": "defjam_model",
    "assets": "hd_assets",
    "corpus": "hd_corpus",
    "audition": "hd_review",
    "swinir": "hd_swinir_review",
}


def read_profile(path):
    if not path:
        return {}
    path = Path(path).expanduser().resolve()
    profile = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(profile, dict) or profile.get("schema") != 1 or set(profile) - {"schema", "dump", "corpus", "workspace", "port"}:
        raise ValueError("Expected a schema 1 local profile with dump/corpus/workspace/port")
    result = {}
    for key in ("dump", "corpus", "workspace"):
        if key not in profile:
            continue
        value = profile[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid profile path: " + key)
        candidate = Path(value).expanduser()
        result[key] = str((path.parent / candidate).resolve() if not candidate.is_absolute() else candidate.resolve())
    if "port" in profile:
        if type(profile["port"]) != int or not 1024 <= profile["port"] <= 65535:
            raise ValueError("Profile port must be between 1024 and 65535")
        result["port"] = profile["port"]
    return result


def dispatch_args(command, arguments, profile):
    prefix = ["serve"] if command == "serve" else []
    defaults = []
    keys = ("dump", "corpus", "workspace") if command == "model" else ("corpus", "workspace", "port") if command in ("serve", "workshop") else ()
    # The workshop has an action positional before its flags. Move only that
    # action ahead of profile defaults; explicit flags after defaults win.
    remaining = list(arguments)
    if command == "workshop" and remaining and remaining[0] in ("serve", "import", "export"):
        prefix = [remaining.pop(0)]
    for key in keys:
        if key in profile:
            defaults += ["--" + key, str(profile[key])]
    return prefix + defaults + remaining


def main(argv=None):
    ap = argparse.ArgumentParser(description="Def Jam modding tools: local texture and static model review")
    default = os.environ.get("DEFJAM_TOOLS_PROFILE") or ("local.json" if Path("local.json").is_file() else None)
    ap.add_argument("--profile", type=Path, default=default, help="Private JSON paths; defaults to local.json or DEFJAM_TOOLS_PROFILE")
    ap.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    ap.add_argument("command", choices=COMMANDS, help="serve: resume gallery; workshop: import/export; model: private GLB; assets/corpus: extraction; audition/swinir: optional legacy tools")
    ap.add_argument("arguments", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    try:
        profile = read_profile(args.profile)
    except (OSError, ValueError) as e:
        ap.error(str(e))
    module = importlib.import_module("defjam_tools." + COMMANDS[args.command])
    saved = sys.argv
    try:
        sys.argv = ["defjam-tools " + args.command, *dispatch_args(args.command, args.arguments, profile)]
        return module.main()
    finally:
        sys.argv = saved
