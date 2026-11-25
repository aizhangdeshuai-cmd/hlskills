"""Check mechanical G2/G3 requirements in one existing knowledge article or section."""
import argparse
from pathlib import Path
import re
import sys


HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.+?)\s*$')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
PLACEHOLDER = re.compile(r'(?:[-—?？.…]+|TODO|TBD|待填(?:写)?|待补(?:充)?|待核|无|未核实|N/A)', re.I)
ANCHOR = re.compile(r'`[a-zA-Z_][^`\n]*`|\b\w+/[\w./-]+|\b\w+\.[a-zA-Z]+\b|\b[a-zA-Z]+_\w+\b')


def markdown_lines(text):
    """Keep physical line counts and omit headings, tables and check marks inside examples."""
    result = []
    fence = ''
    comment = False
    for raw in text.splitlines():
        mark = FENCE.match(raw)
        if fence:
            if mark and mark[1][0] == fence[0] and len(mark[1]) >= len(fence) and not mark[2].strip():
                fence = ''
            raw = ''
        elif mark and not comment:
            fence, raw = mark[1], ''
        else:
            visible = ''
            while raw:
                if comment:
                    _, end, raw = raw.partition('-->')
                    comment = not end
                else:
                    part, start, raw = raw.partition('<!--')
                    visible += part
                    comment = bool(start)
            raw = visible
        heading = HEADING.match(raw)
        result.append((len(heading[1]), re.sub(r'\s+#+$', '', heading[2]).strip())
                      if heading else (0, raw.strip()))
    return result


def section_end(lines, start):
    level = lines[start][0]
    return next((i for i in range(start + 1, len(lines)) if 0 < lines[i][0] <= level), len(lines))


def selected_lines(root, target):
    name, sep, title = target.partition('#')
    path = Path(name)
    if (path.is_absolute() or len(path.parts) < 2 or path.parts[0] != 'knowledge'
            or path.parts[1].casefold() == 'doc' or any(p.startswith('.') for p in path.parts)
            or path.suffix.lower() != '.md'):
        raise ValueError('路径须为当前项目 knowledge/ 中的 Markdown 正文')
    full = root / path
    if any((root / parent).is_symlink() for parent in (path, *path.parents)):
        raise ValueError('知识正文不能经由符号链接')
    lines = markdown_lines(full.read_text(encoding='utf-8-sig'))
    if not sep:
        return lines
    matches = [i for i, (depth, text) in enumerate(lines) if depth and text == title]
    if len(matches) != 1:
        raise ValueError(f'标题「{title}」须唯一，实际匹配 {len(matches)} 处')
    start = matches[0]
    return lines[start:section_end(lines, start)]


def filled(value):
    value = value.strip().strip('`').strip()
    return bool(value) and not PLACEHOLDER.fullmatch(value)


def cells(row):
    return [cell.strip() for cell in re.split(r'(?<!\\)\|', row.strip().strip('|'))]


def qa_count(block):
    for i in range(len(block) - 1):
        header, rule = block[i][1], block[i + 1][1]
        if ('|' not in header or len(cells(header)) != 2 or len(cells(rule)) != 2
                or not all(re.fullmatch(r':?-{3,}:?', col) for col in cells(rule))):
            continue
        count = 0
        for depth, row in block[i + 2:]:
            if depth or '|' not in row:
                break
            values = cells(row)
            if len(values) != 2 or not all(filled(value) for value in values):
                return -1
            count += 1
        return count
    return 0


