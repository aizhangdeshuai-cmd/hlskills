"""Verify release inputs and CI evidence against one immutable Git commit."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"git {args[0]} 检查失败")
    return result.stdout


def committed_file(commit, filename):
    if filename.is_absolute() or ".." in filename.parts:
        raise ValueError(f"请使用仓库根目录内的相对路径：{filename}")
    data = git("show", f"{commit}:{filename.as_posix()}")
    if not data.strip():
        raise ValueError(f"候选提交中的 {filename} 为空")
    return data


def source_version(data, filename, custom_version):
    if filename.name == "package.json":
        return json.loads(data)["version"]
    if filename.name == "pyproject.toml":
        try:
            import tomllib
        except ImportError:
            raise ValueError("解析 pyproject.toml 需要 Python 3.11+")
        project = tomllib.loads(data).get("project", {})
        if "version" in project:
            return project["version"]
        if custom_version is None:
            raise ValueError("缺少 project.version，请提供项目工具从候选提交读取的 --source-version")
    if custom_version is not None:
        return custom_version
    return data.strip()


def has_release_note(line):
    note = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", line.strip())
    note = re.sub(r"^\[[ xX]?\]\s*", "", note)
    note = note.strip(" \t`*_<>[]().:：。…").casefold()
    placeholders = {"todo", "tbd", "fixme", "待补", "待定", "待填写", "待补充", "无变更", "no changes"}
    return note not in placeholders and any(character.isalnum() for character in note)


def check_changelog(data, tag, entry):
    version = tag.removeprefix("v")
    if entry is not None:
        if "{version}" not in entry and "{tag}" not in entry:
            raise ValueError("自定义版本行需包含 {version} 或 {tag} 占位符")
        if entry.count("{note}") > 1:
            raise ValueError("单行变更日志模板最多使用一次 {note}")
        title = re.escape(entry.replace("{version}", version).replace("{tag}", tag))
        title = title.replace(re.escape("{note}"), "(?P<note>.*)") + "$"
        other_version = re.escape(entry)
        for field in ("{version}", "{tag}"):
            other_version = other_version.replace(re.escape(field), r"\S+")
        other_version = other_version.replace(re.escape("{note}"), ".*") + "$"
    else:
        # Common Markdown release headings: "## [1.2.3] - date" or "# Release v1.2.3".
        prefix = r"(?i)#{1,6}[ \t]+(?:release[ \t]+)?\[?v?"
        title = prefix + re.escape(version) + r"(?=\]|[ \t]|$)"
        other_version = prefix + r"(?:\d+\.\d+|unreleased\b)"

    section_level = None
    fence = ""
    for raw_line in re.sub(r"<!--.*?(?:-->|$)", "", data, flags=re.DOTALL).splitlines():
        line = raw_line.strip()
        if fence:
            if line.startswith(fence) and not line.strip(fence[0]):
                fence = ""
            continue
        opening = re.match(r"^`{3,}|^~{3,}", line)
        if opening:
            fence = opening.group()
            continue
        heading = re.match(r"(#{1,6})(?:\s|$)", line)
        if section_level is None:
            match = re.match(title, line)
            if match:
                section_level = len(heading[1]) if heading else 0
                if "note" in match.groupdict():
                    if has_release_note(match["note"]):
                        return
                    break
            continue
        if re.match(other_version, line) or (heading and len(heading[1]) <= section_level):
            break
        if heading or re.match(r"^\[[^]]+\]:", line):
            continue
        if has_release_note(line):
            return
    if section_level is not None:
        raise ValueError(f"{tag} 的变更日志正文为空，请记录本次变更或无变更发布的具体原因")
    raise ValueError(f"候选提交的变更日志缺少本次发布 {tag} 的条目；按项目格式设置 --changelog-entry")


def check_ci(runs, required, commit):
    runs = runs if isinstance(runs, list) else [runs]
    if not runs or any(not isinstance(run, dict) or run.get("headSha") != commit
                       or run.get("status") != "completed" or run.get("conclusion") != "success"
                       for run in runs):
        raise ValueError("必需 CI 记录缺失、尚未成功结束或提交 SHA 不符")
    if len(set(required)) != len(required) or any(not name.strip() for name in required):
        raise ValueError("必需 CI 名称须非空且唯一；同名任务使用稳定的工作流或任务 ID")
    names = [run.get("workflowName") for run in runs]
    for name in required:
        if names.count(name) != 1:
            raise ValueError(f"必需 CI {name!r} 应恰有一份对应候选提交的最终运行记录")


def verify(args):
    if not re.fullmatch(r"(?:[a-f0-9]{40}|[a-f0-9]{64})", args.commit):
        raise ValueError("--commit 须为完整提交 SHA")
    if git("rev-parse", "--verify", args.commit + "^{commit}").strip() != args.commit:
        raise ValueError("候选 SHA 没有直接指向提交")
    ref = "refs/tags/" + args.tag
    git("check-ref-format", ref)
    if args.tag.startswith("-"):
        raise ValueError("标签不能以 - 开头")
    evidence = json.loads(args.ci.read_text())
    check_ci(evidence, args.require_workflow, args.commit)
    version = source_version(committed_file(args.commit, args.version_file), args.version_file, args.source_version)
    if version != args.tag.removeprefix("v"):
        raise ValueError(f"{args.version_file} 的发布版本与 {args.tag} 不匹配")
    check_changelog(committed_file(args.commit, args.changelog), args.tag, args.changelog_entry)
    if args.previous_tag:
        prior = git("rev-parse", "--verify", "refs/tags/" + args.previous_tag + "^{commit}").strip()
        if not git("diff", "--name-only", prior, args.commit, "--", str(args.changelog)).strip():
            raise ValueError(f"{args.changelog} 与上次发布 {args.previous_tag} 相同")
    if args.remote is None:
        changed = git("diff", "--name-only", args.commit, "--", str(args.version_file), str(args.changelog))
        if changed:
            raise ValueError(f"工作区发布文件与候选提交不同：{', '.join(changed.splitlines())}")
        return
    local_tag = git("rev-parse", "--verify", ref).strip()
    if git("rev-parse", "--verify", ref + "^{commit}").strip() != args.commit:
        raise ValueError("本地标签指向其他提交")
    lines = git("ls-remote", "--exit-code", "--", args.remote, ref, ref + "^{}").splitlines()
    remote = {name: sha for sha, name in (line.split("\t") for line in lines)}
    if remote.get(ref) != local_tag or remote.get(ref + "^{}", remote.get(ref)) != args.commit:
        raise ValueError("远端标签对象或解引用后的提交与本次发布不匹配")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--ci", required=True, type=Path, help="来自 CI 的运行记录 JSON，可为数组")
    parser.add_argument("--version-file", required=True, type=Path)
    parser.add_argument("--source-version", help="其他版本格式：由项目版本命令读取候选提交所得的值")
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--changelog-entry", help="完整版本行模板，含 {version} 或 {tag}，单行正文用 {note}")
    parser.add_argument("--require-workflow", action="append", default=[], help="项目规定的必需 CI 名称，可重复传入")
    parser.add_argument("--previous-tag", help="已有上一发布时，比对其 CHANGELOG 与本次提交")
    parser.add_argument("--remote", help="推送后核对本地及远端标签；省略时核对工作区发布文件")
    args = parser.parse_args()
    try:
        verify(args)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        sys.exit(f"发布检查失败：{exc}")
    print(f"{args.tag} {args.commit} {'远端标签与 CI 已核对' if args.remote else '候选提交与 CI 已核对'}")


if __name__ == "__main__":
    main()
