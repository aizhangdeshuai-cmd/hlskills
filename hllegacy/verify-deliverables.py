"""核验现有 knowledge/ 中 hllegacy 交付物的结构、实证位置与独立清单。"""
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
import json
import linecache
from pathlib import Path
import re
import sys

# Use the same document scope as ordinary knowledge retrieval.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'hlkb'))
from kb import markdown_files
from diagram_inventory import validate_diagram
from observations import KINDS as OBSERVABLE, verify_observations


COLUMNS = {
    'stack': '标识 类别 版本依据 用途 证据',
    'modules': '标识 职责 边界与依赖 入口 证据',
    'architecture': '标识 起点 终点 数据或动作 证据',
    'database': '标识 实体与键 关系或约束 迁移或索引 证据',
    'api': '标识 调用方 输入 输出 权限 证据',
    'ui': '标识 状态 样式值 交互 截图 证据',
    'quality': '标识 口径 实测结果 方法 证据',
    'security': '标识 检查范围 方法 发现与影响 处置 证据',
    'debt': '标识 严重性 影响 改进与验收 证据',
}
FIELDS = re.compile(r'^(范围|版本|状态|核验|实测对照|反查依据|反查清单|框架方法|理由)[：:]\s*(.*)$')
HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.*)$')
MARKER = re.compile(r'<!--\s*hllegacy:([a-z]+)\s*-->\s*(?:#+\s*)?$')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
PLACEHOLDER = re.compile(r'^(?:[-—?？.…]+|todo|tbd|fixme|n/?a|占位(?:符)?|待填(?:写)?|待补(?:充)?|待定|未知|未填写|<[^<>]+>)$', re.I)
NOT_CHECKED = re.compile(r'(?:未运行|未执行|未核验|未验证|未测|待核验|待验证|未检查|跳过)[。.]?')
API_ID = re.compile(r'(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|TRACE|CONNECT) /\S*|(?:RPC|EVENT|CLI) \S.*')
LEAKS = {
    '私钥标记': re.compile(r'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----'),
    '凭据标识': re.compile(r'\b(?:AKIA[A-Z0-9]{16}|gh[pousr]_[a-zA-Z0-9]{30,}|github_pat_[\w]{35,}|sk-(?:proj-)?[a-zA-Z0-9_-]{24,}|xox[baprs]-[a-zA-Z0-9-]{15,})\b'),
    '明文 Bearer 凭据': re.compile(r'\bBearer\s+(?!example\b|placeholder\b)[a-z0-9_+/.-]{24,}={0,2}(?!\w)', re.I),
    '带明文密码的连接串': re.compile(
        r'\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s/:@]+:'
        r'(?!(?:redacted|masked|example|placeholder|your_password)@)[A-Za-z0-9][^\s/@<>{}*]*@', re.I),
}
BAD_CONTROL = re.compile(r'[\x00-\x08\x0e-\x1a\x1c-\x1f]')


@dataclass
class Section:
    kind: str
    path: Path
    start: int
    level: int
    end: int = 0
    prose: list = field(default_factory=list)
    diagrams: list = field(default_factory=list)
    leaks: list = field(default_factory=list)


def visible_line(line, in_comment):
    """Remove HTML comments from prose, preserving line numbers."""
    parts = []
    while line:
        if in_comment:
            _, end, line = line.partition('-->')
            in_comment = not end
        else:
            before, begin, line = line.partition('<!--')
            parts.append(before)
            in_comment = bool(begin)
    return ''.join(parts), in_comment


def sections(path):
    stack, result = [], []
    fence = ''
    diagram = None
    in_comment = False
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    for number, raw in enumerate(lines, 1):
        mark = FENCE.match(raw)
        line = ''
        marker = None
        if fence:
            if mark and mark[1][0] == fence[0] and len(mark[1]) >= len(fence) and not mark[2].strip():
                if diagram is not None and stack:
                    stack[-1].diagrams.append(diagram)
                fence, diagram = '', None
            elif diagram is not None:
                diagram.append(raw.strip())
        elif not in_comment and mark:
            fence = mark[1]
            if mark[2].strip().lower() == 'mermaid':
                diagram = []
        else:
            heading = None if in_comment else HEADING.match(raw)
            if heading:
                marker = MARKER.search(heading[2])
            line, in_comment = visible_line(raw, in_comment)
            heading = HEADING.match(line)
            if heading:
                level = len(heading[1])
                while stack and level <= stack[-1].level:
                    stack.pop().end = number - 1
                if marker and marker[1] in COLUMNS:
                    section = Section(marker[1], path, number, level)
                    stack.append(section)
                    result.append(section)
        if stack:
            section = stack[-1]
            section.prose.append((number, line))
            for label, pattern in LEAKS.items():
                if pattern.search(raw):
                    section.leaks.append((number, label))
    for section in stack:
        section.end = len(lines)
    return result