def decision_errors(lines):
    heads = [i for i, (depth, _) in enumerate(lines) if depth]
    quick = next((i for i in heads if '速查' in lines[i][1]), None)
    if quick is None or any(lines[i][0] >= lines[quick][0] for i in heads if i < quick):
        yield '手册的首个主题须为速查'
    elif not 8 <= qa_count(lines[quick + 1:section_end(lines, quick)]) <= 10:
        yield '速查须有 8–10 行非空的两列问答'
    for title in ('规范冲突处理', '配方', '一句话原则'):
        for i, (depth, text) in enumerate(lines):
            if depth:
                if title not in text:
                    continue
                body = ' '.join(t for d, t in lines[i + 1:section_end(lines, i)] if not d)
            else:
                label = re.match(r'^\*\*(.+?)\*\*(.*)$', text)
                if not label or title not in label[1]:
                    continue
                # Bold inline subsections are also used in the original decision manual.
                body_lines = [label[2]]
                for d, t in lines[i + 1:]:
                    if d or t.startswith('**'):
                        break
                    body_lines.append(t)
                body = ' '.join(body_lines)
            if filled(body) and (title != '配方' or re.search(r'(?:\d+[.、)）]|[①-⑳]|步骤\s*\d+)', body)):
                break
        else:
            yield f'缺少有正文的「{title}」' + ('及编号步骤' if title == '配方' else '')


def layer_errors(lines, prefix):
    bans = [i for i, (d, text) in enumerate(lines) if d and '禁止事项' in text]
    if not any(any(filled(t) for d, t in lines[i + 1:section_end(lines, i)] if not d) for i in bans):
        yield '须有含正文的禁止事项小节'
    checks = [i for i, (d, text) in enumerate(lines) if d and '覆盖自检' in text]
    if len(checks) != 1:
        yield '须有唯一覆盖自检小节'
        return
    start = checks[0]
    check_body = lines[start + 1:section_end(lines, start)]
    if not any(filled(t) for d, t in check_body if not d):
        yield '覆盖自检须有正文'
    if any('❌' in re.sub(r'❌\s*数\s*[：:]\s*0\b', '', text) for _, text in check_body):
        yield '覆盖自检报告存在未核项'
    if not prefix:
        return
    ids = {f'{prefix}{n}' for n in range(1, 13)}
    evidence_sections = set()
    for i, (depth, title) in enumerate(lines[:start]):
        if not depth:
            continue
        for first, last in re.findall(rf'(?<![A-Z0-9]){prefix}(\d+)(?:\s*[-–—~至]\s*{prefix}?(\d+))?(?![A-Z0-9])', title):
            end = int(last or first)
            if 1 <= int(first) <= end <= 12:
                body = ' '.join(t for d, t in lines[i + 1:min(start, section_end(lines, i))] if not d)
                if ANCHOR.search(body):
                    evidence_sections.update(f'{prefix}{n}' for n in range(int(first), end + 1))
    seen = set()
    for _, text in check_body:
        for key, status in re.findall(rf'(?<![A-Z0-9])({prefix}\d+)(?:\s*\|)?\s*(✅|❌)', text):
            if status != '✅' or key in seen or key not in ids:
                yield f'{key} 失败、重复或超出本层编号范围'
            seen.add(key)
            if text.startswith('|'):
                row = cells(text)
                if len(row) != 3 or row[:2] != [key, '✅'] or not filled(row[2]) or not ANCHOR.search(row[2]):
                    yield f'{key} 缺少证据锚点'
            elif key not in evidence_sections:
                yield f'{key} 缺少含源码锚点的对应小节'
    missing = sorted(ids - seen, key=lambda key: int(key[1:]))
    if missing:
        yield '覆盖自检缺少 ' + '、'.join(missing)


ORDINAL = r'[一二三四五六七八九十百零〇0-9]+'


