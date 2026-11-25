"""Search the project's Markdown knowledge base and read small, citable excerpts."""
import argparse
from contextlib import closing
import hashlib
import heapq
from itertools import chain, islice
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile


SEARCH_CHARS = 1100
READ_CHARS = 2000
TRUNCATED = '…（已截断）'
# Keep URL paths, dotted names and hyphenated error codes searchable as literals.
WORDS = re.compile(r'[\w/#.{][\w./:{}#-]*')


def markdown_files(base):
    pending = [base]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith('.') or (directory == base and entry.name.casefold() == 'doc'):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.name.lower().endswith('.md') and entry.is_file(follow_symlinks=False):
                    stat = entry.stat(follow_symlinks=False)
                    stamp = f'{stat.st_ino}/{stat.st_size}/{stat.st_mtime_ns}/{stat.st_ctime_ns}'
                    yield Path(entry.path), stamp


def refresh(db, base, project, fts):
    # Serialize scanning with updating: an older concurrent scan cannot restore deleted files.
    db.execute('BEGIN IMMEDIATE')
    db.execute('CREATE TABLE IF NOT EXISTS docs(path TEXT UNIQUE, stamp TEXT, body TEXT)')
    if fts:
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS terms USING fts5(value, tokenize='trigram')")
    else:
        db.execute('CREATE TABLE IF NOT EXISTS terms(value TEXT)')
    previous = {p: (i, s) for i, p, s in db.execute('SELECT rowid, path, stamp FROM docs')}
    for path, stamp in markdown_files(base):
        relative = path.relative_to(project).as_posix()
        rowid, old = previous.pop(relative, (None, None))
        if stamp == old:
            continue
        try:
            body = path.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError as exc:
            raise ValueError(f'{relative} 不是有效的 UTF-8 Markdown 文件') from exc
        if rowid is None:
            rowid = db.execute('INSERT INTO docs VALUES (?, ?, ?)', (relative, stamp, body)).lastrowid
        else:
            db.execute('UPDATE docs SET stamp=?, body=? WHERE rowid=?', (stamp, body, rowid))
            db.execute('DELETE FROM terms WHERE rowid=?', (rowid,))
        value = (relative + '\n' + body).casefold()
        db.execute('INSERT INTO terms(rowid, value) VALUES (?, ?)', (rowid, value))
    stale = [(rowid,) for rowid, _ in previous.values()]
    db.executemany('DELETE FROM terms WHERE rowid=?', stale)
    db.executemany('DELETE FROM docs WHERE rowid=?', stale)
    db.commit()


def trigram_supported():
    with closing(sqlite3.connect(':memory:')) as db:
        try:
            db.execute("CREATE VIRTUAL TABLE probe USING fts5(value, tokenize='trigram')")
        except sqlite3.OperationalError:
            return False
    return True


HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+')
HEADING_STATUS = re.compile(r'[（(]([^（）()]+)[）)]\s*#*\s*$')
STATUS_FIELD = re.compile(r'^[ >*_-]*(?:状态|status)[*:： \t]+', re.I)
STATUS = re.compile(
    r'(?P<old>已废弃|已弃用|已失效|已过期|已(?:被)?(?:取代|替代)|历史(?:版本|规则)|\b(?:deprecated|superseded|obsolete)\b)'
    r'|(?P<pending>待裁决)|(?P<current>现行|当前(?:生效|有效|规则)|已生效|\b(?:current|active|accepted)\b)', re.I)
STATUS_RANK = {'old': -2, 'pending': -1, 'current': 1}


def status(text, *, at_start=False):
    match = STATUS.match(text) if at_start else STATUS.search(text)
    if not match:
        return 0
    return STATUS_RANK[match.lastgroup]


