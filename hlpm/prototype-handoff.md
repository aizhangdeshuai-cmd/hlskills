# 从确认原型还原前端

当已确认的产品原型是前端实现依据时，交付同一版本的 PRD、可操作页面、页面实际加载的资源，以及关键任务的复验方法。业务负责人从 PRD 的演示链接开始。开发者和 AI 从同一张卡的 AC 和 TC 开始。

## 确定要实现的版本

1. 在 PRD 的 BL 功能卡放入真实可点击的演示入口，写明角色、示例数据、起始状态、操作和可见结果。评审人能从这个入口完成正常路径，也能重走影响本次决定的失败、取消或恢复路径。路径涉及模拟服务时注明模拟触发条件。
2. 按用户实际要还原的任务选定页面、状态和视口，记录允许差异与确认决定的位置。采集生产界面时隐藏演示专用的身份切换和重置工具。多角色任务从各自会话或预置身份进入，使画面和操作均可在正式候选重现。视觉采用原型的样式、字体和图标，权限、校验与写入采用同版 PRD 的 AC。有冲突时定位到具体控件和状态，修订后再确认。
   迭代原型的“本次新增／修改”提示、提示开关、BL 钉点和基线对照只用于评审；采集开发还原基线时关闭这些提示并使用修改后的业务页面。开发实现新增字段及其交互，无需实现提示标签或提示开关，也不把它们纳入候选视觉对照。
3. 给接手者一条可以回查的路径。例如 `BL-1 → AC-2 → TC-01 → 页面与控件 → 操作步骤、截图及样式源`。在现有控件表、TC 或验收计划中填入路径。共用组件、图标和字体直接指向原文件或项目组件。记录哪些尺寸随容器伸缩、哪个断点改布局、长文本如何换行，以及焦点、滚动和状态在返回时如何恢复。对于“至少留多少空间”等设计约束，把下限和指定设备的实测值分别标明。

## 固定原型和观察结果

把原始要求中指定按原型还原的来源标记为 `prototype_ui: true`。先在原型上跑该 TC 的业务步骤。对需要复刻的代表状态，用同一个 TC 写[浏览器对照契约](../hlbrowse/reference-check.md)。选取会让错误实现暴露的断言，例如弹框的相对位置、取消后的焦点、错误文案和可再次提交的条件。固定数据、字体与渲染环境的画面可以加 `"screenshot":"exact"` 比较整张视口。

复用浏览器记录证明业务结果时，沿同一条 AC 找到每个能独立出错的结果。例如预约详情和历史分别读取，重复提交要实际触发两次并核对写入次数。约定键盘办理时，从起始页按 Tab 到达入口，并按 Enter 或空格激活。选一个影响办理的动作，在临时副本只改错它的结果并复跑。例如保留“已批准”的文案，把焦点移到筛选器。对应原单详情的 `focused:true` 应报出该检查点。选用整屏像素时交付观察中的 `pixel_environment` 和业务数据；环境有差异的状态要在相同条件下重测。

同一 AC 涉及两种身份时，可分别登记[跨角色业务 TC](handoff-package.md#跨角色验收)与单端视觉 TC。业务 TC 用 `roles` 和 `visits` 核对各端的身份、单号和结果。单端视觉 TC 关联同一 AC，绑定 `prototype_match`；仅验证界面时填写 `visual_only: true`。视觉页在业务路径中只属于一个角色时可直接推定，多个角色共用页面时填写 `prototype_match.role`，并在契约中核验可辨认当前身份的已知控件。

若已确认特定角色、部分页面或多个视口，在对应的 `prototype_ui` 来源补 `"prototype_views":[{"role":"employee","page":"employee.html","viewport":[375,812]}]`。每项都要有该角色、页面和视口的视觉 TC；手机和桌面分别列项。冻结原始要求时一并冻结这份清单。沿用仅有 `prototype_ui: true` 的单端计划时，原有场景与基线可直接复用。

以下示例的路径均从本次版本目录起算。`HLBROWSE_DIR` 指向本库的 hlbrowse 目录。

```sh
cd "$VERSION_DIR"
python3 "$HLBROWSE_DIR/reference_check.py" capture design/checks/TC-01.recipe.json \
  design/appointment.html design/checks/TC-01.approved --prototype
python3 "$HLBROWSE_DIR/reference_check.py" coverage design/checks/TC-01.recipe.json \
  design/checks/TC-01.approved/observation.json
```

`coverage` 离线校验采集报告、契约和各检查点截图，列出该视口下每个状态约定的文字、焦点、样式、布局或整屏像素对照。在已有自检的设计行分别写明采集范围、约定的对照维度、确认记录和候选结果。例如“桌面弹窗已采集，约定位置、圆角与焦点。业务待审，候选待测。”手机布局若也在还原范围，引用对应视口的契约及证据。仅需验证操作的状态沿用业务用例。

展示生成的截图和对应原型，确认它们属于实际获选版本。将真实确认记录与采集输出的摘要放回对应场景。以下是 `acceptance-plan.json` 中该 TC 的一个字段，尖括号内容用实际值替换。

```json
{
  "prototype_match": {
    "origin": "<确认人、日期及可回查的决定位置>",
    "recipe": "design/checks/TC-01.recipe.json",
    "baseline": "design/checks/TC-01.approved/observation.json",
    "sha256": "<采集输出的 SHA-256>"
  }
}
```

按[产品交接步骤](handoff-package.md#文件检查)交付 `plan_sha256` 与 `spec_sha256`。HTML、样式、图片或行为变更后，保留旧基线，为受影响的场景重跑、复核并更新确认记录。有竞品要求时，原型也可保留独立的 `reference` 用来说明哪些部分遵循竞品、哪些是本项目决定。

## 开发和 QA 如何比对

按相同的业务数据与视口打开原型和候选。先还原页面结构、组件状态和样式，使用真实服务替换模拟数据。两边的 DOM 或框架可以不同，逻辑元素名可通过 `--selectors` 映射到候选的控件。将 `CANDIDATE_TARGET` 设为实际受测页面，`CANDIDATE` 取自该检出或部署，`APPROVED_SHA256` 取自交接场景。

```sh
python3 "$HLBROWSE_DIR/reference_check.py" compare design/checks/TC-01.recipe.json \
  "$CANDIDATE_TARGET" "$QA_DIR/TC-01-prototype" \
  --baseline design/checks/TC-01.approved/observation.json \
  --baseline-sha256 "$APPROVED_SHA256" --revision "$CANDIDATE"
```

将生成的 `observation.json` 加入[候选验收清单](../hltest/acceptance-reports.md)，保留基线与实测截图的相对路径。本地候选连同入口和实际加载的依赖一起归档，正式评分按 `resources` 中的摘要复核原受测制品。按同一候选版本的 `prototype_checks` 回填每个 TC 的实际比较结果，缺测保留待测，差异指向具体状态和维度。涉及动效节奏、原生控件、不同设备字体渲染时，用对应的录像或真机记录复核。

例如验收预约改期时，在约定视口实测打开弹窗、取消、冲突恢复、成功保存与刷新。分别核对原单时间、改期历史、有效写入次数和取消后的焦点。刷新后从详情按 Tab 到达「调整时间」，按 Enter 打开弹窗，并核验按钮角色与可访问名称。将各项实测断言按 AC 登记到本版契约。[候选验收记录](../hltest/acceptance-reports.md#已确认原型的候选验收)
