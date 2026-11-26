"""Check definitions and relationships in the delivered Markdown tables."""
import argparse
from collections import defaultdict
from pathlib import Path
import re

from case_assertions import check_case_assertions


BL = r"BL-[0-9]+"
AC = r"AC-[0-9]+"
TC = r"TC-[0-9]+"
NUMBER = re.compile(r"[+\-−]?(?:\d+(?:[,，]\d{3}(?!\d))*(?:[.．]\d+)?|[.．]\d+)(?:[eE][+\-]?\d+)?")
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


def read_markdown(path, *, parse_declaration=True, source=None):
    """Read the format declaration, masking fenced text and comments in place."""
    lines = []
    title_area = True
    declaration = None
    comment = False
    fence = ""
    if source is None:
        source = path.read_text(encoding="utf-8-sig")
    for line in source.splitlines():
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
            directive = re.fullmatch(r"<!--\s*hlpm:(enterprise|module|split|split-mini|single|outline=.+?)\s*-->", line.strip())
            if directive:
                if declaration and declaration != directive[1]:
                    raise ValueError(f"{path.name} 文首的 PRD 目录声明冲突")
                declaration = directive[1]
            elif re.match(r"<!--\s*hlpm:", line.strip()):
                raise ValueError(f"{path.name} 文首的 PRD 格式声明无法识别：{line.strip()}")
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


def same(label, actual, expected, reference="确认计划"):
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing or extra:
        raise ValueError(f"{label} 与{reference}不符；缺少 {missing}，多出 {extra}")


def defined_cases(path, *, source=None):
    lines, _ = read_markdown(path, source=source)
    fields = ("前置条件", "输入与操作", "预期结果")
    cases = checked_rows(tables(path, lines=lines), "TC", {"关联 AC", *fields}, TC)
    for tc, (row, _, location) in cases.items():
        for field in fields:
            if PLACEHOLDER.fullmatch(row[field].strip("`")):
                raise ValueError(f"{location} {tc} 的「{field}」仍是占位内容")
    return cases


def check_case_coverage(path, cases, by_tc, reference):
    same(f"{path.name} TC 定义", cases, by_tc, reference)
    for tc, (row, _, location) in cases.items():
        same(f"{location} {tc} 的 AC", id_set(row["关联 AC"], AC, location), by_tc[tc], reference)


def check_selected_cases(prd, path):
    by_tc = defaultdict(set)
    for ac, (row, _, location) in prd.items():
        if not row.get("可追溯测试"):
            raise ValueError(f"{location} {ac} 缺少所选用例的 TC 编号，请填写「可追溯测试」列")
        for tc in id_set(row["可追溯测试"], TC, location):
            by_tc[tc].add(ac)
    cases = defined_cases(path)
    check_case_coverage(path, cases, by_tc, "PRD 验收表")
    return len(cases)


def check_prd(path, *, enterprise=False, module=False, customer_outline=None, split=False, split_mini=False,
              single=False, stage="prd", review_notes=None):
    cards = {}
    source = path.read_text(encoding="utf-8-sig")
    lines, marked = read_markdown(path, source=source)
    if stage not in {"prd", "test"}:
        raise ValueError(f"未知校验阶段：{stage}")
    for selected, required in ((split, "split"), (split_mini, "split-mini"), (single, "single")):
        if selected and marked != required:
            raise ValueError(f"{path.name} 新稿请在文首写入 <!-- hlpm:{required} -->，以便下游识别交付格式")
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
    split = split or marked == "split"
    split_mini = split_mini or marked == "split-mini"
    single = single or marked == "single"
    if sum((enterprise, module, bool(customer_outline), split, split_mini, single)) > 1:
        raise ValueError(f"{path.name} 命令与 PRD 目录声明冲突")
    rows = list(tables(path, cards=cards, lines=lines))
    if "产品阶段安排" in source and not (marked or enterprise or module or customer_outline):
        from prd_attachments import SUPPLEMENTS
        if any(header == ["内容", "产品阶段安排"] and values[0] in SUPPLEMENTS for header, values, _, _ in rows):
            raise ValueError(f"{path.name} 已登记新版分册，请在文首声明 hlpm:split 或 hlpm:split-mini")
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
    if enterprise or module or split:
        from enterprise_prd import check_enterprise
        notes = check_enterprise(path, lines, prd, rows, owners, module=module, split=split, stage=stage,
                                 review_source=source if review_notes is not None else None)
        if review_notes is not None:
            review_notes.extend(notes)
    elif customer_outline:
        from enterprise_prd import check_customer_outline
        check_customer_outline(path, lines, rows, owners, customer_outline, criteria=prd, stage=stage)
    elif split_mini:
        from prd_attachments import check_attachments
        for index, line in enumerate(lines, 1):
            if re.match(r"^ {0,3}#{1,6}\s+(?:0?8[.、 ]+数据需求设计|0?9[.、 ]+接口需求设计|14[.、 ]+测试及验收标准|15[.、 ]+发布及上线要求)\s*$", line):
                raise ValueError(f"{path.name}:{index} 新版 Mini 正文请按分册目录编写")
        check_attachments(path, lines, rows, owners, prd, mini=True, stage=stage)
    elif single:
        from prd_attachments import check_single
        check_single(path, lines, rows, owners, stage)
    if stage == "test":
        cases = path.with_name("test-cases.md")
        if not cases.is_file() or cases.samefile(path) or cases.resolve().parent != path.parent.resolve():
            raise ValueError(f"{path.name} 测试阶段须提交同版独立的 test-cases.md")
        check_selected_cases(prd, cases)
    return prd, owners, enterprise or module or split


