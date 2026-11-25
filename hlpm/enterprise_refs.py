"""Resolve identifiers cited by enterprise feature cards against the PRD's definition tables."""
import re

from handoff_trace import EXAMPLE, HEADING


PREFIXES = {"字段编号": "FLD", "规则编号": "BR", "校验编号": "VAL", "异常编号": "EX", "AC": "AC"}
REFERENCE = re.compile(r"(?<![A-Za-z0-9_-])(?:FLD|BR|VAL|EX|AC)-[0-9]+(?![A-Za-z0-9_-])")


def check_references(path, lines, table_rows, chapter7_range):
    definitions = {}
    for header, values, _, location in table_rows:
        column = header[0]
        external = column == "引用编号"
        if not external and column not in PREFIXES:
            continue
        if column == "AC" and "验收点" not in header:
            continue  # An AC index points to definitions in its cards.
        key = values[0]
        if not REFERENCE.fullmatch(key):
            continue
        if external:
            if "来源及版本" not in header or len(values) != len(header):
                raise ValueError(f"{location} 外部引用 {key} 须填写来源及版本")
            source = values[header.index("来源及版本")].strip()
            if not source or re.match(r"^(?:TBD|N/?A|待补(?:充)?|待确认)(?:$|[\s（(:：，,])|^[-—…]+$", source, re.I):
                raise ValueError(f"{location} 外部引用 {key} 须填写来源及版本")
        elif key.partition("-")[0] != PREFIXES[column]:
            raise ValueError(f"{location} {key} 与{column}的类型 {PREFIXES[column]} 不符")
        if key in definitions:
            raise ValueError(f"{location} 重复定义 {key}，首次定义于 {definitions[key]}")
        definitions[key] = location

    start, stop = chapter7_range
    example_level = 0
    for index in range(start, stop):
        line = lines[index]
        heading = HEADING.match(line)
        if heading and (not example_level or len(heading[1]) <= example_level):
            example_level = len(heading[1]) if EXAMPLE.match(heading[2]) else 0
        if example_level:
            continue
        for key in REFERENCE.findall(line):
            if key not in definitions:
                raise ValueError(f"{path.name}:{index + 1} 第 07 章引用 {key} 缺少定义，"
                                 "请核对本版定义表或在外部引用索引注明来源及版本")
