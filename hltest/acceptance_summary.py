"""Compact developer-facing view of the verified candidate results."""
import re


LABELS = {"failed": "失败", "invalid_evidence": "证据失效", "skipped": "跳过", "not_run": "缺测"}
SENSITIVE = re.compile(
    r"password|passwd|secret|token|api[-_ ]?key|authorization|bearer\s|cookie|private[-_ ]?key"
    r"|session(?:id)?\s*[:=]|密码|密钥|令牌|凭据|[\w.+-]+@[\w.-]+\.\w+|(?<!\d)1[3-9]\d{9}(?!\d)"
    r"|://[^/\s]+@|(?:sk-|gh[pousr]_|AKIA)[A-Za-z0-9_-]{8,}|eyJ[\w-]+\.[\w-]+\.[\w-]+", re.I,
)


def excerpt(value):
    if SENSITIVE.search(value):
        return "[已隐藏敏感内容]"
    text = " ".join("".join(c if c.isprintable() else " " for c in value).split())
    return text if len(text) <= 180 else text[:179] + "…"


def junit_diagnostic(case, failure, metadata):
    detail = {}
    body = failure.text or ""
    message = failure.get("message") or ""
    # A plain-looking value can be a credential identified only by the test name or property key.
    context = [*case.attrib.values(), *failure.attrib.values(), body, *metadata.keys(), *metadata.values()]
    if any(SENSITIVE.search(value) for value in context if value):
        return {"case": "[用例参数已隐藏]", "diagnostic": "[已隐藏敏感内容]"}
    if not message:
        message = "\n".join(line[2:].strip() for line in body.splitlines() if line.startswith("E "))
    if not message and body.strip() and not body.lstrip().startswith("Traceback "):
        message = body.strip()
    if "expected" in failure.attrib and "actual" in failure.attrib:
        detail["diagnostic"] = f"预期 {excerpt(failure.get('expected'))}，实测 {excerpt(failure.get('actual'))}"
    elif message.strip():
        lines = message.strip().splitlines()
        # Some reporters put an assertion or its values after a custom failure title.
        evidence = [lines[0], *(s.strip() for s in lines[1:]
                    if re.match(r"\s*(?:assert\s|expected\b|actual\b|but was\b|预期|实测)", s, re.I))]
        detail["diagnostic"] = excerpt(" · ".join(evidence[:3]))
    elif failure.get("type"):
        detail["diagnostic"] = excerpt(failure.get("type"))

    if case.get("file"):
        source = case.get("file")
        if case.get("line"):
            source += f" (JUnit line={case.get('line')})"
        detail["source"] = excerpt(source)
    else:
        location = re.search(r"^([^\r\n]+\.py:\d+): [\w.]+(?:Error|Exception)\b", body, re.M)
        if location:
            detail["source"] = excerpt(location.group(1))
    rerun = (metadata.get("rerun_command") or "").strip()
    if rerun and excerpt(rerun) == rerun:
        detail["rerun"] = rerun
    return detail


def format_summary(result):
    verdict = "通过" if result["acceptance"] == "passed" else "阻断"
    lines = [f"验收{verdict} · 通过 {len(result['passed'])}/{result['planned']} · "
             f"阻断场景 {len(result['blocking_checks'])} · 报告问题 {len(result['report_errors'])}",
             f"候选 {result['revision']} · {excerpt(result['scope'])}"]
    for state, label in LABELS.items():
        for key in result[state]:
            lines.append(f"{key} {label}")
            for row in result["evidence"][key]:
                if row["status"] != state:
                    continue
                # A stale case can have parameterized values from an unrelated run.
                parts = [] if state == "invalid_evidence" else [excerpt(row["case"])]
                if row.get("flaky"):
                    parts.append("重试后通过，首次运行失败")
                if "diagnostic" in row:
                    parts.append(row["diagnostic"])
                parts.append(excerpt(row["artifact"]))
                if "source" in row:
                    parts.append(row["source"])
                lines.append("  " + " · ".join(parts))
                if "rerun" in row:
                    lines.append("  报告所列复跑命令 " + row["rerun"])
    for problem in result["report_errors"]:
        lines.append("报告问题 · " + excerpt(problem))
    return "\n".join(lines)
