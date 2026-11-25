"""Capture an approved UI reference and replay its checkpoints on another implementation."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import struct
import sys
from urllib.parse import unquote, urlsplit

from browse import Session, address, navigate


BASELINE = "ui-reference-baseline"
COMPARISON = "ui-reference-comparison"
BOX = {"x", "y", "width", "height"}
LOCATOR_ACTIONS = {"click": 2, "dblclick": 2, "hover": 2, "fill": 3, "select": 3, "scroll": 2, "wait": 2}
OTHER_ACTIONS = {"press": 2, "back": 1, "forward": 1, "reload": 1}
FONT_PROBES = ("system-ui", "serif", "monospace")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    data = json.loads(Path(path).read_bytes())
    require(isinstance(data, dict), f"需要 JSON 对象：{path}")
    return data


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path, directory):
    return os.path.relpath(Path(path).resolve(), directory.resolve())


def number(value):
    return type(value) in (float, int) and math.isfinite(value)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def recipe(path):
    plan = load(path)
    require(set(plan) == {"scope", "tc", "viewport", "elements", "steps"}, "契约字段应为 scope/tc/viewport/elements/steps")
    require(string(plan["scope"]) and re.fullmatch(r"TC-[0-9]+", plan["tc"]), "scope 或 TC 无效")
    view = plan["viewport"]
    require(isinstance(view, list) and len(view) == 2 and all(type(n) is int and n > 0 for n in view),
            "viewport 应为两个正整数（CSS px）")
    elements = plan["elements"]
    require(isinstance(elements, dict) and elements, "缺少 elements")
    for name, sel in elements.items():
        require(string(name) and (string(sel) or isinstance(sel, dict) and
                set(sel) == {"reference", "candidate"} and all(string(v) for v in sel.values())),
                f"无效的元素映射 {name}")
    require(isinstance(plan["steps"], list), "缺少 steps")
    names = set()
    for step in plan["steps"]:
        require(isinstance(step, dict), "步骤应为对象")
        if "action" in step:
            words = step["action"]
            require(set(step) == {"action"} and isinstance(words, list) and words and all(string(w) for w in words),
                    "action 应为非空命令数组")
            cmd = words[0]
            require({**LOCATOR_ACTIONS, **OTHER_ACTIONS}.get(cmd) == len(words), f"不支持此动作或参数个数：{cmd}")
            if cmd in LOCATOR_ACTIONS:
                require(words[1] in elements, f"动作元素未定义：{words[1]}")
            continue
        name = step.get("name")
        require(string(name) and name not in names and step.get("element") in elements, f"重复或不完整的检查点：{name}")
        names.add(name)
        require(set(step) <= {"name", "element", "visible", "focused", "value", "checked", "enabled", "text", "role", "accessible_name", "css", "box", "screenshot"}, f"{name} 有未知验收字段")
        require("value" not in step or isinstance(step["value"], str), f"{name} 的 value 应为脱敏样本字符串")
        require("text" not in step or isinstance(step["text"], str), f"{name} 的 text 应为预期可见文案")
        for key in ("role", "accessible_name"):
            require(key not in step or string(step[key]), f"{name} 的 {key} 应为非空字符串")
        require("screenshot" not in step or step["screenshot"] == "exact", f"{name} 的截图比较支持 exact")
        for field in ("visible", "focused", "checked", "enabled"):
            require(field not in step or type(step[field]) is bool, f"{name} 的 {field} 必须为布尔值")
        styles = step.get("css", [])
        require(isinstance(styles, list) and all(isinstance(s, str) and re.fullmatch(r"-*[a-z][a-z0-9-]*", s)
                for s in styles) and len(set(styles)) == len(styles), f"{name} 的 CSS 属性无效")
        box = step.get("box", {})
        require(isinstance(box, dict) and set(box) <= BOX | {"relative_to"}, f"{name} 的 box 无效")
        if "relative_to" in box:
            require(box["relative_to"] in elements and set(box) & {"x", "y"}, f"{name} 的相对坐标锚点无效")
        for dim in BOX.intersection(box):
            require(number(box[dim]) and box[dim] >= 0, f"{name} 的 {dim} 容差须为非负数字")
        require(fields(step), f"{name} 缺少验收维度")
        require(step.get("visible", True) or not (styles or box or step.get("focused") or {"enabled", "text", "role", "accessible_name"} & step.keys()), f"{name} 同时要求隐藏和可见属性")
    require(names, "契约至少需要一个检查点")
    return plan


def selectors_for(plan, side, overrides):
    require(isinstance(overrides, dict) and overrides.keys() <= plan["elements"].keys() and
            all(string(v) for v in overrides.values()), "选择器覆盖含无效名称或值")
    return {k: overrides.get(k, v if isinstance(v, str) else v[side]) for k, v in plan["elements"].items()}


def fields(step):
    return ([key for key in ("visible", "focused", "value", "checked", "text", "enabled", "role", "accessible_name") if key in step] +
            ["css." + name for name in step.get("css", [])] +
            ["box." + key for key in step.get("box", {}) if key in BOX])


def measure(page, step, sels):
    from playwright.sync_api import expect, TimeoutError as BrowserTimeout

    element = page.locator(sels[step["element"]])
    try:
        if {"visible", "box", "css", "text", "enabled", "role", "accessible_name"} & step.keys():
            element.wait_for(state="visible" if step.get("visible", True) else "hidden", timeout=1800)
        elif "value" in step or "checked" in step:
            element.wait_for(state="attached", timeout=1800)
        if step.get("focused"):
            expect(element).to_be_focused(timeout=1800)
        if "text" in step:
            expect(element).to_have_text(step["text"], use_inner_text=True, timeout=1800)
        if "enabled" in step:
            expect(element).to_be_enabled(enabled=step["enabled"], timeout=1800)
    except (BrowserTimeout, AssertionError):
        pass  # Preserve a screenshot and the actual mismatching state.
    require(element.count() <= 1, f"{step['name']} 的选择器匹配多个元素")
    exists = element.count() == 1
    visible = exists and element.is_visible()
    if visible and (step.get("box") or step.get("css")):
        # Sample settled controls even when a parent drawer positions them with a transition.
        element.evaluate("""async el => {
          const pending = [];
          for (let node = el; node; node = node.parentElement) {
            for (const animation of node.getAnimations()) {
              if (animation.playState === 'running' && Number.isFinite(animation.effect.getComputedTiming().endTime))
                pending.push(animation.finished.catch(() => {}));
            }
          }
          if (pending.length) await Promise.race([Promise.all(pending), new Promise((_, reject) =>
            setTimeout(() => reject(Error('控件动效尚未稳定，请选择可复测的结束状态')), 3000))]);
        }""")
    values = {}
    if "visible" in step:
        values["visible"] = visible
    if "focused" in step:
        values["focused"] = element.evaluate("el => el.matches(':focus')") if exists else None
    if "text" in step:
        values["text"] = element.inner_text().split() == step["text"].split() if visible else None
    if "enabled" in step:
        values["enabled"] = element.is_enabled() if visible else None
    for key in ("role", "accessible_name"):
        if key not in step:
            continue
        values[key] = None
        if visible:
            try:
                if key == "role":
                    expect(element.and_(page.get_by_role(step[key]))).to_have_count(1, timeout=1800)
                else:
                    expect(element).to_have_accessible_name(step[key], timeout=1800)
                values[key] = True
            except AssertionError:
                values[key] = False
    if "value" in step:
        if exists:
            supported = element.evaluate("""el => el.matches('textarea,select,input') &&
                !el.matches('input[type=password],input[type=hidden],input[type=file],select[multiple]')""")
            require(supported, f"{step['name']} 的 value 需要可核验的单值原生控件")
            # Return only whether the documented sample matched. The actual input stays in the page.
            values["value"] = element.evaluate("(el, sample) => el.value === sample", step["value"])
        else:
            values["value"] = None
    if "checked" in step:
        if exists:
            require(element.evaluate("el => el.matches('input[type=checkbox],input[type=radio]')"),
                    f"{step['name']} 的 checked 需要原生复选或单选控件")
        values["checked"] = element.is_checked() if exists else None
    for prop in step.get("css", []):
        values["css." + prop] = (element.evaluate("(el,p) => getComputedStyle(el).getPropertyValue(p)", prop)
                                  if visible else None)
        require("url(" not in (values["css." + prop] or "").lower(), f"{step['name']} 的 {prop} 包含资源地址，请使用截图核验")
    box = step.get("box", {})
    rect = element.bounding_box() if box and visible else None
    anchor = {"x": 0, "y": 0}
    if rect and "relative_to" in box:
        parent = page.locator(sels[box["relative_to"]])
        require(parent.count() <= 1, f"{step['name']} 的锚点不唯一")
        anchor = parent.bounding_box() if parent.count() else None
    for dim in BOX.intersection(box):
        value = rect[dim] if rect else None
        if value is not None and dim in ("x", "y"):
            value = value - anchor[dim] if anchor else None
        values["box." + dim] = value
    return {"present": exists, "values": values}


def frame_difference(reference, candidate):
    """Compare rendered pixels independently of PNG metadata and compression."""
    try:
        from PIL import Image, ImageChops
    except ImportError as exc:
        raise ValueError("精确画面对照需要安装 hlbrowse/requirements.txt 中的 Pillow") from exc
    with Image.open(reference) as original, Image.open(candidate) as current:
        return ImageChops.difference(original.convert("RGBA"), current.convert("RGBA")).getbbox(alpha_only=False)


def pixel_environment(context, browser, channel):
    # Use a separate blank page so the font sample is independent of the app's CSS and history.
    with context.new_page() as probe:
        probe.set_content("".join(f'<span id="f{i}" style="font-family:{family}">Aa09 中あ</span>'
                                  for i, family in enumerate(FONT_PROBES)))
        measured = probe.evaluate("""() => ({locale: navigator.language, dpr: devicePixelRatio,
                                             viewport: [innerWidth, innerHeight]})""")
        cdp = context.new_cdp_session(probe)
        cdp.send("DOM.enable")
        cdp.send("CSS.enable")
        root = cdp.send("DOM.getDocument")["root"]["nodeId"]
        fonts = {}
        for i, family in enumerate(FONT_PROBES):
            node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": f"#f{i}"})
            rendered = cdp.send("CSS.getPlatformFontsForNode", node)["fonts"]
            fonts[family] = sorted({font.get("postScriptName") or font["familyName"] for font in rendered})
    system = platform.system()
    release = platform.mac_ver()[0] if system == "Darwin" else platform.release()
    return dict(measured, channel=channel or "playwright-chromium", browser_version=browser.version,
                platform=f"{system} {release} {platform.machine()}", fonts=fonts)


def check_pixel_environment(env, viewport):
    labels = ("locale", "channel", "browser_version", "platform")
    require(isinstance(env, dict) and set(env) == {*labels, "dpr", "viewport", "fonts"}
            and all(string(env[key]) for key in labels), "整屏像素的渲染环境记录无效")
    require(number(env["dpr"]) and env["dpr"] > 0 and env["viewport"] == viewport
            and all(type(n) is int for n in env["viewport"]), "渲染环境的 DPR 或视口无效")
    fonts = env["fonts"]
    require(isinstance(fonts, dict) and set(fonts) == set(FONT_PROBES) and all(
        isinstance(names, list) and names and all(string(name) for name in names)
        for names in fonts.values()), "渲染环境缺少固定样本的实测字体")


class ComparisonDifferences(list):
    """Keep the public list of messages and distinguish unassessable pixels from measured differences."""

    def __init__(self, environment_issues):
        super().__init__(environment_issues)
        self.environment_count = len(environment_issues)


def verify_states(record, path, plan, approved=None, approved_dir=None):
    checks = [s for s in plan["steps"] if "name" in s]
    states = record.get("states")
    require(isinstance(states, list) and len(checks) == len(states), "检查点记录不完整")
    environment_issues = []
    if any(step.get("screenshot") == "exact" for step in checks):
        env = record.get("pixel_environment")
        if "pixel_environment" in record:
            check_pixel_environment(env, plan["viewport"])
        if approved is not None and "pixel_environment" in approved:
            require(env is not None, "候选缺少已采集基线对应的整屏像素渲染环境")
            for key, expected in approved["pixel_environment"].items():
                if env[key] != expected:
                    environment_issues.append(f"整屏像素不可判定 · {key}：基线 {expected!r}，候选 {env[key]!r}")
    differences = ComparisonDifferences(environment_issues)
    witnessed = set()
    for i, (step, state) in enumerate(zip(checks, states)):
        name = step["name"]
        require(isinstance(state, dict) and state.get("name") == name and type(state.get("present")) is bool,
                f"{name} 的检查点记录无效")
        if state["present"]:
            witnessed.add(step["element"])
        shot = path.parent / f"state-{i+1:03}.png"
        require(shot.resolve().parent == path.parent.resolve() and shot.is_file(), f"{name} 的截图不在报告目录或已缺失")
        require(state.get("screenshot") == shot.name and digest(shot) == state.get("sha256"),
                f"{name} 的截图不完整或已变更")
        with shot.open("rb") as file:
            header = file.read(24)
        require(len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n" and
                list(struct.unpack(">II", header[16:])) == plan["viewport"], f"{name} 截图与目标视口不符")
        if step.get("screenshot") == "exact" and approved is not None and not environment_issues:
            bounds = frame_difference(approved_dir / shot.name, shot)
            if bounds:
                differences.append(f"{name} · screenshot：画面像素有差异，范围 {bounds}（左、上、右、下）")
        actual = state["values"]
        require(isinstance(actual, dict) and set(actual) == set(fields(step)), f"{name} 缺少约定的读数")
        require(state["present"] or all(v is None or k == "visible" and v is False for k, v in actual.items()),
                f"{name} 对未定位的元素登记了实测值")
        for key, value in actual.items():
            if key in ("text", "value", "role", "accessible_name"):
                if value is not True:
                    label = {"text": "可见文案", "value": "控件实际值", "role": "可访问角色", "accessible_name": "可访问名称"}[key]
                    expected = repr(step[key]) if key in ("role", "accessible_name") else "约定样本"
                    differences.append(f"{name} · {key}：{label}未匹配{expected}")
                continue
            if key in ("visible", "focused", "checked", "enabled"):
                valid = type(value) is bool and value == step[key]
                expected = step[key]
            elif key.startswith("box."):
                valid = number(value)
                expected = approved["states"][i]["values"][key] if approved is not None else "已测量的坐标/尺寸"
                if approved is not None and valid:
                    valid = abs(value - expected) <= step["box"][key[4:]]
            else:
                valid = string(value)
                expected = approved["states"][i]["values"][key] if approved is not None else "已测量的 CSS 值"
                if approved is not None:
                    valid = valid and value == expected
            if not valid:
                differences.append(f"{name} · {key}：期望 {expected!r}，实测 {value!r}")
    for name in sorted({s["element"] for s in checks} - witnessed):
        differences.append(f"{name} 在所有检查点均未定位，请增加出现时的检查点以确认映射")
    return differences


def linked_path(report_file, value, expected=None):
    require(string(value) and not Path(value).is_absolute(), "引用应使用相对路径")
    path = (report_file.parent / value).resolve()
    require(expected is None or path == Path(expected).resolve(), f"引用与指定文件不符：{path.name}")
    return path


def verify_local_resources(path, record, target, resource_root):
    linked_path(path, record.get("target_file"), target)
    assets = record.get("resources")
    require(isinstance(assets, dict) and record["target_file"] in assets, "缺少被测入口的资源摘要")
    checked = set()
    for name, expected in assets.items():
        asset = linked_path(path, name)
        if resource_root is not None:
            require(asset.is_relative_to(Path(resource_root).resolve()), f"被测原型资源越出设计目录：{asset.name}")
        require(asset.is_file(), f"被测文件缺失：{asset.name}")
        require(digest(asset) == expected, f"被测文件已变更：{asset.name}")
        checked.add(asset)
    return checked


def verify_prototype_source(path, base, contract, pages, design):
    require(base.get("prototype") is True, "原型基线须由 capture --prototype 采集")
    linked_path(path, base.get("contract"), contract)
    checked = verify_local_resources(path, base, pages[0], design)
    missing = [target.name for target in pages if target.resolve() not in checked]
    require(not missing, "确认原型的采集缺少场景页面：" + "、".join(missing))


def read_capture(path, contract):
    base = load(path)
    plan = recipe(contract)
    require(base.get("kind") == BASELINE and base.get("contract_sha256") == digest(contract)
            and base.get("scope") == plan["scope"] and base.get("tc") == plan["tc"], "参考观察与契约或范围不符")
    problems = verify_states(base, path, plan)
    require(not problems, "参考观察未满足契约：" + "、".join(problems))
    return base, plan


def validate_baseline(path, expected_hash, contract):
    require(digest(path) == expected_hash, "参考观察摘要与确认记录不符")
    return read_capture(path, contract)


def capture_coverage(contract, observation):
    """Describe the verified capture and the dimensions specified for later comparison."""
    record, plan = read_capture(observation, contract)
    checks = [step for step in plan["steps"] if "name" in step]
    exact = sum(step.get("screenshot") == "exact" for step in checks)
    width, height = plan["viewport"]
    lines = [f"{plan['tc']} · {width}×{height} · 已采集 {len(checks)} 个检查点 · 契约约定 {exact} 个整屏像素对照"]
    if exact:
        env = record.get("pixel_environment")
        lines.append((f"渲染环境 · {env['channel']} {env['browser_version']} · {env['platform']} · "
                      f"{env['locale']} · DPR {env['dpr']} · 字体见 pixel_environment.fonts")
                     if env else "旧观察未记录渲染环境，按原有像素契约核验")
    for step in checks:
        dimensions = fields(step)
        if step.get("screenshot") == "exact":
            dimensions.append("整屏像素")
        lines.append(f"{step['name']} · {', '.join(dimensions)}")
    return "\n".join(lines)


def local_file(url):
    parts = urlsplit(url)
    require(parts.scheme == "file" and not parts.netloc, "预期本地原型文件")
    return Path(unquote(parts.path)).resolve()


@contextmanager
def browser_step(label):
    from playwright.sync_api import Error
    try:
        yield
    except Error as exc:
        # Chromium call logs can contain full URLs, typed form values and private DOM text.
        raise ValueError(f"{label}未完成（{type(exc).__name__}），请核对页面状态和定位器") from None


def verify_report(report_path, baseline_sha256, *, scope, tc, revision=None, contract_path=None, baseline_path=None,
                  target=None, resource_root=None, prototype_pages=None):
    """Recompute comparisons locally. Invalid evidence raises ValueError; differences are returned."""
    try:
        path = Path(report_path).resolve()
        record = load(path)
        require(record.get("kind") == COMPARISON and record.get("scope") == scope and record.get("tc") == tc and
                record.get("revision") == revision, "对照记录类型、范围、TC 或候选版本不符")
        contract = linked_path(path, record["contract"], contract_path)
        base_path = linked_path(path, record["baseline"], baseline_path)
        require(record.get("baseline_sha256") == baseline_sha256, "此次比较使用了其他参考观察")
        base, plan = validate_baseline(base_path, baseline_sha256, contract)
        require(base.get("prototype", False) is (prototype_pages is not None), "基线来源与场景约定不一致")
        require(record.get("contract_sha256") == digest(contract) and plan["scope"] == scope and plan["tc"] == tc,
                "对照报告的契约已变更")
        if target is not None:
            verify_local_resources(path, record, target, resource_root)
        if prototype_pages is not None:
            verify_prototype_source(base_path, base, contract, prototype_pages, resource_root)
            if "target_file" in record:
                tested = linked_path(path, record["target_file"])
                require(not tested.is_relative_to(Path(resource_root).resolve()), "候选报告测试了产品原型，请改测开发实现")
        if revision is not None and target is None:
            if "target_file" in record or "resources" in record:
                verify_local_resources(path, record, None, None)
            else:
                source = urlsplit(record.get("source", ""))
                require(source.scheme in {"http", "https"} and source.hostname,
                        "本地候选缺少被测入口和资源摘要，请用同一候选制品重新比较")
        return verify_states(record, path, plan, base, base_path.parent)
    except (KeyError, OSError, TypeError, UnicodeError) as exc:
        raise ValueError(f"缺少或无法读取 UI 对照证据：{exc}") from exc


def run(args):
    from playwright.sync_api import sync_playwright
    contract = args.contract.resolve()
    contract_sha = digest(contract)
    plan = recipe(contract)
    capture = args.mode == "capture"
    prototype = capture and args.prototype
    out = args.output.resolve()
    target_url = address(args.target)
    side = "reference" if capture else "candidate"
    sels = selectors_for(plan, side, load(args.selectors) if not capture and args.selectors else {})
    record = {"kind": BASELINE if capture else COMPARISON, "tc": plan["tc"], "scope": plan["scope"],
              "contract": relative(contract, out), "contract_sha256": contract_sha, "selectors": sels, "states": []}
    if not capture:
        rev = args.revision
        require(rev is None or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", rev), "revision 需要完整 Git SHA")
        base_path = args.baseline.resolve()
        base_hash = args.baseline_sha256 if args.baseline_sha256 is not None else digest(base_path)
        base, _ = validate_baseline(base_path, base_hash, contract)
        record.update(baseline=relative(base_path, out), baseline_sha256=base_hash, revision=rev)
    width, height = plan["viewport"]
    local = urlsplit(target_url).scheme == "file"
    require(not prototype or local, "产品原型基线须从版本包的本地 HTML 采集")
    if prototype:
        record["prototype"] = True
    out.mkdir(parents=True, exist_ok=False)
    if local:
        entry = local_file(target_url)
        record["source"] = entry.name
    else:
        url = urlsplit(target_url)
        require(url.scheme in {"https", "http"}, "目标须为本地文件或网页")
        host = url.hostname or ""
        if ":" in host:
            host = "[" + host + "]"
        record["source"] = f"{url.scheme}://{host}" + (f":{url.port}" if url.port else "") + url.path
    with sync_playwright() as pw:
        browser = pw.chromium.launch(chromium_sandbox=True, channel=args.channel)
        context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1,
                                      offline=local, service_workers="block", locale=args.locale)
        context.set_default_timeout(5000)
        if any(step.get("screenshot") == "exact" for step in plan["steps"]):
            with browser_step("采集整屏像素渲染环境"):
                record["pixel_environment"] = pixel_environment(context, browser, args.channel)
        files = set()
        remote = set()
        def track(request):
            scheme = urlsplit(request.url).scheme
            if scheme == "file":
                files.add(local_file(request.url))
            if scheme in ("http", "https"):
                remote.add(scheme)
        if local:
            context.on("request", track)
        page = context.new_page()
        session = Session(page)
        value_fields = {s["element"] for s in plan["steps"] if "value" in s}
        masks = [page.locator("input[type=password]"), *(page.locator(sels[name]) for name in value_fields)]
        with browser_step("打开目标页"):
            navigate(page, target_url)
        for index, step in enumerate(plan["steps"], 1):
            if "action" in step:
                words = step["action"].copy()
                label = words[0]
                if words[0] in LOCATOR_ACTIONS:
                    label += " " + words[1]
                    words[1] = sels[words[1]]
                with browser_step(f"第 {index} 步 {label}"):
                    session.run(words)
                continue
            filename = f"state-{len(record['states'])+1:03}.png"
            shot = out / filename
            with browser_step(f"第 {index} 步 {step['name']}"):
                page.wait_for_function("document.fonts.status === 'loaded'", timeout=5000)
                state = measure(page, step, sels)
                page.screenshot(path=shot, mask=masks, timeout=5000,
                                animations="disabled" if step.get("screenshot") == "exact" else "allow")
            record["states"].append(dict(state, name=step["name"], screenshot=filename, sha256=digest(shot)))
        browser.close()
    if local:
        require(not remote, "本地样本依赖外部资源，无法离线复核")
        if not capture or prototype:
            record["target_file"] = relative(entry, out)
            record["resources"] = {relative(f, out): digest(f) for f in sorted(files | {entry})}
    require(digest(contract) == contract_sha, "运行中契约发生变化")
    report = out / "observation.json"
    differences = (verify_states(record, report, plan) if capture else
                   verify_states(record, report, plan, base, base_path.parent))
    if capture:
        require(not differences, "参考观察未满足契约：" + "、".join(differences))
    record["differences"] = differences
    report.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(report)
    if not capture and "pixel_environment" in record and "pixel_environment" not in base:
        print("旧观察未记录渲染环境，按原有像素契约核验")
    if capture:
        print("sha256=" + digest(report))
    for message in differences:
        print(message)
    return 1 if differences else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    coverage = modes.add_parser("coverage", help="核对已采集的原型或参考报告并按视口列出各检查点的约定维度")
    coverage.add_argument("contract", type=Path)
    coverage.add_argument("observation", type=Path)
    for mode in ("capture", "compare"):
        child = modes.add_parser(mode)
        child.add_argument("contract", type=Path)
        child.add_argument("target")
        child.add_argument("output", type=Path, help="本次运行的新目录")
        child.add_argument("--channel", choices=["chrome", "msedge"])
        child.add_argument("--locale", help="浏览器区域设置，例如 zh-CN。省略时使用浏览器默认值")
        if mode == "capture":
            child.add_argument("--prototype", action="store_true", help="记录供开发还原的本地产品原型及资源摘要")
        else:
            child.add_argument("--baseline", required=True, type=Path)
            child.add_argument("--baseline-sha256", help="产品确认时另存的参考观察摘要")
            child.add_argument("--revision")
            child.add_argument("--selectors", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "coverage":
            print(capture_coverage(args.contract, args.observation))
            return 0
        try:
            from playwright.sync_api import Error
        except ImportError:
            parser.exit(2, "需要按 hlbrowse/SKILL.md 安装 Playwright\n")
        try:
            return run(args)
        except Error as exc:
            parser.exit(2, f"浏览器初始化或会话结束失败（{type(exc).__name__}）\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"UI 对照证据无效：{exc}\n")


if __name__ == "__main__":
    sys.exit(main())
