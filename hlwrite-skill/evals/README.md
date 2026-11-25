# 技能改版对照评测

从仓库根运行以下命令。将项目题集保存为 UTF-8 JSON，令 `SUITE` 为该文件的路径。选 `routing` 测入口，选 `delivery` 测交付，选 `all` 同时评测两类。每类至少准备一道题，单独评测时文件只需包含所选类别。各版本使用同一题集、模型和宿主，每位答题者只接触一个版本。比率只代表这组样本。

| 题集字段 | 每道题的格式 |
|---|---|
| `routing` | 数组，每题四项依次为题号、题面、统计分组、期望技能名。前三项为文字，无需调用技能时第四项填 JSON `null`。 |
| `delivery` | 数组，每题为含 `id`、`prompt`、`criteria` 的对象。前两项为文字，`criteria` 将每个判据编号映射到可核验的预期结果。 |

同类题号须唯一。同时评测两类时，交付题号与路由统计分组也须分别命名。已有本地流程把题集放在评分脚本旁的 `cases.json` 时，可以省略 `--cases`。

```sh
python3 hlwrite-skill/evals/evaluate.py --cases "$SUITE" blind routing
python3 hlwrite-skill/evals/evaluate.py --cases "$SUITE" blind delivery
python3 hlwrite-skill/evals/evaluate.py --cases "$SUITE" rubric
```

1. 把 `blind` 输出中的题面交给答题者，保存该次 `suite_sha256`。评分条件只给复核人。要测宿主实际触发，用相同安装环境逐题新开会话，记录宿主首先实际选中的技能名，未触发记 JSON `null`。仅让模型对描述清单作选择时，在记录的 `host` 中注明“描述分类”，该数字衡量清单的可分辨性。
2. 交付题每套每题用独立会话，保留完整输出与实际产生的证据。将两版输出随机打乱，移去版本、路径等身份信息，交给看不到版本的复核人。复核人结合题面和 `rubric` 逐条判定。判通过附原文引句，必要时据实际产物与命令记录核实；判失败写明遗漏或相反的证据。将匿名记录映射回对应版本后评分。
3. 用相同范围的两份 JSON 作对比。未知技能名会作为误选保留，缺题、未复核、通过却缺少原文引句会列为 `incomplete` 并返回非零。已有可核查的失败记作有效评测结果。命令只核对记录、证据引句和归集分数，业务判定由独立复核人负责。

路由记录中 `routing` 按题号映射到一个技能名或 `null`，省略题号表示尚未执行。交付记录中 `delivery` 按题号填写回答和逐条判断。两份均填所选套件摘要、本次确切版本或工作区指纹、宿主及模型。以下为格式片段。

```json
{
  "suite_sha256": "<blind 输出的摘要>",
  "revision": "<本次版本>",
  "host": "<宿主及测量方式>",
  "model": "<实际模型>",
  "routing": {"R01": "<实际选择>", "R03": null},
  "delivery": {
    "D01": {
      "output": "<完整交付原文>",
      "checks": {
        "balance": {"pass": true, "evidence": "<从交付原文摘录的依据>"},
        "open": {"pass": false, "evidence": "<遗漏的业务决定>"}
      }
    }
  },
  "metrics": {"input_tokens": null, "cached_input_tokens": null, "output_tokens": null, "elapsed_seconds": null, "followups": null}
}
```

```sh
python3 hlwrite-skill/evals/evaluate.py --cases "$SUITE" score routing baseline.json candidate.json
python3 hlwrite-skill/evals/evaluate.py --cases "$SUITE" score delivery baseline.json candidate.json
```

只传一份记录时可先查遗漏。路由按题集定义的分组显示答对数与总数，交付按每道题统计已通过的判据数。相同题集全部完成且宿主、模型配对时才给质量差额，其他情况保留各版原始分数，比较项显示 `comparable: false`。费用字段只填宿主真实用量，缓存输入如为输入的子集，照原字段分别登记。没有计量时留空或填 `null`。两边宿主及模型可比并有实测值时才输出该项差额。耗时与补问次数也需对两版采用相同的采集口径。
