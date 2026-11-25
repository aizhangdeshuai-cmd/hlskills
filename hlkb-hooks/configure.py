"""Install and remove only the hook handlers owned by hlkb-hooks."""
import argparse
import fcntl
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

TAG = "# hlkb-hooks managed command\n"
SENTINEL_TEXT = "Created by hlkb-hooks\n"


def commands(p, legacy=False):
    # Preset fragments are embedded in a shell case or a quoted ERE.
    for key, pattern in p.items():
        if not re.fullmatch(r"[A-Za-z0-9_./*?|()+^-]+", pattern):
            raise ValueError(f"Unsupported path pattern in {key}: {pattern!r}")
        if key.endswith("_globs") and not re.fullmatch(r"[A-Za-z0-9_./*?^-]+(?:\|[A-Za-z0-9_./*?^-]+)*", pattern):
            raise ValueError(f"Invalid shell glob in {key}: {pattern!r}")
    read_input = "jq -r '.tool_input.command'"
    command_input = read_input if legacy else 'printf "%s\\n" "$CMD"'
    pre_cmd = (("" if legacy else f"CMD=$({read_input}); ") +
        f"{command_input} | grep -qE '^[[:space:]]*git commit' || exit 0; "
        f"{command_input} | grep -qE 'no-verify|\\[skip-kb-sync\\]' && exit 0; "
        "([ -f .hlskills ] || [ -d knowledge ]) || exit 0; "
        "CHANGED=$(git diff --cached --name-only); "
        f"echo \"$CHANGED\" | grep -qE '^({p['root_dirs']})/' || exit 0; "
        "MISS=''; "
        "for f in $CHANGED; do "
        "  case \"$f\" in "
        f"    {p['api_globs']}) "
        f"echo \"$CHANGED\" | grep -qE '^({p['sync_api_dir']})/' || MISS=\"$MISS api:$f\";; "
        f"    {p['db_globs']}) "
        f"echo \"$CHANGED\" | grep -qE '^({p['sync_db_dir']})/' || MISS=\"$MISS db:$f\";; "
        f"    {p['enum_globs']}) "
        f"echo \"$CHANGED\" | grep -qE '^({p['sync_enum_dir']})/' || MISS=\"$MISS enum:$f\";; "
        f"    {p['error_globs']}) "
        f"echo \"$CHANGED\" | grep -qE '^({p['sync_error_dir']})/' || MISS=\"$MISS err:$f\";; "
        f"    {p['test_globs']}) "
        f"echo \"$CHANGED\" | grep -qE '^({p['sync_test_dir']})/' || MISS=\"$MISS test:$f\";; "
        "  esac; "
        "done; "
        "[ -z \"$MISS\" ] && exit 0; "
        "echo '🚨 知识库未同步:' >&2; "
        "echo \"$MISS\" >&2; "
        "echo '' >&2; "
        "echo '请同步 knowledge/ 或 git commit --no-verify / commit message 加 [skip-kb-sync]' >&2; "
        "exit 2"
    )

    def to_case_patterns(globs):
        parts = globs.split('|')
        out = []
        for part in parts:
            # */controllers/* → *controllers*(任意位置出现即可)
            if part.endswith('/*'):
                out.append(f"*{part[:-2]}*")
            elif '*' in part:
                out.append(part)
            else:
                out.append(f"*{part}*")
        return '|'.join(out)

    # 渲染 PostToolUse command
    post_cmd = (
        "F=$(jq -r '.tool_input.file_path'); "
        "([ -f .hlskills ] || [ -d knowledge ]) || exit 0; "
        "case \"$F\" in "
        f"    {to_case_patterns(p['api_globs'])}) echo '🔔 接口文件变更,若涉及契约请同步 knowledge/api/';;"
        f"    {to_case_patterns(p['db_globs'])}) echo '🔔 数据库/架构变更,请同步 knowledge/db/ 或新建 ADR';; "
        f"    {to_case_patterns(p['enum_globs'])}) echo '🔔 枚举变更,请同步 knowledge/enums/';; "
        f"    {to_case_patterns(p['error_globs'])}) echo '🔔 错误码变更,请同步 knowledge/error-codes/';; "
        f"    {to_case_patterns(p['test_globs'])}) echo '🔔 测试变更,请同步 knowledge/tests/';; "
        "esac; exit 0"
    )
    return {"PreToolUse": ("Bash", pre_cmd), "PostToolUse": ("Write|Edit|MultiEdit", post_cmd)}


