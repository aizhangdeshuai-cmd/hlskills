"""Score recorded QA checks and compare runs with the same plan."""
import argparse
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile


WEIGHTS = {"function": 20, "console": 15, "accessibility": 15, "usability": 15,
           "visual": 10, "performance": 10, "links": 10, "content": 5}


def load_run(path):
    run = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(run, dict) or not isinstance(run.get("checks"), list) or not run["checks"]:
        raise ValueError(f"{path}: 缺少检查清单")
    for field in ("scope", "revision"):
        if not isinstance(run.get(field), str) or not run[field].strip():
            raise ValueError(f"{path}: 缺少 {field}")
    runs = run.get("runs", {})
    if not isinstance(runs, dict):
        raise ValueError(f"{path}: runs 应按运行 ID 索引")
    for name, record in runs.items():
        if (not name.strip() or not isinstance(record, dict)
                or not isinstance(record.get("revision"), str) or not record["revision"].strip()
                or not isinstance(record.get("outcomes"), dict)):
            raise ValueError(f"{path}: 无效的运行记录 {name!r}")
    ids = set()
    for row in run["checks"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError(f"{path}: 检查缺少稳定 ID")
        key = row["id"]
        if key in ids:
            raise ValueError(f"{path}: 重复 ID {key}")
        ids.add(key)
        if row.get("category") not in WEIGHTS or row.get("status") not in ("pass", "fail", "unverified", "na"):
            raise ValueError(f"{path}: {key} 的类别或状态无效")
        if not isinstance(row.get("required"), bool) or (row["required"] and row["status"] == "na"):
            raise ValueError(f"{path}: {key} 的必测标记与适用范围不一致")
        if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
            raise ValueError(f"{path}: {key} 缺少证据或原因")
    return run


def assess(run):
    checks = []
    for original in run["checks"]:
        row = original.copy()
        checks.append(row)
        if row["status"] not in ("pass", "fail"):
            continue
        record = run.get("runs", {}).get(row.get("run_id"))
        if record is None:
            issue = "缺少对应的运行记录"
        elif record["outcomes"].get(row["id"]) != row["status"]:
            issue = "运行记录中的检查 ID 或结果不符"
        else:
            row["tested_revision"] = record["revision"]
            if record["revision"] == run["revision"]:
                continue
            reuse = row.get("reuse")
            if (not row["required"] and isinstance(reuse, dict)
                    and reuse.get("for_revision") == run["revision"]
                    and isinstance(reuse.get("reason"), str) and reuse["reason"].strip()):
                continue
            issue = "运行版本与候选版本不符"
        row.update(status="unverified", evidence_issue=issue)
    return dict(run, checks=checks)


def score(run):
    weighted, weight = 0, 0
    incomplete = []
    blocked = []
    for category, share in WEIGHTS.items():
        rows = [row for row in run["checks"] if row["category"] == category]
        applicable = [row for row in rows if row["status"] != "na"]
        if not rows:
            incomplete.append(category)
        for row in applicable:
            if row["status"] == "unverified":
                incomplete.append(row["id"])
            if row["required"] and row["status"] != "pass":
                blocked.append(row["id"])
        if applicable:
            passed = sum(row["status"] == "pass" for row in applicable)
            weighted += share * passed / len(applicable)
            weight += share
    value = round(100 * weighted / weight, 1) if weight and not incomplete else None
    return {"qa_health": value, "missing_evidence": incomplete, "blocking_checks": blocked}


def compare(previous, current):
    def plan(run):
        return {r["id"]: (r["category"], r["required"], r["status"] == "na") for r in run["checks"]}
    if previous["scope"] != current["scope"] or plan(previous) != plan(current):
        raise ValueError("基线范围或检查计划不同，无法比较")
    before = {r["id"]: r["status"] for r in previous["checks"]}
    return {r["id"]: [before[r["id"]], r["status"]] for r in current["checks"]
            if before[r["id"]] != r["status"]}


def main():
    parser = argparse.ArgumentParser(description="按产品计划对账候选提交，或统计已登记 QA 观察")
    parser.add_argument("observations", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", type=Path, help="产品确认的 acceptance-plan.json")
    mode.add_argument("--health-only", action="store_true", help="仅计算已登记质量观察的健康分")
    parser.add_argument("--plan-sha256", help="产品交接的已确认计划文件 SHA-256")
    parser.add_argument("--spec-sha256", help="验收产品交付包时，传入交接记录中的定稿文档 SHA-256")
    parser.add_argument("--candidate", help="独立取得的候选完整提交 SHA")
    parser.add_argument("--summary", action="store_true", help="将正式验收结果输出为开发交接简报")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--save-baseline", type=Path, help="保存本次原始证据到新文件")
    args = parser.parse_args()
    try:
        if args.plan:
            if not args.candidate or not args.plan_sha256 or args.baseline or args.save_baseline:
                parser.error("--plan 需 --candidate 和已确认的 --plan-sha256，健康基线选项只适用于 --health-only")
            from acceptance import evaluate
            result = evaluate(args.observations, args.plan, args.candidate, args.plan_sha256, args.spec_sha256,
                              with_diagnostics=args.summary)
            if args.summary:
                from acceptance_summary import format_summary
                print(format_summary(result))
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["acceptance"] == "passed" else 1
        if args.candidate or args.plan_sha256 or args.spec_sha256 is not None or args.summary:
            parser.error("--candidate/--plan-sha256/--spec-sha256/--summary 仅用于 --plan 的候选验收")
        observations = load_run(args.observations)
        run = assess(observations)
        result = score(run)
        result.update(mode="health-only", acceptance="not_assessed")
        result["revision"] = run["revision"]
        result["checks"] = run["checks"]
        if args.baseline:
            result["changes"] = compare(assess(load_run(args.baseline)), run)
        if args.save_baseline:
            serialized = json.dumps(observations, ensure_ascii=False, indent=2) + "\n"
            with NamedTemporaryFile(dir=args.save_baseline.parent, delete=False) as pending:
                temporary = Path(pending.name)
            try:
                temporary.write_text(serialized, encoding="utf-8")
                os.link(temporary, args.save_baseline)
            finally:
                temporary.unlink()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["blocking_checks"] else 0
    except (ValueError, OSError, TypeError) as error:
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
