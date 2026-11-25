"""Validate the outline and trace indexes declared by a full enterprise PRD."""
from pathlib import Path
import re

from enterprise_content import check_risks, require_body
from enterprise_refs import check_references
from handoff_trace import AC, HEADING, id_set, read_markdown


NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)(?:[.、]\s*|\s+)(.+)$")
TABLE_COLUMNS = {
    "字段编号": (4, ("字段名称", "英文字段名", "字段类型", "控件类型", "是否必填", "默认值", "数据来源", "是否可编辑", "校验规则", "字段说明")),
    "按钮名称": (4, ("功能说明", "触发条件", "操作结果")),
    "列名称": (4, ("数据来源", "显示规则", "排序规则", "筛选规则")),
    "用户操作": (5, ("触发条件", "系统响应", "页面变化", "数据变化")),
    "规则编号": (6, ("规则名称", "触发条件", "业务规则", "处理结果")),
    "校验编号": (7, ("校验对象", "校验条件", "校验时机", "校验结果", "错误提示")),
    "异常编号": (8, ("异常场景", "触发条件", "系统处理", "用户提示", "恢复方式")),
    "数据对象": (9, ("操作类型", "处理内容", "关联对象", "处理规则")),
}


def outline(path, lines, chapter_titles=None):
    """Group numbered children by their actual Markdown parent, with physical line ranges."""
    children = {}
    parents = []
    seen = set()
    for offset, line in enumerate(lines):
        heading = HEADING.match(line)
        if not heading:
            continue
        depth = len(heading[1])
        while parents and parents[-1][0] >= depth:
            _, previous = parents.pop()
            if previous:
                previous[3] = offset
        match = NUMBERED.match(re.sub(r"\s+#+\s*$", "", heading[2]).strip())
        section = None
        if match and depth > 1:
            number = tuple(map(int, match[1].split(".")))
            parent = parents[-1][1] if parents else None
            if depth != len(number) + 1 or (number[:-1] and (not parent or parent[0] != number[:-1])):
                chapter = (chapter_titles or {}).get(number[0], "")
                raise ValueError(f"{path.name}:{offset + 1} 企业目录编号 {match[1]} 的标题层级或父级不符，"
                                 f"请核对第 {number[0]} {chapter} 章")
            if number in seen:
                raise ValueError(f"{path.name}:{offset + 1} 企业目录重复编号 {match[1]}")
            seen.add(number)
            section = [number, match[2], offset, len(lines)]
            children.setdefault(number[:-1], []).append(section)
        parents.append((depth, section))
    return children


def title_key(value):
    # The reference also publishes bilingual chapter names.
    value = re.sub(r"\s*[(（][A-Za-z][^()（）]*[)）]\s*$", "", value)
    value = re.sub(r"[(（](?:按需|选填|建议补充)[)）]\s*$", "", value)
    return "".join(value.split()).replace("待确认事项及风险", "风险及待确认事项")


def check_sequence(path, sections_found, expected, scope, start=0):
    observed = [(number, title_key(title)) for number, title, _, _ in sections_found]
    wanted = [(number, title_key(title)) for number, title in expected]
    if observed == wanted:
        return
    index = next((i for i, pair in enumerate(zip(observed, wanted)) if pair[0] != pair[1]),
                 min(len(observed), len(wanted)))
    where = f"{path.name}:{sections_found[index][2] + 1 if index < len(observed) else start + 1}"
    if index == len(wanted):
        raise ValueError(f"{where} {scope} 出现多余的编号或标题 {sections_found[index][1]}")
    number, title = expected[index]
    label = ".".join(map(str, number))
    missing = [".".join(map(str, n)) for n, name in wanted if (n, name) not in observed]
    suffix = f"，缺少或错名：{'、'.join(missing)}" if missing else ""
    raise ValueError(f"{where} {scope} 应按顺序包含 {label} {title}{suffix}")


def customer_sections(template):
    lines, _ = read_markdown(template)
    expected = outline(template, lines)
    if [entry[0] for entry in expected.get((), [])] != [(n,) for n in range(1, 17)]:
        raise ValueError(f"{template.name} 客户目录原件须依次提供 01 至 16 章的编号 Markdown 标题")
    return expected


