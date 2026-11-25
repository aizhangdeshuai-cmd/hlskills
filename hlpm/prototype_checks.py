"""Generate and check the per-AC observations in a prototype interaction report."""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from handoff_trace import HEADING, PLACEHOLDER, cells, check_prd, read_markdown, tables


COLUMNS = ("BL", "AC", "PRD 验收点", "场景与操作", "交互实测", "数据实测", "异常恢复实测", "原型结论", "证据", "后续验证")
DIMENSIONS = COLUMNS[4:7]
STATUSES = ("通过", "模拟通过", "失败", "未测", "仅候选待验", "不适用")
N_A = re.compile(r"^(?:不适用|N/?A\b)(?:\s*[:：]\s*(.*))?", re.I)
BARE = {"无", "无异常", "正常", "成功", "通过", "符合预期", "已验证", "已测试", "已完成", "未测", "不适用", "原因",
        "不涉及", "无需验证", "无变化", "无数据变化", "按预期", "同上", "待验", "待验证", "待实测", "候选待验", "暂无"}
LINK = re.compile(r"\[[^\]\n]+\]\((?:<([^>]+)>|([^()\s]+))\)")
CASE_ID = re.compile(r"(?<![\w-])(?:AC|TC)-[0-9]+(?![A-Za-z0-9-])", re.ASCII)


class HtmlObservations(HTMLParser):
    """Collect visible text per report row or anchored section, without executing the document."""
    VOID = set("area base br col embed hr img input link meta param source track wbr".split())
    SIBLINGS = {"td": ({"td", "th"}, {"tr"}), "th": ({"td", "th"}, {"tr"}),
                "tr": ({"tr"}, {"table"}), "li": ({"li"}, {"ul", "ol"}), "p": ({"p"}, set())}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.text = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SIBLINGS:
            self.finish_through(*self.SIBLINGS[tag])
        if tag in {"br", "td", "th", "li", "p"}:
            self.text.append(" ")
        if tag in self.VOID:
            return
        attrs = dict(attrs)
        hidden = (tag in {"head", "script", "style", "template"} or "hidden" in attrs
                  or attrs.get("aria-hidden") == "true" or bool(self.stack and self.stack[-1][1]))
        anchor = attrs.get("id", "")
        record = bool(anchor or tag in {"tr", "article", "section", "li", "p"})
        self.stack.append((tag, hidden, anchor, len(self.text) if record else None))

    def handle_endtag(self, tag):
        self.finish_through({tag}, set())

    def finish_through(self, tags, boundaries):
        for i in range(len(self.stack) - 1, -1, -1):
            tag = self.stack[i][0]
            if tag in boundaries:
                return
            if tag in tags:
                while len(self.stack) > i:
                    self.finish_element()
                return

    def finish_element(self):
        _, hidden, anchor, start = self.stack.pop()
        if not hidden and start is not None:
            content = " ".join("".join(self.text[start:]).split())
            ids = set(CASE_ID.findall(anchor + " " + content))
            if ids and content:
                self.records.append((anchor, ids, content))

    def handle_data(self, value):
        if self.stack and not self.stack[-1][1]:
            self.text.append(value)

    def close(self):
        super().close()
        while self.stack:
            self.finish_element()


def html_evidence(prd):
    @lru_cache(maxsize=1)
    def input_hashes():
        # These are delivered prototype pages, even if their UI itself displays AC or TC metadata.
        lines, _ = read_markdown(prd)
        links = (urlsplit(a or b) for a, b in LINK.findall("\n".join(lines)))
        paths = {(prd.parent / unquote(link.path)).resolve() for link in links
                 if not link.scheme and not link.netloc and link.path.lower().endswith((".html", ".htm"))
                 and Path(link.path).parts[:1] == ("design",)}
        plan_file = prd.with_name("acceptance-plan.json")
        if plan_file.is_file():
            from acceptance_plan import read_json
            # A prototype-only review may precede completion of the acceptance plan.
            for case in read_json(plan_file).get("scenarios", []):
                entries = [urlsplit(role["entry"]).path for role in case.get("roles", {}).values() if role.get("entry")]
                paths.update((prd.parent / "design" / page).resolve() for page in [*case.get("pages", []), *entries])
        return {hashlib.sha256(path.read_bytes()).digest() for path in paths
                if path.is_relative_to(prd.parent) and path.is_file()}

    @lru_cache(maxsize=None)
    def records(path):
        content = path.read_bytes()
        if hashlib.sha256(content).digest() in input_hashes():
            return []
        parser = HtmlObservations()
        parser.feed(content.decode("utf-8-sig"))
        parser.close()
        return parser.records

    return records


