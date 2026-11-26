# 候选验收报告

从可信的项目测试任务或 CI 下载并保留实际产物。执行清单只列报告路径。源文件与清单一同归档，交接方可以用相同命令复算。上游修改范围时重新确认计划及摘要。

每个可独立漏验的必测分支优先分配独立 TC。如果同一 AC 明确要求服务端拒绝访问和页面隐藏按钮，两层可各用一个 TC。同一 TC 下共用多个必测参数、测试层或分片时，按下文登记必测集合。

普通 UI 场景在计划中指定 `viewport` 时，候选报告须为该 TC 提供对应实测宽高。JUnit 在 testcase property（整套测试同一视口时可用 suite property）、人工记录在该条 record 中写 `viewport`，值如 `1024x768`。自动化测试读取正在操作的页面，例如用 Playwright 的 `page.viewport_size` 取宽高后写入报告，人工记录填写实际运行条件。原生竞品对照报告按契约核查截图尺寸。每项已约定视口都关联到自己的 TC 和业务结果。

同一 TC 下的菜单和导出若分由两个浏览器测试负责，两者都要在约定视口至少通过一次。跨运行保留稳定的 JUnit `classname` 和 `name`，使同一用例在其他尺寸的补充运行可归到一起。无窗口的 UT、IT 省略视口。混合运行时在各浏览器 testcase 上记实测宽高。

同一 UI 场景约定了视口和 `required_variants` 时，每个必测变体各自提交该尺寸的通过记录，即使原生用例同名也逐项核对。服务测试可共用 TC 作为补充；需独立验收的无窗口业务条件另列 TC。

接收 hlpm 产品包时，从产品交接记录读取 `plan_sha256` 和 `spec_sha256`，分别传给 `qa-score.py` 的 `--plan-sha256` 和 `--spec-sha256`。保留计划旁的 `acceptance-sources.sha256`、`prd.md`、`test-cases.md` 和 `non-functional-requirements.md`。分册版还要保留附录所列的 `acceptance-criteria.md` 以及用户选交的数据、接口分册，启动测试前按验收分册核对范围与通过条件。在启动测试时核对本次运行采用的基线，把两项摘要写入原生 JUnit 或人工报告。评分器同时核对产品包、交接值与当次执行记录。历史产品报告缺摘要时，保留其原件，按本版确认用例补跑；复核阶段不能给旧报告补写当前摘要。文档变更导致摘要失配时，回到产品段复核修订。

独立 QA 也可使用单独确认的计划。在确认范围时运行下列命令，把输出保存在交接记录或 CI 的已批准输入。使用该独立计划验收时只传 `--plan-sha256` 和候选 SHA。新运行记录登记 `plan_sha256`。历史独立报告沿用 `revision` 和 `scope`，已登记的计划摘要必须匹配；报告声明了规格摘要时，同时提供相应的确认文档与 `--spec-sha256`。

```sh
python3 -c 'import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$VERSION_DIR/acceptance-plan.json"
```

```json
{"scope":"发票/v1","reports":["outputs/invoice.xml","outputs/manual.json"]}
```

## 必测变体

在原计划的 `scenarios` 中为该 TC 增加 `required_variants`，每项给一个唯一、跨运行稳定的标识。计划摘要随本次确认一并交接。按参数、测试层或分片登记真正要执行的检查。分片覆盖多个独立必测条件时，登记各条件。单一场景和原有计划可以省略此字段。

```json
{"id":"TC-01","acs":["AC-01"],"pages":[],"required_variants":["csv-empty","csv-rows"]}
```

