"""Validate a split PRD's appendix decisions and the selected chapter files."""
from pathlib import Path
import re

from enterprise_content import require_body
from enterprise_prd import check_acceptance_index, check_sequence, check_template_prompts, outline
from handoff_trace import read_markdown, tables


SUPPLEMENTS = {
    "08 数据需求设计": (8, "data-requirements.md"),
    "09 接口需求设计": (9, "interface-requirements.md"),
    "14 测试及验收标准": (14, "acceptance-criteria.md"),
}


def selected_supplements(path, rows, *, mini=False, stage="test"):
    """Return the declared local files after checking all three independent decisions."""
    files = {}
    seen = set()
    root = path.parent.resolve()
    appendix = r"^(?:[0-9.、 ]+)?附录(?:$|[\s：:·（(])" if mini else r"^17[.、 ]+附录(?:$|[\s（(])"
    for header, values, headings, location in rows:
        if header != ["内容", "产品阶段安排"] or not any(re.match(appendix, h) for h in headings):
            continue
        if not values or values[0] not in SUPPLEMENTS:
            continue  # The same appendix may also list a prototype or detailed test cases.
        if len(values) != 2 or values[0] in seen:
            raise ValueError(f"{location} 附录分册登记项无效或重复：{' | '.join(values)}")
        label, choice = values
        chapter, filename = SUPPLEMENTS[label]
        seen.add(label)
        link = re.fullmatch(r"\[[^\]\n]+\]\(([^)\n]+)\)", choice)
        if not link:
            if chapter == 14 and choice == "测试阶段生成" and stage == "prd":
                continue
            if (chapter != 14 and "](" not in choice and
                    re.match(r"^(?:开发阶段编写|产品阶段不生成|本期不涉及)(?:$|[\s：:，,。；;（(、·—-])", choice)):
                continue
            raise ValueError(f"{location} {label} 请登记本版 {filename} 的链接"
                             + ("，此分册必交" if chapter == 14 else "或已确认的产品阶段安排"))
        if link[1] not in {filename, "./" + filename}:
            raise ValueError(f"{location} {label} 应链接本版同目录的 {filename}")
        target = root / filename
        if not target.is_file() or not target.resolve().is_relative_to(root) or target.samefile(path):
            raise ValueError(f"{location} {filename} 缺失或未指向本版独立分册")
        files[chapter] = target
    missing = SUPPLEMENTS.keys() - seen
    if missing:
        raise ValueError(f"{path.name} 附录「内容 | 产品阶段安排」缺少：{'、'.join(sorted(missing))}")
    return files


def check_features_link(path, lines, scope_section, appendix):
    anchor = re.compile(r"""<a\s+id\s*=\s*["']features["']\s*>\s*</a>""", re.I)
    start, stop = scope_section[2:]
    # Existing Markdown authoring tools may put the anchor just before the heading.
    while start > 0 and not lines[start - 1].strip():
        start -= 1
    targets = [pos for pos, line in enumerate(lines) for _ in anchor.finditer(line)]
    if len(targets) != 1 or not max(0, start - 1) <= targets[0] < stop:
        raise ValueError(f"{path.name}:{scope_section[2] + 1} 4.3 须提供可唯一定位的 features 锚点")
    if not any(re.search(r"\[[^\]]+\]\(#features\)", line) for line in lines[appendix[2] + 1:appendix[3]]):
        raise ValueError(f"{path.name}:{appendix[2] + 1} 附录须链接到第 04 章的 #features")


def check_omitted_links(path, lines, omitted):
    if not omitted:
        return
    for index, line in enumerate(lines, 1):
        visible = re.sub(r"(`+).*?\1", "", line)
        for match in re.finditer(r"(?<!\\)\[[^\]\n]*\]\(\s*<?(?:\./)?([^/#?\s)>]+)(?=[?#>\s)])", visible):
            if match[1] in omitted:
                raise ValueError(f"{path.name}:{index} 附录已确认本期不生成 {match[1]}，请修正该处链接")


def check_single(path, lines, rows, owners, stage):
    if stage == "test" or any(h == ["内容", "产品阶段安排"] and v[0] in SUPPLEMENTS for h, v, _, _ in rows):
        raise ValueError(f"{path.name} 单文件 PRD 追加分册或测试交付时须改用 split-mini 或 split")
    check_omitted_links(path, lines, {name for _, name in SUPPLEMENTS.values()} | {"test-cases.md"})
    sections = [i for i, line in enumerate(lines) if re.fullmatch(r" {0,3}##\s+验收索引\s*", line)]
    if len(sections) != 1:
        raise ValueError(f"{path.name} 单文件 PRD 须提供唯一的「## 验收索引」")
    start = sections[0]
    stop = next((i for i in range(start + 1, len(lines)) if re.match(r"^ {0,3}#{1,2}\s", lines[i])), len(lines))
    check_acceptance_index(path, rows, owners, ((), "验收索引", start, stop), label="验收索引")


def check_attachments(path, main_lines, rows, owners, criteria, *, mini=False, stage="test"):
    definition_rows = []
    selected = selected_supplements(path, rows, mini=mini, stage=stage)
    omitted = {filename for chapter, filename in SUPPLEMENTS.values() if chapter not in selected}
    if 14 not in selected:
        omitted.add("test-cases.md")
    check_omitted_links(path, main_lines, omitted)
    for chapter, attachment in selected.items():
        template = Path(__file__).parent / "templates" / attachment.name
        source = template.read_text(encoding="utf-8")
        standard = outline(template, source.splitlines())
        lines, _ = read_markdown(attachment)
        check_template_prompts(attachment, lines, source)
        check_omitted_links(attachment, lines, omitted)
        actual = outline(attachment, lines)
        check_sequence(attachment, actual.get((), []), [s[:2] for s in standard[()]], "分册目录")
        children = actual.get((chapter,), [])
        required = standard[(chapter,)]
        if mini and chapter == 14:
            included = {s[0] for s in children}
            required = [s for s in required if s[0] in included or s[0] == (14, 13)]
        check_sequence(attachment, children, [s[:2] for s in required], "分册小节")
        attachment_rows = list(tables(attachment, lines=lines))
        for header, _, _, location in attachment_rows:
            if header[0] == "AC" and "验收点" in header:
                raise ValueError(f"{location} AC 验收点请在 prd.md 的所属 BL 卡内定义，分册引用已有编号")
        data_rows = {int(loc.rsplit(":", 1)[1]) - 1: (header, values)
                     for header, values, _, loc in attachment_rows}
        for section in children:
            require_body(attachment, lines, section, data_rows)
        if chapter == 14:
            if mini and not any(s[0] in {(14, 1), (14, 11), (14, 12)} for s in children):
                # A compact acceptance document can state scope and pass conditions in its introduction.
                _, title, start, _ = actual[()][0]
                require_body(attachment, lines, ((14,), title, start, children[0][2]), data_rows)
            check_acceptance_index(attachment, attachment_rows, owners, children[-1], criteria=criteria, stage=stage)
        definition_rows.extend(attachment_rows)
    return definition_rows