def update(settings, previous, legacy, desired):
    hooks = settings.get("hooks", {})
    if not desired and not hooks:
        return
    settings["hooks"] = hooks
    for event, legacy_commands in legacy.items():
        groups = hooks.get(event, [])
        kept = []
        found_old = False
        for group in groups:
            handlers = []
            for handler in group["hooks"]:
                command = handler.get("command", "")
                if handler.get("type") == "command" and command in legacy_commands:
                    found_old = True
                elif not (handler.get("type") == "command" and command.startswith(TAG)):
                    handlers.append(handler)
            if handlers or not group["hooks"]:
                kept.append(dict(group, hooks=handlers))
        if found_old:
            # Old installers overwrote this event. Recover its original groups when available.
            for group in previous.get("hooks", {}).get(event, []):
                if group not in kept and not any(h.get("command") in legacy_commands for h in group["hooks"]):
                    kept.append(group)
        if event in desired:
            matcher, command = desired[event]
            kept.append({"matcher": matcher, "hooks": [{"type": "command", "command": TAG + command}]})
        was_empty = previous.get("hooks", {}).get(event) == []
        if kept or (event in hooks and (not groups or was_empty)):
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if not hooks and previous.get("hooks") != {}:
        settings.pop("hooks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="default")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    settings = Path(".claude/settings.local.json")
    backup = settings.with_suffix(".json.hlkb-hooks.bak")
    sentinel = Path(".hlskills")
    presets = json.loads(Path(__file__).with_name("presets.json").read_text())
    rendered = {name: commands(spec["patterns"], legacy=True) for name, spec in presets.items()}
    legacy = {event: {pair[event][1] for pair in rendered.values()} for event in rendered["default"]}
    desired = {}
    if not args.uninstall:
        if args.preset in rendered:
            desired = commands(presets[args.preset]["patterns"])
        elif Path(args.preset).is_file():
            desired = commands(json.loads(Path(args.preset).read_text())["patterns"])
        else:
            parser.error("未知 preset: " + args.preset)

    lock = os.open(".", os.O_RDONLY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        apply(settings, backup, sentinel, legacy, desired, args)
    finally:
        os.close(lock)


def apply(settings, backup, sentinel, legacy, desired, args):
    original = settings.read_text() if settings.exists() else "{}"
    data = json.loads(original)
    previous = json.loads(backup.read_text()) if backup.is_file() else {}
    update(data, previous, legacy, desired)
    changed = data != json.loads(original)
    if args.dry_run:
        print("dry-run:", settings.resolve(), "配置将更新" if changed else "配置无变化")
        return
    if changed:
        settings.parent.mkdir(parents=True, exist_ok=True)
        if settings.is_file() and not backup.exists():
            shutil.copy2(settings, backup)
        with tempfile.NamedTemporaryFile(mode="w", dir=settings.parent, delete=False) as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp.write("\n")
        Path(tmp.name).replace(settings)
    if args.uninstall:
        if sentinel.is_file() and sentinel.read_bytes() == SENTINEL_TEXT.encode():
            sentinel.unlink()
    elif not sentinel.exists():
        sentinel.write_text(SENTINEL_TEXT)
    print("已卸载 hlkb-hooks" if args.uninstall else "已安装 hlkb-hooks", settings.resolve())


if __name__ == "__main__":
    main()
