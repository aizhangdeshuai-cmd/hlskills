"""Compare Mermaid's documented inventory notation with the deliverable's primary table."""
import re


IDENTIFIER = r'(?:"[^"]+"|[\w.]+(?:[-/][\w.]+)*)'
NODE = re.compile(rf'({IDENTIFIER})(?:\[.*\]|\(.*\)|\{{.*\}})?' r'(?:::{1,2}[\w-]+)?')
FLOW_ARROW = re.compile(r'\s*(?:--+>|==+>|-\.+->)(?:\s*\|[^|]*\|)?\s*')
MESSAGE = re.compile(rf'({IDENTIFIER})\s*-{{1,2}}>{{1,2}}[+-]?\s*({IDENTIFIER})\s*:.*')
ENTITY = re.compile(rf'({IDENTIFIER})(?:\s*\[.*\])?\s*\{{')
RELATION = re.compile(rf'({IDENTIFIER})\s+([|o{{}}]+)(?:--|\.\.)([|o{{}}]+)\s*({IDENTIFIER})\s*:\s*(.*)')


def graph_edges(lines, sequence):
    edges = set()
    nodes = set()
    for line in lines:
        if sequence:
            message = MESSAGE.fullmatch(line)
            if message:
                edges.add((message[1].strip('"'), message[2].strip('"')))
            elif line.startswith(('participant ', 'actor ')):
                declaration = re.match(rf'(?:participant|actor)\s+({IDENTIFIER})', line)
                if declaration:
                    nodes.add(declaration[1].strip('"'))
            elif re.search(r'[<>-][<>-]', line):
                raise ValueError('时序图消息请使用 A->>B: 动作 或 A-->>B: 回复')
        else:
            if line.startswith(('subgraph ', 'direction ', 'classDef ', 'class ', 'style ',
                                'linkStyle ', 'click ')) or line == 'end':
                continue
            chain = FLOW_ARROW.split(line)
            parsed = [NODE.fullmatch(token.strip()) for token in chain]
            if not all(parsed):
                raise ValueError('流程图请用单行的 A --> B、A -->|动作| B 或连续有向边；表内填写节点 ID')
            names = [match[1].strip('"') for match in parsed]
            nodes.update(names)
            edges.update(zip(names, names[1:]))
    if nodes - {node for edge in edges for node in edge}:
        raise ValueError('架构图含无连线的节点')
    return edges


def er_entities(lines):
    entities = set()
    in_entity = False
    for line in lines:
        if in_entity:
            if line == '}':
                in_entity = False
            continue
        entity = ENTITY.fullmatch(line)
        relation = RELATION.fullmatch(line)
        if entity:
            entities.add(entity[1].strip('"'))
            in_entity = True
        elif relation:
            entities.update((relation[1].strip('"'), relation[4].strip('"')))
        elif not line.startswith(('direction ', 'classDef ', 'class ', 'style ')):
            raise ValueError('ER 图请用实体属性块，或带基数与说明的实体关系')
    if in_entity:
        raise ValueError('ER 图实体属性块未闭合')
    return entities


def validate_diagram(kind, diagrams, rows):
    identifiers = set()
    for diagram in diagrams:
        lines = [part.strip() for line in diagram if not line.lstrip().startswith('%%')
                 for part in line.split(';') if part.strip()]
        if not lines:
            continue
        header, body = lines[0], lines[1:]
        if kind == 'architecture' and (
            re.fullmatch(r'(?:graph|flowchart)\s+(?:TD|TB|BT|LR|RL)', header) or header == 'sequenceDiagram'
        ):
            identifiers.update(graph_edges(body, header == 'sequenceDiagram'))
        elif kind == 'database' and header == 'erDiagram':
            identifiers.update(er_entities(body))

    if not identifiers:
        raise ValueError('缺少有内容的对应 Mermaid 图')
    if kind == 'database':
        expected = {row['标识'] for _, row in rows}
        # Uppercase display names in ER diagrams are common. Require exact spelling
        # where folding would merge distinct entities (e.g. quoted SQL identifiers).
        if len(expected) == len({s.casefold() for s in expected}) and len(identifiers) == len({s.casefold() for s in identifiers}):
            expected = {s.casefold() for s in expected}
            identifiers = {s.casefold() for s in identifiers}
    else:
        expected = {(row['起点'], row['终点']) for _, row in rows}
    if expected != identifiers:
        raise ValueError(f'图与主表不符，图中缺少 {len(expected - identifiers)} 项，多出 {len(identifiers - expected)} 项')
