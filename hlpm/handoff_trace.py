"""Check definitions and relationships in the delivered Markdown tables."""
import argparse
from collections import defaultdict
from pathlib import Path
import re

from case_assertions import check_case_assertions


BL = r"BL-[0-9]+"
AC = r"AC-[0-9]+"
TC = r"TC-[0-9]+"
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+)")
SECTION = r"(?:§?[0-9]+(?:\.[0-9]+)*[.、]?\s+)?"
CARD = re.compile(r"(?:§?[0-9]+(?:\.[0-9]+)?[.、]?\s+)?(" + BL + r")(?![a-zA-Z0-9.-])")
EXAMPLE = re.compile(SECTION + r"(?:格式示例|历史示例|示例|示意)(?:$|[ ：:（(])")
INDEX = re.compile(r"(?:14[.、]?\s+测试及验收标准|" + SECTION
                   + r"(?:附录|目录|功能清单|功能索引|验收索引|验收标准索引|功能模块总览|"
                     r"延期清单|非本期范围|本期不包含(?:的?功能|内容)?))(?:$|[\s：:（(·])")
PLACEHOLDER = re.compile(
    r"[-—…?.]+|(?:TBD|TODO|N/?A|待填(?:写)?|待补(?:充)?|待确认)[。.]?"
    r"|(?:TBD|TODO|N/?A)(?:\s*[:：+＋（(【—–-]|\s+(?:负责人|责任人|理由|原因)).+", re.I)


def cells(line, header=None):
    fields = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [v.strip() if header and i < len(header) and header[i] in {"预期结果", "验收点", "PRD 验收点"}
            else v.strip().strip("`")
            for i, v in enumerate(fields)]


def read_markdown(path, *, parse_declaration=True):
    """Read the format declaration, masking fenced text and comments in place."""
    lines = []
    title_area = True
    declaration = None
    comment = False
    fence = ""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(r" {0,3}" + fence[0] + "{" + str(len(fence)) + r",}\s*", line):
                fence = ""
            lines.append("")
            continue
        if marker and not comment:
            fence = marker[1]
            title_area = False
            lines.append("")
            continue
        if parse_declaration and title_area and not comment:
            directive = re.fullmatch(r"<!--\s*hlpm:(enterprise|module|outline=.+?)\s*-->", line.strip())
            if directive:
                if declaration and declaration != directive[1]:
                    raise ValueError(f"{path.name} 文首的 PRD 目录声明冲突")
                declaration = directive[1]
        visible = []
        while line:
            if comment:
                _, end, line = line.partition("-->")
                comment = not end
            else:
                part, start, line = line.partition("<!--")
                visible.append(part)
                comment = bool(start)
        line = "".join(visible)
        lines.append(line)
        if line.strip() and not re.match(r"^ {0,3}#\s+", line):
            title_area = False
    return lines, declaration


def tables(path, *, cards=None, lines=None, include_headers=False):
    if lines is None:
        lines, _ = read_markdown(path)
    headings = []
    header = None
    example = False
    for i, line in enumerate(lines):
        heading = HEADING.match(line)
        if heading:
            while headings and headings[-1][0] >= len(heading[1]):
                headings.pop()
            headings.append((len(heading[1]), heading[2]))
            example = any(EXAMPLE.match(title) for _, title in headings)
            if (cards is not None and not example and not any(INDEX.match(title) for _, title in headings)
                    and (card := CARD.match(heading[2]))):
                key = card[1]
                if key in cards:
                    raise ValueError(f"{path.name}:{i+1} 重复功能编号 {key}，首次定义于 {cards[key]}")
                cards[key] = f"{path.name}:{i+1}"
        if not line.lstrip().startswith("|"):
            header = None
            continue
        if example:
            continue
        fields = cells(line, header)
        if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|") and all(
            re.fullmatch(r":?-{3,}:?", v) for v in cells(lines[i + 1])
        ):
            header = fields
            if include_headers:
                yield header, fields, [title for _, title in headings], f"{path.name}:{i+1}"
        elif header and not all(re.fullmatch(r":?-{3,}:?", v) for v in fields):
            yield header, fields, [title for _, title in headings], f"{path.name}:{i+1}"


def id_set(value, pattern, location):
    ids = re.split(r"[,，、\s]+", value.strip())
    if not all(re.fullmatch(pattern, item) for item in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"{location} 无效或重复的关联编号：{value}")
    return set(ids)


def checked_rows(tables_in_file, first, required, pattern):
    rows = {}
    for header, values, headings, location in tables_in_file:
        if header[0] != first or not required.issubset(header):
            continue
        if len(values) != len(header) or len(header) != len(set(header)):
            raise ValueError(f"{location} 表格列数不符或表头重复")
        row = dict(zip(header, values))
        key = row[first]
        if not re.fullmatch(pattern, key) or key in rows:
            raise ValueError(f"{location} 无效或重复的 {first} 定义：{key}")
        if any(not row[name] for name in required):
            raise ValueError(f"{location} {key} 必填内容为空")
        rows[key] = row, headings, location
    return rows


def same(label, actual, expected):
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing or extra:
        raise ValueError(f"{label} 与确认计划不符；缺少 {missing}，多出 {extra}")