def outline(prd_path):
    prd, owners, _ = check_prd(prd_path)
    rows = [COLUMNS, ["---"] * len(COLUMNS)]
    for ac, (row, _, _) in prd.items():
        scenario = "；".join(row[k] for k in ("前置条件", "操作步骤") if row.get(k))
        rows.append((owners[ac], ac, row["验收点"], scenario or row.get("测试场景", ""), "", "", "", "未测", "", ""))
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def concrete(value):
    return bool(value and value.rstrip("。.") not in BARE and not PLACEHOLDER.fullmatch(value))


def observation_table(header):
    return ("PRD 验收点" in header
            or {"BL", "AC"}.issubset(header) and bool(set(DIMENSIONS).intersection(header)))


def markdown_anchor(path, fragment, *, same_report):
    lines, _ = read_markdown(path)
    for i, line in enumerate(lines):
        heading = HEADING.match(line)
        explicit = re.search(r"""\bid\s*=\s*["']""" + re.escape(fragment) + r"""["']""", line)
        if not explicit and not (heading and re.sub(r"[^\w\s-]", "", heading[2]).strip().lower().replace(" ", "-") == fragment):
            continue
        if not same_report:
            return True
        # A self-link must lead to a separate observation, not back to the checklist.
        has_body = False
        for following in lines[i + 1:]:
            if not following.strip():
                continue
            if HEADING.match(following):
                if explicit and not has_body:
                    explicit = False
                    continue
                break
            if following.lstrip().startswith("|") and observation_table(cells(following)):
                return False
            has_body = True
        return has_body
    return False


def native_evidence(package):
    """Resolve the ACs actually exercised when a link points to a hlpm browser run."""
    from acceptance_plan import load_plan
    from prototype_evidence import check_steps

    design = (package / "design").resolve()

    @lru_cache(maxsize=1)
    def scenarios():
        plan = load_plan(package / "acceptance-plan.json")
        return plan, {case["id"]: case for case in plan["scenarios"]}

    @lru_cache(maxsize=None)
    def verified(path):
        canonical = path.parent == design / "checks" and re.fullmatch(r"TC-\d+", path.stem)
        record = json.loads(path.read_text(encoding="utf-8"))
        if not canonical and not (isinstance(record, dict)
                                  and "steps_sha256" in record and "scenario" in record):
            return None
        scenario = record.get("scenario") if isinstance(record, dict) else None
        key = scenario.get("id") if isinstance(scenario, dict) else None
        plan, cases = scenarios()
        if not isinstance(key, str) or key not in cases or (canonical and key != path.stem):
            raise ValueError(f"{path.name} 所属 TC 与本版计划或文件名不符")
        check_steps(design, plan, cases[key], record)
        return cases[key]["acs"]

    return verified


def check_evidence(row, report, prd, executed, expected_cases, verify_native, html_records):
    value, ac = row["证据"], row["AC"]
    links = [one or two for one, two in LINK.findall(value)]
    if not links:
        if executed or (value and value != "无"):
            raise ValueError("证据须链接到本版本的实测记录")
        return
    has_record = False
    for link in links:
        target = urlsplit(link)
        name = Path(unquote(target.path))
        if target.scheme or target.netloc or name.is_absolute():
            raise ValueError(f"证据须使用本版本内的相对链接：{link}")
        path = (report.parent / name).resolve() if target.path else report
        if not path.is_relative_to(prd.parent) or not path.is_file() or not path.stat().st_size:
            raise ValueError(f"找不到本版本内的非空证据文件：{link}")
        if target.fragment and path.suffix.lower() == ".md" and not markdown_anchor(
                path, unquote(target.fragment), same_report=path == report):
            raise ValueError(f"证据小节不存在或指回核对表：{link}")
        if path.suffix.lower() in {".html", ".htm"}:
            # HTML alone is an observation only when the cited case actually contains the quoted readout.
            matches = set()
            for key in DIMENSIONS:
                value = row[key]
                if concrete(value) and not N_A.match(value):
                    matches.add(" ".join(value.strip("。.!！").split()))
                    matches.update(quote for quote in re.findall(r"`([^`]+)`", value) if concrete(quote))
            fragment = unquote(target.fragment)
            for anchor, ids, content in html_records(path):
                if ((not fragment or anchor == fragment) and ids <= expected_cases
                        and any(value in content for value in matches)):
                    has_record = True
                    break
            continue
        if (path != prd and (path != report or target.fragment)
                and path.name != "acceptance-plan.json" and not path.name.endswith((".recipe.json", ".business.json"))
                and path.suffix.lower() not in {".steps", ".py", ".js", ".mjs", ".ts", ".sh", ".css"}):
            if path.suffix.lower() == ".json" and executed:
                try:
                    covered = verify_native(path)
                except (ValueError, OSError, KeyError, TypeError) as error:
                    raise ValueError(f"{path.name} 实测记录无效：{error}") from error
                if covered is not None and ac not in covered:
                    raise ValueError(f"{path.name} 未执行 {ac}")
            has_record = True
    if executed and not has_record:
        raise ValueError("须链接实际执行记录；原型入口、步骤、脚本和计划只用于定位操作")


