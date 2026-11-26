"""Bind selected competitor UI requirements to evidence inside the product package."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_path(name):
    if (not isinstance(name, str) or not name.strip() or Path(name).is_absolute()
            or name != Path(name).as_posix() or ".." in Path(name).parts or "\\" in name):
        raise ValueError(f"需要版本包内的相对文件路径：{name!r}")


def artifact(root, name):
    check_path(name)
    root = root.resolve()
    path = (root / name).resolve()
    if root not in path.parents or not path.is_file() or not path.stat().st_size:
        raise ValueError(f"包内证据缺失或为空：{name}")
    return path


def nonempty(record, fields):
    return all(isinstance(record.get(key), str) and record[key].strip() for key in fields)


def validate_browser_paths(ref):
    check_path(ref.get("recipe"))
    check_path(ref.get("baseline"))
    if not isinstance(ref.get("sha256"), str) or not re.fullmatch("[0-9a-f]{64}", ref["sha256"]):
        raise ValueError("sha256 须为已确认的基线摘要")


def validate_reference(case):
    ref = case["reference"]
    if not case["pages"] or not isinstance(ref, dict) or not nonempty(ref, ("origin",)):
        raise ValueError("须指定 UI 页面与 reference.origin（可定位的来源）")
    mode = ref.get("mode")
    if "adaptation" in ref and not nonempty(ref, ("adaptation",)):
        raise ValueError("适配决定 adaptation 须说明范围与依据")
    if mode == "pending":
        if not nonempty(ref, ("reason",)):
            raise ValueError("待证项须说明具体原因")
        return
    if mode not in ("browser", "manual"):
        raise ValueError("reference.mode 须为 browser、manual 或 pending")
    if mode == "browser":
        validate_browser_paths(ref)
        return
    check_path(ref.get("baseline"))
    if not isinstance(ref.get("sha256"), str) or not re.fullmatch("[0-9a-f]{64}", ref["sha256"]):
        raise ValueError("reference.sha256 须为已批准的原始参考证据摘要")
    kind = ref.get("kind")
    dimension = ref.get("dimension")
    if kind not in ("screenshot", "recording", "observation") or dimension not in ("appearance", "interaction", "motion"):
        raise ValueError("人工对照须填写证据 kind 和待核的 dimension")
    if kind == "screenshot" and dimension != "appearance":
        raise ValueError("单张截图仅能证明对应画面的 appearance；交互或动效须补充观察")


def page_roles(cases):
    by_page = {}
    for case in cases:
        for visit, page in zip(case["visits"], case["pages"]):
            role = visit["role"]
            by_page.setdefault(page, {}).setdefault(role, set()).add(tuple(case["roles"][role]["identity"]))
    return by_page


def visual_role(case, roles):
    """Only infer a role when the page belongs to one participant."""
    return case["prototype_match"].get("role") or (next(iter(roles)) if len(roles) == 1 else None)


def verify_shared_page_identity(root, case, role, identities):
    browser = browser_checks()
    contract = browser.recipe(artifact(root, case["prototype_match"]["recipe"]))
    selectors = browser.selectors_for(contract, "reference", {})
    observed = {(selectors[s["element"]], s["text"]) for s in contract["steps"] if "text" in s}
    if not observed.intersection(identities):
        raise ValueError(f"{case['id']} 的共用页面缺少角色 {role} 对应 identity 的文字检查点")


def validate_prototype_views(plan, root):
    """Bind each selected role, page and viewport to an observed prototype case."""
    from acceptance_plan import html_path, scenario_viewport, text

    for source in plan["sources"]:
        if not source.get("prototype_ui") and "prototype_views" not in source:
            continue
        views = source.get("prototype_views", [])
        if "prototype_views" in source and (not source.get("prototype_ui") or not isinstance(views, list) or not views):
            raise ValueError(f"{source['id']} 的 prototype_views 需与 prototype_ui 一起登记确认画面")
        for view in views:
            if (not isinstance(view, dict) or set(view) != {"role", "page", "viewport"}
                    or not text(view["role"]) or not html_path(view["page"])
                    or not isinstance(view["viewport"], list) or len(view["viewport"]) != 2
                    or any(type(n) is not int or n <= 0 for n in view["viewport"])):
                raise ValueError(f"{source['id']} 确认画面须指定 role、page 和两个正整数的 viewport")
        for ac in source["acs"]:
            related = [case for case in plan["scenarios"] if ac in case["acs"]]
            cross_role = [case for case in related if case.get("roles") and case["pages"]]
            visual = [case for case in related if "prototype_match" in case]
            owners = page_roles(cross_role)
            for case in visual:
                role = case["prototype_match"].get("role")
                if not role or case.get("roles"):
                    continue
                for page in set(case["pages"]):
                    roles = owners.get(page, {})
                    if len(roles) > 1 and role in roles:
                        verify_shared_page_identity(root, case, role, roles[role])
            for view in views:
                role, page = view["role"], view["page"]
                roles = owners.get(page, {})
                if cross_role and role not in roles:
                    raise ValueError(f"{source['id']} {ac} 的业务路径缺少确认角色 {role} 访问的页面 {page}")
                if not any(page in case["pages"] and scenario_viewport(root, case) == view["viewport"]
                           and visual_role(case, roles) == role for case in visual):
                    raise ValueError(f"{source['id']} {ac} 缺少 {role} {page} {view['viewport']} 的 prototype_match 场景")
            if views:
                continue
            for business in cross_role:
                if "prototype_match" in business:
                    continue
                visits = page_roles([business])
                if not any(not case.get("roles") and visual_role(case, visits[page]) in visits[page]
                           and ("viewport" not in business or scenario_viewport(root, case) == business["viewport"])
                           for case in visual for page in case["pages"] if page in visits):
                    raise ValueError(f"{business['id']} {ac} 缺少与业务角色、页面及视口相符的单端 prototype_match；"
                                     "共用页面请标明 prototype_match.role，部分端或多视口请在来源登记 prototype_views")


def validate_reference_scope(plan, root):
    required = {ac for source in plan["sources"] if source.get("reference_ui") for ac in source["acs"]}
    covered = set()
    prototype_acs = {ac for source in plan["sources"] if source.get("prototype_ui") for ac in source["acs"]}
    matched = set()
    for case in plan["scenarios"]:
        if "prototype_match" in case:
            ref = case["prototype_match"]
            if not case["pages"] or not isinstance(ref, dict) or not nonempty(ref, ("origin",)):
                raise ValueError(f"{case['id']} 的 prototype_match 须有 UI 页面和可定位的确认记录 origin")
            validate_browser_paths(ref)
            if "role" in ref and not nonempty(ref, ("role",)):
                raise ValueError(f"{case['id']} 的 prototype_match.role 须为已确认的角色")
            matched.update(case["acs"])
        elif case["pages"] and prototype_acs.intersection(case["acs"]) and not case.get("roles"):
            raise ValueError(f"{case['id']} 关联原型还原要求，缺少 prototype_match")
        if "reference" not in case:
            continue
        linked = required.intersection(case["acs"])
        if not linked:
            raise ValueError(f"{case['id']} 的 reference 未关联已确认的 reference_ui 来源")
        try:
            validate_reference(case)
            if ("prototype_match" in case and case["reference"].get("sha256") == case["prototype_match"]["sha256"]):
                raise ValueError("竞品与确认原型须分别采集基线")
        except ValueError as exc:
            raise ValueError(f"{case['id']}：{exc}") from exc
        covered.update(linked)
    if required - covered:
        raise ValueError("竞品 UI 约束缺少关联的 reference 场景：" + "、".join(sorted(required - covered)))
    if prototype_acs - matched:
        raise ValueError("原型还原约束缺少关联的 prototype_match 场景：" + "、".join(sorted(prototype_acs - matched)))
    validate_prototype_views(plan, root)


def baseline_file(root, case):
    ref = case["reference"]
    baseline = artifact(root, ref["baseline"])
    if file_digest(baseline) != ref["sha256"]:
        raise ValueError(f"{case['id']} 参考证据已变：{ref['baseline']}")
    if ref["mode"] == "manual":
        if ref["kind"] in ("screenshot", "recording"):
            verify_media_file(baseline, ref["kind"], ref["dimension"] == "motion")
        elif (ref["dimension"] != "appearance"
              and baseline.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".svg", ".heic"}):
            raise ValueError("单张静态图无法支持交互或动效结论，请补相应的参考证据")
    return baseline


def verify_manual_artifact(case, record, report_path):
    ref = case["reference"]
    if ref["kind"] == "observation":
        return
    if not nonempty(record, ("actual_artifact", "actual_sha256")):
        raise ValueError("人工对照缺少实际画面的 actual_artifact 或 actual_sha256")
    path = artifact(Path(report_path).parent, record["actual_artifact"])
    if file_digest(path) != record["actual_sha256"]:
        raise ValueError(f"实际画面摘要不符：{record['actual_artifact']}")
    verify_media_file(path, "either", ref["dimension"] == "motion")


def verify_media_file(path, kind, motion):
    with path.open("rb") as stream:
        head = stream.read(32)
    png = (head.startswith(b"\x89PNG\r\n\x1a\n") and head[12:16] == b"IHDR"
           and int.from_bytes(head[16:20], "big") > 0 and int.from_bytes(head[20:24], "big") > 0)
    gif = head.startswith((b"GIF87a", b"GIF89a"))
    webp = head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    photo = head[4:8] == b"ftyp" and head[8:12] in (b"avif", b"heic", b"heix", b"mif1")
    image = png or gif or webp or photo or head.startswith((b"\xff\xd8\xff", b"BM"))
    if image and kind != "recording" and not motion:
        return
    if kind == "screenshot":
        raise ValueError(f"未识别为截图：{path.name}")
    animated = gif or (webp and head[12:16] == b"VP8X" and len(head) > 20 and head[20] & 2)
    if image and not animated:
        raise ValueError(f"单张静态图无法作为录屏或动效证据：{path.name}")
    # Accept common video containers and animated GIF; limit decoding to the start of a short local clip.
    if not (animated or head[4:8] == b"ftyp" or head.startswith(b"\x1a\x45\xdf\xa3")
            or head.startswith(b"RIFF") and head[8:12] == b"AVI "):
        raise ValueError(f"未识别为截图或短录屏：{path.name}")
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe", "-select_streams", "v:0",
             "-read_intervals", "%+#128", "-show_entries", "frame=width", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("短录屏无法用本机 ffprobe 读取，请核对工具与片段") from exc
    frames = json.loads(probe.stdout or "{}").get("frames", []) if probe.returncode == 0 else []
    if sum(bool(frame.get("width")) for frame in frames) < (2 if motion or animated else 1):
        raise ValueError(f"录屏缺少可读画面，动效至少需要两帧：{path.name}")


def browser_checks():
    library = str(Path(__file__).resolve().parents[1] / "hlbrowse")
    if library not in sys.path:
        sys.path.insert(0, library)
    import reference_check
    return reference_check


def browser_differences(root, case, report, scope, *, revision=None, target=None, kind="reference"):
    ref = case[kind]
    pages = [artifact(root, "design/" + p) for p in case["pages"]] if kind == "prototype_match" else None
    return browser_checks().verify_report(
        report, ref["sha256"], scope=scope, tc=case["id"], revision=revision,
        contract_path=artifact(root, ref["recipe"]), baseline_path=artifact(root, ref["baseline"]),
        target=target, prototype_pages=pages, resource_root=root / "design")


def check_prototype_baseline(root, case, scope):
    ref = case["prototype_match"]
    path = artifact(root, ref["baseline"])
    browser = browser_checks()
    contract = artifact(root, ref["recipe"])
    baseline, recipe = browser.validate_baseline(path, ref["sha256"], contract)
    if recipe["tc"] != case["id"] or recipe["scope"] != scope:
        raise ValueError("原型基线与本场景或范围不符")
    pages = [artifact(root, "design/" + p) for p in case["pages"]]
    browser.verify_prototype_source(path, baseline, contract, pages, root / "design")


def check_reference_handoff(root, plan):
    errors = []
    for case in plan["scenarios"]:
        if "prototype_match" in case:
            try:
                check_prototype_baseline(root, case, plan["scope"])
            except (OSError, ValueError, KeyError, TypeError) as exc:
                errors.append(f"{case['id']} 原型基线：{exc}")
        if "reference" not in case:
            continue
        tc = case["id"]
        ref = case["reference"]
        try:
            if ref["mode"] == "pending":
                raise ValueError(f"竞品行为待证：{ref['reason']}")
            report = artifact(root, f"design/checks/{tc}.reference/observation.json")
            if ref["mode"] == "browser":
                issues = browser_differences(root, case, report, plan["scope"],
                                             target=artifact(root, "design/" + case["pages"][0]))
                if issues:
                    raise ValueError("；".join(issues))
            else:
                baseline_file(root, case)
                record = json.loads(report.read_text(encoding="utf-8"))
                if (not isinstance(record, dict) or record.get("scenario") != tc
                        or record.get("status") != "pass" or record.get("baseline_sha256") != ref["sha256"]
                        or not nonempty(record, ("reviewer", "when", "expected", "actual"))):
                    raise ValueError("人工对照记录须含同一场景、参考摘要、评审人、时间、预期、实测与通过结论")
                current = artifact(root, f"design/checks/{tc}.json")
                if record.get("prototype_sha256") != file_digest(current):
                    raise ValueError("原型运行记录已变或缺 prototype_sha256，请复核实际画面")
                verify_manual_artifact(case, record, report)
        except (OSError, ValueError) as exc:
            errors.append(f"{tc}：{exc}")
    if errors:
        raise ValueError("；".join(errors))