def check_customer_outline(path, lines, rows, owners, template):
    if path.resolve() == template.resolve():
        raise ValueError("客户目录须使用独立的已确认目录原件")
    expected = customer_sections(template)
    actual = outline(path, lines)
    for parent, siblings in expected.items():
        check_sequence(path, actual.get(parent, []), [entry[:2] for entry in siblings], "客户目录")
    chapters = actual[()]
    data_rows = {int(location.rsplit(":", 1)[1]) - 1: (header, values)
                 for header, values, _, location in rows}
    for siblings in actual.values():
        for number, title, start, stop in siblings:
            children = actual.get(number, [])
            require_body(path, lines, (number, title, start, children[0][2] if children else stop),
                         data_rows, required=not children)
    check_risks(path, chapters[15], rows, lines)
    index = {}
    for header, values, _, location in rows:
        offset = int(location.rsplit(":", 1)[1]) - 1
        if header[:1] == ["AC"] and "验收点" in header and not chapters[6][2] < offset < chapters[6][3]:
            raise ValueError(f"{location} 客户第 07 章须承载 BL 功能卡的 AC 定义")
        if chapters[13][2] < offset < chapters[13][3] and {"BL", "AC", "验证方式"}.issubset(header):
            if len(header) != len(values) or len(set(header)) != len(header):
                raise ValueError(f"{location} 客户验收索引列数不符或列名重复")
            row = dict(zip(header, values))
            for key in id_set(row["AC"], AC, location):
                if key in index or not row["验证方式"]:
                    raise ValueError(f"{location} {key} 重复或缺少验证方式")
                index[key] = row["BL"]
    if index != owners:
        wrong = sorted(key for key in index.keys() | owners.keys() if index.get(key) != owners.get(key))
        raise ValueError(f"{path.name} 客户第 14 章索引与第 07 章 BL/AC 不符：{'、'.join(wrong)}")


def check_tables(path, tables, chapters, cards, owners):
    scope = set()
    index = {}
    for header, values, headings, location in tables:
        offset = int(location.rsplit(":", 1)[-1]) - 1
        if chapters[6][2] < offset < chapters[6][3] and header[0] in TABLE_COLUMNS:
            detail, required = TABLE_COLUMNS[header[0]]
            if not any(re.match(rf"^7\.\d+\.{detail}(?:[.、]|\s)", title) for title in headings):
                continue
            columns = ["是否必填" if name == "必填" else name for name in header]
            if len(columns) != len(values) or len(set(columns)) != len(columns):
                raise ValueError(f"{location} {header[0]}表列数不符或列名重复")
            row = dict(zip(columns, values))
            missing = [name for name in (header[0], *required) if not row.get(name)]
            if missing:
                raise ValueError(f"{location} {header[0]}表缺少定义：{'、'.join(missing)}")
        elif any(re.match(r"^0?4\.3(?:[.、]|\s)", title) for title in headings) and header[:1] == ["功能编号"]:
            if not {"功能名称", "功能说明", "优先级", "版本"}.issubset(header) or len(header) != len(values):
                raise ValueError(f"{location} 本期功能清单须列功能编号、功能名称、功能说明、优先级和版本")
            key = values[0]
            if key in scope or any(not value for value in values):
                raise ValueError(f"{location} 功能清单有重复编号或未填写项 {key}")
            scope.add(key)
        elif any(re.match(r"^14\.13(?:[.、]|\s)", title) for title in headings) and {"BL", "AC", "验证方式"}.issubset(header):
            if len(header) != len(values):
                raise ValueError(f"{location} 验收索引列数不符")
            row = dict(zip(header, values))
            for ac in re.split(r"[,，、\s]+", row["AC"]):
                if ac in index or not row["验证方式"]:
                    raise ValueError(f"{location} 验收索引重复或缺少验证方式 {ac}")
                index[ac] = row["BL"]
    if scope != cards:
        raise ValueError(f"{path.name}:{chapters[3][2] + 1} 第 04 章 4.3 本期功能清单与第 07 章卡片不符，"
                         f"清单独有 {sorted(scope - cards)}，卡片独有 {sorted(cards - scope)}")
    if index != owners:
        wrong = sorted(ac for ac in index.keys() | owners.keys() if index.get(ac) != owners.get(ac))
        raise ValueError(f"{path.name}:{chapters[13][2] + 1} 第 14 章 14.13 验收索引缺少、多出或错配 BL/AC：{', '.join(wrong)}")