def check_ac_value(prd, ac, context, expected):
    """Compare an independently derived value at one named place in an AC result."""
    if ac not in prd:
        raise ValueError(f"找不到待复核的验收条件 {ac}")
    row, _, location = prd[ac]
    label = f"{location} {ac}"
    if context.count("{}") != 1 or not expected.strip():
        raise ValueError(f"{label} 复算需要一个 {{}} 标出读数位置，并提供独立求得的值")
    before, after = context.split("{}")
    cell = row["验收点"]
    # Match plain text only. A number in a link target or HTML is not an outcome.
    if re.search(r"\]\s*[(\[]|<[/!A-Za-z]|~~", cell):
        raise ValueError(f"{label} 含标记的验收点请使用对应断言核对实值")
    if before and cell.count(before) != 1:
        raise ValueError(f"{label} 无法唯一定位「{before}」，请包含业务对象或办理时点")
    start = cell.index(before) + len(before) if before else 0
    # A context delimiter such as "." must not cut 8.5 down to a passing "8".
    numbers = list(NUMBER.finditer(cell))
    def inside_number(pos):
        return any(n.start() < pos < n.end() for n in numbers)

    if inside_number(start):
        raise ValueError(f"{label} 短句从数值中间开始，请保留完整读数")
    end = len(cell)
    if after:
        ends = re.compile(re.escape(after)).finditer(cell, start)
        end = next((match.start() for match in ends if not inside_number(match.start())), None)
        if end is None:
            raise ValueError(f"{label} 完整读数后缺少「{after}」")
    actual = cell[start:end]
    if actual.strip() != expected.strip():
        raise ValueError(f"{label} 复算预期「{expected}」，正文为「{actual}」")


def check_trace(root, plan, *, require_prd_results=False):
    by_tc = {s["id"]: set(s["acs"]) for s in plan["scenarios"]}
    by_ac = defaultdict(set)
    pages = defaultdict(set)
    for s in plan["scenarios"]:
        for ac in s["acs"]:
            by_ac[ac].add(s["id"])
            pages[ac].update(s["pages"])

    prd, owners, _ = check_prd(root / "prd.md", stage="test")
    same("prd.md AC 定义", prd, by_ac)
    for ac, (row, _, location) in prd.items():
        if not row.get("可追溯测试"):
            raise ValueError(f"{location} {ac} 完整交接须在「可追溯测试」列填写 TC 编号")
        same(f"{location} {ac} 的 TC", id_set(row["可追溯测试"], TC, location), by_ac[ac])

    cases_path = root / "test-cases.md"
    cases = defined_cases(cases_path)
    check_case_coverage(cases_path, cases, by_tc, "确认计划")
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
    profile.add_argument("--single", action="store_true", help="核对仅交单份 PRD 的正文及文内验收索引")
    profile.add_argument("--split", action="store_true", help="核对新版标准 PRD、附录和分册")
    profile.add_argument("--split-mini", action="store_true", help="核对新版 Mini PRD、附录和分册")
    profile.add_argument("--enterprise", action="store_true", help="核对内置企业目录全部编号小节和功能验收")
    profile.add_argument("--module", action="store_true", help="核对新功能模块目录及功能验收，第 15 章按需展开")
    profile.add_argument("--outline", type=Path, help="按客户提供的 16 章编号 Markdown 目录核对")
    parser.add_argument("--stage", choices=("prd", "test"), help="默认核对 PRD；测试阶段核对已交验收标准和本版用例")
    parser.add_argument("--cases", type=Path, help="核对本次单列的用例文件与 PRD 中的 AC、TC 对应关系")
    parser.add_argument("--expect-ac", nargs=3, action="append", default=[],
                        metavar=("AC", "带{}的短句", "预期值"), help="核对指定验收点中的独立复算值，可重复")
    args = parser.parse_args()
    if args.cases and args.stage == "prd":
        parser.error("核对详细用例请使用 --stage test")
    try:
        review_notes = []
        marked = read_markdown(args.prd)[1]
        stage = args.stage or ("test" if args.cases and marked in {"single", "split", "split-mini"} else "prd")
        prd, owners, enterprise = check_prd(args.prd, enterprise=args.enterprise, module=args.module,
                                            split=args.split, split_mini=args.split_mini,
                                            single=args.single, stage=stage,
                                            customer_outline=args.outline, review_notes=review_notes)
        for ac, context, expected in args.expect_ac:
            check_ac_value(prd, ac, context, expected)
        if stage == "test":
            if args.cases and not args.cases.samefile(args.prd.with_name("test-cases.md")):
                raise ValueError("--stage test 须使用同版 test-cases.md")
            print("已核对本版 test-cases.md 的完整用例及与 PRD 的双向对应")
        elif args.cases:
            if args.prd.samefile(args.cases):
                raise ValueError("--cases 须指向独立于 PRD 的用例文件")
            count = check_selected_cases(prd, args.cases)
            print(f"{args.cases}：已核对 {count} 条用例与 PRD 的双向对应及必填字段")
        if args.split or args.split_mini or marked in {"split", "split-mini"}:
            print("已核对本阶段分册安排和已交分册")
        elif marked == "single":
            print("已核对单文件 PRD 的功能卡和文内验收索引")
        elif enterprise:
            print("企业目录、各级编号小节及正文、不适用和待确认标注、功能验收索引已核对")
        elif args.outline or marked:
            print("客户目录、编号小节及正文、功能验收索引已核对")
        for note in review_notes:
            print(note)
        print(f"{args.prd}：已核对 {len(set(owners.values()))} 张功能卡、{len(prd)} 条验收条件及其归属")
        if args.expect_ac:
            print(f"验收点正文与独立提供的预期值相符：{len(args.expect_ac)} 项")
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
