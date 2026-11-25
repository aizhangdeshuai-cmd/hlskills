"""Reconcile confirmed product scenarios against actual run artifacts."""
import hashlib
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET


TC = re.compile(r"(?<![A-Za-z0-9])TC-[0-9]+(?![A-Za-z0-9])")
SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
STATES = ("failed", "invalid_evidence", "skipped", "not_run", "passed")
SKIPPED_STATUSES = {"notrun", "disabled", "skipped"}
FAILURE_TAGS = {"error", "failure", "rerunFailure", "rerunError"}
FLAKY_TAGS = {"flakyFailure", "flakyError"}


def combined_status(statuses):
    return next((status for status in STATES if status in statuses), "not_run")


def is_skipped(case):
    return case.find("skipped") is not None or (case.get("status") or "").lower() in SKIPPED_STATUSES


def load_object(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} 应包含 JSON 对象")
    return data


def properties(element, identity):
    found = {}
    for p in element.findall("./properties/property"):
        key, value = p.get("name"), p.get("value", p.text)
        if key in identity and key in found and found[key] != value:
            raise ValueError(f"JUnit 的 {key} 声明冲突")
        found[key] = value
    return found


def viewport_metadata(data):
    if "viewport" not in data:
        return {}
    value = data["viewport"]
    valid = isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", value)
    return {"viewport": value if valid else None}


def viewport_gaps(rows, expected, required_variants):
    # A service-level helper may share the TC. Only browser checks declare a viewport.
    by_check = {}
    for row in rows:
        if "viewport" in row:
            identity = (row.get("classname"), row["case"], row.get("variant"))
            by_check.setdefault(identity, set()).add(row["viewport"])
    gaps = [f"{'.'.join(filter(None, identity))} 缺约定视口 {expected} 的通过记录"
            for identity, observed in by_check.items() if expected not in observed]
    for variant in required_variants:
        if any(row.get("variant") == variant for row in rows) and not any(k[2] == variant for k in by_check):
            gaps.append(f"{variant} 缺约定视口 {expected} 的候选实测记录")
    return gaps if by_check or gaps else [f"缺约定视口 {expected} 的候选实测记录"]


def identity_errors(metadata, expected, *, complete=False):
    mismatched = {key for key, value in expected.items() if key in metadata and (value is None or metadata[key] != value)}
    if complete:
        required = expected.keys() if expected["spec_sha256"] is not None else {"scope", "revision"}
        mismatched.update(required - metadata.keys())
    return mismatched


def junit_rows(path, identity, with_diagnostics=False, *, cases=None):
    if with_diagnostics:
        from acceptance_summary import junit_diagnostic
    root = ET.parse(path).getroot()
    if root.tag not in ("testsuite", "testsuites"):
        raise ValueError("需要 JUnit testsuite 或 testsuites")
    rows = []
    problems = []

    def visit(suite, metadata, parent_errors):
        metadata = {**metadata, **properties(suite, identity)}
        suite_errors = parent_errors | identity_errors(metadata, identity)
        testcases = suite.findall("testcase")
        contained = suite.findall(".//testcase")
        if "tests" in suite.attrib and int(suite.get("tests")) != len(contained):
            problems.append(f"{suite.get('name', '<suite>')}: 测试总数与实际用例记录不符")
        for field, tag in (("errors", "error"), ("failures", "failure")):
            if field in suite.attrib and int(suite.get(field)) > sum(c.find(tag) is not None for c in contained):
                problems.append(f"{suite.get('name', '<suite>')}: 含未能定位到用例的 {field}")
        for field in ("skipped", "disabled"):
            if field in suite.attrib and int(suite.get(field)) > sum(is_skipped(c) for c in contained):
                problems.append(f"{suite.get('name', '<suite>')}: 含未能定位到用例的 {field}")
        invalid_identity = set()
        for case in testcases:
            case_metadata = properties(case, identity)
            errors = suite_errors | identity_errors({**metadata, **case_metadata}, identity, complete=True)
            invalid_identity.update(errors)
            identity_ok = not errors
            name = case.get("name", "").strip()
            failure = next((child for child in case if child.tag in FAILURE_TAGS), None)
            if failure is None:
                failure = next((child for child in case if child.tag in FLAKY_TAGS), None)
            result = (case.get("status") or "").lower()
            if failure is not None:
                status = "failed"
            elif is_skipped(case):
                status = "skipped"
            elif name and result in {"", "run", "passed", "success", "completed"}:
                status = "passed"
            else:
                status = "invalid_evidence"
            explicit = case_metadata.get("scenario")
            ids = list(dict.fromkeys(TC.findall(name)))
            if explicit is not None and explicit not in ids:
                ids.append(explicit)
            if len(ids) == 1 and isinstance(ids[0], str) and TC.fullmatch(ids[0]):
                evidence = {"case": name, **viewport_metadata(case_metadata if "viewport" in case_metadata else metadata)}
                if identity_ok and cases and cases.get(ids[0], {}).get("required_variants"):
                    native_id = f"{case.get('classname', '')}::{name}"
                    variant = case_metadata.get("variant", native_id)
                    if variant in cases[ids[0]]["required_variants"]:
                        evidence["variant"] = variant
                if identity_ok and failure is not None and failure.tag in FLAKY_TAGS and not is_skipped(case):
                    evidence["flaky"] = True
                for field in ("page_visits", "role_visits"):
                    if field in case_metadata:
                        evidence[field] = case_metadata[field]
                if "viewport" in evidence:
                    evidence["classname"] = case.get("classname") or case.get("file") or suite.get("name") or ""
                if with_diagnostics and identity_ok and failure is not None:
                    evidence.update(junit_diagnostic(case, failure, case_metadata))
                rows.append((ids[0], status if identity_ok else "invalid_evidence", evidence))
            elif ids or status in {"failed", "invalid_evidence"}:
                problems.append(f"无法归入场景的测试 {name!r}（{status}）")
        if invalid_identity:
            problems.append(f"{suite.get('name', '<suite>')}: 执行记录的 {', '.join(sorted(invalid_identity))} 缺失或不匹配")
        for child in suite:
            if child.tag in ("testsuite", "testsuites"):
                visit(child, metadata, suite_errors)

    visit(root, {}, set())
    if not root.findall(".//testcase"):
        raise ValueError("JUnit 报告没有任何 testcase")
    return rows, problems