def sections(body):
    """Resolve explicit section/ADR status before emitting even the entry's title."""
    lines = body.split('\n')
    starts = [(0, 0)]
    states = [0]
    stack = [(0, 0)]  # heading level and section index
    status_owner = None
    fence = ''
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('~~~', '```')):
            marker = stripped[0] * (len(stripped) - len(stripped.lstrip(stripped[0])))
            if not fence:
                fence = marker
            elif marker.startswith(fence) and stripped == marker:
                fence = ''
            continue
        if fence:
            continue
        heading = HEADING.match(line)
        if heading:
            level = len(heading[1])
            while stack[-1][0] >= level:
                stack.pop()
            parent = stack[-1][1]
            stack.append((level, len(starts)))
            starts.append((i, parent))
            suffix = HEADING_STATUS.search(line)
            declared = status(suffix[1].strip(), at_start=True) if suffix else 0
            states.append(declared or status(line))
            title = line[heading.end():].strip(' #').casefold()
            status_owner = parent if title in ('状态', 'status') else None
        elif status_owner is not None and stripped:
            declared = status(stripped.strip(' >*`'), at_start=True)
            if declared:
                states[status_owner] = declared
            status_owner = None
        elif STATUS_FIELD.match(line):
            declared = status(line)
            if declared:
                states[-1] = declared

    titles = ['']
    for i, (start, parent) in enumerate(starts):
        states[i] = states[i] or states[parent]
        if i:
            title = HEADING.sub('', lines[start], count=1).strip(' #')
            titles.append(' › '.join(filter(None, (titles[parent], title))))
        end = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        if start < end:
            yield states[i], titles[i], start, lines[start:end]


def excerpt(line, focus='', size=155):
    start = max(0, line.casefold().find(focus) - 30) if focus else 0
    return ('…' if start else '') + line[start:start + size] + ('…' if start + size < len(line) else '')


def section_hits(path, body, words, phrase, *, handoff=False):
    versions = {w: re.compile(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9]|\.\d)')
                for w in words if re.fullmatch(r'v\d+(?:\.\d+)*', w)}

    identifiers = dict(versions)
    if handoff:
        identifiers.update({w: re.compile(r'(?<![a-z0-9_-])' + re.escape(w) + r'(?![a-z0-9_-])')
                            for w in words if re.fullmatch(r'[a-z]+-?\d+', w)})

    def matched(folded):
        return {w for w in words if w in folded and (w not in identifiers or identifiers[w].search(folded))}

    path_terms = matched(path.casefold())
    any_hit = False
    first = None
    labels = {-2: '历史/已失效', -1: '待裁决', 0: '状态未注明', 1: '现行'}
    for inherited, title, offset, lines in sections(body):
        title_terms = matched(title.casefold())
        named_versions = len(versions.keys() & (title_terms | path_terms))
        best = {}
        pending_table = False
        for index, line in enumerate(lines):
            line = line.strip()
            if handoff:
                # The first column names the subject of a row (e.g. AC or 待决事项).
                if not line.startswith('|'):
                    pending_table = False
                elif index + 1 < len(lines) and re.match(r'^\s*\|\s*:?-{3,}', lines[index + 1]):
                    pending_table = bool(re.search(r'待决|待确认|未确认', line.split('|')[1]))
            if not line:
                continue
            number = offset + index + 1
            if first is None:
                first = number, f'[{"交接稿 · " if handoff else ""}{labels[inherited]}] {excerpt(line)}'
            folded = line.casefold()
            hits = matched(folded)
            if not hits:
                continue
            # A table can put both an obsolete and a current record under the same heading.
            state = inherited
            if line.startswith('|'):
                state = next((s for cell in line.strip('|').split('|')
                              if (s := status(cell.strip(' *`'), at_start=True))), inherited)
            # Count the heading and this record together. Sibling sections and separate
            # table rows cannot contribute missing terms to this record's relevance.
            heading = index == 0 and bool(title)
            contextual = hits | title_terms
            neighbor = None
            extra = set()
            if len(contextual) < len(words) and not heading and not line.startswith('|'):
                for other in (index - 1, index + 1):
                    if not (0 <= other < len(lines)) or lines[other].lstrip().startswith('|'):
                        continue
                    added = matched(lines[other].casefold()) - contextual
                    if len(added) > len(extra):
                        neighbor, extra = other, added
                contextual |= extra
            if versions and not versions.keys() <= (contextual | path_terms):
                continue
            subject = line.strip('|').split('|', 1)[0].casefold() if handoff and line.startswith('|') else ''
            primary = handoff and Path(path).name in ('prd.md', 'test-cases.md')
            score = (len(contextual), len(contextual | path_terms), len(matched(subject)), int(primary),
                     named_versions, state, len(hits),
                     int(not heading), int(phrase in folded), sum(map(len, hits)))
            if state in best and score <= best[state][0]:
                continue
            focus = max(hits, key=lambda word: (len(word), word))
            snippet = excerpt(line, focus)
            if heading:
                for following, detail in enumerate(lines[1:], number + 1):
                    if detail.lstrip().startswith('|'):
                        break
                    if detail.strip() and not STATUS_FIELD.match(detail):
                        snippet += f' · L{following} {excerpt(detail.strip(), size=100)}'
                        break
            elif title:
                snippet = f'{excerpt(title, size=80)} · {snippet}'
            if neighbor is not None:
                term = max(extra, key=lambda word: (len(word), word))
                snippet += f' · L{offset + neighbor + 1} {excerpt(lines[neighbor].strip(), term, size=100)}'
            label = '待确认' if pending_table else labels[state]
            snippet = f'[{"交接稿 · " if handoff else ""}{label}] {snippet}'
            best[state] = score, number, snippet
        for score, number, snippet in best.values():
            any_hit = True
            yield tuple(-part for part in score), path, number, snippet
    if not any_hit and first and len(path_terms) == len(words):
        yield (0, -len(path_terms), 0, 0, 0, 0, 0, 0, 0, 0), path, *first


