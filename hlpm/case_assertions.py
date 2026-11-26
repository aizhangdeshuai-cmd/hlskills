"""Bind the visible expected results in PRD and TC rows to the same executable assertions."""
import re
import shlex

STEP_RANGE = re.compile(r"L([1-9][0-9]*)(?:-L([1-9][0-9]*))?")
RESULT_LINK = re.compile(
    r"(?<![!\\])\[((?:\\.|[^\[\]\\\n])+)\]\(((?:design/checks/[^()\s]+\.steps#|acceptance-plan\.json#/case_assertions/)[^()\s]+)\)"
)
STATES = {"expect-hidden": "隐藏", "expect-disabled": "禁用", "expect-enabled": "启用"}


def step_result(lines, anchor, label):
    match = STEP_RANGE.fullmatch(anchor) if isinstance(anchor, str) else None
    if not match:
        raise ValueError(f"{label} 无效的断言位置 {anchor!r}，请用 L3 或 L3-L5")
    first, last = int(match[1]), int(match[2] or match[1])
    if not first <= last <= len(lines):
        raise ValueError(f"{label} 断言位置 {anchor} 超出步骤范围")
    values, fields = [], []
    for line_no in range(first, last + 1):
        words = shlex.split(lines[line_no - 1])
        if len(words) == 3 and words[0] in ("expect-visible-text", "expect-object"):
            value = words[2]
        elif len(words) == 2 and words[0] in STATES:
            value = STATES[words[0]]
        else:
            raise ValueError(f"{label} 第 {line_no} 行须是业务断言")
        values.append(value)
        fields.append(f"{words[1]}={value}")
    return " / ".join(values), "、".join(fields)


def validate_assertions(config, is_ui, label):
    if not isinstance(config, dict) or not config or config.keys() - {"steps", "values"}:
        raise ValueError(f"{label} case_assertions 须登记 steps 或 values")
    if "steps" in config:
        anchors = config["steps"]
        if (not is_ui or not isinstance(anchors, list) or not anchors
                or any(not isinstance(a, str) or not STEP_RANGE.fullmatch(a) for a in anchors)
                or len(anchors) != len(set(anchors))):
            raise ValueError(f"{label} steps 须为本 UI 场景已运行的断言位置列表")
    if "values" in config:
        values = config["values"]
        if not isinstance(values, dict) or not values:
            raise ValueError(f"{label} values 须按字段登记可供测试读取的预期值")
        for key, value in values.items():
            if (not re.fullmatch(r"[A-Za-z0-9_-]+", key) or type(value) not in (str, int, bool)
                    or isinstance(value, str) and (not value.strip() or len(value.splitlines()) != 1)):
                raise ValueError(f"{label} values 须用稳定字段名和单行非空文本、整数或布尔值")


def expected_links(root, tc, config, is_ui, label):
    validate_assertions(config, is_ui, label)
    checked = {}
    if "steps" in config:
        from prototype_evidence import local
        file = f"checks/{tc}.steps"
        lines = local((root / "design").resolve(), file).read_text(encoding="utf-8").splitlines()
        for anchor in config["steps"]:
            checked[f"design/{file}#{anchor}"] = step_result(lines, anchor, label)
    for key, value in config.get("values", {}).items():
        rendered = str(value).lower() if isinstance(value, bool) else str(value)
        checked[f"acceptance-plan.json#/case_assertions/{tc}/values/{key}"] = rendered, key
    return checked


def result_links(cell):
    content = re.sub(r"(`+).*?\1", "", cell)
    return [(re.sub(r"\\([\\|\[\]])", r"\1", actual), target)
            for actual, target in RESULT_LINK.findall(content)]


def check_case_assertions(root, plan, cases, prd, require_prd_results):
    if not require_prd_results and "case_assertions" not in plan:
        return 0
    bindings = plan.get("case_assertions", {})
    if not isinstance(bindings, dict) or bindings.keys() - cases.keys():
        raise ValueError("case_assertions 须按计划内的 TC 登记关键预期")
    ui = {s["id"] for s in plan["scenarios"] if s["pages"]}
    acs_by_tc = {case["id"]: case["acs"] for case in plan["scenarios"]}
    targets = {}
    count = 0
    for tc, (row, _, location) in cases.items():
        label = f"{location} {tc}"
        checked = expected_links(root, tc, bindings[tc], tc in ui, label) if tc in bindings else {}
        # Only count links visible in this row's expected-result cell.
        links = result_links(row["预期结果"])
        seen = set()
        for actual, target in links:
            if target in seen or target not in checked:
                raise ValueError(f"{label} 重复或未登记的预期断言：{target}")
            seen.add(target)
            expected, fields = checked[target]
            if actual != expected:
                raise ValueError(f"{label} 关键预期应为「{expected}」({fields})，用例写为「{actual}」：{target}")
            targets[target] = tc, expected
        missing = checked.keys() - seen
        if missing:
            raise ValueError(f"{label} 预期结果缺少已登记的断言链接：{', '.join(sorted(missing))}")
        if ([p for _, p in links if p.startswith("design/")] !=
                [p for p in checked if p.startswith("design/")]):
            raise ValueError(f"{label} 用例中的关键断言顺序与 steps 登记顺序不符")
        count += len(seen)
    cited = set()
    for ac, (row, _, location) in prd.items():
        for actual, target in result_links(row["验收点"]):
            if target not in targets:
                raise ValueError(f"{location} {ac} 引用了未登记的关键预期：{target}")
            tc, expected = targets[target]
            if ac not in acs_by_tc[tc]:
                raise ValueError(f"{location} {ac} 引用了未关联的 {tc}：{target}")
            if actual != expected:
                raise ValueError(f"{location} {ac} 的预期「{actual}」与 {tc} 的「{expected}」不符：{target}")
            cited.add(target)
    if require_prd_results and (missing := targets.keys() - cited):
        details = [f"{target}（{', '.join(acs_by_tc[targets[target][0]])}）" for target in sorted(missing)]
        raise ValueError("prd.md 对应 AC 的验收点缺少已登记的关键预期链接：" + "、".join(details))
    return count
