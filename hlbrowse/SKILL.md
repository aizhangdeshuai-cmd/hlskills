---
name: hlbrowse
description: 在隔离的测试浏览器中复核页面交互、三种视口布局、设计稿及上线冒烟，输出截图、可访问性快照和控制台证据。Use when 用户要求浏览器 QA、验证设计稿或收集界面缺陷证据时使用。
---

# 浏览器交互 QA

对用户指定的本地 HTML、测试站点或已部署页面运行一条真实操作路径。默认只报告；当任务也包含修复时，用相同的输入和步骤复验修复结果。涉及线上修改操作时使用获准的测试账户与数据。

## 准备

从本次加载的 hlbrowse 目录定位 `browse.py`。交互执行使用 Python 3.10+、Playwright 和 Chromium 系浏览器。精确画面比对使用 Pillow。在业务项目根执行下列命令，首次使用可在项目虚拟环境中安装依赖。

```sh
HLBROWSE_DIR="/所选仓库/hlbrowse"
python3 -m pip install -r "$HLBROWSE_DIR/requirements.txt"
python3 -m playwright install chromium
python3 "$HLBROWSE_DIR/browse.py" about:blank 'expect-clean'
```

已安装 Google Chrome 或 Edge 的环境可以省略下载 Chromium，在每次运行时加 `--channel chrome` 或 `--channel msedge`。每次打开临时测试上下文，可用 `--headed` 查看操作。若宿主直接提供浏览器，也可在宿主按下面的验收步骤实际操作，一并记录宿主和浏览器。缺少可用浏览器时注明哪些操作未验证。

## 操作与断言

把目标和步骤放进同一条命令，导航、填表、点击和截图共享页面状态。下例的选择器与预期文本需替换成目标页面的实际值：

```sh
python3 "$HLBROWSE_DIR/browse.py" "knowledge/doc/v1/design/order.html" \
  'snapshot' 'fill #search 待处理' 'click #apply' 'expect-visible-text #status 已筛选' \
  'snapshot -D' 'snapshot -a -o knowledge/qa/filter-evidence.png' 'expect-clean'
```

设计稿交接时，按产品段清单为每个适用页面生成指定名称的截图：

```sh
python3 "$HLBROWSE_DIR/browse.py" "knowledge/doc/v1/design/order.html" \
  'visible main' 'screenshot knowledge/doc/v1/design/screenshot-order.png'
```

需要边看结果边决定下一步时，仅传目标，在同一终端逐行输入下表的命令；每条完成后输出结果，EOF 结束会话。批量调用也可用标准输入传入同样的多行步骤。选择器使用 Playwright locator 语法，含空格的参数在步骤内使用引号，例如 `'click "text=Save draft"'`。断言、导航或命令失败时返回非零，后续步骤不会执行。