def matches(db, base, project, fts, words, phrase, limit):
    refresh(db, base, project, fts)
    conditions = []
    params = []
    for word in words:
        if fts and len(word) >= 3:
            conditions.append('terms MATCH ?')
            params.append('"' + word.replace('"', '""') + '"')
        else:
            conditions.append('instr(value, ?) > 0')
            params.append(word)
    sql = 'SELECT path, body FROM terms JOIN docs ON docs.rowid=terms.rowid WHERE '
    rows = db.execute(sql + ' AND '.join(conditions), params)
    handoff = base != project / 'knowledge'
    hits = (hit for path, body in rows
            for hit in section_hits(path, body, words, phrase, handoff=handoff))
    return heapq.nsmallest(limit, hits)


def cache_dirs(project):
    configured = os.environ.get('XDG_CACHE_HOME')
    if configured:
        yield Path(configured) / 'hlkb'
        return
    yield Path.home() / ('Library/Caches' if sys.platform == 'darwin' else '.cache') / 'hlkb'
    if hasattr(os, 'getuid'):
        try:
            private = Path(tempfile.gettempdir()).resolve(strict=True)
            info = private.stat()
        except OSError:
            return
        directory = private / 'hlkb'
        if (info.st_uid == os.getuid() and not info.st_mode & 0o077 and not directory.is_symlink()
                and directory != project and project not in directory.parents):
            yield directory


def cached_matches(base, project, fts, words, phrase, limit):
    kind = 'fts' if fts else 'plain'
    key = project if base == project / 'knowledge' else base
    digest = hashlib.sha256(os.fsencode(key)).hexdigest()
    for index, directory in enumerate(cache_dirs(project)):
        try:
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            db = sqlite3.connect(directory / f'{digest}-v1-{kind}.sqlite3', timeout=10)
        except (OSError, sqlite3.Error) as exc:
            reason = exc
            continue
        with closing(db):
            try:
                hits = matches(db, base, project, fts, words, phrase, limit)
            except sqlite3.DatabaseError as exc:
                reason = exc
                continue
        if index:
            print(f'使用私有临时缓存：{directory}', file=sys.stderr)
        return hits
    print(f'缓存不可用，使用内存索引：{reason}', file=sys.stderr)
    with closing(sqlite3.connect(':memory:')) as temporary:
        return matches(temporary, base, project, fts, words, phrase, limit)


def search(base, project, query, limit):
    phrase = query.casefold().strip()
    # Separate a Latin identifier immediately followed by Chinese text as well.
    chunks = re.split(r'([\u3400-\u9fff]+)', phrase)
    words = list(dict.fromkeys(w for chunk in chunks for w in WORDS.findall(chunk)))
    if not words or len(phrase) > 400 or len(words) > 24:
        raise ValueError('请提供 1 至 24 个关键词，总长最多 400 字符')
    fts = trigram_supported()
    hits = cached_matches(base, project, fts, words, phrase, limit)
    if not hits:
        print('未命中。可改用业务关键词、别名、接口路径或错误码。')
        return 1
    print_excerpt(((path, number, snippet) for _, path, number, snippet in hits), SEARCH_CHARS)
    return 0