def json_rows(path, identity, package, cases, with_diagnostics=False):
    report = load_object(path)
    scope, candidate = identity["scope"], identity["revision"]
    if report.get("kind") == "ui-reference-comparison":
        from reference_evidence import browser_differences

        key = report.get("tc")
        case = cases.get(key) if isinstance(key, str) else None
        if not case:
            raise ValueError(f"{key} 没有已约定的浏览器对照")
        kinds = [kind for kind in ("reference", "prototype_match") if kind in case
                 and (kind != "reference" or case[kind]["mode"] == "browser")]
        kind = next((k for k in kinds if case[k]["sha256"] == report.get("baseline_sha256")), None)
        if kind is None:
            error = f"{key} 的报告未使用约定基线"
            return [(key, "invalid_evidence", {"case": key})], [error], {}
        try:
            if mismatched := identity_errors(report, identity):
                raise ValueError(f"候选对照记录的 {', '.join(sorted(mismatched))} 与确认基线不匹配")
            differences = browser_differences(package, case, path, scope, revision=candidate, kind=kind)
        except (ValueError, OSError) as exc:
            return [(key, "invalid_evidence", {"case": key, "comparison": kind})], [str(exc)], {(key, kind): [str(exc)]}
        environment = differences[:differences.environment_count]
        measured = differences[differences.environment_count:]
        status = "passed"
        if measured:
            status = "failed"
        elif environment:
            status = "invalid_evidence"
        observation = {"case": key, "comparison": kind}
        if status == "passed" and "business_checkpoints" in case[kind]:
            observation["business_checkpoints"] = case[kind]["business_checkpoints"]
        if differences and with_diagnostics:
            from acceptance_summary import excerpt
            source = "确认原型" if kind == "prototype_match" else "竞品参考"
            notes = [f"{source}有 {len(measured)} 项差异，首项为 {excerpt(measured[0])}"] if measured else []
            if environment:
                notes.append(excerpt(environment[0]))
            observation["diagnostic"] = "。".join(notes)
        return [(key, status, observation)], [], {(key, kind): differences}

    header_errors = identity_errors(report, identity, complete=True)
    records = report.get("records")
    if report.get("kind") != "manual" or not isinstance(records, list) or not records:
        raise ValueError("人工执行报告需 kind=manual 与非空 records")
    rows, comparisons, errors = [], {}, []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not TC.fullmatch(record["id"]):
            raise ValueError("人工执行记录缺少场景编号")
        key = record["id"]
        mismatched = header_errors | identity_errors(record, identity)
        if mismatched:
            errors.append(f"{key} 人工执行记录的 {', '.join(sorted(mismatched))} 缺失或不匹配")
            rows.append((key, "invalid_evidence", {"case": key}))
            continue
        status = {"pass": "passed", "fail": "failed", "skipped": "skipped"}.get(record.get("status"))
        fields = ("executor", "when", "expected", "actual")
        if not status or not all(isinstance(record.get(k), str) and record[k].strip() for k in fields):
            status = "invalid_evidence"
        if "baseline_sha256" in record:
            from reference_evidence import baseline_file, verify_manual_artifact

            case = cases.get(key)
            if not case or case.get("reference", {}).get("mode") != "manual":
                raise ValueError(f"{key} 没有已约定的人工竞品对照")
            try:
                baseline_file(package, case)
                if record["baseline_sha256"] != case["reference"]["sha256"]:
                    raise ValueError("人工对照使用的竞品证据与产品基线不符")
                if (status == "passed" and case.get("viewport")
                        and record.get("viewport") != "x".join(map(str, case["viewport"]))):
                    raise ValueError("人工对照记录的实测 viewport 缺失或与约定视口不符")
                verify_manual_artifact(case, record, path)
            except (ValueError, OSError) as exc:
                status = "invalid_evidence"
                errors.append(f"{key}: {exc}")
            comparisons.setdefault((key, "reference"), []).append(record.get("actual"))
        observation = {"case": key, **viewport_metadata(record)}
        if "baseline_sha256" in record:
            observation["comparison"] = "reference"
        for field in ("page_visits", "role_visits"):
            if field in record:
                observation[field] = record[field]
        rows.append((key, status, observation))
    return rows, errors, comparisons