为实际运行的 JUnit testcase 记录 property `variant`。pytest 可在对应参数实例写入 `record_property("variant", variant_id)`，Playwright 可用[原生 annotation](browser-qa.md#正式-ci-和重试)。每次执行只标记实际验证的一项。原生 XML 已有稳定参数名时，也可在计划直接使用精确的 `classname::name`，例如 `test_export::test_orders[TC-01-empty]`。显式 `variant` 优先，匹配区分大小写。

候选和范围匹配的各份 JUnit 可合并。只报告有数据分支时，TC-01 记缺测并列出 `csv-empty`。重复提交同一变体、其他 TC 的同名变体、人工汇总或空分片不能补足缺项。变体实际失败或跳过时保留对应状态。全量通过并满足该 TC 的其他约定后才可验收。新增加入的必测条件由上游修订计划和摘要，禁止根据本次实际输出缩减已确认范围。

## 已确认原型的候选验收

场景带有 `prototype_match` 时，按[原型交接的候选命令](../hlpm/prototype-handoff.md#开发和-qa-如何比对)操作实际前端，传入该 TC 的基线摘要及候选提交，将结果加入 `reports`。检查业务终态、约定的布局与外观，并用项目的接口或集成测试验证真实数据变化。JSON 中的 `prototype_checks` 列出逐 TC 的原型比对结果和具体差异。同一 TC 也引用竞品时，两份确认依据分别提供结果。

竞品和原型对照均按同一规则验收。默认把 TC 作为业务场景处理，已有对照只证明契约列出的检查点。混合场景补交同一候选的业务 JUnit 或人工实测，可与对照列在同一份执行清单。评分核对普通 JUnit 的身份、TC 与执行结果；QA 评审该用例的实际断言是否覆盖对应 AC。

单页纯视觉或控件交互 TC 在计划标记 `"visual_only":true`，对照通过即可。涉及对象、跨页或已登记 `case_assertions` 时保留业务验收。若同一次浏览器回放覆盖全部业务结果，在确认的 `prototype_match` 或浏览器 `reference` 内按 AC 登记本版契约的具名检查点。例如改期成功须更新详情和历史且仅写入一次，可填 `"business_checkpoints":{"AC-03":["成功后时间","成功后历史","双击只写入一次"]}`。每个名称须对应契约中操作后的实际结果断言，测同单还须断言计划对象。复算成功后这份记录可同时证明业务与 UI。QA 与产品在冻结计划前核对每个 AC 的状态、数据和恢复路径。另有 `case_assertions`、跨页回访或必测变体时，提供对应原始执行记录。

## 同角色跨页和回访

按计划 `pages` 的每一次访问记录，包括回到列表或重新加载同页。用同一条 testcase property `page_visits` 写 JSON 数组，人工实测在同一条 record 写数组。有 `object` 时逐页读取对象标识；纯导航用计划中的 `no_object_reason` 说明原因。逐页业务预期可在计划的 `visits` 中冻结，例如 `[{"expect":{"#status":"待审核"}},{"expect":{"#status":"已通过"}},{"expect":{"#status":"已通过"}}]`。

候选访问的一项形如 `{"page":"detail.html","object":"I-004","results":{"#status":"已通过"}}`。旧计划只有页面顺序时，在对应观测增加 `"expect":{"#status":"已通过"}`，从既有批准用例取得预期，实测从当前页面读取。纯导航逐页记录到达后的可见结果。页面顺序、对象和业务值均须核对。存在必测变体时每个变体独立提交完整行程。

## 跨角色候选记录

计划中含 `roles` 的 TC，用各角色的候选测试账号办理同一张单。在一次连贯执行中按 `visits` 顺序记录实际的角色、入口、身份、单号和各项结果。在原始 JUnit 的该条 testcase property `role_visits` 写入 JSON 数组，人工执行则写入同一条 record 的 `role_visits` 数组。

UI 场景用 `page` 记录页面，约定了视口时一并记录实测 `viewport`。产品计划的页面和控件名作为逻辑定位，候选的路由或组件不同可在测试内映射。身份与业务读数来自正在操作的页面。

例如员工回访的最后一项可为 `{"role":"employee","page":"employee.html","identity":"林沐","object":"L-004","results":{"#status":"已通过","#frozen":"0"}}`。漏传回访、角色身份不符或读数仍为待审批时，评分器指出对应 TC 及原因。其他服务测试可以共用该 TC，一个完整执行记录承载跨端结果。[产品计划字段及原型步骤](../hlpm/handoff-package.md#跨角色验收)

纯服务场景用 `operation` 记录当次调用的方法及路径或命令。例如退款审批的实测项为 `{"role":"finance","operation":"refund approve R-2","identity":"F-1","object":"R-2","results":{"writes":1}}`。从本次认证会话取得实际账号，从响应或命令输出读取单号与业务字段，保留约定的数据类型。按计划顺序保留申请、审批及回查各次读数。

## 竞品 UI 对照

沿用产品计划中的 TC、参考材料摘要、约定视口和适配决定，在实际候选上执行。每个可独立验收的行为或视觉要求有对应场景。已确认沿用本项目的样式在交接记录注明，比较项按约定选择。

- **可操作的网页。** 在实际受测候选检出或部署环境取得完整提交 SHA。按[对照命令](../hlbrowse/reference-check.md)用产品留存的基线和规则运行 `compare`，传入 `--revision "$CANDIDATE"`。把生成的候选 `observation.json` 路径加入原有 `reports` 清单，保留规则、基线、运行附图及相对目录。QA 核对 TC、范围、提交和参考证据，并重算逐项差异。原型的报告只用于产品交接。
- **截图、录屏或人工观察。** 打开已确认的原件，按计划中的维度在候选上实测。使用下方人工报告格式，在对应的每条 `records` 内附 `baseline_sha256`，值取自该 TC 的已确认参考。原件是截图或录屏时，随该行填写 `actual_artifact`（相对于人工报告的本地实测画面）和 `actual_sha256`；动效对照附候选短录屏，视频核验用本机 ffprobe。预期与实测写明观察的位置、画面或操作结果。单张截图可证明其可见外观；关闭、焦点和动效需有相应过程证据。
- **待证。** 标记 `pending` 的要求保留缺口及原因，取得参考证据或重新确认范围后再验。普通 JUnit 结果可用于同一功能的其他断言，正式竞品 TC 还须有约定方法的对照证据。评分器在 `reference_checks` 中逐 TC 列出对照状态、已批准的适配、原始报告与实测差异。

## JUnit

正式验收命令加 `--summary` 可直接阅读失败的 TC、用例、报告和来源位置。简报只摘录当前范围和候选上已有的失败说明。报告显式给出 `failure` 的 `expected`、`actual` 属性时分别展示两个值，普通 pytest 比较式按原文显示。报告只有状态时保留状态。有已验证的项目复跑命令时，可在该 testcase 的 property `rerun_command` 中记录，简报按文本展示。采集阶段使用脱敏样本。摘要会隐藏常见凭据或个人联系方式，并略去堆栈和长日志。

JUnit 的 suite properties 记录实际被测提交 `revision`、计划范围 `scope`、执行计划 `plan_sha256`，正式产品验收另记 `spec_sha256`。Playwright 等只在 testcase 输出这些信息时，可用原生 annotations 提供相同字段。每条用例的最终范围与提交须齐全，嵌套 suite、testcase 中出现的声明均须与实测候选一致。每个业务 testcase 的名称包含单个完整 TC 编号，或在 testcase properties 中指定 `scenario`。失败或错误会阻断，任一参数分支跳过也会列出。正式 CI 须保留 runner 的最终退出状态和每次重试结果。按[不稳定测试接入示例](browser-qa.md#正式-ci-和重试)验证首败次过会被报告并阻断。每份登记的报告应包含至少一个计划内场景。机器记录与文件权限、签名或 CI 身份的信任关系由项目执行环境提供。

例如，在现有 pytest 项目的干净候选检出中，通过 `conftest.py` 记录 suite properties。CI 在启动本次运行前核对测试所采用的规则与产品签出记录，将该记录中的摘要导出为下列环境变量。测试浏览器或独立服务时，从实际部署记录取得该服务所测版本。

```python
import os
import subprocess
import pytest

@pytest.fixture(scope="session", autouse=True)
def identify_run(record_testsuite_property):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    record_testsuite_property("revision", revision)
    record_testsuite_property("scope", "发票/v1")
    record_testsuite_property("plan_sha256", os.environ["HANDOFF_PLAN_SHA256"])
    record_testsuite_property("spec_sha256", os.environ["HANDOFF_SPEC_SHA256"])
```

通过已有参数用例的 `ids=["TC-01", "TC-02"]`，可在原生 XML 中得到 `test_void[TC-01]` 等名称。已有测试名称可用 `record_property("scenario", "TC-01")` 显式映射。用例预期来自已经确认的规则。运行 `python3 -m pytest --junitxml=outputs/invoice.xml` 后核对生成的原始报告；测试进程失败或提前中断时保留状态并跟进。完成验收所需的其他 CI 任务也须核对最终运行状态。

## 人工记录

在报告根对象记录本次实际采用的计划与规格摘要，下面的占位值使用执行当时的确认值替换。按实际参与者、发生时间、候选版本、场景、预期与实测结果填写。每个执行记录提供一种状态，取 `pass`、`fail` 或 `skipped`。跳过时在 actual 中说明原因。交接时可沿报告文件和 TC 编号定位原文。

```json
{
  "kind":"manual", "scope":"发票/v1", "revision":"6d30f4af8336a62eb1226290e4520ff8ba961ed0",
  "plan_sha256":"<本次执行的计划摘要>", "spec_sha256":"<本次执行的规格摘要>",
  "records":[{"id":"TC-02","executor":"当班验收人","when":"2026-11-20T10:00:00+08:00",
              "expected":"读屏按顺序播报原因和确认按钮","actual":"签核设备上两项按预期顺序播报","status":"pass"}]
}
```

**业务读数。** 若该 TC 登记了 [case_assertions](../hlpm/handoff-package.md#把关键业务预期连到断言)，申请通过时在同一条 record 记录实际读到的全部关键结果。计划指定 `object` 时，填写本次实际办理的对象标识。有约定视口的 UI 业务须在该视口实测并记录宽高；另一次运行的外观核对只证明当时见到的界面。按 TC 约定的前置条件、办理顺序和时点取数，使用原类型区分整数 0、布尔 false 和文本 "0"。

- `values` 的读数放入 `observed_values`，沿用登记的字段名。例如清空草稿后查询实际条数，填写 `"observed_values":{"remaining":0}`。同一字段在不同时点需独立验收时，可在计划中命名为 `before_remaining`、`after_remaining`。
- `steps` 的读数放入 `observed_steps`。键取该 TC 登记的锚点；值按相同步骤顺序记录页面上实际读到的文字或控件状态，多行用 ` / ` 连接。例如 `"object":"ZN-2026-002","observed_steps":{"L8-L10":"0 / 5 / 3","L17-L19":"0 / 0 / 8"}`。评分依据为确认规格中该 TC「预期结果」格的可见链接文字。使用独立计划且只登记了外部步骤位置时，可交验证这些步骤的原生测试报告，或补充确认规格后执行人工核对。

两种断言同时登记时，分别提交两组读数。可归属的实测值与预期不符即失败。缺字段、对象不符或缺确认依据会阻断人工通过。原报告缺登记读数时保留原件，复测后交新报告。仅做人工竞品外观比对时沿用原对照格式；同一记录要证明已登记的业务结果时须同时提供相应读数。无已登记业务断言的体验或旧场景继续按文字实测验收。执行者与复核者须核对文字、读数及对象是否来自实际运行。
