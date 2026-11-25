"""Cross-check the handoff with samples exported by HTTP, schema and browser probes."""
from collections import Counter
import hashlib
import json
import re

from diagram_inventory import RELATION


KINDS = ('api', 'database', 'ui')


def unique_keys(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('实测 JSON 出现重复键')
    return result


def string(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'实测记录缺少有效的 {key}')
    return value


def verify_http(record, row):
    status = record.get('status')
    if type(status) is not int or not 100 <= status <= 599 or 'content_type' not in record:
        raise ValueError('HTTP 实测需有有效状态码与响应类型')
    mime = '无 Content-Type'
    if record['content_type'] is not None:
        mime = string(record, 'content_type').partition(';')[0].strip().lower()
        token = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
        if not re.fullmatch(rf'{token}/{token}', mime):
            raise ValueError('HTTP 响应类型无效')
    output = row['输出'].replace('`', '')
    pair = rf'(?<![0-9]){status}\s+{re.escape(mime)}(?![a-z0-9+./-])'
    if not re.search(pair, output, re.I):
        raise ValueError('输出未列出该次实测的状态码与 MIME 组合')
    if 'attachment' in record:
        filename = string(record, 'attachment')
        if not re.search(r'(?<![\w.-])' + re.escape(filename) + r'(?![\w.-])', output, re.ASCII):
            raise ValueError('输出的附件名与实测不符')
    effects = record.get('effects', {})
    if not isinstance(effects, dict):
        raise ValueError('effects 须为变化指标与实测整数的对象')
    for name, value in effects.items():
        if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', name) or type(value) is not int:
            raise ValueError('效果指标须有稳定标识与整数实测值')
        if not re.search(rf'(?<!\w){name}={value}(?![\w.])', output, re.ASCII):
            raise ValueError('输出的数据变化与实测不符')
    fields = record.get('fields')
    if not isinstance(fields, dict):
        raise ValueError('fields 须为实际请求键和提交次数的对象，无输入时用 {}')
    inputs = row['输入'].replace('`', '')
    values = record.get('values', {})
    if not isinstance(values, dict) or not values.keys() <= fields.keys():
        raise ValueError('values 只可引用已采集的请求键')
    for key, value in values.items():
        if not isinstance(value, str) or not re.fullmatch(r'[\w.-]+', value, re.ASCII):
            raise ValueError('场景值仅支持脱敏后的公开枚举')
        if not re.search(r'(?<![\w.\[\]-])' + re.escape(f'{key}={value}') + r'(?![\w.-])',
                         inputs, re.ASCII):
            raise ValueError('场景的请求枚举与该笔采集记录不符')
    for key, count in fields.items():
        if not key.strip() or type(count) is not int or count < 1:
            raise ValueError('请求键须非空，提交次数须为正整数')
        token = rf'(?<![\w.\[\]-]){re.escape(key)}(?![\w.\[\]-])'
        if count > 1:
            token += rf'\s*[（(](?:可重复|实发{count}次)[）)]'
        if not re.search(token, inputs, re.ASCII):
            raise ValueError('输入的实际请求键或可重复标注与该次捕获不符')


def verify_ui(record, row, resolve_file):
    if (row.get('实测路径') != string(record, 'url')
            or row.get('实测动作') != string(record, 'action')):
        raise ValueError('实测路径或实测动作与浏览器记录不符')
    digest = string(record, 'sha256').lower()
    if not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('截图 sha256 格式无效')
    checksum = hashlib.sha256()
    with resolve_file(row['截图']).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            checksum.update(block)
    if checksum.hexdigest() != digest:
        raise ValueError('该状态对应的原始截图摘要与主表截图不符')


def er_edges(diagrams):
    edges = []
    for diagram in diagrams:
        statements = [part.strip() for line in diagram if not line.startswith('%%')
                      for part in line.split(';') if part.strip()]
        if not statements or statements[0] != 'erDiagram':
            continue
        for line in statements[1:]:
            match = RELATION.fullmatch(line)
            if match:
                edges.append(tuple(value.strip('"') for value in match.groups()))
    return edges


def verify_fk(record, edges):
    parent, child = string(record, 'parent'), string(record, 'child')
    nullable, unique = record.get('nullable'), record.get('unique')
    if type(nullable) is not bool or type(unique) is not bool:
        raise ValueError('物理外键的 nullable 和 unique 须为布尔值')
    label = string(record, 'label') if 'label' in record else None
    candidates = [edge for edge in edges if {edge[0], edge[3]} == {parent, child}
                  and (label is None or edge[4] == label)]
    if len(candidates) != 1:
        raise ValueError('物理外键在 ER 图中缺失或不唯一，多条同端点的边须指定 label')
    left, left_card, right_card, right, _ = candidates[0]
    # Mermaid left end is mirrored. One FK cannot require a child for every parent.
    direct = (parent, '|o' if nullable else '||', 'o|' if unique else 'o{', child)
    reverse = (child, '|o' if unique else '}o', 'o|' if nullable else '||', parent)
    if (left, left_card, right_card, right) not in (direct, reverse):
        raise ValueError('ER 图基数与实测物理外键的可空性或唯一性不符')
    return candidates[0]


def verify_observations(kind, path, rows, diagrams, resolve_file, cases=()):
    if path.suffix.lower() != '.json':
        raise ValueError('实测对照须引用独立的 JSON 采集记录')
    data = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_keys)
    records = data.get(kind) if isinstance(data, dict) else None
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise ValueError(f'实测对照缺少有效的 {kind} 记录数组')
    by_id = {row['标识']: (number, row) for number, row in rows}
    if kind == 'database':
        edges = er_edges(diagrams)
        if not records:
            basis = resolve_file(string(data, 'database_basis'))
            if basis == path or basis.stat().st_size == 0:
                raise ValueError('物理外键为零须提供独立的实际数据库结构或检查记录')
        matched_edges = {verify_fk(record, edges) for record in records}
        if len(matched_edges) != len(records):
            raise ValueError('同一物理外键在实测清单中重复')
        return f'物理外键实测 {len(records)} 条，图中关系 {len(edges)} 条'
    if kind == 'api':
        by_id = {key: item for key, item in by_id.items()
                 if not key.startswith(('RPC ', 'EVENT ', 'CLI '))}
    if by_id and not records:
        raise ValueError('实测清单为空')
    case_rows = {(row['标识'], row['场景']): (number, row) for number, row in cases}
    if len(case_rows) != len(cases):
        raise ValueError('同一接口的实测场景名重复')
    case_ids = {key for key, _ in case_rows}
    for key in case_ids | {key for key, (_, row) in by_id.items()
                          if '见实测场景' in (row.get('输入'), row.get('输出'))}:
        if key not in by_id or key not in case_ids:
            raise ValueError('实测场景表与主表引用未对应')
        main = by_id[key][1]
        if main['输入'] != '见实测场景' or main['输出'] != '见实测场景':
            raise ValueError('使用场景表时，主表输入和输出均须写「见实测场景」')
    covered_cases = set()
    seen = Counter()
    for index, record in enumerate(records, 1):
        key = string(record, 'id')
        if key not in by_id:
            raise ValueError(f'第 {index} 笔实测的标识未列入主表')
        seen[key] += 1
        number, row = by_id[key]
        if kind == 'api' and (key in case_ids or 'case' in record):
            scenario = (key, string(record, 'case'))
            if scenario not in case_rows:
                raise ValueError(f'第 {index} 笔实测的场景未列入表')
            number, row = case_rows[scenario]
            covered_cases.add(scenario)
        try:
            if kind == 'api':
                verify_http(record, row)
            else:
                verify_ui(record, row, resolve_file)
        except ValueError as error:
            raise ValueError(f'第 {index} 笔实测（文档第 {number} 行）：{error}') from error
    if covered_cases != set(case_rows):
        raise ValueError('实测场景表存在没有对应采集记录的行')
    if kind == 'ui' and (any(n != 1 for n in seen.values()) or set(seen) != set(by_id)):
        raise ValueError('每个 UI 状态须对应一笔原始截图记录')
    return f'实测 {len(records)} 笔，覆盖 {len(seen)}/{len(by_id)} 个标识'
