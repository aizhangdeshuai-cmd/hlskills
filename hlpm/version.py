"""Select a PRD guide, discover version directories, and manage handoff markers."""
import argparse
from contextlib import contextmanager
import json
import os
import re
import sys
from pathlib import Path


ROOTS = (Path("knowledge/doc"), Path("docs"))
VERSION = re.compile(r"v[1-9][0-9]*")
DELIVERY_ENDPOINTS = {"prd": "4.5", "prototype": "6b.6", "workflow": "8.5", "handoff": "12.5"}
STANDARD_CHAPTERS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17)
PRD_SCALES = {
    "micro": ("iteration", (1, 2, 4, 7)),
    "iteration": ("iteration", (1, 2, 3, 4, 7, 16)),
    "module": ("standard", STANDARD_CHAPTERS),
    "product": ("standard", STANDARD_CHAPTERS),
    "rebuild": ("standard", STANDARD_CHAPTERS),
}
MARKERS = {
    "rejected": ".dev-rejected",
    "accepted": ".dev-accepted",
    "completed": ".dev-completed",
    "archived": ".product-archived",
}
ACTIONS = {
    "reject": ("rejected", {"ready", "rejected"}),
    "accept": ("accepted", {"ready", "rejected", "accepted"}),
    "complete": ("completed", {"accepted", "completed"}),
    "archive": ("archived", {"ready", "rejected", "archived"}),
}


@contextmanager
def locked_directory(directory):
    # Both mechanisms release the lock when a process exits, including a crash.
    if os.name == "nt":
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_TEMPORARY
        try:
            descriptor = os.open(directory / ".hl-version-lock", flags)
        except (FileExistsError, PermissionError) as exc:
            raise ValueError(f"无法锁定 {directory}，请检查权限或稍后重试") from exc
    else:
        import fcntl
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(descriptor)
            if isinstance(exc, BlockingIOError):
                raise ValueError(f"版本状态正在变更：{directory}。稍后重试。") from exc
            raise
    try:
        yield
    finally:
        os.close(descriptor)


def state(directory):
    found = []
    labels = {name: status for status, name in MARKERS.items()}
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.name in labels:
                if not entry.is_file(follow_symlinks=False):
                    raise ValueError(f"状态标记必须是普通文件：{entry.path}")
                found.append(labels[entry.name])
    if len(found) > 1:
        return "conflict"
    return found[0] if found else "ready"


def discover(project):
    versions = []
    for root in ROOTS:
        base = project / root
        if base.resolve() != base:
            raise ValueError(f"版本根目录包含符号链接：{base}")
        if not base.exists():
            continue
        for entry in base.iterdir():
            if VERSION.fullmatch(entry.name):
                if entry.is_symlink() or not entry.is_dir():
                    raise ValueError(f"版本路径必须是实际目录：{entry}")
                versions.append(entry)
    return sorted(versions, key=lambda p: (int(p.name[1:]), p.relative_to(project)))


def resolve_version(project, versions, selector):
    if VERSION.fullmatch(selector):
        matches = [p for p in versions if p.name == selector]
    else:
        candidate = (project / selector).resolve(strict=True)
        matches = [p for p in versions if p == candidate]
    if len(matches) != 1:
        choices = "、".join(str(p.relative_to(project)) for p in matches)
        raise ValueError(f"未唯一定位版本 {selector}。请指定完整目录。{choices}")
    return matches[0]


def retro_records(project, versions):
    retro_dir = project / "knowledge/retro"
    if retro_dir.resolve() != retro_dir or (retro_dir.exists() and not retro_dir.is_dir()):
        raise ValueError(f"需要项目内的实际复盘目录：{retro_dir}")
    records = []
    for directory in versions:
        package = directory.relative_to(project)
        path = retro_dir / package.with_suffix(".md")
        if path.resolve() != path or (path.exists() and not path.is_file()):
            raise ValueError(f"复盘文件须位于实际目录内：{path}")
        records.append({"package": package.as_posix(), "state": state(directory),
                        "report": path.relative_to(project).as_posix(), "exists": path.is_file()})
    # Older reports used a version number alone. Never attach one to both packages.
    legacy = []
    for path in sorted(retro_dir.glob("v*.md")):
        if not VERSION.fullmatch(path.stem):
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"需要普通旧复盘文件：{path}")
        candidates = [r["package"] for r in records if Path(r["package"]).name == path.stem]
        legacy.append({"report": path.relative_to(project).as_posix(), "candidates": candidates})
    return {"packages": records, "legacy": legacy}