def content(value):
    value = value.strip().strip('`').strip()
    return bool(value) and not PLACEHOLDER.fullmatch(value)


def cells(line):
    # Markdown requires an embedded pipe to be escaped even within a code span.
    return [v.strip().strip('`').replace(r'\|', '|').strip()
            for v in re.split(r'(?<!\\)\|', line.strip()[1:-1])]


def table_rows(section, issue, *, required=True, columns=None):
    wanted = (columns or COLUMNS[section.kind]).split()
    header, seen_table = None, False
    rows = []
    for i, (number, raw) in enumerate(section.prose):
        line = raw.strip()
        if not (line.startswith('|') and line.endswith('|')):
            header = None
            continue
        values = cells(line)
        if i + 1 < len(section.prose):
            next_line = section.prose[i + 1][1].strip()
            if next_line.startswith('|') and next_line.endswith('|') and all(
                re.fullmatch(r':?-{3,}:?', cell) for cell in cells(next_line)
            ):
                header = None
                if set(wanted).issubset(values):
                    seen_table = True
                    if len(values) != len(set(values)) or len(cells(next_line)) != len(values):
                        issue(number, '主表表头重复或分隔行列数不符')
                    else:
                        header = values
                continue
        if header is None or all(re.fullmatch(r':?-{3,}:?', cell) for cell in values):
            continue
        if len(values) != len(header):
            issue(number, '主表数据列数不符')
            continue
        row = dict(zip(header, values))
        for col in wanted:
            if not content(row[col]):
                issue(number, f'主表的「{col}」缺值或含占位符')
        rows.append((number, row))
    if required and not seen_table:
        issue(section.start, f'缺少主表或必填列（{COLUMNS[section.kind]}）')
    elif required and not rows:
        issue(section.start, '主表缺少数据行')
    return rows


def project_file(sources, name):
    label = ''
    if '//' in name:
        label, name = name.split('//', 1)
        if not label or label not in sources:
            raise ValueError('证据根未在 knowledge/hllegacy-sources.json 或 --source 中声明')
    part = Path(name)
    blocked_dirs = {'.git', '.ssh', '.aws', '.gnupg', '.kube', '.azure'}
    blocked_names = {'.env', '.netrc', '.npmrc', '.pypirc', 'credentials', 'id_rsa',
                     'id_dsa', 'id_ed25519', 'id_ecdsa'}
    lower = part.name.casefold()
    if (not name or part.is_absolute() or '..' in part.parts
            or any(c.casefold() in blocked_dirs for c in part.parts)
            or lower in blocked_names or lower.startswith('.env.')
            or part.suffix.casefold() in {'.pem', '.key', '.p12', '.pfx', '.jks'}):
        raise ValueError('须引用项目内非敏感的实际文件')
    path = sources[label] / part
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError('须引用项目内普通文件，路径不能含符号链接')
    return path


def evidence_sources(root, overrides):
    """Project manifests may name bundled directories; selecting outside roots is an explicit CLI action."""
    sources = {'': root}
    manifest = root / 'knowledge' / 'hllegacy-sources.json'
    aliases = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]*')
    if manifest.is_symlink():
        raise ValueError('证据根清单不能是符号链接')
    if manifest.exists():
        def unique(pairs):
            if len(pairs) != len(dict(pairs)):
                raise ValueError('证据根清单内名称重复')
            return dict(pairs)

        mapping = json.loads(manifest.read_text(encoding='utf-8-sig'), object_pairs_hook=unique)
        if not isinstance(mapping, dict):
            raise ValueError('证据根清单须为名称到项目内目录的 JSON 对象')
        for label, directory in mapping.items():
            if not aliases.fullmatch(label) or not isinstance(directory, str) or not directory:
                raise ValueError('证据根清单中的名称或目录无效')
            part = Path(directory)
            if part.is_absolute() or any(p.startswith('.') for p in part.parts):
                raise ValueError('清单中的目录须位于项目内，外仓用 --source 显式指定')
            location = root / part
            if location.resolve() != location:
                raise ValueError('清单中的证据根不能经过符号链接')
            sources[label] = location
    explicit = set()
    for item in overrides:
        label, sep, directory = item.partition('=')
        if not sep or not directory or not aliases.fullmatch(label) or label in explicit:
            raise ValueError('--source 应为 NAME=DIR，名称唯一且以字母开头')
        selected_root = Path(directory)
        if selected_root.is_symlink() or not selected_root.is_dir():
            raise ValueError('--source 须指向本地实际目录')
        explicit.add(label)
        sources[label] = selected_root.resolve(strict=True)
    return sources


