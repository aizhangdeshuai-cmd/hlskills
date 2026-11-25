"""Manage the documented project rules in .claude/settings.local.json."""
import argparse
import fcntl
import json
import os
import subprocess
import tempfile
from pathlib import Path


def save(path, data):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
    Path(tmp.name).replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--off", action="store_true")
    args = parser.parse_args()
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = Path(result.stdout.rstrip("\n")) if result.returncode == 0 else Path.cwd()
    lock = os.open(root, os.O_RDONLY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        update(root, args.off)
    finally:
        os.close(lock)


def update(root, off):
    settings = root / ".claude/settings.local.json"
    state = settings.with_name(".hl-permission.json")
    data = json.loads(settings.read_text()) if settings.exists() else {}
    allow = data.get("permissions", {}).get("allow", [])
    rules = [f"Edit({root}/**)", f"Write({root}/**)", f"Bash(*:{root}*)", f"Read({root}/**)"]
    owned = json.loads(state.read_text()) if state.exists() else []

    if off:
        # Legacy installs had no ownership record. --off retains their exact-match removal.
        remove = owned if state.exists() else rules
        remaining = [rule for rule in allow if rule not in remove]
        if remaining != allow:
            data["permissions"]["allow"] = remaining
            save(settings, data)
        if state.exists() and owned:
            save(state, [])
        print(f"已移除 {len(allow) - len(remaining)} 项授权：{settings}")
    else:
        settings.parent.mkdir(parents=True, exist_ok=True)
        added = [rule for rule in rules if rule not in allow]
        if added:
            save(state, list(dict.fromkeys(owned + added)))
            data.setdefault("permissions", {})["allow"] = allow + added
            save(settings, data)
        print(f"已添加 {len(added)} 项授权：{settings}")


if __name__ == "__main__":
    main()