def evaluate(manifest_path, plan_path, candidate, expected_digest, expected_spec=None, *, with_diagnostics=False):
    # Installed skills share the same hlskills root, even when invoked through links.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hlpm"))
    from acceptance_plan import (RoleOutcomeMismatch, check_visit_observations, load_plan,
                                 scenario_viewport, spec_digest)

    if not SHA.fullmatch(candidate):
        raise ValueError("--candidate 需要完整 Git 提交 SHA")
    digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
    if digest != expected_digest:
        raise ValueError("验收计划 sha256 与产品交接基线不符")
    if expected_spec is None and plan_path.with_name("acceptance-sources.sha256").exists():
        raise ValueError("验收产品交付包需要交接记录中的 --spec-sha256")
    if expected_spec is not None:
        spec_digest(plan_path.parent, expected_spec)
    plan = load_plan(plan_path)
    if hashlib.sha256(plan_path.read_bytes()).hexdigest() != digest:
        raise ValueError("验收计划在读取期间已变化")
    manifest = load_object(manifest_path)
    scope = plan["scope"]
    identity = {"scope": scope, "revision": candidate, "plan_sha256": digest, "spec_sha256": expected_spec}
    if manifest.get("scope") != scope:
        raise ValueError("执行清单 scope 与确认计划不同")
    reports = manifest.get("reports")
    if not isinstance(reports, list) or any(not isinstance(p, str) or not p.strip() for p in reports):
        raise ValueError("执行清单需 reports 路径数组；没有运行记录时使用 []")

    cases = {s["id"]: s for s in plan["scenarios"]}
    visit_cases = {key: ("role_visits" if "roles" in case else "page_visits")
                   for key, case in cases.items() if "roles" in case or len(case["pages"]) > 1}
    visit_viewports = {key: scenario_viewport(plan_path.parent, cases[key]) for key in visit_cases}
    evidence = {key: [] for key in cases}
    comparison_runs = {(key, kind): [] for key, case in cases.items()
                       for kind in ("reference", "prototype_match") if kind in case}
    problems = []
    seen = set()
    for filename in reports:
        path = manifest_path.parent / filename
        try:
            canonical = path.resolve()
            if canonical in seen:
                raise ValueError("执行清单重复引用此文件")
            seen.add(canonical)
            if path.suffix.lower() == ".xml":
                rows, errors = junit_rows(path, identity, with_diagnostics, cases=cases)
            elif path.suffix.lower() == ".json":
                rows, errors, comparisons = json_rows(path, identity, plan_path.parent, cases, with_diagnostics)
                for (key, kind), details in comparisons.items():
                    status = combined_status({s for tc, s, row in rows if tc == key and row.get("comparison") == kind})
                    comparison_runs[key, kind].append({"artifact": filename, "status": status, "details": details})
            else:
                raise ValueError("支持 JUnit XML、人工执行 JSON 或竞品对照 observation.json")
            problems.extend(f"{filename}: {error}" for error in errors)
            if not any(key in evidence for key, _, _ in rows):
                problems.append(f"{filename}: 未包含本期计划的场景")
        except (ValueError, OSError, ET.ParseError) as error:
            problems.append(f"{filename}: {error}")
            continue
        for key, status, observation in rows:
            field = visit_cases.get(key)
            for other in ("role_visits", "page_visits"):
                if other != field:
                    observation.pop(other, None)
            if field in observation:
                visits = observation.pop(field)
                if status == "passed":
                    try:
                        if path.suffix.lower() == ".xml":
                            visits = json.loads(visits or "null")
                        viewport = visit_viewports[key]
                        if viewport and observation.get("viewport") != "x".join(map(str, viewport)):
                            raise ValueError(f"{key} {field} 缺少约定视口 {viewport[0]}x{viewport[1]} 的实测")
                        check_visit_observations(cases[key], visits)
                    except RoleOutcomeMismatch as exc:
                        status = "failed"
                        problems.append(f"{filename}: {exc}")
                    except ValueError as exc:
                        status = "invalid_evidence"
                        problems.append(f"{filename}: {key} {field} 证据无效：{exc}")
                    else:
                        observation["verified_visits"] = len(visits)
            if key in evidence:
                evidence[key].append({"status": status, "artifact": filename, **observation})
            elif status in {"failed", "invalid_evidence"}:
                problems.append(f"{filename}: 计划外场景 {key} 为 {status}，须核对")
    groups = {label: [] for label in STATES}
    summaries = {"reference": {}, "prototype_match": {}}
    viewports = {}
    for key, case in cases.items():
        browser_contract = "prototype_match" in case or case.get("reference", {}).get("mode") == "browser"
        if (browser_contract and case.get("required_variants")) or (not browser_contract and "viewport" in case):
            viewports[key] = "x".join(map(str, scenario_viewport(plan_path.parent, case)))
    for key, observations in evidence.items():
        statuses = {row["status"] for row in observations}
        required = cases[key].get("required_variants", [])
        if key in visit_cases and statuses == {"passed"}:
            observed_variants = {row.get("variant") for row in observations}
            for variant in [v for v in required if v in observed_variants] or [None]:
                if not any(row.get("verified_visits") and (variant is None or row.get("variant") == variant)
                           for row in observations):
                    statuses.add("invalid_evidence")
                    label = f"{key} {variant}" if variant else key
                    problems.append(f"{label}: 缺候选同一次办理的完整 {visit_cases[key]} 实测记录")
        if (statuses == {"passed"} and not cases[key].get("visual_only")
                and all(row.get("comparison") and not row.get("business_checkpoints") and not row.get("verified_visits")
                        for row in observations)):
            statuses.add("not_run")
            problems.append(f"{key}: 对照通过，缺候选业务结果的执行记录或已约定的业务检查点")
        if key in viewports and statuses == {"passed"}:
            gaps = viewport_gaps(observations, viewports[key], required)
            if gaps:
                statuses.add("invalid_evidence")
                problems.extend(f"{key}: {gap}" for gap in gaps)
        for kind in summaries:
            if (key, kind) not in comparison_runs:
                continue
            ref = cases[key][kind]
            runs = comparison_runs[key, kind]
            reference_status = combined_status({run["status"] for run in runs})
            mode = "browser" if kind == "prototype_match" else ref["mode"]
            summary = {"mode": mode, "status": reference_status, "runs": runs}
            if "adaptation" in ref:
                summary["adaptation"] = ref["adaptation"]
            if not runs:
                summary["reason"] = ("缺确认原型的候选对照记录" if kind == "prototype_match"
                                     else ref.get("reason") or f"缺 {mode} 候选对照记录")
                problems.append(f"{key}: {summary['reason']}")
            summaries[kind][key] = summary
            statuses.add(reference_status)
        missing = set(required) - {row.get("variant") for row in observations}
        if missing:
            statuses.add("not_run")
            problems.append(f"{key}: 缺少必测变体的候选记录：" + "、".join(sorted(missing)))
        groups[combined_status(statuses)].append(key)
    blockers = [key for state in ("failed", "invalid_evidence", "skipped", "not_run")
                for key in groups[state]]
    return {
        "mode": "acceptance", "acceptance": "blocked" if blockers or problems else "passed",
        "scope": scope, "revision": candidate, "plan_sha256": digest, "planned": len(evidence),
        **({"spec_sha256": expected_spec} if expected_spec is not None else {}),
        **({"reference_checks": summaries["reference"]} if summaries["reference"] else {}),
        **({"prototype_checks": summaries["prototype_match"]} if summaries["prototype_match"] else {}),
        **groups, "blocking_checks": blockers, "report_errors": problems, "evidence": evidence,
    }