def line_index(path, cache):
    if path not in cache:
        line_count, blank = 0, set()
        try:
            with path.open(encoding='utf-8-sig') as stream:
                for line_count, text in enumerate(stream, 1):
                    if BAD_CONTROL.search(text):
                        raise ValueError('二进制控制字符')
                    if not text.strip():
                        blank.add(line_count)
            cache[path] = (line_count, blank)
        except (UnicodeError, ValueError):
            cache[path] = None
    if cache[path] is None:
        raise ValueError('引用须指向 UTF-8 文本文件中的实证行')
    return cache[path]


def evidence(sources, value, report_ranges, lengths):
    for ref in value.split('；'):
        match = re.fullmatch(r'(.+):([1-9]\d*)(?:#([\w.$-]+))?', ref.strip().strip('`'))
        if not match:
            raise ValueError('证据应使用相对路径:正行号，可追加 #符号，多条用中文分号分隔')
        path = project_file(sources, match[1])
        line = int(match[2])
        if any(start <= line <= end for start, end in report_ranges.get(path, ())):
            raise ValueError('报告段落不能作为这些交付物的独立证据')
        line_count, blank = line_index(path, lengths)
        if line > line_count:
            raise ValueError('引用行号超出文件范围')
        if line in blank:
            raise ValueError('引用行为空，请定位到实际证据')
        if match[3]:
            source = linecache.getline(str(path), line)
            if not re.search(r'(?<!\w)' + re.escape(match[3]) + r'(?!\w)', source):
                raise ValueError('所列符号与证据行不符，请复核版本和位置')