def check_prd(path, *, enterprise=False, module=False, customer_outline=None):
    cards = {}
    lines, marked = read_markdown(path)
    if marked and marked.startswith("outline="):
        relative = Path(marked.removeprefix("outline="))
        declared = (path.parent / relative).resolve()
        if relative.is_absolute() or not declared.is_relative_to(path.parent.resolve()):
            raise ValueError(f"{path.name} 客户目录须使用本版内的相对路径")
        if customer_outline and declared != customer_outline.resolve():
            raise ValueError(f"{path.name} 命令与文首声明的客户目录不一致")
        customer_outline = declared
    enterprise = enterprise or marked == "enterprise"
    module = module or marked == "module"
    if sum((enterprise, module, bool(customer_outline))) > 1:
        raise ValueError(f"{path.name} 企业目录、模块目录或客户目录声明冲突")
    rows = tables(path, cards=cards, lines=lines)
    if enterprise or module or customer_outline:
        rows = list(rows)  # The chapter indexes and AC definitions use the same parsed rows.
    prd = checked_rows(rows, "AC", {"验收点"}, AC)
    if not cards:
        raise ValueError(f"{path.name} 缺少本期 BL 功能卡片标题")
    owners = {}
    for ac, (row, headings, location) in prd.items():
        owner = next((m[1] for title in reversed(headings) if (m := CARD.match(title))), None)
        if owner is None or any(INDEX.match(title) for title in headings):
            raise ValueError(f"{location} {ac} 须在 BL 功能卡片标题下定义，索引只引用编号")
        if PLACEHOLDER.fullmatch(row["验收点"].strip("`")):
            raise ValueError(f"{location} {ac} 缺少可观察的验收结果")
        owners[ac] = owner
    missing = cards.keys() - set(owners.values())
    if missing:
        locations = "、".join(f"{key}（{cards[key]}）" for key in sorted(missing))
        raise ValueError(f"本期功能缺少所属验收条件 AC：{locations}")
    if enterprise or module:
        from enterprise_prd import check_enterprise
        check_enterprise(path, lines, prd, rows, owners, module=module)
    elif customer_outline:
        from enterprise_prd import check_customer_outline
        check_customer_outline(path, lines, rows, owners, customer_outline)
    return prd, owners, enterprise or module


def check_trace(root, plan, *, require_prd_results=False):
    by_tc = {s["id"]: set(s["acs"]) for s in plan["scenarios"]}
    by_ac = defaultdict(set)
    pages = defaultdict(set)
    for s in plan["scenarios"]:
        for ac in s["acs"]:
            by_ac[ac].add(s["id"])
            pages[ac].update(s["pages"])

    prd, owners, _ = check_prd(root / "prd.md")
    same("prd.md AC 定义", prd, by_ac)
    for ac, (row, _, location) in prd.items():
        if not row.get("可追溯测试"):
            raise ValueError(f"{location} {ac} 完整交接须在「可追溯测试」列填写 TC 编号")
        same(f"{location} {ac} 的 TC", id_set(row["可追溯测试"], TC, location), by_ac[ac])

    cases = checked_rows(tables(root / "test-cases.md"), "TC",
                         {"关联 AC", "前置条件", "输入与操作", "预期结果"}, TC)
    same("test-cases.md TC 定义", cases, by_tc)
    for tc, (row, _, location) in cases.items():
        same(f"{location} {tc} 的 AC", id_set(row["关联 AC"], AC, location), by_tc[tc])
    outcome_count = check_case_assertions(root, plan, cases, prd, require_prd_results)

    matrix = list(tables(root / "consistency-matrix.md"))
    scope = checked_rows(matrix, "AC", {"所属 BL 及规则位置", "设计页面或 N/A 原因", "关联 TC", "验收方法"}, AC)
    implementation = checked_rows(matrix, "AC", {"关联 TC", "实现状态"}, AC)
    for label, rows in (("§1 业务规则", scope), ("§5 实现追踪", implementation)):
        same(f"consistency-matrix.md {label}的 AC", rows, by_ac)
        for ac, (row, _, location) in rows.items():
            same(f"{location} {ac} 的 TC", id_set(row["关联 TC"], TC, location), by_ac[ac])
    for ac, (row, _, location) in scope.items():
        owner = re.findall(r"(?<![A-Za-z0-9-])" + BL + r"(?![A-Za-z0-9-])", row["所属 BL 及规则位置"])
        same(f"{location} {ac} 的 BL", owner, {owners[ac]})
        displayed = row["设计页面或 N/A 原因"]
        if pages[ac]:
            same(f"{location} {ac} 的页面", re.split(r"\s*[,，、]\s*", displayed), pages[ac])
        elif not re.fullmatch(r"N/A\s*[:：—-]?\s*[^\s:：—-].*", displayed):
            raise ValueError(f"{location} {ac} 无 UI 须填写 N/A 和原因")
    return outcome_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="核对 PRD 中的 BL 功能卡与 AC 验收点")
    parser.add_argument("prd", type=Path, help="当前版本的 PRD Markdown 文件")
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument("--enterprise", action="store_true", help="核对内置企业目录全部编号小节和功能验收")
    profile.add_argument("--module", action="store_true", help="核对新功能模块目录及功能验收，第 15 章按需展开")
    profile.add_argument("--outline", type=Path, help="按客户提供的 16 章编号 Markdown 目录核对")
    args = parser.parse_args()
    try:
        prd, owners, enterprise = check_prd(args.prd, enterprise=args.enterprise, module=args.module,
                                            customer_outline=args.outline)
        if enterprise:
            print("企业目录、各级编号小节及正文、不适用和待确认标注、功能验收索引已核对")
        elif args.outline or read_markdown(args.prd)[1]:
            print("客户目录、编号小节及正文、功能验收索引已核对")
        print(f"{args.prd}：已核对 {len(set(owners.values()))} 张功能卡、{len(prd)} 条验收条件及其归属")
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