def mark(directory, action):
    if not directory.is_dir() or not VERSION.fullmatch(directory.name):
        raise ValueError(f"需要所选版本的实际目录：{directory}")
    directory = directory.absolute()
    root = directory.parent
    if root.name == "docs":
        project = root.parent
    elif root.name == "doc" and root.parent.name == "knowledge":
        project = root.parent.parent
    else:
        raise ValueError(f"版本目录应位于项目的 docs/ 或 knowledge/doc/ 下：{directory}")
    canonical = project.resolve(strict=True) / directory.relative_to(project)
    if directory.resolve(strict=True) != canonical:
        raise ValueError(f"版本目录包含符号链接或非规范路径：{directory}")
    with locked_directory(directory):
        current = state(directory)
        target, allowed = ACTIONS[action]
        if current not in allowed:
            raise ValueError(f"{directory} 当前为 {current}，不能执行 {action}")
        if current != target:
            marker = directory / MARKERS[target]
            if current == "ready":
                marker.touch(exist_ok=False)
            else:
                (directory / MARKERS[current]).rename(marker)
        return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    form = sub.add_parser("prd-form", help="按项目现状及用户选择返回本技能内的 PRD 指引")
    form.add_argument("project_state", choices=("existing", "new", "unknown"))
    form.add_argument("--form", choices=("iteration", "standard", "mini"),
                      help="用户明确选择的形式，mini 为 iteration 的旧称")
    form.add_argument("--scale", choices=PRD_SCALES,
                      help="已明确的需求规模，结合 --delivery 输出应覆盖的章节")
    form.add_argument("--delivery", choices=DELIVERY_ENDPOINTS,
                      help="指定本次交付范围，以 JSON 返回 PRD 指引和结束步骤")
    form.add_argument("--single", action="store_true", help="用户明确只交一份自包含 PRD")
    form.add_argument("--outline", type=Path, help="客户已确认的 16 章编号 Markdown 目录文件")
    for command in ("list", "resolve", "new", "retro"):
        cmd = sub.add_parser(command)
        cmd.add_argument("project", type=Path)
        if command == "resolve":
            cmd.add_argument("version", help="版本号或相对于项目的完整版本目录，也可为绝对路径")
        elif command == "retro":
            cmd.add_argument("version", nargs="?", help="仅显示选定包及该编号的旧复盘")
    cmd = sub.add_parser("mark")
    cmd.add_argument("directory", type=Path)
    cmd.add_argument("action", choices=ACTIONS)
    args = parser.parse_args()
    if args.command == "prd-form":
        if args.single and (args.outline or args.form == "standard" or args.delivery not in (None, "prd")):
            parser.error("单文件简稿只适用于仅交 PRD；固定目录、标准分册或后续阶段请选对应格式")
        default_form = {"existing": "iteration", "new": "standard", "unknown": None}[args.project_state]
        selected = ("mini" if args.single else args.form) or ("standard" if args.outline else None) or (
            PRD_SCALES[args.scale][0] if args.scale else default_form)
        guides = {"iteration": "prd-mini.md", "mini": "prd-mini.md", "standard": "prd-cards.md"}
        guide = guides[selected] if selected else "ask"
        if args.delivery or args.outline or args.single:
            result = {"guide": guide}
            delivery = args.delivery or ("prd" if args.single else "workflow")
            result["stop_after"] = DELIVERY_ENDPOINTS[delivery]
            if delivery in {"workflow", "handoff"}:
                result["test_stage_files"] = ["test-cases.md"] if args.outline else ["acceptance-criteria.md", "test-cases.md"]
            if args.outline:
                if selected != "standard":
                    parser.error("客户固定目录适用于标准稿，请核对与 --form 的选择")
                from enterprise_prd import customer_sections
                chapters = customer_sections(args.outline)[()]
                result.update(chapters=[item[0][0] for item in chapters],
                              declaration=f"<!-- hlpm:outline={args.outline.name} -->")
            elif selected:
                if selected == "standard":
                    chapters = STANDARD_CHAPTERS
                    profile = "split"
                else:
                    chapters = PRD_SCALES["micro" if args.scale == "micro" else "iteration"][1]
                    profile = "single" if args.single else "split-mini"
                    result["chapter_basis"] = "standard_topic_mapping"
                result["chapters"] = list(chapters)
                result["declaration"] = f"<!-- hlpm:{profile} -->"
            if selected and not args.single and not args.outline:
                result["ask_separately"] = ["data-requirements.md", "interface-requirements.md"]
            print(json.dumps(result))
        else:
            print(guide)
        return
    if args.command == "mark":
        print(mark(args.directory, args.action))
        return

    project = args.project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError(f"项目目录不存在：{project}")
    versions = discover(project)
    if args.command == "resolve":
        print(resolve_version(project, versions, args.version))
        return
    if args.command == "retro":
        result = retro_records(project, versions)
        if args.version:
            selected = resolve_version(project, versions, args.version).relative_to(project)
            result["packages"] = [r for r in result["packages"] if r["package"] == selected.as_posix()]
            result["legacy"] = [r for r in result["legacy"] if Path(r["report"]).stem == selected.name]
        print(json.dumps(result, ensure_ascii=False))
        return

    next_number = int(versions[-1].name[1:]) + 1 if versions else 1
    next_dir = ROOTS[0] / f"v{next_number}"
    if args.command == "new":
        # Do not silently adopt a directory created concurrently.
        try:
            (project / next_dir).mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            raise ValueError(f"版本目录已被创建：{next_dir}。请重新列出目录，再选择续写或新建。") from None
        print(project / next_dir)
    else:
        rows = [{"version": p.name, "path": str(p.relative_to(project)), "state": state(p)}
                for p in versions]
        print(json.dumps({"versions": rows, "next": str(next_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