def check(prd_path, report_path):
    prd_path, report_path = prd_path.resolve(), report_path.resolve()
    prd, owners, _ = check_prd(prd_path)
    seen = set()
    counts = Counter()
    errors = []
    covered = set()
    verify_native = native_evidence(prd_path.parent)
    html_records = html_evidence(prd_path)
    for header, fields, _, location in tables(report_path):
        if not observation_table(header):
            continue
        if set(COLUMNS) - set(header) or len(set(header)) != len(header) or len(header) != len(fields):
            raise ValueError(f"{location} 核对表缺列、表头重复或列数不符，应包括 {'、'.join(COLUMNS)}")
        row = dict(zip(header, fields))
        ac, scenario, status = row["AC"], row["场景与操作"], row["原型结论"]
        label = f"{location} {ac}（{scenario or '未填场景'}）"
        if ac not in prd:
            errors.append(f"{label} 当前 PRD 无此 AC")
            continue
        if row["BL"] != owners[ac]:
            errors.append(f"{label} 所属功能应为 {owners[ac]}")
        if row["PRD 验收点"] != prd[ac][0]["验收点"] and not (row["PRD 验收点"] == "同上" and ac in covered):
            errors.append(f"{label} 验收点与当前 PRD 原文不符")
        covered.add(ac)
        if not concrete(scenario) or (ac, scenario) in seen:
            errors.append(f"{label} 场景与操作缺失或重复")
        seen.add((ac, scenario))
        if status not in STATUSES:
            errors.append(f"{label} 未知原型结论 {status!r}，可选 {'、'.join(STATUSES)}")
            continue
        counts[status] += 1
        executed = status in ("通过", "模拟通过", "失败")
        if executed:
            observed = False
            for key in DIMENSIONS:
                value = row[key]
                exemption = N_A.match(value)
                if exemption and concrete(exemption[1]):
                    continue
                if not exemption and concrete(value):
                    observed = True
                else:
                    errors.append(f"{label} {key}须填具体观察或“不适用：原因”")
            if not observed:
                errors.append(f"{label} 实测结论至少要有一项适用观察")
        if status != "通过" and not concrete(row["后续验证"]):
            errors.append(f"{label} 后续验证须写适用边界、未验原因或复验动作")
        if status in ("失败", "未测"):
            errors.append(f"{label} 原型{status}，{row['后续验证'] or '须补验'}")
        try:
            expected_cases = {ac, *CASE_ID.findall(prd[ac][0].get("可追溯测试", ""))}
            check_evidence(row, report_path, prd_path, executed, expected_cases, verify_native, html_records)
        except ValueError as error:
            errors.append(f"{label} {error}")
    for ac in sorted(prd.keys() - covered):
        errors.append(f"{report_path.name} 缺少 {owners[ac]} / {ac} 的核对记录")
    if errors:
        raise ValueError("\n".join(errors))
    summary = "，".join(f"{status} {counts[status]}" for status in STATUSES if counts[status])
    return f"已核对 {len(covered)} 条 AC、{sum(counts.values())} 条场景记录：{summary}。"


def main():
    parser = argparse.ArgumentParser(description="从当前 PRD 生成或核对原型逐 AC 实测表")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("outline", help="向标准输出写空表，可追加到现有实测记录").add_argument("prd", type=Path)
    verify = commands.add_parser("check", help="核对原型实测表的覆盖、归属、适用性和证据链接")
    verify.add_argument("prd", type=Path)
    verify.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        print(outline(args.prd) if args.command == "outline" else check(args.prd, args.report))
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
