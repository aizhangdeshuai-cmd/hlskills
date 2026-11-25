# 对照产品原型或竞品的界面与交互

为每个要还原的用例建立一份 JSON 契约。选择可重复到达的页面、视口、测试数据和关键状态。本项目确认的前端原型按[原型交接](../hlpm/prototype-handoff.md)以 `capture --prototype` 采集。本页的竞品示例使用普通 `capture`。浏览器安装见 [hlbrowse](SKILL.md)。

## 菜单示例

保存为 `analysis/reference/TC-01.json`。这个用例要求菜单相对按钮的位置、宽度、关闭和焦点返回与参考一致。项目决定沿用自己的品牌色，因此不用比较菜单背景。需要比较该属性时，在“打开菜单”检查点加 `"css":["background-color"]`。

```json
{
  "scope":"订单/v1","tc":"TC-01","viewport":[1280,720],
  "elements":{"trigger":{"reference":"#open","candidate":"#filter-toggle"},"menu":"#menu"},
  "steps":[
    {"action":["click","trigger"]},
    {"name":"打开菜单","element":"menu","visible":true,"focused":true,
     "box":{"relative_to":"trigger","x":2,"y":2,"width":3}},
    {"action":["press","Escape"]},
    {"name":"关闭菜单","element":"menu","visible":false},
    {"name":"焦点归还","element":"trigger","focused":true}
  ]
}
```

示例中的菜单可获得焦点。若实际页面把焦点移到首个菜单项，给该选项分配元素名，在打开后单独断言它获得焦点。预期“焦点归还”时先验证焦点确实离开触发器；实际始终停在触发器的路径只能证明焦点保持。

若任务是“在门店的 1024×768 终端导出订单”，为它单列 TC，沿用该终端约定的 CSS 视口，路径走到导出成功。在 `elements` 登记 `export` 为可点击菜单项、`done` 为本次导出成功才可见的反馈。从初始未导出状态运行以下步骤，能区分成功、点不到导出项以及点击后无反馈。收起菜单的独立用例继续按上例验收。

```json
[
  {"name":"尚未导出","element":"done","visible":false},
  {"action":["click","trigger"]},
  {"action":["click","export"]},
  {"name":"订单导出完成","element":"done","text":"导出完成"}
]
```

筛选表单可在应用后返回或关闭重开，检查 `{"name":"状态保留","element":"status","value":"done"}` 和 `{"name":"仅看我的","element":"mine","checked":true}`。前者适用于原生单值 input、select 或 textarea，填写已批准的脱敏预期。工具只返回匹配与否，并在各检查点截图中遮蔽这些控件。密码、隐藏输入、文件输入及多选列表不能用于 value。后者核对原生复选框或单选框的实际勾选状态。筛选后列表展示了哪些业务记录，另用业务 TC 中的断言核对。

`viewport` 写 CSS 像素的宽高，采集与比较使用 Chromium、设备像素比 1。需要独立验收手机或另一条任务时，分配对应 TC 和视口。每条 `action` 使用逻辑元素名，支持 `click/dblclick/hover/fill/select/scroll/wait`、`press` 和 `back/forward/reload`。只对明确获准操作的页面执行这些步骤；真实表单提交或会改变业务数据的操作选用演示环境。数据、定位器、URL 和截图均应可在项目内留存。工具只用新的浏览器会话，截图遮住密码输入框，供检查的其他字段需提前脱敏。

每个检查点有唯一名称。`visible`、`focused`、`enabled`、`checked` 填布尔预期，`text` 填控件的可见文案并按合并空白后的全文核对。文案或可用性逐项核验，操作是否成功还要真实点击到结果。`css` 列出需要一致的计算样式属性名。`box` 的 `x/y/width/height` 各填允许的绝对差值（CSS px）。指定 `relative_to` 时与锚点左上角比较，否则相对视口。预期消失的元素至少在一个检查点实际定位。

关键控件有语义要求时，在该元素的检查点加 `"role":"button","accessible_name":"调整时间"`。工具通过 Playwright 按角色查询同一个元素，按浏览器语义计算的名称逐项断言，覆盖文字按钮、关联标签和 `aria-labelledby` 命名的对话框。报告保留是否符合预期。键盘焦点和可见文字各自按已有字段核验。

