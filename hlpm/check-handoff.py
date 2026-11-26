"""Check a version's files, confirmed acceptance plan, trace tables and prototype evidence."""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import sys

from acceptance_plan import SPEC_FILES, load_plan, role_entry_paths, scenario_viewport, source_format, spec_digest, spec_supplements
from handoff_trace import check_trace, tables


BASE_FILES = (*SPEC_FILES, "consistency-matrix.md", "handoff-self-check.md")


def page_path(value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".html":
        raise argparse.ArgumentTypeError("页面须为相对 design/ 的 .html 文件")
    return path


def verify_screenshots(root, images, plan):
    from prototype_evidence import local
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError("解码必交 PNG 需要 Pillow，见 hlbrowse/requirements.txt") from exc
    design = (root / "design").resolve()
    required = {path.resolve(): page for page, path in images.items()}
    declared = plan.get("screenshot_viewports", {})
    if not isinstance(declared, dict):
        raise ValueError("screenshot_viewports 须按 design/ 内的 PNG 路径关联 TC")
    cases = {case["id"]: case for case in plan["scenarios"]}
    sizes = {}
    for name, key in declared.items():
        path = local(design, name)
        case = cases.get(key) if isinstance(key, str) else None
        if path.suffix != ".png" or not case or not (view := scenario_viewport(root, case)):
            raise ValueError(f"{name} 的 screenshot_viewports 须关联有视口的有效 TC，实际为 {key}")
        if path in required and required[path] not in set(case["pages"]) | role_entry_paths(case):
            raise ValueError(f"{name} 的 {key} 未覆盖该截图页面 {required[path]}")
        sizes[path] = tuple(view)
    for path in required.keys() | sizes.keys():
        try:
            with Image.open(path, formats=["PNG"]) as image:
                image.verify()
            with Image.open(path, formats=["PNG"]) as image:
                image.load()
                size = image.size
        except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
            raise ValueError(f"{path.name} 不是可解码的 PNG：{exc}") from exc
        if path in sizes and size != sizes[path]:
            w, h = sizes[path]
            raise ValueError(f"{path.name} 为 {size[0]}×{size[1]}，约定视口为 {w}×{h}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version_dir", type=Path)
    for option in ("ui", "screenshots", "competitive"):
        parser.add_argument("--" + option, choices=("yes", "no"), required=True)
    parser.add_argument("--page", action="append", default=[], type=page_path,
                        help="预期交付的 HTML，相对于 design/，可重复传入")
    parser.add_argument("--files-only", action="store_true", help="仅盘点既有文件，不验证验收计划或交接")
    parser.add_argument("--spec-sha256", help="接收方从产品交接记录取得的定稿文档摘要")
    args = parser.parse_args()
    if args.files_only and args.spec_sha256 is not None:
        parser.error("--spec-sha256 需要正式交接检查")
    if args.ui == "no" and (args.screenshots == "yes" or args.page):
        parser.error("页面或截图要求本次涉及 UI")
    root = args.version_dir
    required = [root / filename for filename in BASE_FILES]
    if args.files_only and (root / "prd.md").is_file():
        required.extend(root / name for name in spec_supplements(root, (root / "prd.md").read_bytes()))
    plan_pages = set()
    if not args.files_only:
        plan_path = root / "acceptance-plan.json"
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        plan = load_plan(plan_path)
        format_version = source_format(plan_path, plan)
        plan_pages = {Path(p) for s in plan["scenarios"] for p in s["pages"]}
        plan_pages.update(Path(entry) for case in plan["scenarios"] for entry in role_entry_paths(case))
        if (args.ui == "yes") != bool(plan_pages):
            raise ValueError("--ui 与确认计划中场景的 pages 不一致")
        if plan.get("screenshot_viewports") and args.screenshots == "no":
            raise ValueError("--screenshots no 与计划中已约定的视口截图不一致")
        uncovered = set(args.page) - plan_pages
        if uncovered:
            raise ValueError("交接清单中的页面缺少验收场景：" + "、".join(str(p) for p in sorted(uncovered)))
    if args.competitive == "yes":
        required.append(root / "analysis/competitive-analysis.md")
    missing = []
    screenshots = {}
    if args.ui == "yes":
        design = root / "design"
        pages = {path for path in design.rglob("*.html") if path.is_file()}
        if not args.files_only:
            orphaned = {p.relative_to(design) for p in pages} - plan_pages
            if orphaned:
                raise ValueError("设计包中的 HTML 缺少场景：" + "、".join(str(p) for p in sorted(orphaned)))
        pages.update(design / relative for relative in args.page)
        pages.update(design / relative for relative in plan_pages)
        if not args.files_only:
            required.append(design / "interaction-check.md")
        if not pages:
            missing.append("design/**/*.html")
            if args.screenshots == "yes":
                missing.append("design/**/screenshot-*.png")
        counts = Counter(page.stem for page in pages)
        for page in sorted(pages):
            required.append(page)
            if args.screenshots == "yes":
                name = f"screenshot-{page.stem}.png"
                local_image = page.with_name(name)
                legacy_image = design / name
                if counts[page.stem] == 1 and not local_image.exists() and legacy_image.is_file():
                    local_image = legacy_image
                required.append(local_image)
                screenshots[page.relative_to(design).as_posix()] = local_image
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(str(path.relative_to(root)))
    if missing:
        raise SystemExit("缺失或为空：" + "、".join(missing))
    categories = len(BASE_FILES) + sum(v == "yes" for v in (args.ui, args.screenshots, args.competitive))
    if args.files_only:
        print(f"{root}：{categories} 类适用交付物文件已盘点；尚未验证需求、用例或交互")
        return
    spec = spec_digest(root, args.spec_sha256)
    outcome_count = check_trace(root, plan, require_prd_results=format_version >= 3)
    if plan_pages:
        from prototype_checks import check, observation_table
        from prototype_evidence import check_interactions
        from reference_evidence import check_reference_handoff
        if screenshots:
            verify_screenshots(root, screenshots, plan)
        report = root / "design" / "interaction-check.md"
        check_interactions(report.parent, plan["scenarios"])
        check_reference_handoff(root, plan)
        if format_version >= 2 or any(observation_table(header) for header, *_ in tables(report, include_headers=True)):
            print(check(root / "prd.md", report))
    if hashlib.sha256(plan_path.read_bytes()).hexdigest() != digest:
        raise ValueError("验收计划在交接检查期间发生变化，请重新检查")
    spec_digest(root, spec)
    print(f"{root}：{categories} 类交付物、来源关联和适用的原型证据已核对")
    print(f"已逐值核对用例与断言的关键预期：{outcome_count} 项")
    compared = [case["id"] for case in plan["scenarios"] if "reference" in case]
    if compared:
        print("已核对竞品与原型：" + "、".join(compared))
    approved = [case["id"] for case in plan["scenarios"] if "prototype_match" in case]
    if approved:
        print("已核对供开发还原的原型基线：" + "、".join(approved))
    print(f"plan_sha256={digest}")
    print(f"spec_sha256={spec}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
