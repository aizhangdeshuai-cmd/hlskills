"""Check the actual text of enterprise PRD sections and their status declarations."""
import re


RISK_COLUMNS = ["未确认需求", "外部依赖", "后续优化事项"]
OWNER = r"负责人|责任人|决定人"
MILESTONE = r"确认节点|确认时点|确认期限|确认时间"
REASON = r"原因|理由|业务原因"
STATUS = re.compile(
    r"(?<![A-Za-z0-9_-])(?:N/A|TBD)(?![A-Za-z0-9_-])|"
    r"(?:不适用|待确认)(?=$|[\s。；;，,：:、（(]|负责人[：:]|原因[：:])", re.I)
PLACEHOLDER = re.compile(
    r"无|略|同上|见上文|同前|见下文|暂无|无要求|无内容|空|TBD|TODO|N/?A|待定|待确认|待明确|待补充?|待填写?|"
    r"未填写|占位(?:符)?|暂不确定|暂未确定|未确定|另行确认|后续(?:确认|补充|再定)|不适用|(?:本期|本次|本项目)?"
    r"(?:暂)?(?:不涉及|不需要|无此需求|不适用|不支持|不考虑)|相关(?:人员|负责人)|某某|具体业务理由|角色或姓名|"
    r"日期或明确的评审节点|视情况(?:而定)?|后续|另定|待通知", re.I)


def meaningful(value):
    value = value.strip(" \t\n>*_~`-—–…:：。.,，；;（）()【】[]+「」“”\"'")
    return (bool(re.search(r"\w", value)) and not PLACEHOLDER.fullmatch(value)
            and not re.fullmatch(r"\{[^{}]+\}|x{2,}|待(?:产品|业务|开发)?确认", value, re.I))


def label_value(text, names):
    match = re.search(rf"(?:{names})\s*[：:]\s*(.*?)(?=[。；;\n]|(?:{OWNER}|{MILESTONE}|{REASON})\s*[：:]|$)", text)
    return match[1] if match else ""


def check_pending(text, where):
    for names, label in ((OWNER, "负责人"), (MILESTONE, "确认节点")):
        if not meaningful(label_value(text, names)):
            raise ValueError(f"{where} 待确认事项缺少可识别的{label}")


def check_status(text, where):
    """Each declaration owns its explanation, including when several share a paragraph."""
    # Quoted UI strings (e.g. 状态显示「待确认」) describe product behavior.
    text = text.replace("**", "").replace("__", "").replace("`", "")
    quotes = [m.span() for m in re.finditer(r"[「“\"][^」”\"\n]*[」”\"]", text)]
    # Owner or milestone value 'TBD' belongs to the preceding declaration.
    markers = []
    for match in STATUS.finditer(text):
        if any(start < match.start() < end for start, end in quotes):
            continue
        prefix, suffix = text[:match.start()], text[match.end():]
        if re.search(rf"(?:{OWNER}|{MILESTONE}|{REASON})\s*[：:]\s*$", prefix):
            continue
        # A declaration starts a clause or finishes a stated open issue.
        # A UI feedback string such as 保存结果待确认，请查询结果 is not a declaration.
        if (match[0].upper() not in ("TBD", "N/A")
                and prefix.strip(" \t*_>-") and not re.search(r"[。；;：:，,\n]\s*[*_]*$", prefix)
                and not re.match(rf"\s*(?:$|[。；;：:]|(?:{OWNER}|{MILESTONE}|{REASON})\s*[：:])", suffix)):
            continue
        markers.append(match)
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        rest = text[marker.end():end]
        if marker[0].upper() in ("N/A", "不适用"):
            reason = label_value(rest, REASON)
            if not reason:
                stated = re.match(r"[\s。；;：:，,（(—-]*(?:因为|由于|因)(?![：:])(.+)", rest)
                reason = stated[1] if stated else ""
            if not meaningful(reason):
                raise ValueError(f"{where} 不适用项缺少具体业务原因")
        else:
            check_pending(rest, where)
    return bool(markers)


def check_risks(path, chapter, table_rows, lines):
    _, _, start, stop = chapter
    rows = [(header, values, location) for header, values, _, location in table_rows
            if start < int(location.rsplit(":", 1)[1]) - 1 < stop]
    if any(re.match(r"^ {0,3}#{2,6}\s", line) for line in lines[start + 1:stop]):
        raise ValueError(f"{path.name}:{start + 1} 第 16 章请将全部事项归入指定三栏")
    if not rows or any(header != RISK_COLUMNS or len(values) != 3 for header, values, _ in rows):
        raise ValueError(f"{path.name}:{start + 1} 第 16 章须使用且仅使用有数据的三栏表：{'、'.join(RISK_COLUMNS)}")
    for _, values, location in rows:
        for col, value in enumerate(values):
            if value.strip() == "无":
                continue
            where = f"{location} 第 16 章「{RISK_COLUMNS[col]}」"
            qualified = check_status(value, where)
            if not meaningful(value):
                raise ValueError(f"{where} 请填写实项或“无”")
            if not qualified and col == 0:
                check_pending(value, where)


def require_body(path, lines, section, data_rows, *, required=True):
    number, title, start, stop = section
    name = ".".join(map(str, number)) + " " + title
    has_body = False
    paragraph = []

    def check_paragraph():
        if paragraph:
            where = f"{path.name}:{paragraph[0][0] + 1} {name}"
            text = "\n".join(line for _, line in paragraph)
            check_status(text, where)
            has_value = any(meaningful(line) for _, line in paragraph)
            paragraph.clear()
            return has_value
        return False

    for pos in range(start + 1, stop):
        line = re.sub(r"</?[A-Za-z][^>]*>", "", lines[pos]).strip()
        if not line or line.startswith(("#", "|")):
            has_body |= check_paragraph()
            if pos in data_rows:
                header, row = data_rows[pos]
                metadata = "。".join(f"{label}：{value}" for label, value in zip(header, row)
                                     if re.fullmatch(OWNER + "|" + MILESTONE + "|" + REASON, label))
                for col, value in enumerate(row):
                    # An explicitly labelled data column can qualify a status in the same row.
                    if col < len(header) and not re.fullmatch(OWNER + "|" + MILESTONE + "|" + REASON, header[col]):
                        check_status(value + ("。" + metadata if metadata else ""), f"{path.name}:{pos + 1} {name}")
                if any(meaningful(value) for value in row):
                    has_body = True
            continue
        bullet = re.match(r"(?:[-*+] |\d+[.)] )", line)
        if bullet and not re.match(rf"(?:{OWNER}|{MILESTONE}|{REASON})\s*[：:]", line[bullet.end():]):
            has_body |= check_paragraph()
        paragraph.append((pos, line))
    has_body |= check_paragraph()
    if required and not has_body:
        raise ValueError(f"{path.name}:{start + 1} {name} 缺少正文，不适用请说明原因，待确认请写负责人和确认节点")
