"""Prepare answer-free skill evaluations and compare reviewed runs offline."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


CASES = Path(__file__).with_name("cases.json")
METRICS = ("input_tokens", "cached_input_tokens", "output_tokens", "elapsed_seconds", "followups")


def read(path):
    def unique(pairs):
        row = dict(pairs)
        if len(row) != len(pairs):
            raise ValueError(f"{path} 有重复的 JSON 字段或题号")
        return row
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def load_cases(path, suite):
    if path is None and not CASES.is_file():
        raise ValueError("请使用 --cases <题集.json> 指定本次题集。题集格式见 evals/README.md。")
    cases = read(path or CASES)
    selected = ("routing", "delivery") if suite == "all" else (suite,)
    groups = set()
    for section in selected:
        rows = cases.get(section) if isinstance(cases, dict) else None
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"题集 {section} 须包含本次要评测的题目")
        ids = set()
        for index, row in enumerate(rows, 1):
            label = f"题集 {section} 第 {index} 题"
            if section == "routing":
                if not isinstance(row, list) or len(row) != 4:
                    raise ValueError(f"{label} 须依次填写题号、题面、分组、期望技能名或 null")
                key, prompt, group, expected = row
                if not isinstance(group, str) or not group.strip() or (
                        expected is not None and (not isinstance(expected, str) or not expected.strip())):
                    raise ValueError(f"{label} 的分组或期望技能名无效")
                groups.add(group)
            else:
                if not isinstance(row, dict):
                    raise ValueError(f"{label} 须填写 id、prompt 和 criteria")
                key, prompt, criteria = row.get("id"), row.get("prompt"), row.get("criteria")
                if not isinstance(criteria, dict) or not criteria or not all(
                        name.strip() and isinstance(rule, str) and rule.strip() for name, rule in criteria.items()):
                    raise ValueError(f"{label} 须提供具名的评分判据")
            if not isinstance(key, str) or not key.strip() or not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"{label} 须填写文字题号和题面")
            if key in ids or (section == "delivery" and key in groups):
                raise ValueError(f"{label} 的题号 {key} 重复或与路由统计分组重名")
            ids.add(key)
    return cases


def fingerprint(cases, suite):
    selected = {k: v for k, v in cases.items() if suite == "all" or k == suite}
    data = json.dumps(selected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def blind(cases, suite):
    packet = {"suite": suite, "suite_sha256": fingerprint(cases, suite)}
    if suite in ("routing", "all"):
        packet["routing"] = [{"id": key, "prompt": prompt} for key, prompt, *_ in cases["routing"]]
    if suite in ("delivery", "all"):
        packet["delivery"] = [{k: case[k] for k in ("id", "prompt")} for case in cases["delivery"]]
    return packet


def score(run, cases, suite):
    if not isinstance(run, dict) or run.get("suite_sha256") != fingerprint(cases, suite):
        raise ValueError("suite_sha256 须与本次盲测题集和范围一致")
    values = run.get("metrics", {})
    if not isinstance(values, dict) or values.keys() - set(METRICS):
        raise ValueError("metrics 字段无效")
    for key, value in values.items():
        if value is not None and (type(value) not in (int, float) or value < 0 or not math.isfinite(value)
                                  or (key != "elapsed_seconds" and type(value) is not int)):
            raise ValueError(f"{key} 须填实际非负用量或 null")
    result = {
        "revision": run.get("revision"), "host": run.get("host"), "model": run.get("model"),
        "metrics": {k: values.get(k) for k in METRICS}, "scores": {}, "misses": [], "incomplete": [],
    }

    def tally(group, passed):
        counts = result["scores"].setdefault(group, {"passed": 0, "total": 0})
        counts["total"] += 1
        counts["passed"] += int(passed)

    def answers(group, ids):
        rows = run.get(group, {})
        if not isinstance(rows, dict) or rows.keys() - set(ids):
            raise ValueError(f"{group} 须按本次题号填写，不能附加未知题目")
        return rows

    if suite in ("routing", "all"):
        routes = answers("routing", [r[0] for r in cases["routing"]])
        for key, _, group, expected in cases["routing"]:
            actual = routes.get(key)
            if key not in routes or (actual is not None and not isinstance(actual, str)):
                result["incomplete"].append(key)
                tally(group, False)
                continue
            tally(group, actual == expected)
            if actual != expected:
                result["misses"].append({"id": key, "expected": expected, "actual": actual})

    if suite in ("delivery", "all"):
        rows = answers("delivery", [c["id"] for c in cases["delivery"]])
        for case in cases["delivery"]:
            key = case["id"]
            item = rows.get(key, {})
            if not isinstance(item, dict):
                raise ValueError(f"{key} 的交付记录格式无效")
            output, checks = item.get("output"), item.get("checks", {})
            if not isinstance(checks, dict) or checks.keys() - case["criteria"].keys():
                raise ValueError(f"{key} 的评审条款编号不符")
            for name in case["criteria"]:
                mark = checks.get(name)
                item_id = f"{key}/{name}"
                valid = isinstance(output, str) and bool(output.strip()) and isinstance(mark, dict)
                if valid:
                    passed, evidence = mark.get("pass"), mark.get("evidence")
                    valid = (type(passed) is bool and isinstance(evidence, str) and bool(evidence.strip())
                             and (not passed or evidence in output))
                if not valid:
                    result["incomplete"].append(item_id)
                elif not passed:
                    result["misses"].append({"id": item_id, "reason": evidence})
                tally(key, bool(valid and passed))
    return result


def compare(old, new):
    comparable = (not old["incomplete"] and not new["incomplete"]
                  and all(old[k] and old[k] == new[k] for k in ("host", "model")))
    return {
        "comparable": comparable,
        "candidate_minus_baseline_passed": {
            k: new["scores"][k]["passed"] - counts["passed"] if comparable else None
            for k, counts in old["scores"].items()
        },
        "candidate_minus_baseline_metrics": {
            k: new["metrics"][k] - old["metrics"][k] if
            comparable and old["metrics"][k] is not None and new["metrics"][k] is not None else None
            for k in METRICS
        },
    }


def main():
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument("--cases", type=Path, default=argparse.SUPPRESS, metavar="FILE", help="本次评测的 JSON 题集")
    parser = argparse.ArgumentParser(description=__doc__, parents=[options])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("rubric", parents=[options], help="仅供独立交付评审读取")
    for name in ("blind", "score"):
        sub = commands.add_parser(name, parents=[options])
        sub.add_argument("suite", choices=("routing", "delivery", "all"))
        if name == "score":
            sub.add_argument("baseline", type=Path)
            sub.add_argument("candidate", type=Path, nargs="?")
    args = parser.parse_args()
    cases = load_cases(getattr(args, "cases", None), getattr(args, "suite", "delivery"))
    if args.command == "blind":
        report = blind(cases, args.suite)
    elif args.command == "rubric":
        report = {c["id"]: c["criteria"] for c in cases["delivery"]}
    else:
        old = score(read(args.baseline), cases, args.suite)
        report = {"baseline": old}
        if args.candidate:
            new = score(read(args.candidate), cases, args.suite)
            report.update(candidate=new, comparison=compare(old, new))
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return int(any(r.get("incomplete") for k, r in report.items() if k in ("baseline", "candidate")))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        sys.exit(f"评测无效：{error}")
