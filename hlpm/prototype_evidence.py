"""Run and verify scenario evidence for locally delivered HTML prototypes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit
from urllib.request import url2pathname

from acceptance_plan import check_role_observations, role_entry_paths, scenario_viewport, validate_roles


ASSERTIONS = {"expect-visible-text", "expect-hidden", "expect-disabled", "expect-enabled"}
# Navigation must follow controls in this very prototype. Diagnostics stay in browse.py.
ACTIONS = {"click", "dblclick", "fill", "select", "press", "type", "hover", "reload", "back",
           "forward", "tab", "wait", "visible", "scroll", "expect-clean", "expect-object"}


def local(design, name):
    path = Path(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"需要 design/ 内的相对路径：{name}")
    file = (design / path).resolve()
    if design not in file.parents:
        raise ValueError(f"路径越出 design/：{name}")
    return file


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interaction_scenario(case):
    # Sign-off attaches the final capture after the prototype interaction has been run.
    return {key: value for key, value in case.items() if key != "prototype_match"}


def plan_revision(plan, case):
    sources = [row for row in plan["sources"] if set(case["acs"]).intersection(row.get("acs", []))]
    data = json.dumps([plan["scope"], sources, interaction_scenario(case)], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()


def check_steps(design, plan, case, record):
    key = case["id"]
    path = local(design, f"checks/{key}.steps")
    lines = [shlex.split(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if record.get("scenario") != interaction_scenario(case) or record.get("steps_sha256") != digest(path):
        raise ValueError("场景定义或操作步骤已变，请复验")
    if record.get("plan_revision") != plan_revision(plan, case):
        raise ValueError("场景的确认范围或原始约束已变，请复验")
    if record.get("status") != "pass":
        raise ValueError(f"交互结果 {record.get('status')}，{record.get('error', '尚无完成记录')}")
    view = scenario_viewport(design.parent, case)
    # Reports predating viewport selection always ran at Playwright's 1280×720 default.
    if view is not None and record.get("viewport", [1280, 720]) != view:
        raise ValueError(f"原型证据与本场景约定视口 {view[0]}×{view[1]} 不符，请复验")
    resources = record.get("resources", {})
    if not isinstance(resources, dict):
        raise ValueError("缺原型文件摘要")
    missing = (set(case["pages"]) | role_entry_paths(case)) - resources.keys()
    if missing:
        raise ValueError("缺实际页面来源：" + ", ".join(sorted(missing)))
    for name, expected in resources.items():
        if digest(local(design, name)) != expected:
            raise ValueError(f"设计文件已变：{name}")
    observed = record.get("step_pages")
    if not isinstance(observed, list) or len(observed) != len(lines):
        raise ValueError("执行步骤不完整")
    if "roles" in case:
        checkpoints = record.get("checkpoints")
        check_role_observations(case, checkpoints)
        current = None
        opened = set()
        position = 0
        for words, page in zip(lines, observed):
            if words[:1] == ["role"]:
                if len(words) != 2 or words[1] not in case["roles"]:
                    raise ValueError(f"未登记的角色步骤：{words}")
                current = words[1]
                opened.add(current)
            if not current or words[:1] == ["tab"]:
                raise ValueError("跨角色场景须用 role 选择已登记的页签")
            if words == ["checkpoint"]:
                if position >= len(checkpoints):
                    raise ValueError("存在多余的 checkpoint")
                actual = checkpoints[position]
                if (current, page) != (actual["role"], actual["page"]):
                    raise ValueError(f"第 {position + 1} 次访问与角色步骤或实测页面不符")
                position += 1
        if position != len(checkpoints):
            raise ValueError("步骤未覆盖计划中的所有 checkpoint")
        if opened != case["roles"].keys():
            raise ValueError("有已登记角色未实际打开")
        return
    visits = []
    for words, page in zip(lines, observed):
        if not words or not isinstance(page, str):
            raise ValueError("缺操作或实测页面")
        if not visits or visits[-1]["page"] != page or words[0] == "reload":
            visits.append({"page": page, "business": False, "identified": False, "results": {}})
        if words[0] in ASSERTIONS:
            visits[-1]["business"] = True
        if words[0] == "expect-visible-text" and len(words) == 3:
            visits[-1]["results"][words[1]] = words[2]
        if words[0] == "expect-object" and len(words) == 3 and words[2] == case.get("object"):
            visits[-1]["identified"] = True
    itinerary = iter(visits)
    for position, target in enumerate(case["pages"], 1):
        expected = case["visits"][position - 1]["expect"] if "visits" in case else {}
        if not any(visit["page"] == target and visit["business"]
                   and expected.items() <= visit["results"].items()
                   and (not case.get("object") or visit["identified"]) for visit in itinerary):
            identity = f"及对象 {case['object']} 的标识" if case.get("object") else ""
            outcome = f" {expected}" if expected else ""
            raise ValueError(f"第 {position} 个计划页面 {target} 缺同次访问的业务断言{outcome}{identity}")


def check_interactions(design_dir, scenarios):
    design = design_dir.resolve()
    ui = [case for case in scenarios if case["pages"]]
    if not ui:
        return
    issues = []
    try:
        notes = local(design, "interaction-check.md").read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"缺少可读的 design/interaction-check.md：{exc}") from exc
    plan = json.loads((design.parent / "acceptance-plan.json").read_text(encoding="utf-8"))
    links = set(re.findall(r"\[[^\]\n]+\]\((?:\./)?(checks/[^)\n]+\.json)\)", notes))
    for case in ui:
        key = case["id"]
        try:
            filename = f"checks/{key}.json"
            if filename not in links:
                raise ValueError(f"interaction-check.md 缺运行报告链接 {filename}")
            record = json.loads(local(design, filename).read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("交互报告须为 JSON 对象")
            check_steps(design, plan, case, record)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            issues.append(f"{key}：{exc}")
    if issues:
        raise ValueError("；".join(issues))


def write_record(path, record):
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as out:
        json.dump(record, out, ensure_ascii=False, indent=2)
    pending = Path(out.name)
    try:
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def browser_page(design, url):
    parts = urlsplit(url)
    if parts.scheme != "file" or parts.netloc:
        raise ValueError("请在本地交付的 HTML 中验证业务页面")
    return Path(url2pathname(parts.path)).resolve().relative_to(design).as_posix()


def verify_pins(page):
    issues = page.evaluate("""() => {
      if (!document.querySelector('.bl-pin, #bl-drawer')) return [];
      const detail = {};
      document.dispatchEvent(new CustomEvent('bl:check-pins', { detail }));
      return detail.issues ?? ['无法读取钉点配置，请更新本页的 bl-marker.js'];
    }""")
    if issues:
        raise ValueError("钉点核验失败：" + "、".join(issues))


def visible_value(session, selector, expected):
    session.run(["expect-visible-text", selector, expected])
    return session.page.locator(selector).filter(visible=True).inner_text().strip()


def run_role_step(words, session, tabs, active, design, case, record):
    from browse import navigate

    if words[0] == "role":
        if len(words) != 2 or words[1] not in case["roles"]:
            raise ValueError(f"未登记的角色步骤：{words}")
        active = words[1]
        config = case["roles"][active]
        if active not in tabs:
            page = session.page.context.new_page() if tabs else session.page
            url = urlsplit(config["entry"])
            entry = urlsplit(local(design, url.path).as_uri())._replace(query=url.query, fragment=url.fragment)
            navigate(page, entry.geturl())
            tabs[active] = page
        session.page = tabs[active]
        visible_value(session, *config["identity"])
        return active
    if not active or words[0] == "tab":
        raise ValueError("跨角色场景须用 role 选择已登记的页签")
    if words[0] == "checkpoint":
        index = len(record["checkpoints"])
        if words != ["checkpoint"] or index >= len(case["visits"]):
            raise ValueError("无效或多余的 checkpoint")
        visit = case["visits"][index]
        page = browser_page(design, session.page.url)
        if (active, page) != (visit["role"], case["pages"][index]):
            raise ValueError(f"第 {index + 1} 次访问应在 {visit['role']}/{case['pages'][index]}，实测 {active}/{page}")
        record["checkpoints"].append({
            "role": active, "page": page, "identity": visible_value(session, *case["roles"][active]["identity"]),
            "object": visible_value(session, visit["object_at"], case["object"]),
            "results": {selector: visible_value(session, selector, expected)
                        for selector, expected in visit["expect"].items()},
        })
        verify_pins(session.page)
    return active


def run_case(package, key, channel):
    design = (package / "design").resolve()
    plan = json.loads((package / "acceptance-plan.json").read_text(encoding="utf-8"))
    cases = [row for row in plan["scenarios"] if row["id"] == key]
    if len(cases) != 1 or not cases[0]["pages"] or not re.fullmatch(r"[\w.-]+", key):
        raise ValueError(f"需要唯一的界面场景：{key}")
    case = cases[0]
    path = local(design, f"checks/{key}.steps")
    output = local(design, f"checks/{key}.json")
    record = {"scenario": interaction_scenario(case), "status": "running", "step_pages": [], "resources": {}}
    write_record(output, record)
    step = "启动"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hlbrowse"))
        from browse import Session, navigate
        from playwright.sync_api import sync_playwright
        validate_roles(case)
        tabs = {}
        active = None
        if "roles" in case:
            record["checkpoints"] = []
        record["plan_revision"] = plan_revision(plan, case)
        record["steps_sha256"] = digest(path)
        width, height = scenario_viewport(package, case) or [1280, 720]
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=channel, chromium_sandbox=True)
            context = browser.new_context(viewport={"width": width, "height": height}, offline=True, service_workers="block")
            context.set_default_timeout(5000)
            requested = set()
            context.on("request", lambda req: requested.add(req.url))
            page = context.new_page()
            actual = page.viewport_size
            record["viewport"] = [actual["width"], actual["height"]]
            session = Session(page)
            if "roles" not in case:
                navigate(page, str(local(design, case["pages"][0])))
            for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                step = f"{key}.steps 第 {index} 行"
                words = shlex.split(line)
                verb = words[0]
                if "roles" in case:
                    if verb == "checkpoint" and active:
                        step += f" · 第 {len(record['checkpoints']) + 1} 次访问 {active}/{browser_page(design, session.page.url)}"
                    active = run_role_step(words, session, tabs, active, design, case, record)
                    if verb in {"role", "checkpoint"}:
                        record["step_pages"].append(browser_page(design, session.page.url))
                        continue
                if verb not in ACTIONS and verb not in ASSERTIONS:
                    raise ValueError(f"不支持的原型步骤 {verb}")
                if verb == "expect-object":
                    if len(words) != 3 or words[2] != case.get("object"):
                        raise ValueError("对象断言须引用计划中的 object")
                    words[0] = "expect-visible-text"
                session.run(words)
                if verb in ASSERTIONS:
                    verify_pins(session.page)
                record["step_pages"].append(browser_page(design, session.page.url))
            for url in sorted(requested):
                parts = urlsplit(url)
                if parts.scheme in {"http", "https"}:
                    raise ValueError(f"原型依赖外部资源，请随设计稿交付：{parts.path}")
                if parts.scheme == "file":
                    name = browser_page(design, url)
                    record["resources"][name] = digest(local(design, name))
            step = "浏览器页面和控制台终检"
            session.run(["expect-clean"])
            browser.close()
        record["status"] = "pass"
        check_steps(design, plan, case, record)
    except Exception as exc:
        record.update(status="fail", error=f"{step}：{exc}")
        write_record(output, record)
        raise ValueError(record["error"]) from exc
    write_record(output, record)
    print(f"{key} 通过：{output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run"])
    parser.add_argument("package", type=Path)
    parser.add_argument("scenario")
    parser.add_argument("--channel", choices=["chrome", "msedge"])
    args = parser.parse_args()
    try:
        run_case(args.package, args.scenario, args.channel)
    except (ValueError, TypeError, OSError, KeyError) as exc:
        parser.exit(1, f"原型验证失败：{exc}\n")