| 目的 | 命令 | 证据或行为 |
|---|---|---|
| 导航、标签页 | `goto URL`、`load-html FILE`、`back`、`forward`、`reload`、`url`、`newtab URL`、`tabs`、`tab 0` | 目标可以是 http(s)、本地路径、file URL 或 about:blank。标签索引从零开始 |
| 操作、断言 | `click SEL`、`dblclick SEL`、`fill SEL "值"`、`select SEL "值"`、`hover SEL`、`press Enter`、`type "文本"`、`scroll [SEL]`、`expect-text SEL "预期全文"` | type 向焦点元素输入文本。scroll 将元素滚入视口，省略选择器时滚到页底 |
| 可见业务文案 | `expect-visible-text SEL "预期全文"` | 在可见元素上核对渲染文本。验收提示、空态等用户反馈时，在操作前后分别验证。另有 `expect-text` 可核对 DOM 文本，包括隐藏元素 |
| 控件状态 | `expect-disabled SEL`、`expect-enabled SEL`、`expect-hidden SEL` | 核对控件禁用、启用或隐藏。隐藏断言允许目标不存在，验证从显示变为隐藏时先核对操作前的存在性。 |
| 等待页面 | `wait SEL`、`visible SEL`、`wait --load`、`wait --networkidle` | 前两者等待元素可见。验证业务就绪时优先等具体页面元素或预期文本 |
| 读取内容 | `text`、`text SEL`、`links`、`forms`、`css SEL color` | 文本、链接、表单字段名与类型、计算后样式；表单清单不采集输入值 |
| 结构差异 | `snapshot`、`accessibility`、`snapshot -s SEL`、`snapshot -D`、`snapshot -D -s SEL` | 前两者读取整页可访问性树。用同一个选择器可只比较对应区域。差异命令需要同范围的基准快照 |
| 视觉证据 | `screenshot PATH`、`screenshot --viewport PATH`、`screenshot SEL PATH`、`snapshot -a -o PATH`、`pdf PATH` | 全页、当前视口、元素和带编号标注的 PNG，以及打印版 PDF。省略全页或视口截图路径时写入当前目录 screenshot.png |
| 断点布局 | `responsive PREFIX` | 同一页面状态输出 mobile 375×812、tablet 768×1024、desktop 1280×720 三张视口截图，并恢复原视口 |
| 上线冒烟 | `console --errors`、`expect-clean`、`perf` | 查看本次会话页面异常与控制台错误，或断言没有错误。perf 读取当前导航的 TTFB、DOM 就绪和加载耗时，单位 ms |
| 网络取证 | `network` | 从首次导航起列出当前会话各标签页的 HTTP(S) 响应与失败事件。每条记录仅包含方法、状态和 URL 路径，连接失败标为 failed。省去域名、查询串和片段，不收集请求头、Cookie 或请求体 |

比较已确认的产品原型或指定竞品时，使用[界面与交互对照命令](reference-check.md)采集基线，按 TC 在候选前端重跑。

## 验收与迁移

- **产品、测试。** 从产品需求选一个可观察的行为，如点开一个业务标记、提交无效表单或切换页面状态。先记基线，再操作并断言预期状态。设计稿截图写入约定的版本目录，缺陷报告写明 URL、视口、步骤、预期、实测、证据路径和未验证项。
- **文案可见性。** `expect-visible-text` 使用 Playwright 的可见性判断（元素有布局尺寸且未被 visibility 隐藏）并匹配渲染文本。若验收还要求文字在当前视口可见、无覆盖或对比度达标，需在指定视口用截图检查遮挡和透明度，并测量对比度。
- **布局、性能。** 用相同输入生成两版 PNG 后并排检查溢出、遮挡和布局变化。已有像素对比测试的项目可将这两组图片交给项目的比较器。`snapshot -D` 检查文本结构，图片变化需另行判断。`perf` 需在同设备、相同网络条件下与基线比较。
- **命令兼容。** 旧的守护进程和跨命令共享状态改为单进程内的步骤序列；登录流程使用临时测试上下文，不导入真实浏览器 Cookie。旧 `@eN` 引用改为页面 locator，编号截图上的序号只用于缺陷报告。高级网络调试、存储检查或多页复杂流程交给项目内 Playwright 测试或浏览器开发者工具。收集产物前检查遮蔽要求，脚本截图自动遮蔽密码框，其他字段、页面文本、PDF 和日志需使用脱敏测试数据。
- **运行验证。** 准备步骤中的 `about:blank` 命令可验证浏览器能启动。核验交付时，在目标页面执行已确认的操作和可见结果断言，记录退出码与证据。涉及请求失败或断线恢复时，按测试环境提供的条件重现，并核对 `network` 及页面反馈。生产环境回滚由部署流程根据实际证据决定。

流程参考 [gstack v1.102.0.0](https://github.com/garrytan/gstack/releases/tag/v1.102.0.0) 的宿主浏览器与备用驱动方案；本目录提供独立实现。底层行为见 [Playwright 快照](https://playwright.dev/python/docs/aria-snapshots) 和 [截图](https://playwright.dev/python/docs/screenshots)。