def screenshot(sources, name):
    path = project_file(sources, name)
    size = path.stat().st_size
    with path.open('rb') as stream:
        data = stream.read(32)
        stream.seek(max(0, size - 12))
        tail = stream.read(12)
    formats = {
        '.png': (data.startswith(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
                 and int.from_bytes(data[16:20], 'big') and int.from_bytes(data[20:24], 'big')
                 and tail == b'\x00\x00\x00\x00IEND\xaeB`\x82'),
        '.jpg': size >= 32 and data.startswith(b'\xff\xd8\xff') and tail.endswith(b'\xff\xd9'),
        '.gif': (data.startswith((b'GIF87a', b'GIF89a'))
                 and int.from_bytes(data[6:8], 'little') and int.from_bytes(data[8:10], 'little')
                 and tail.endswith(b';')),
        '.webp': (data.startswith(b'RIFF') and int.from_bytes(data[4:8], 'little') + 8 == size
                  and data[8:12] == b'WEBP' and data[12:16] in (b'VP8 ', b'VP8L', b'VP8X')),
    }
    suffix = path.suffix.casefold()
    if not formats.get('.jpg' if suffix == '.jpeg' else suffix):
        raise ValueError('截图须为具有有效文件结构的 PNG、JPEG、GIF 或 WebP 图片')


def candidates(sources, kind, value, report_ranges, *, allow_empty=False):
    if value.startswith('@openapi-json:'):
        if kind != 'api':
            raise ValueError('OpenAPI 清单只适用于 api')
        path = project_file(sources, value.removeprefix('@openapi-json:'))
        if path in report_ranges:
            raise ValueError('反查来源不能使用标记报告自身')
        from openapi_inventory import endpoint_ids
        try:
            values = endpoint_ids(path)
        except ValueError as error:
            raise ValueError('OpenAPI 清单格式无效或存在未解析的路径') from error
    elif value.startswith('@'):
        path = project_file(sources, value[1:])
        if path in report_ranges:
            raise ValueError('反查来源不能使用标记报告自身')
        values = [s.strip() for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    else:
        values = [s.strip() for s in value.split('；')]
    if (not values and not allow_empty) or not all(content(v) for v in values):
        raise ValueError('反查清单缺少实际标识')
    if len(set(values)) != len(values):
        raise ValueError('反查清单内标识重复')
    return values


def implicit_methods(sources, value, report_ranges, expected, keys):
    if not value.startswith('@') or value.startswith('@openapi-json:'):
        raise ValueError('须引用框架注册导出的独立逐行清单')
    automatic = set(candidates(sources, 'api', value, report_ranges, allow_empty=True))
    if not automatic.issubset(expected):
        raise ValueError('框架方法超出完整注册清单')
    # A method with its own business behavior belongs in the primary table.
    visible_paths = {key.partition(' ')[2] for key in keys if API_ID.fullmatch(key)
                     and key.partition(' ')[0] not in ('CLI', 'EVENT', 'RPC', 'HEAD', 'OPTIONS')}
    for entry in automatic:
        method, _, path = entry.partition(' ')
        if not API_ID.fullmatch(entry) or method not in ('HEAD', 'OPTIONS') or path not in visible_paths:
            raise ValueError('只能折叠正文已有业务路由的自动 HEAD/OPTIONS')
        if method == 'HEAD' and 'GET ' + path not in keys:
            raise ValueError('折叠 HEAD 时须保留同路径的 GET')
    return automatic


def verify_section(section, sources, report_ranges, lengths, *, require_observations=False):
    errors = []
    observation_summary = ''
    relative = section.path.relative_to(sources[''])

    def issue(line, message):
        errors.append(f'{section.kind} {relative}:{line} {message}')

    def observation_file(name):
        source = project_file(sources, name)
        if source in report_ranges:
            raise ValueError('实测原件不能引用本次交付正文')
        return source

    def check(line, field_name, action, *args, **kwargs):
        try:
            return action(*args, **kwargs)
        except (OSError, UnicodeError, RuntimeError):
            issue(line, f'{field_name}：文件不可读、路径不存在或编码无效')
        except ValueError as error:
            issue(line, f'{field_name}：{error}')

    for number, label in section.leaks:
        issue(number, f'交付内容疑似暴露{label}，请脱敏')
    fields = {}
    for number, raw in section.prose:
        match = FIELDS.fullmatch(raw.strip())
        if match:
            name, value = match.groups()
            if name in fields:
                issue(number, f'字段「{name}」重复')
            fields[name] = (number, value.strip())
    for name in ['范围', '版本', '状态', '核验', '反查依据']:
        if name not in fields or not content(fields[name][1]):
            issue(section.start, f'缺少有效「{name}」')
    if '反查依据' in fields:
        number, value = fields['反查依据']
        check(number, '反查依据', evidence, sources, value, report_ranges, lengths)

    state = fields.get('状态', (0, ''))[1]
    verified_at, verification = fields.get('核验', (section.start, ''))
    if state != '未完成' and NOT_CHECKED.fullmatch(verification):
        issue(verified_at, '核验记录尚未执行')
    if state == '未完成':
        issue(section.start, '状态为未完成')
    elif state == '不适用' or state == '无发现':
        allowed = (state == '不适用' and section.kind in ('database', 'api', 'ui')
                   or state == '无发现' and section.kind == 'debt')
        if not allowed:
            issue(section.start, '此类别不支持声明的例外状态')
        if not content(fields.get('理由', (0, ''))[1]):
            issue(section.start, '例外状态缺少理由')
        if table_rows(section, issue, required=False):
            issue(section.start, '例外状态与主表中的实际数据行矛盾')
        number, value = fields.get('反查清单', (0, ''))
        if value and value != '无' and check(number, '反查清单', candidates, sources, section.kind,
                                           value, report_ranges, allow_empty=True):
            issue(number, '例外状态与非空反查清单矛盾')
    elif state != '完成':
        issue(section.start, '状态无效')
    else:
        keys = {}
        rows = table_rows(section, issue)
        for number, row in rows:
            key = row['标识']
            if key in keys:
                issue(number, '主表含重复标识')
            keys[key] = number
            check(number, '证据', evidence, sources, row['证据'], report_ranges, lengths)
            if section.kind == 'api' and not API_ID.fullmatch(key):
                issue(number, 'API 标识需含 HTTP 方法与绝对路由，或 RPC、EVENT、CLI 与名称')
            if section.kind == 'debt' and row['严重性'] not in ('严重', '重要', '次要'):
                issue(number, '严重性只能为严重、重要、次要')
            if section.kind == 'quality' and NOT_CHECKED.fullmatch(row['实测结果']):
                issue(number, '质量指标缺少本次实测结果')
            if section.kind == 'ui':
                check(number, '截图', screenshot, sources, row['截图'])
        if section.kind in ('architecture', 'database'):
            check(section.start, '图表对账', validate_diagram, section.kind, section.diagrams, rows)
        if section.kind in OBSERVABLE:
            if '实测对照' in fields:
                number, ref = fields['实测对照']
                path = check(number, '实测对照', project_file, sources, ref)
                if path:
                    cases = (table_rows(section, issue, required=False, columns='标识 场景 输入 输出')
                             if section.kind == 'api' else [])
                    observation_summary = check(number, '实测对照', verify_observations, section.kind,
                                                path, rows, section.diagrams,
                                                observation_file, cases)
            elif section.kind == 'api' and rows and all(
                    key.startswith(('RPC ', 'EVENT ', 'CLI ')) for key in keys):
                observation_summary = '清单仅含非 HTTP 入口，按对应协议复核'
            elif require_observations:
                issue(section.start, '缺少实测对照，无法核验交接中的业务事实')
            else:
                observation_summary = '仅结构核验，未绑定实测对照'
        if '反查清单' not in fields:
            issue(section.start, '状态为完成时须提供反查清单')
        else:
            number, value = fields['反查清单']
            expected = check(number, '反查清单', candidates, sources, section.kind, value, report_ranges)
            if expected is not None:
                expected_keys = set(expected)
                folded = set()
                if '框架方法' in fields:
                    at, inventory = fields['框架方法']
                    if section.kind != 'api':
                        issue(at, '框架方法只适用于 api')
                    else:
                        folded = check(at, '框架方法', implicit_methods, sources, inventory,
                                       report_ranges, expected_keys, keys) or set()
                missing = [i for i, candidate in enumerate(expected, 1) if candidate not in keys and candidate not in folded]
                extra = [line for key, line in keys.items() if key not in expected_keys]
                if missing:
                    issue(number, f'反查清单有 {len(missing)} 项未入表，候选序号（前 10）{missing[:10]}')
                if extra:
                    issue(number, f'主表有 {len(extra)} 项缺少反查来源，文档行号（前 10）{extra[:10]}')
    return state, errors, observation_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='待核验的项目根')
    parser.add_argument('--only', choices=COLUMNS, action='append', help='只核验指定类别，可重复')
    parser.add_argument('--require-observations', action='store_true',
                        help='完成态的 API、数据库和 UI 须与独立实测 JSON 对照')
    parser.add_argument('--source', action='append', metavar='NAME=DIR', default=[],
                        help='另行选定的本地源码目录，引用用 NAME//相对路径，可重复')
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.only or COLUMNS))
    report_ranges, found, lengths = defaultdict(list), defaultdict(list), {}
    try:
        root = args.root.resolve(strict=True)
        base = root / 'knowledge'
        if base.is_symlink() or not base.is_dir():
            raise ValueError('项目缺少实际的 knowledge/ 目录')
        sources = evidence_sources(root, args.source)
        for path, _ in sorted(markdown_files(base)):
            for section in sections(path):
                report_ranges[path].append((section.start, section.end))
                if section.kind in selected:
                    found[section.kind].append(section)
    except (ValueError, RuntimeError) as error:
        print(f'知识库或证据根无效：{error}', file=sys.stderr)
        return 2
    except OSError:
        print('无法读取项目 knowledge/ 中的实际 UTF-8 Markdown 文件', file=sys.stderr)
        return 2
    failed = 0
    for kind in selected:
        found_sections = found[kind]
        if len(found_sections) != 1:
            print(f'{kind}：须有一个对应标记章节，实际 {len(found_sections)}', file=sys.stderr)
            failed += 1
            continue
        section = found_sections[0]
        state, errors, observed = verify_section(section, sources, report_ranges, lengths,
                                                  require_observations=args.require_observations)
        if errors:
            failed += 1
            for error in errors:
                print(error, file=sys.stderr)
        else:
            detail = f'，{observed}' if observed else ''
            print(f'{kind} {section.path.relative_to(root)}:{section.start} 自动项通过（{state}）{detail}')
    print(f'自动项通过 {len(selected) - failed}/{len(selected)} 类。需复核事实、反查来源覆盖范围与人工判断。')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