def print_excerpt(rows, budget):
    remaining = budget
    reserve = len(TRUNCATED) + 1
    for path, number, value in rows:
        prefix = f'{path}:{number} '
        available = remaining - len(prefix) - 1 - reserve
        if available < 1:
            if remaining == budget:
                raise ValueError('文件路径超过输出预算，无法显示完整引用')
            print(TRUNCATED)
            return
        print(prefix + value[:available])
        if len(value) > available:
            print(TRUNCATED)
            return
        remaining -= len(prefix) + len(value) + 1


def read(base, project, relative, start, count):
    part = Path(relative)
    scope = base.relative_to(project)
    if (not part.is_relative_to(scope) or (scope == Path('knowledge') and len(part.parts) > 1
            and part.parts[1].casefold() == 'doc') or part.suffix.lower() != '.md'
            or any(p.startswith('.') for p in part.parts)):
        raise ValueError('请选择本次查询范围内的 Markdown 条目')
    path = project / part
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError('请选择实际 Markdown 文件，路径中不能含符号链接')
    with path.open(encoding='utf-8-sig') as stream:
        window = islice(stream, start - 1, start - 1 + count)
        first = next(window, None)
        if first is None:
            raise ValueError(f'指定行 {start} 超出文件范围')
        lines = enumerate(chain([first], window), start)
        print_excerpt(((part.as_posix(), i, line.rstrip('\n')) for i, line in lines), READ_CHARS)


def handoff_directory(project, selector):
    # Use exactly the same accepted versions and ambiguity rules as product handoff.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'hlpm'))
    from version import discover, resolve_version
    if selector == 'current':
        from handoff_trace import read_markdown
        index = project / 'knowledge/prd.md'
        if index.resolve() != index or not index.is_file():
            raise ValueError('缺少 knowledge/prd.md 的当前交接包指针，可用 --handoff 指定版本目录')
        lines, _ = read_markdown(index, parse_declaration=False)
        links = re.findall(r'^\[当前交接包\]\(([^)\n]*)\)[ \t]*$', '\n'.join(lines), re.M)
        if len(links) != 1 or not re.fullmatch(r'(?:doc/|\.\./docs/)v[1-9]\d*/prd\.md', links[0]):
            raise ValueError('请在 knowledge/prd.md 单独一行标出唯一的 [当前交接包](doc/vN/prd.md)，或用 --handoff 指定版本目录')
        target = (index.parent / links[0]).resolve(strict=True)
        source_dir = (index.parent / links[0]).parent
        package = resolve_version(project, discover(project), str(source_dir))
        if target != package / 'prd.md' or not target.is_file() or (source_dir / 'prd.md').is_symlink():
            raise ValueError('当前交接包指针须指向版本内实际的 prd.md')
        return package
    return resolve_version(project, discover(project), selector)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='项目根目录')
    commands = parser.add_subparsers(dest='command', required=True)
    find = commands.add_parser('search', help='按关键词查询当前知识库')
    find.add_argument('query')
    find.add_argument('--limit', type=int, default=3, metavar='1..10')
    view = commands.add_parser('read', help='从指定行读取 Markdown 原文')
    view.add_argument('path')
    view.add_argument('line', type=int)
    view.add_argument('--lines', type=int, default=8, metavar='1..40')
    for command in (find, view):
        command.add_argument('--handoff', nargs='?', const='current', metavar='版本或目录',
                             help='限定到当前交接包，亦可显式指定版本或版本目录')
    args = parser.parse_args()
    try:
        project = args.root.resolve(strict=True)
        base = handoff_directory(project, args.handoff) if args.handoff else project / 'knowledge'
        if base.is_symlink() or not base.is_dir():
            raise ValueError('项目中缺少实际的 knowledge/ 目录')
        if args.command == 'search':
            if not 1 <= args.limit <= 10:
                raise ValueError('--limit 必须在 1 到 10 之间')
            return search(base, project, args.query, args.limit)
        if args.line < 1 or not 1 <= args.lines <= 40:
            raise ValueError('行号须为正数，--lines 必须在 1 到 40 之间')
        read(base, project, args.path, args.line, args.lines)
    except (OSError, UnicodeError, sqlite3.Error, ValueError) as exc:
        print(f'知识库错误：{exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