对必须逐像素一致的稳定状态，加 `"screenshot":"exact"`，固定业务数据并等到页面完成写入。报告的 `pixel_environment` 登记浏览器渠道与版本、系统版本及架构、区域、DPR、视口，以及系统字体、衬线和等宽字体渲染固定中西文样本时实际使用的字体名称。项目自带字体随原型资源归档。可用 `--channel`、`--locale zh-CN` 复现基线条件。

新基线与候选环境一致时逐像素核对 PNG，并给出差异矩形。环境不同会列出具体字段，整屏结果标为不可判定，其他控件和焦点继续核验，命令退出 1。正式 QA 将仅有环境差异的场景归入 `invalid_evidence`；同时测得控件偏离时归入 `failed`，保留两类原因。旧观察可按原有像素规则复核，`coverage` 会提示缺少历史环境。只检查布局或行为的配方沿用原有流程。

## 采集、比较与复核

`HLBROWSE_DIR` 指向本库 hlbrowse 目录，`VERSION_DIR` 为业务项目的版本目录，`REFERENCE_TARGET` 和 `CANDIDATE_TARGET` 分别为参考页面和被测实现的 URL 或本地 HTML 路径。仅在有代表性的安全样本上采集。每次指定新的输出目录。

```sh
RECIPE="$VERSION_DIR/analysis/reference/TC-01.json"
REF_DIR="$VERSION_DIR/analysis/reference/TC-01"
python3 "$HLBROWSE_DIR/reference_check.py" capture "$RECIPE" "$REFERENCE_TARGET" "$REF_DIR"
python3 "$HLBROWSE_DIR/reference_check.py" coverage "$RECIPE" "$REF_DIR/observation.json"

# 审阅截图和读数，将当时确认的 sha256 输出保存在产品交接记录，读取为 REFERENCE_SHA256。
python3 "$HLBROWSE_DIR/reference_check.py" compare "$RECIPE" "$VERSION_DIR/design/list.html" \
  "$VERSION_DIR/design/checks/TC-01.reference" --baseline "$REF_DIR/observation.json" --baseline-sha256 "$REFERENCE_SHA256"

python3 "$HLBROWSE_DIR/reference_check.py" compare "$RECIPE" "$CANDIDATE_TARGET" \
  "$QA_DIR/TC-01" --baseline "$REF_DIR/observation.json" --baseline-sha256 "$REFERENCE_SHA256" --revision "$CANDIDATE"
```

采集成功时输出 `observation.json` 的 SHA-256。审阅该文件及截图，将确认的摘要随场景交接。参考变动时另存新的观察并重新确认。原型或候选的组件选择器不同，可在 compare 命令末尾加 `--selectors mapping.json`，文件如 `{"trigger":"#actual-filter-button"}`，只允许覆写契约已有的逻辑元素。实际映射保存在报告中。每个本地 HTML 使用离线会话，其脚本、数据和样式需要随包交付。

两种运行均保留每个检查点的视口 PNG 和读数。compare 写入相对路径、契约与基线摘要、各项差异，传入 `--revision` 时还记录被测提交。候选完整 SHA 从干净检出或实际部署记录取得。QA 交接须保留文件相对关系，包括基线观察、每组截图和契约。结果退出码为 0 表示约定维度全部通过，1 表示完成比较且存在差异，2 表示执行或证据不完整。定位不到操作按钮等执行错误会返回 2，已完成步骤的截图可用于排查。上游根据同一份契约重算各项结果。

对本地构建，正式 QA 还会复核 `target_file` 与 `resources` 清单内每个文件的 SHA-256。可将被测构建目录连同报告按原相对层级归档，在其他工作区离线复核。入口或依赖缺失、被覆盖时记录为无效证据；恢复原制品可复核历史版本，签认新构建需重新运行对照。HTTP(S) 报告对应记录时的部署与候选版本，复核报告不会重新访问站点。

产品交接固定读取 `design/checks/TC-01.reference/observation.json`。修稿重跑时，先将已有 `TC-01.reference` 在同一父目录重命名为一个空闲运行号（如 `TC-01.reference.run-002`），保留同目录层级和原始截图，再向固定路径执行 compare。候选 QA 每次可使用不同运行目录。已确认的参考观察单独归档，重新采集前保留原目录及对应的产品确认记录。
