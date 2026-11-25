"""Load the product acceptance plan shared by handoff and candidate QA."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit

from reference_evidence import artifact, validate_reference_scope


SPEC_FILES = ("prd.md", "test-cases.md", "non-functional-requirements.md")


def spec_digest(directory, expected=None):
    """Bind each approved filename to the SHA-256 of its exact bytes."""
    digest = hashlib.sha256()
    for name in SPEC_FILES:
        content_digest = hashlib.sha256((directory / name).read_bytes()).digest()
        digest.update(name.encode("ascii") + b"\0" + content_digest)
    value = digest.hexdigest()
    if expected is not None and value != expected:
        raise ValueError("spec_sha256 与产品交接基线不符，请核对 PRD、测试用例和非功能要求")
    return value


def text(value):
    return isinstance(value, str) and bool(value.strip())


def records(plan, name, prefix):
    rows = plan.get(name)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{name} 应有至少一项")
    seen = set()
    for row in rows:
        key = row.get("id") if isinstance(row, dict) else None
        if not isinstance(key, str) or not re.fullmatch(prefix + r"-[0-9]+", key) or key in seen:
            raise ValueError(f"{name} 编号无效或重复：{key!r}")
        seen.add(key)
    return rows


def sources(plan):
    if not isinstance(plan, dict) or not text(plan.get("scope")):
        raise ValueError("acceptance-plan.json 缺少 scope")
    rows = records(plan, "sources", "REQ")
    for row in rows:
        if not text(row.get("origin")) or not text(row.get("text")):
            raise ValueError(f"{row['id']} 须保留用户原始约束与确认来源")
        for flag in ("reference_ui", "prototype_ui", "cross_role"):
            if flag in row and type(row[flag]) is not bool:
                raise ValueError(f"{row['id']} 的 {flag} 须为布尔值")
    return rows


def acs(row):
    values = row.get("acs")
    if (not isinstance(values, list) or
            any(not isinstance(v, str) or not re.fullmatch(r"AC-[0-9]+", v) for v in values) or
            len(set(values)) != len(values)):
        raise ValueError(f"{row['id']} 的 acs 应为唯一 AC 编号的数组")
    return set(values)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"无法读取 {path}：{exc}") from exc


def scenario_viewport(root, case):
    """Resolve the CSS viewport the project selected for this UI scenario."""
    views = [case["viewport"]] if "viewport" in case else []
    ref = case.get("reference", {})
    if not isinstance(ref, dict):
        raise ValueError(f"{case['id']} 的 reference 须为对象")
    if ref.get("mode") == "browser":
        contract = read_json(artifact(root, ref.get("recipe")))
        views.append(contract.get("viewport") if isinstance(contract, dict) else None)
    if "prototype_match" in case:
        match = case["prototype_match"]
        if not isinstance(match, dict):
            raise ValueError(f"{case['id']} 的 prototype_match 须为对象")
        contract = read_json(artifact(root, match.get("recipe")))
        views.append(contract.get("viewport") if isinstance(contract, dict) else None)
    if not views:
        return None
    for view in views:
        if (not case["pages"] or not isinstance(view, list) or len(view) != 2
                or any(type(size) is not int or size <= 0 for size in view)):
            raise ValueError(f"{case['id']} 的 viewport 须为 UI 页面的两个正整数（CSS px 宽、高）")
        if view != views[0]:
            raise ValueError(f"{case['id']} 的 viewport 与对照契约不一致")
    return views[0]


def html_path(value):
    return (text(value) and value == Path(value).as_posix() and not Path(value).is_absolute()
            and ".." not in Path(value).parts and "\\" not in value and Path(value).suffix == ".html")


def role_entry_paths(case):
    return {urlsplit(config["entry"]).path for config in case.get("roles", {}).values()}


def result_map(value):
    return isinstance(value, dict) and bool(value) and all(text(k) and text(v) for k, v in value.items())


def validate_roles(case):
    if "roles" not in case:
        if "visits" in case:
            visits = case["visits"]
            if (len(case["pages"]) < 2 or not isinstance(visits, list) or len(visits) != len(case["pages"])
                    or not all(isinstance(v, dict) and set(v) == {"expect"} and result_map(v["expect"]) for v in visits)):
                raise ValueError(f"{case['id']} 同角色 visits 须按 pages 的每次访问登记 expect 业务结果")
        return
    key, roles, visits = case["id"], case.get("roles"), case.get("visits")
    if not isinstance(roles, dict) or len(roles) < 2 or not text(case.get("object")):
        raise ValueError(f"{key} 跨角色场景须声明至少两个 roles 和同一业务 object")
    identities = set()
    for role, config in roles.items():
        if not text(role) or not isinstance(config, dict) or not text(config.get("entry")):
            raise ValueError(f"{key} 角色 {role} 缺少 entry")
        url = urlsplit(config["entry"])
        if url.scheme or url.netloc or not html_path(url.path):
            raise ValueError(f"{key} 角色 {role} 入口须为 design/ 内的 HTML，可附查询串")
        identity = config.get("identity")
        if not isinstance(identity, list) or len(identity) != 2 or not all(map(text, identity)):
            raise ValueError(f"{key} 角色 {role} 的 identity 须为 [身份控件, 可见文字]")
        marker = (url.path, *identity)
        if marker in identities:
            raise ValueError(f"{key} 同页角色 {role} 需要可区分的界面身份标识")
        identities.add(marker)
    if not isinstance(visits, list) or len(visits) != len(case["pages"]):
        raise ValueError(f"{key} 的 visits 需与 pages 逐项对应")
    used = set()
    for index, visit in enumerate(visits, 1):
        role = visit.get("role") if isinstance(visit, dict) else None
        if not text(role) or role not in roles or not text(visit.get("object_at")):
            raise ValueError(f"{key} 第 {index} 次访问须指定已登记的角色与同单标识控件 object_at")
        expected = visit.get("expect")
        if (not result_map(expected)
                or not (expected.keys() - {visit["object_at"], roles[role]["identity"][0]})):
            raise ValueError(f"{key} 第 {index} 次访问须登记业务结果 expect（控件与预期可见文字）")
        used.add(role)
    if len(used) < 2:
        raise ValueError(f"{key} 的 visits 须在至少两个不同角色处核对同一业务")


class RoleOutcomeMismatch(ValueError):
    """A complete role observation shows a different business outcome."""


def check_visit_observations(case, observations):
    """Compare all visits in one run, including returns to an earlier page."""
    pages = case["pages"]
    if not isinstance(observations, list) or len(observations) != len(pages):
        raise ValueError(f"{case['id']} 须提供全部 {len(pages)} 次访问的实测结果：{' → '.join(pages)}")
    for index, (page, actual) in enumerate(zip(pages, observations), 1):
        visit = case["visits"][index - 1] if "visits" in case else {}
        role = visit.get("role")
        label = f"{case['id']} 第 {index} 次访问 " + (f"{role}/{page}" if role else page)
        if not isinstance(actual, dict):
            raise ValueError(f"{label} 缺观测")
        required = {"page": page}
        if role:
            required.update(role=role, identity=case["roles"][role]["identity"][1])
        for field, value in required.items():
            if actual.get(field) != value:
                raise ValueError(f"{label} 的 {field} 应为 {value!r}，实测 {actual.get(field)!r}")
        expected = visit.get("expect", actual.get("expect"))
        results = actual.get("results")
        if not result_map(expected) or not isinstance(results, dict) or results.keys() != expected.keys():
            raise ValueError(f"{label} 缺少逐页业务预期或对应的实测结果控件")
        if not all(isinstance(value, str) for value in results.values()):
            raise ValueError(f"{label} 的业务观测须为实际可见文字")
        if "object" in case and not text(actual.get("object")):
            raise ValueError(f"{label} 缺少同单标识")
        if "object" in case and actual["object"] != case["object"]:
            raise RoleOutcomeMismatch(f"{label} 对象应为 {case['object']!r}，实测 {actual['object']!r}")
        for selector, value in expected.items():
            if results[selector] != value:
                raise RoleOutcomeMismatch(f"{label} 的 {selector} 应为 {value!r}，实测 {results[selector]!r}")


check_role_observations = check_visit_observations


def validate_comparison_scope(root, case, separate_assertions):
    key = case["id"]
    contracts = [case[k] for k in ("reference", "prototype_match") if k in case]
    if "visual_only" in case and type(case["visual_only"]) is not bool:
        raise ValueError(f"{key} 的 visual_only 须为布尔值")
    if case.get("visual_only") and (not contracts or len(case["pages"]) != 1 or "object" in case or separate_assertions):
        raise ValueError(f"{key} 的 visual_only 须为单页纯 UI 对照；同单、跨页及独立业务断言需另验")
    for contract in contracts:
        if "business_checkpoints" not in contract:
            continue
        mapping = contract["business_checkpoints"]
        if (case.get("visual_only") or separate_assertions or contract.get("mode", "browser") != "browser"
                or not isinstance(mapping, dict) or set(mapping) != set(case["acs"])):
            raise ValueError(f"{key} 的 business_checkpoints 须关联本场景全部 AC；独立业务断言须由业务测试验证")
        from reference_evidence import browser_checks
        steps = browser_checks().recipe(artifact(root, contract["recipe"]))["steps"]
        if "object" in case and not any(case["object"] in (s.get("text"), s.get("value")) for s in steps):
            raise ValueError(f"{key} 的业务对照须在契约中实际断言同一对象 {case['object']}")
        acted, outcomes = False, set()
        for step in steps:
            if "action" in step:
                if step["action"][0] != "wait":
                    acted = True
            elif acted and step.keys() & {"text", "value", "checked", "enabled", "visible"}:
                outcomes.add(step["name"])
        for ac, names in mapping.items():
            if (not isinstance(names, list) or not names or not all(map(text, names))
                    or len(set(names)) != len(names) or set(names) - outcomes):
                raise ValueError(f"{key} {ac} 的 business_checkpoints 须指向契约中操作后的结果断言")


def load_plan(path):
    """Return the validated plan, leaving source confirmation to the product owner."""
    plan = read_json(path)
    required = set()
    for row in sources(plan):
        ids = acs(row)
        waiver = row.get("waiver")
        if ids:
            if waiver is not None:
                raise ValueError(f"{row['id']} 同时声明了验收条件和豁免")
        elif not isinstance(waiver, dict) or not all(text(waiver.get(k)) for k in ("reason", "origin")):
            raise ValueError(f"{row['id']} 缺少对应 AC 或确认豁免的 reason、origin")
        required.update(ids)
    covered = set()
    role_covered = set()
    for row in records(plan, "scenarios", "TC"):
        ids = acs(row)
        if not ids or ids - required:
            raise ValueError(f"{row['id']} 须关联有效来源中的 AC，实际为 {sorted(ids)}")
        if "required_variants" in row:
            variants = row["required_variants"]
            if (not isinstance(variants, list) or not variants
                    or any(not text(v) or not v.isprintable() or v != v.strip() for v in variants)
                    or len(set(variants)) != len(variants)):
                raise ValueError(f"{row['id']} 的 required_variants 须为非空且唯一的稳定用例标识数组")
        pages = row.get("pages")
        if not isinstance(pages, list) or not all(map(html_path, pages)):
            raise ValueError(f"{row['id']} 的 pages 须为相对 design/ 的 HTML 路径列表（无 UI 用 []）")
        for field in ("object", "no_object_reason"):
            if field in row and not text(row[field]):
                raise ValueError(f"{row['id']} 的 {field} 须为非空文字")
        if "object" in row and "no_object_reason" in row:
            raise ValueError(f"{row['id']} 同时指定了 object 与 no_object_reason")
        if len(set(pages)) > 1 and not (row.get("object") or row.get("no_object_reason")):
            raise ValueError(f"{row['id']} 跨页须声明 object，或以 no_object_reason 说明本场景无需跟踪实体的原因")
        validate_roles(row)
        if "roles" in row:
            role_covered.update(ids)
        covered.update(ids)
    if required - covered:
        raise ValueError("已确认 AC 缺少必测场景：" + "、".join(sorted(required - covered)))
    for row in plan["sources"]:
        if row.get("cross_role") and (missing := acs(row) - role_covered):
            raise ValueError(f"{row['id']} 的跨角色约束缺少多角色 TC：" + "、".join(sorted(missing)))
    validate_reference_scope(plan, Path(path).parent)
    assertions = plan.get("case_assertions", {})
    if not isinstance(assertions, dict):
        raise ValueError("case_assertions 须按 TC 登记")
    for row in plan["scenarios"]:
        validate_comparison_scope(Path(path).parent, row, row["id"] in assertions)
        if "viewport" in row or "prototype_match" in row:
            scenario_viewport(Path(path).parent, row)
    return plan


def source_digest(plan):
    # Only confirmed inputs are frozen here. AC and TC are assigned in later steps.
    inputs = sorted((row["id"], row["origin"], row["text"]) for row in sources(plan))
    payload = [plan["scope"], inputs]
    selected = sorted(row["id"] for row in plan["sources"] if row.get("reference_ui"))
    if selected:
        payload.append(selected)
    prototypes = sorted(row["id"] for row in plan["sources"] if row.get("prototype_ui"))
    if prototypes:
        payload.append({"prototype_ui": prototypes})
    views = sorted((row["id"], json.dumps(row["prototype_views"], sort_keys=True, ensure_ascii=False))
                   for row in plan["sources"] if "prototype_views" in row)
    if views:
        payload.append({"prototype_views": views})
    roles = sorted(row["id"] for row in plan["sources"] if row.get("cross_role"))
    if roles:
        payload.append({"cross_role": roles})
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def handoff_seal(digest, version=3):
    prefix = f"hlpm-v{version}"
    return prefix + " " + hashlib.sha256((prefix + "\0" + digest).encode("ascii")).hexdigest()


def source_format(path, plan):
    seal = path.with_name("acceptance-sources.sha256")
    digest = source_digest(plan)
    actual = seal.read_text(encoding="utf-8").strip() if seal.is_file() else ""
    for version in (3, 2):
        if actual == handoff_seal(digest, version):
            return version
    if actual == digest:
        return 1
    raise ValueError("来源清单缺少确认基线或与基线不一致：复核原始需求及范围，再登记 freeze-sources")


def verify_sources(path, plan):
    """Verify the confirmed inputs and retain the original per-AC-table boolean API."""
    return source_format(path, plan) >= 2


def freeze(path, renew):
    digest = source_digest(read_json(path))
    seal = path.with_name("acceptance-sources.sha256")
    if seal.exists():
        actual = seal.read_text(encoding="utf-8").strip()
        if actual == handoff_seal(digest) or (not renew and actual in (digest, handoff_seal(digest, 2))):
            return
        if not renew:
            raise ValueError("原始约束发生变化；回核原件并记录新确认后才可用 --renew")
    with NamedTemporaryFile(mode="w", encoding="ascii", dir=seal.parent, delete=False) as pending:
        pending.write(handoff_seal(digest) + "\n")
        temporary = Path(pending.name)
    try:
        if renew:
            temporary.replace(seal)
        else:
            seal.hardlink_to(temporary)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["freeze-sources"])
    parser.add_argument("plan", type=Path)
    parser.add_argument("--renew", action="store_true", help="已复核并重新确认本次来源变更")
    args = parser.parse_args()
    try:
        freeze(args.plan, args.renew)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
    print("原始约束已登记")
