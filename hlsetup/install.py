"""Install the selected checkout and reconcile links owned by earlier installs."""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile


def layout(host, home):
    base = home / ("." + host)
    skills = home / ".agents/skills" if host == "codex" else base / "skills"
    groups = {skills: "skills"}
    if host == "claude":
        groups.update({base / "commands": ".claude/commands", base / "agents": "agents"})
    return groups


def source_for(root, group, name):
    if group == "skills":
        if name == "hlskills":
            return root
        if name.startswith("hl"):
            return root / name
    elif name.endswith(".md"):
        return root / group / name
    return None


def expected(root, groups):
    links = {}
    for dest, group in groups.items():
        if group == "skills":
            links[dest / "hlskills"] = root
            files = [entry.parent for entry in root.glob("hl*/SKILL.md")]
        else:
            files = (root / group).glob("*.md")
        links.update((dest / entry.name, entry) for entry in files)
    return links


def direct_link(path, target):
    # Compare the first hop, even for a retired source. Never claim an indirect alias.
    return target is not None and path.is_symlink() and path.parent / os.readlink(path) == target


def inventory(root, host, home, ledger, uninstall):
    groups = layout(host, home)
    wanted = expected(root, groups)
    old_skills = home / ".codex/skills"
    if host == "codex":
        groups[old_skills] = "skills"
    owned = {}
    old_anchor = home / ("." + host) / "skills/hlskills"
    # v1 installed the catalog and each skill (including hlsetup) together.
    # A user's standalone catalog shortcut does not identify a legacy installation.
    has_old_install = (ledger is None and direct_link(old_anchor, root)
                       and any(p != old_anchor and direct_link(p, source_for(root, "skills", p.name))
                               for p in old_anchor.parent.glob("hl*")))
    for directory, group in groups.items():
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            target = source_for(root, group, path.name)
            if not direct_link(path, target):
                continue
            # The old installer created direct links in the host-specific directories.
            # Codex shared links pre-dating its new installer are borrowed.
            if ledger is None:
                managed = has_old_install and (host != "codex" or directory == old_skills)
            else:
                managed = str(path.relative_to(home)) in ledger
            if managed:
                owned[path] = target
    conflicts = []
    if not uninstall:
        conflicts = [p for p, src in wanted.items()
                     if (p.exists() or p.is_symlink()) and p.resolve() != src]
        # Both host-specific and shared paths can feed a catalog. Reject foreign shadows.
        shadow = {"codex": old_skills, "cursor": home / ".agents/skills"}.get(host)
        if shadow:
            for path, src in wanted.items():
                other = shadow / path.name
                if (other.exists() or other.is_symlink()) and other.resolve() != src:
                    conflicts.append(other)
    missing = {p for p in wanted if not p.exists() and not p.is_symlink()}
    return wanted, owned, missing, conflicts


def save(path, owned, home):
    with NamedTemporaryFile("w", dir=path.parent, encoding="utf8", delete=False) as tmp:
        json.dump(sorted(str(p.relative_to(home)) for p in owned), tmp, ensure_ascii=False)
    os.replace(tmp.name, path)


def lock_state(stack, folder):
    # Serialize install/uninstall across hosts and checkouts. Read-only checks do not create state.
    folder.mkdir(parents=True, exist_ok=True)
    handle = stack.enter_context((folder / "install.lock").open("a+b"))
    if os.name == "nt":
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(handle, fcntl.LOCK_EX)


def run(args):
    root = Path(__file__).resolve().parents[1]
    home = Path.home()
    state = home / ".local/state/hlskills"
    key = hashlib.sha256(os.fsencode(root)).hexdigest()
    hosts = ("claude", "codex", "cursor") if args.host == "all" else [args.host]
    print("技能来源：", root)
    with ExitStack() as stack:
        if not args.check:
            lock_state(stack, state)
        plans = []
        errors = []
        total = 0
        for host in hosts:
            manifest = state / f"{host}-{key}.json"
            ledger = None
            if manifest.exists():
                values = json.loads(manifest.read_text(encoding="utf8"))
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    raise ValueError(f"安装记录格式错误：{manifest}")
                ledger = set(values)
            wanted, owned, missing, conflicts = inventory(root, host, home, ledger, args.uninstall)
            errors.extend(f"来源冲突：{p}" for p in conflicts)
            retired = owned.keys() - wanted.keys()
            if args.check:
                errors.extend(f"缺失：{p}" for p in sorted(missing))
                errors.extend(f"需清理旧入口：{p}" for p in sorted(retired))
            plans.append((manifest, wanted, owned, missing, retired))
            total += len(wanted)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        if not args.check:
            for manifest, wanted, owned, missing, retired in plans:
                # Save intent before touching files so an interrupted upgrade can be retried.
                tracked = set(owned) if args.uninstall else owned.keys() | missing
                save(manifest, tracked, home)
                if not args.uninstall:
                    for path in sorted(missing):
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.symlink_to(wanted[path], target_is_directory=wanted[path].is_dir())
                for path in sorted(owned if args.uninstall else retired):
                    if direct_link(path, owned[path]):
                        path.unlink()
                if args.uninstall:
                    manifest.unlink()
                else:
                    save(manifest, tracked - retired, home)
    print("已卸载本副本的链接" if args.uninstall else f"已核对 {total} 个入口")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=["claude", "codex", "cursor", "all"])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--uninstall", action="store_true")
    mode.add_argument("--check", action="store_true")
    try:
        sys.exit(run(parser.parse_args()))
    except (OSError, ValueError, RuntimeError) as exc:
        sys.exit(str(exc))