def integration_mapping(lines, target, sources):
    """Compare chapter identities, independent of the numbers claimed by the view."""
    errors, totals = [], []
    def chapters(article, name):
        depth = article[0][0] + 1 if '#' in name and article else 2
        titles = [text for level, text in article if level == depth]
        if not titles or len(set(titles)) != len(titles):
            errors.append(f'{name} 的直接子标题为空或重复')
        return titles

    dest = chapters(lines, target)
    aliases = {}
    for title in dest:
        match = re.match(rf'^({ORDINAL})[、.．]\s*', title)
        if match:
            num = match[1]
            aliases[num] = None if num in aliases else title
    expected = {name: chapters(article, name) for name, article in sources.items()}
    # The original package uses doc/std/foo.md where existing knowledge uses knowledge/std/foo.md.
    names = {re.sub(r'^knowledge/', '', name): name for name in sources}
    mapped = {name: set() for name in expected}
    tables = set()
    maps = [i for i, (d, title) in enumerate(lines) if d and '来源映射' in title]
    if len(maps) != 1:
        return ['须有唯一来源映射小节'], []
    block = lines[maps[0] + 1:section_end(lines, maps[0])]
    for i, (_, raw) in enumerate(block):
        header = cells(raw)
        if len(header) != 2 or not header[0].endswith('二级标题'):
            continue
        key = header[0][:-4].strip().strip('`')
        name = names.get(re.sub(r'^(?:doc|knowledge)/', '', key))
        if not name or name in tables:
            errors.append(f'映射表来源未声明或重复：{key}')
            continue
        tables.add(name)
        if (header[1] != '本篇位置' or i + 1 >= len(block)
                or not re.fullmatch(r'\|?\s*:?-{3,}:?\s*\|\s*:?-{3,}:?\s*\|?', block[i + 1][1])):
            errors.append(f'{name} 缺少两列来源映射表')
            continue
        for depth, row in block[i + 2:]:
            if depth or '|' not in row:
                break
            fields = cells(row)
            if len(fields) != 2:
                errors.append(f'{name} 映射行须为两列')
                continue
            src, dests = fields
            if src not in expected[name] or src in mapped[name]:
                errors.append(f'{name} 来源标题未知或重复：{src}')
            mapped[name].add(src)
            if re.fullmatch(rf'{ORDINAL}(?:、{ORDINAL})*', dests):
                targets = [aliases.get(n) for n in dests.split('、')]
            else:
                targets = [t.strip() for t in re.split('[；;]', dests)]
            if any(t not in dest for t in targets) or len(set(targets)) != len(targets):
                errors.append(f'{name}「{src}」落点缺失、歧义或重复：{dests}')
    for name, titles in expected.items():
        missing = set(titles) - mapped[name]
        if missing:
            errors.append(f'{name} 漏映射：' + '、'.join(sorted(missing)))
        totals.append(f'{name} {len(set(titles) & mapped[name])}/{len(titles)}')
    return errors, totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='项目根目录')
    parser.add_argument('kind', choices=('decision', 'standard', 'data', 'remote', 'integration'))
    parser.add_argument('target', help='knowledge/文件.md 或 knowledge/文件.md#精确标题')
    parser.add_argument('--source', action='append', default=[], help='集成视图的规范正文或章节，可重复')
    args = parser.parse_args()
    if (args.kind == 'integration') != bool(args.source):
        parser.error('integration 必须提供 --source，其他模式不接受 --source')
    if len(set(args.source)) != len(args.source) or args.target in args.source:
        parser.error('来源须独立且唯一')
    try:
        root = args.root.resolve()
        lines = selected_lines(root, args.target)
        sources = {name: selected_lines(root, name) for name in args.source}
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f'{args.target}：{error}\n')
    totals = []
    if args.kind == 'integration':
        errors, totals = integration_mapping(lines, args.target, sources)
    else:
        decision = args.kind == 'decision'
        limit = 800 if decision else 200
        prefix = {'data': 'D', 'remote': 'F'}.get(args.kind)
        errors = list(decision_errors(lines) if decision else layer_errors(lines, prefix))
        if len(lines) > limit:
            errors.append(f'{len(lines)} 行超过 {limit} 行上限')
    if errors:
        for error in errors:
            print(f'{args.target}：{error}', file=sys.stderr)
        return 1
    if totals:
        print('来源映射：' + '，'.join(totals))
    print(f'{args.target}（{len(lines)} 行）结构核验通过。证据含义、历史需求盲验与负责人确认另行记录。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