def check_enterprise(path, lines, prd, tables, owners, *, module=False):
    template = Path(__file__).parent / "templates" / "enterprise-prd.md"
    source = template.read_text(encoding="utf-8")
    standard = outline(template, source.splitlines())
    actual = outline(path, lines, {n[0]: name for n, name, _, _ in standard[()]})
    chapters = actual.get((), [])
    chapter_index = {item[0]: item for item in chapters}
    required = [item[:2] for item in standard[()] if item[0] != (15,) or not module or (15,) in chapter_index]
    check_sequence(path, chapters, required, "企业目录")
    # Recognize the actual writing prompts without rejecting real API paths such as /projects/{id}.
    braces = re.compile(r"\{[^{}\n]+\}")
    prompts = set(braces.findall(source))
    for index, line in enumerate(lines, 1):
        for value in braces.findall(line):
            if value in prompts:
                raise ValueError(f"{path.name}:{index} 请填写模板占位内容 {value}")
    data_rows = {int(location.rsplit(":", 1)[1]) - 1: (header, values)
                 for header, values, _, location in tables}
    require_body(path, lines, ((), "首页", -1, chapters[0][2]), data_rows, required=False)
    for siblings in actual.values():
        for number, title, begin, end in siblings:
            if children := actual.get(number):
                require_body(path, lines, (number, title, begin, children[0][2]), data_rows, required=False)

    def check_children(parent):
        number, title, begin, _ = parent
        children = actual.get(number, [])
        check_sequence(path, children, [item[:2] for item in standard.get(number, [])], title, begin)
        for child in children:
            require_body(path, lines, child, data_rows)

    for chapter in chapters:
        if chapter[0] != (7,):
            check_children(chapter)
    check_risks(path, chapter_index[(16,)], tables, lines)
    _, _, start, stop = chapters[6]
    functions = actual.get((7,), [])
    if not functions or functions[0][0] != (7, 1) or title_key(functions[0][1]) != "功能模块总览":
        raise ValueError(f"{path.name}:{start + 1} 第 07 章须以 7.1 功能模块总览起稿")
    check_children(functions[0])
    if len(functions) < 2:
        raise ValueError(f"{path.name} 第 07 章缺少 7.2 起的 BL 功能卡")
    outputs = {}
    for position, (number, title, begin, end) in enumerate(functions[1:], 2):
        card = re.fullmatch(r"(BL-[0-9]+)\s+\S.*", title)
        if number != (7, position) or not card:
            raise ValueError(f"{path.name}:{begin + 1} 预期 7.{position} BL-编号 功能名称")
        key = card[1]
        details = actual.get(number, [])
        included = {item[0][-1] for item in details}
        required = [(number + (template_num[-1],), name) for template_num, name, _, _ in standard[(7, 2)]
                    if template_num[-1] <= 10 or template_num[-1] in included]
        check_sequence(path, details, required, key, begin)
        for item in details:
            require_body(path, lines, item, data_rows)
        outputs[key] = details[9][2:]
    for ac, (row, _, location) in prd.items():
        offset = int(location.rsplit(":", 1)[-1]) - 1
        begin, end = outputs.get(owners[ac], (-1, -1))
        if not begin < offset < end:
            raise ValueError(f"{location} {ac} 定义应在所属 BL 的第 10 项「输出及验收」内")
        if any(not row.get(name) for name in ("测试场景", "前置条件", "操作步骤", "验收点")):
            raise ValueError(f"{location} {ac} 须填写测试场景、前置条件、操作步骤和验收点")
    check_tables(path, tables, chapters, set(outputs), owners)
    check_references(path, lines, tables, (start, stop))
