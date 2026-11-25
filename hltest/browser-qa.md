# 浏览器与端到端验收

根据产品约定的设备、页面和视口测试变更。使用已有 Playwright 测试与页面对象复用定位器和动作。在每个必测视口实际操作到用户看到结果，核对响应、可见对象和状态。记录动作前后画面、实测宽高与差异。视觉还原或对照竞品时沿用确认的基线和范围。[候选验收格式](acceptance-reports.md)

## 响应式和无障碍

可用本库 `hlbrowse responsive` 浏览 375×812、768×1024、1280×720 的布局。产品另有视口时在该尺寸执行实际用例。检查遮挡、溢出、截断、Tab 次序、关闭弹窗后的焦点、错误提示播报，以及产品适用的触控目标尺寸和间距例外。失败时可用 `snapshot -a -o knowledge/qa/issue-01.png` 注明控件，附实测操作及反馈。[浏览器入口](../hlbrowse/SKILL.md) · [WCAG 2.5.8 与项目设计标准](../hla11y/SKILL.md#设计阶段)

## 正式 CI 和重试

使用 Playwright Test 支持 JUnit `includeRetries` 的版本。以下配置用于正式候选验收。并发、超时按项目环境设置，测试数据和账号应能隔离。首轮失败保留截图，首次重试留追踪，按需保留失败录像。临时用 `--repeat-each=10` 可诊断不稳定项。

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: 2,
  failOnFlakyTests: true,
  reporter: [['list'], ['junit', { outputFile: 'outputs/e2e.xml', includeRetries: true }]],
  use: { screenshot: 'only-on-failure', trace: 'on-first-retry', video: 'retain-on-failure' },
});
```

在业务测试上使用 Playwright 原生 annotations 登记范围和版本。示例假设已配置 baseURL、已登录测试账号，筛选后没有订单。按项目替换 URL、按钮和实际表头。由 CI 从实测部署记录设置 `TESTED_REVISION`，测试本地检出时也可从该检出读取 `git rev-parse HEAD`。每个 testcase 的 `variant` 对应本次真正执行的断言。无变体时省略该条。报告同样支持套件级的范围和提交，若两级都写须一致。[必测变体](acceptance-reports.md#必测变体)

```ts
import { expect, test } from '@playwright/test';
import { readFile } from 'node:fs/promises';

const candidate = process.env.TESTED_REVISION;
const plan = process.env.HANDOFF_PLAN_SHA256;
const spec = process.env.HANDOFF_SPEC_SHA256;
if (!candidate || !plan || !spec) throw new Error('正式产品验收需要受测提交与本次用例采用的计划、规格摘要');
test('TC-01 空表导出', { annotation: [
  { type: 'revision', description: candidate },
  { type: 'plan_sha256', description: plan },
  { type: 'spec_sha256', description: spec },
  { type: 'scope', description: '订单导出/v1' },
  { type: 'variant', description: 'csv-empty' },
] }, async ({ page }, info) => {
  await page.goto('/orders?status=archived');
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: '导出 CSV' }).click();
  const path = info.outputPath('orders.csv');
  await (await download).saveAs(path);
  expect((await readFile(path, 'utf8')).replace(/\r?\n$/, '')).toBe('订单号,状态');
});
```

在候选的干净检出跑项目正式全量命令，把生成的 `outputs/e2e.xml` 纳入本次执行清单。以下为 CI 判定示例，沿用本项目已确认的计划和提交变量，`QA_DIR` 指向本次运行目录。失败时也归档原始 JUnit、退出码、追踪和验收输出。补测时同一候选下保留原失败，正式放行需要修复后的一次完整运行。

```sh
runner_status=0
npx playwright test || runner_status=$?
printf '%s\n' "$runner_status" > "$QA_DIR/playwright.exit"
qa_status=0
python3 "$HLTEST_DIR/qa-score.py" "$QA_DIR/run.json" --plan "$VERSION_DIR/acceptance-plan.json" \
  --plan-sha256 "$HANDOFF_PLAN_SHA256" --spec-sha256 "$HANDOFF_SPEC_SHA256" \
  --candidate "$CANDIDATE" > "$QA_DIR/acceptance.json" || qa_status=$?
if [ "$runner_status" -ne 0 ]; then exit "$runner_status"; fi
exit "$qa_status"
```

稳定通过时两项退出码均应为 0。首败次过时 runner 应非零，JUnit 含 `flakyFailure` 或 `flakyError`，验收简报标明重试后通过并阻断。持续失败时 JUnit 记录 `failure` 或 `error` 并阻断。接入现有 reporter 时用这三类样本验证实际报告。如果 reporter 省略重试历史，使用正式配置重跑，或让不支持该选项的版本在正式验收时关闭重试。[Playwright 配置](https://playwright.dev/docs/api/class-testconfig#test-config-fail-on-flaky-tests) · [JUnit 重试记录](https://github.com/microsoft/playwright/blob/v1.60.0/packages/playwright/src/reporters/junit.ts)
