"""Compare measured manual outcomes with the confirmed TC and its signed specification."""
from functools import cached_property

from case_assertions import result_links
from handoff_trace import defined_cases


class ManualAssertions:
    def __init__(self, package, plan, signed_cases):
        self.package = package
        self.bindings = plan.get("case_assertions", {})
        self.signed_cases = signed_cases

    @cached_property
    def case_rows(self):
        if self.signed_cases is None:
            raise ValueError("人工核对 steps 需已确认的规格摘要与对应的 test-cases.md")
        return defined_cases(self.package / "test-cases.md", source=self.signed_cases.decode("utf-8-sig"))

    def step_values(self, tc, anchors):
        row = self.case_rows.get(tc)
        if not row:
            raise ValueError("已确认的用例表缺本 TC 的预期结果")
        prefix = f"design/checks/{tc}.steps#"
        found = {}
        for value, target in result_links(row[0]["预期结果"]):
            if target.startswith(prefix):
                anchor = target[len(prefix):]
                if anchor in found:
                    raise ValueError(f"已确认的用例表重复引用 {anchor}")
                found[anchor] = value
        if found.keys() != set(anchors):
            raise ValueError("已确认用例的步骤锚点与计划不一致")
        return found

    def check(self, case, record):
        tc = case["id"]
        config = self.bindings[tc]
        if "object" in case and record.get("object") != case["object"]:
            return "invalid_evidence", "缺少计划对象的实测标识，或标识不符"

        expected = {}
        gaps, differences = [], []
        if "values" in config:
            expected["observed_values"] = config["values"]
        if "steps" in config:
            try:
                expected["observed_steps"] = self.step_values(tc, config["steps"])
            except (OSError, ValueError) as exc:
                gaps.append(str(exc))

        for name, fields in expected.items():
            observed = record.get(name)
            if not isinstance(observed, dict):
                gaps.append(f"缺少 {name} 的实测字段")
                continue
            if observed.keys() - fields.keys():
                gaps.append(f"{name} 含本 TC 未登记的字段")
            for field, wanted in fields.items():
                value = observed.get(field)
                if type(value) not in (str, int, bool):
                    gaps.append(f"{name}.{field} 缺少有效实测值")
                elif type(value) is not type(wanted) or value != wanted:
                    differences.append(f"{name}.{field}")

        if differences:
            return "failed", "；".join(["实测与确认预期不符：" + "、".join(differences), *gaps])
        if gaps:
            return "invalid_evidence", "；".join(gaps)
        return "passed", ""
