# 健康评分系统

已登记质量观察可计算加权健康度（0–100）。正式验收以确认计划内每个场景的结果为准。

| 类别 | 权重 | 检查项 |
|------|:---:|------|
| 功能正确性 | 20% | 核心路径是否正常、表单提交、数据展示 |
| 控制台错误 | 15% | console.error 数量与严重性 |
| 无障碍 | 15% | WCAG 2.2 AA 合规度 |
| 用户体验 | 15% | 交互流畅度、加载态/空态/错误态处理 |
| 视觉一致性 | 10% | 与设计稿对比、响应式适配 |
| 性能 | 10% | 首屏加载时间、LCP、CLS |
| 链接有效性 | 10% | 死链检测、外链可达性 |
| 内容完整性 | 5% | 文案正确、无缺失、无乱码 |

### 健康度与历史基线

执行前固定 `scope`（流程、环境、视口或接口契约和计划版本）及每个检查的稳定 ID、类别、是否必测。执行后将观察存入项目 QA 目录。将 CI 或本地测试报告的运行 ID、实测提交和逐项结果导出到 `runs`，在每条已执行的检查上引用该 `run_id`。人工验收使用可回查的执行记录号、实际测试版本和结果。交接时核对原报告的来源、运行链接或本地存档。以下字段为示例值：

```json
{
  "scope": "订单导出/API/test/v1",
  "revision": "6d30f4af8336a62eb1226290e4520ff8ba961ed0",
  "runs": {
    "orders-ci/417": {
      "revision": "6d30f4af8336a62eb1226290e4520ff8ba961ed0",
      "outcomes": {"TC-021": "pass"}
    }
  },
  "checks": [
    {"id":"TC-021","category":"function","required":true,"status":"pass",
     "run_id":"orders-ci/417","evidence":"reports/417/export.xml#TC-021"}
  ]
}
```

类别依上表顺序为 `function`、`console`、`accessibility`、`usability`、`visual`、`performance`、`links`、`content`。状态取 `pass`、`fail`、`unverified`、`na`。证据字段填写实测定位或缺测、不适用的具体原因。执行如下命令；基线文件名取尚未存在的路径。

脚本将运行 ID、检查 ID、运行结果和提交相互核对。缺记录、结果冲突、必测项仅有其他提交的证据时，该项变为 `unverified` 并说明原因。旧观测和旧基线仍可读取，缺运行记录的历史结果按待验比较。对于明确允许复用的非必测项，保留原运行 ID、来源版本，在该行写入 `"reuse":{"for_revision":"当前候选的完整 SHA","reason":"适用范围及仍可沿用的依据"}`。再次换版时须重核适用性。

```sh
python3 "$HLTEST_DIR/qa-score.py" knowledge/qa/observations.json --health-only --save-baseline knowledge/qa/baseline.json
python3 "$HLTEST_DIR/qa-score.py" knowledge/qa/candidate.json --health-only --baseline knowledge/qa/baseline.json
```

`HLTEST_DIR` 是已加载的 hltest 目录。每个适用类别得分为其通过数除以适用检查数，再按上表权重加权并对适用权重归一。缺类别或存在未验证项时，`qa_health` 为空，输出证据缺口。必测项未通过时列在 `blocking_checks` 并返回 1；输入有误或基线不可比时返回 2。返回 0 表示输入已处理且已列明的必测项无阻碍，仍需检查覆盖范围。回归比较仅在同范围、同检查 ID、同适用性下进行。

报告附候选提交、原始观测、与基线不同的检查 ID 和证据。[hlreview](../hlreview/SKILL.md) 单独给出发布准备度。必需的 CI、UAT 或关键路径失败时暂停放行；未执行时记录待补证据。
