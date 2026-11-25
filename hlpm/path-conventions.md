---
name: hlpm-path-conventions
description: >-
  交付文档目录规范中央文档（版本管理）。定义 14 项交付物的完整路径、版本目录结构、命名约定、深度限制、特殊情况处理。**v12 关键变更**: 每次产品段流程产出交付物到独立版本目录 `docs/vN/`,启动时自动扫描历史未开发版本。**v18 变更**: 产品段交付物由 8 项扩为 9 项(新增"设计稿截图"),6 必出 + 3 条件出。**v19 变更**: 验收标准合并入一致性矩阵 §1"验收方法"列,产品段交付物由 9 项减为 8 项(5 必出 + 3 条件出),交付物总数 15 → 14。**v29 变更**: 生成文档根 `docs/` → `knowledge/`,版本快照 `docs/vN/` → `knowledge/doc/vN/`,扫描双读兼容老 `docs/v*/`。被 SKILL.md / hlpm / hldev 三个文件共同引用。Use when 用户询问"输出到哪"、"目录怎么组织"、"文件命名规则"。
---

# 交付文档完整目录规范

> 属于 `hlskills` 技能系统的**中央规范文档**。
> 被以下 3 个文件共同引用：
> - 主入口 `SKILL.md`（通用规则：文件输出路径）
> - `hlpm/SKILL.md`（完整交接的 8 类产物。仅交 PRD 或原型时按选定终点使用相应路径）
> - `hldev/SKILL.md`（开发段 6 项补充交付物）
>
> **目的**：解决"路径规范散落 3 个文件 + 不完整（5 个问题）"的现状，作为单一可信源（single source of truth）。

---

## 零、版本目录与状态

### 0.1 发现版本

从目标项目根运行随技能分发的 [version.py](version.py)。`HLPM_DIR` 指向本次加载的 hlpm 目录。`list` 只读扫描新根 `knowledge/doc/` 与旧根 `docs/` 的 `vN` 子目录，N 是从 1 起的整数。输出 JSON 的 `versions` 按数值排序，每项有 `version`、相对于项目的 `path` 和 `state`；`next` 是尚未创建的新根建议路径。

```sh
python3 "$HLPM_DIR/version.py" list .
# 继续现有包时使用选定的编号或路径；同号须指定路径
VERSION_DIR=$(python3 "$HLPM_DIR/version.py" resolve . docs/v7) || exit 1
```

### 0.2 选择版本

- 已指定版本目录时优先解析该目录。只给编号且两个根均有同号时，脚本列出两个实际目录并返回非零，待选定后继续。
- 创建产品版本时，有 ready 或 rejected 包就列出实际目录，让用户选续写或新建；accepted 表示开发正在使用，completed 和 archived 作为历史保留。若没有待续写包，或用户已选新建，运行 `python3 "$HLPM_DIR/version.py" new .` 创建并取得绝对路径。编号取两根中的最大编号加 1，无历史版本时为 v1。
- 开发段接收已交接的明确路径。缺少路径时选本次任务对应的可接收包，如有歧义先核对。accepted 版本可续办开发。conflict 表示已有互斥标记并存，应保留现场并核实记录后再继续。
### 0.2.1 旧版本原地续写

在交付摘要写明版本目录和适用条件。后文用 `{version_dir}` 表示这一实际目录，`{ver}` 仅表示如 v7 的编号。新包创建在 `knowledge/doc/`，续修的文档、拒收单和标记全部写回选定目录。跨版本共享文档仍在 `knowledge/`。

### 0.2.2 包身份与复盘

从项目根运行 `python3 "$HLPM_DIR/version.py" retro . "$VERSION_DIR"`。输出 `packages[0].package` 是包相对项目的路径，`report` 是该包唯一的复盘位置。例如 `docs/v7` 写到 `knowledge/retro/docs/v7.md`，`knowledge/doc/v7` 写到 `knowledge/retro/knowledge/doc/v7.md`。创建父目录后在报告首部登记实际包路径，各阶段按同一包和章节更新。阶段结论关联本次修订、验证日期，开发完成时记录候选 SHA 与完成日期。

早期的 `knowledge/retro/v7.md` 保存在原处。命令在 `legacy` 中列出旧文件及其可能对应的包。首次续办时依据旧记录中的包路径、交接记录或提交确认归属，再把该包已有的阶段结果和旧文件引用记入对应 `report`。同号旧文件归属不明或混有多包时，只采用能确认来源的部分，其余列入待核。统计按 `package` 去重，产品和开发的同包记录算一期。

### 0.3 接收、拒收与复验

状态脚本只记录已经做出的决定。文件检查与人工内容验收见[产品交接清单](handoff-package.md)。

| list 输出 | 空标记 | 可做的工作 |
|---|---|---|
| ready | 无 | 待产品打包或开发接收，按条件继续。 |
| rejected | `.dev-rejected` | 开发在 `{version_dir}/handoff-rejection.md` 追加问题、定位与日期，再执行 `mark "$VERSION_DIR" reject`。产品追加修订证据，重新执行步骤 9.5 和 11，将原包交回复验。 |
| accepted | `.dev-accepted` | 开发第 0 步对文件与适用内容均验收通过后执行 `mark "$VERSION_DIR" accept`。复验通过时替换拒收标记，拒收单和修订历史保留。 |
| completed | `.dev-completed` | 第 13 步验证开发成果后，由写入角色根据 verifier 结论执行 `mark "$VERSION_DIR" complete`。发布与部署有各自的证据。 |
| archived | `.product-archived` | 产品决定归档待接收或已拒收的包时执行 `mark "$VERSION_DIR" archive`。之后的发现操作仍展示历史状态。 |

```sh
# 命令格式。动作只选本次实际决定的一项。
python3 "$HLPM_DIR/version.py" mark "$VERSION_DIR" accept
```

重复同一动作可安全重试。无标记的新旧包均按 ready 处理。旧 `.dev-rejected` 可走同一复验流程，旧 `.dev-completed` 和 `.product-archived` 可直接识别。迁移前已进入开发但无 accepted 标记的版本，沿用原接收记录或复验后登记 accept。状态冲突、并发争用或目录错误会返回非零并说明原因。

### 0.4 完整目录结构（含版本目录）

```
{项目根目录}/
├── knowledge/                              # 生成文档根(v29 起;原 docs/)
│   ├── doc/                                # 版本快照区(hlpm 管,不属 hlkb 13 类总库)
│   │   ├── v1/                                 # 版本 1
│   │   │   ├── prd.md
│   │   │   ├── test-cases.md
│   │   │   ├── non-functional-requirements.md
│   │   │   ├── consistency-matrix.md          # 含验收标准(§1 业务规则覆盖矩阵"验收方法"列)
│   │   │   ├── acceptance-plan.json            # 已确认来源、AC 和必测 TC，供交接与候选测试读取
│   │   │   ├── acceptance-sources.sha256       # 需求澄清时冻结的来源清单摘要
│   │   │   ├── handoff-self-check.md
│   │   │   ├── design/
│   │   │   │   ├── *.html
│   │   │   │   ├── bl-marker.css                   # bl-marker 钉点资产(v23 起随设计稿复制)
│   │   │   │   └── bl-marker.js                    # bl-marker 钉点资产(v23 起随设计稿复制)
│   │   │   ├── analysis/
│   │   │   │   └── competitive-analysis.md
│   │   │   └── .dev-accepted                   # 当前状态示例；其余状态见 §0.3
│   │   └── v2/                                 # 版本 2（独立）
│   │       └── ... （同 v1 结构）
│   ├── design/                             # 全局设计规范（与版本无关）
│   │   ├── spec.md
│   │   ├── SKILL.md
│   │   └── *.md
│   ├── adr/                                # 全局 ADR（与版本无关;与 hlkb 总库 adr/ 自然合并）
│   │   └── NNNN-slug.md
│   ├── user/                               # 全局用户文档
│   │   ├── manual.md
│   │   └── help.md
│   ├── tech-design.md                      # 全局技术设计（开发段输出,与最新版本对齐）
│   ├── rollback.md                         # 全局回滚方案
│   ├── qa/                                 # 全局测试报告
│   │   └── *.md
│   ├── prd.md                              # hlkb 总 PRD(跨版本累计,hlpm 步骤 12 追加)
│   ├── glossary.md                         # hlkb 术语表(通用语言,hlpm 步骤 1 梳理)
│   ├── api/ db/ state-machines/ enums/ error-codes/ dependencies/ env-vars/ tests/ pitfalls/ retro/   # hlkb 各类总库
│   └── README.md                           # hlkb 知识库总目录
├── CHANGELOG.md                            # 根目录（业界惯例）
├── DESIGN.md                               # 根目录（跨目录兜底）
└── .hl/memory/                             # 项目记忆（AI 跨会话工作记忆,隐藏）
    ├── project.md
    └── ...
```

### 0.5 与"文档深度 ≤ 4 层"规则的关系

**标准路径的目录深度**：

- 旧路径(v12-v28)：`docs/v1/prd.md`（深度 2)
- 新路径(v29 起)：`knowledge/doc/v1/prd.md`（深度 3,**符合 ≤ 4 限制**）
- 设计稿：`knowledge/doc/v1/design/order-detail.html`（深度 4,**符合 ≤ 4 限制**）

如果未来版本目录嵌套（如 `knowledge/doc/v1/release-a/`），需要重新审视深度限制。

---

## 一、根级规则

### 1.1 项目根目录定位

- **项目地址已知**（`.hl/memory/` 存在 或 用户已指定）→ 输出到项目根目录的对应子目录
- **项目地址未知** → 🚨 **立即向用户提问**："请指定项目根目录地址"，用户回复后再输出文件
- **严禁**将文件输出到 `/tmp`、`~` 等临时或个人目录

### 1.2 命名规范（强制）

| 规则 | 说明 | 唯一例外 |
|------|------|---------|
| 文件名 | **小写 + 短横线**（kebab-case） | `CHANGELOG.md`（业界惯例大写） |
| 文件数 | **单数**（不是 `matrixs` / `caseses`） | 无 |
| 路径深度 | **≤ 4 层**（如 `knowledge/doc/v1/design/order-detail.html`;v29 起快照区多一层,由 ≤ 3 放宽） | 设计稿 `components/` / `flows/` 子目录为历史例外 |
| 文件后缀 | `.md`（文档） / `.html`（设计稿） | 无 |
| 目录名 | **小写 + 复数**（如 `knowledge/design/` / `knowledge/adr/`） | 版本快照区 `knowledge/doc/`(单数,固定名) |

### 1.3 特殊根目录文件（不在 `knowledge/` 下）

| 文件 | 路径 | 原因 |
|------|------|------|
| `CHANGELOG.md` | 项目根目录 | 业界惯例（GitHub / npm / Cargo 等放根目录） |
| `DESIGN.md` | 项目根目录 | 6a.1 步骤的跨目录兜底（项目级而非文档级） |
| `knowledge/` | 项目根目录 | hlskills 生成文档根(v29 起):含 hlpm 版本快照区 `doc/vN/` + 全局文档(design/adr/user/qa/tech-design.md/rollback.md) + hlkb 项目总文件库(13 类跨版本累计:PRD/术语表/接口/数据库/ADR/状态机/枚举/错误码/依赖/环境变量/总测试库/踩坑记录/版本复盘)。放根目录可见,与 src/ 同 commit |
| `.hl/memory/` | 项目根目录 | hlskills 体系约定的 AI 跨会话工作记忆目录(hlmemory 维护)。点开头隐藏,因属工具内部状态非正式交付 |

---

## 二、完整目录结构

```
{项目根目录}/
├── knowledge/                               # 生成文档根(v29 起;原 docs/)
│   ├── doc/                                 # 版本快照区(hlpm 版本目录,详见 §零)
│   │   └── vN/                              # 单版本快照:prd.md / test-cases.md / consistency-matrix.md / handoff-self-check.md / design/ / analysis/
│   ├── tech-design.md                       # 开发段：技术设计(全局,与最新版本对齐)
│   ├── rollback.md                          # 开发段：回滚方案(全局)
│   ├── design/                              # 全局设计规范(与版本无关)
│   │   ├── spec.md                          # 项目设计规范（6a.1 优先查找 #1）
│   │   ├── SKILL.md                         # 项目设计规范（6a.1 优先查找 #2）
│   │   └── *.md                             # 其他设计规范文档（6a.1 兜底 #3）
│   ├── analysis/                            # 分析相关(全局;版本快照在 doc/vN/analysis/)
│   │   └── competitive-analysis.md          # 产品段：竞品分析报告
│   ├── adr/                                 # 架构决策记录(与 hlkb 总库 adr/ 合并)
│   │   └── NNNN-slug.md                     # 开发段：单个 ADR（编号 + 短横线描述）
│   ├── user/                                # 用户文档
│   │   ├── manual.md                        # 开发段：用户操作手册
│   │   └── help.md                          # 开发段：帮助文档
│   ├── qa/                                  # 测试报告（来自主入口规范）
│   │   └── *.md                             # 测试报告、健康评分、审计报告
│   ├── prd.md                               # hlkb 总 PRD(跨版本累计)
│   ├── glossary.md                          # hlkb 术语表
│   ├── api/ db/ state-machines/ enums/ error-codes/ dependencies/ env-vars/ tests/ pitfalls/ retro/   # hlkb 各类总库
│   └── README.md                            # hlkb 知识库总目录
├── CHANGELOG.md                             # 开发段：变更日志（根目录特例）
├── DESIGN.md                                # 项目设计规范（6a.1 跨目录兜底 #4）
└── .hl/memory/                              # 项目记忆（来自 hlmemory 技能,AI 工作记忆,隐藏）
    ├── project.md                           # 项目概述
    ├── techstack.md                         # 技术栈
    ├── architecture.md                      # 架构
    ├── conventions.md                       # 约定
    └── working.md                           # 工作记忆
```

---

## 三、14 项交付物完整路径映射

### 3.1 产品段交付物（5 必出 + 3 条件出，验收标准并入一致性矩阵，适用项进实际 `{version_dir}`）

| # | 交付物 | 路径 | Agent | 步骤 |
|---|--------|------|-------|------|
| 1 | 竞品分析报告 | `{version_dir}/analysis/competitive-analysis.md` | `analyst` 核证，主代理形成建议并写入 | 2b/2c |
| 2 | PRD 文档 | `{version_dir}/prd.md` | `analyst` 生成 → 写入文件 | 4 |
| 3 | 设计稿 | `{version_dir}/design/<相对页面路径>.html` | `designer` | 6b |
| 4 | 设计稿截图 | 与 HTML 同目录的 `screenshot-<文件主名>.png` | `designer` 调 `hlbrowse` | 6b.5 |
| 5 | 测试用例快照 | `{version_dir}/test-cases.md` | `test-engineer`（产品验收用例） | 8 |
| 6 | 非功能需求 | `{version_dir}/non-functional-requirements.md` | `analyst` 生成 → 写入文件 | 10 |
| 7 | 一致性矩阵(含验收标准) | `{version_dir}/consistency-matrix.md` | `analyst` 生成 + `verifier` 验证 | 9.5 |
| 8 | 自检报告 | `{version_dir}/handoff-self-check.md` | `analyst` 生成 → 写入文件 | 11 |

一致性矩阵的机器可读附件是同目录的 `acceptance-plan.json` 和来源摘要 `acceptance-sources.sha256`。自检报告保存本次交接输出的 `plan_sha256`（验收计划）与 `spec_sha256`（PRD、用例和非功能需求正文）。涉及 UI 时，交接同包的 `design/interaction-check.md` 及其引用的实际运行证据。[交接格式](handoff-package.md)

每个适用页面保留一张默认态截图。例：`design/components/cart.html` 对应 `design/components/screenshot-cart.png`，`design/orders.diff.html` 对应 `design/screenshot-orders.diff.png`。旧包将截图集中在 design/ 时，仅在文件主名全包唯一时可以匹配。附加状态图按验收条款补充。

### 3.2 开发段交付物（6 项，hldev 步骤 13 验收）

| # | 文档 | 路径 | 负责 Agent | 步骤 |
|---|------|------|-----------|------|
| 9 | 技术设计文档 | `knowledge/tech-design.md` | `architect` | 3 |
| 10 | 架构决策记录 | `knowledge/adr/NNNN-<slug>.md` | `architect` | 3 |
| 11 | 用户操作手册 | `knowledge/user/manual.md` | `writer` | 13 |
| 12 | 帮助文档 | `knowledge/user/help.md` | `writer` | 13 |
| 13 | 变更日志 | `CHANGELOG.md`（根目录） | `executor` | 13 |
| 14 | 回滚方案 | `knowledge/rollback.md` | `architect` | 13 |

开发段步骤 10 另行更新跨版本的总测试库 `knowledge/tests/{module}.md`，其内容按 hlkb 的总测试库规范验收。

### 3.3 项目记忆（1 项，可选，由 hlmemory 技能管理）

| # | 文档 | 路径 | 负责 Agent |
|---|------|------|-----------|
| 15 | 项目记忆文件 | `.hl/memory/*.md` | 详见 hlmemory 技能 |

---

## 四、关键路径的细化规则

### 4.1 设计稿命名（knowledge/doc/{ver}/design/*.html）

**kebab-case + 单数**，示例（来自 `consistency-rules.md` 矩阵）：

```
knowledge/doc/{ver}/design/order-detail.html
knowledge/doc/{ver}/design/refund.html
knowledge/doc/{ver}/design/cart.html
knowledge/doc/{ver}/design/register.html
knowledge/doc/{ver}/design/login.html
```

**反例（不允许）**：
- `knowledge/doc/{ver}/design/order_detail.html`（下划线）
- `knowledge/doc/{ver}/design/orders.html`（复数）
- `knowledge/doc/{ver}/design/pages/order-detail.html`（路径深度 > 4）

### 4.2 设计规范文件查找优先级（6a.1 步骤）

按以下顺序查找项目设计规范，**找到第一个即用**：

```
1. knowledge/design/spec.md       ← 主规范
2. knowledge/design/SKILL.md      ← 次规范
3. knowledge/design/ 下任意 .md    ← 兜底
4. 项目根目录 DESIGN.md            ← 跨目录兜底
5. hlkb 搜索 hllegacy:ui          ← 已归档在其他知识条目中的前端规范章节，回读适用范围与核验状态
```

如全部未找到，输出"未发现设计规范"报告，继续后续步骤。

### 4.3 ADR 命名（knowledge/adr/NNNN-*.md）

**NNNN = 4 位顺序编号**（如 `0001-use-postgresql.md` / `0002-adopt-microservices.md`）

- 编号递增，不重用
- 删除 ADR 不重排编号（保留历史）
- 取代时新建 ADR 并在旧 ADR 中标注"已被 NNNN 取代"

### 4.4 一致性矩阵版本号（knowledge/doc/{ver}/consistency-matrix.md）

**文件内版本号 ≠ 文件路径**：路径始终是 `consistency-matrix.md`（无版本号），版本号在文件内部标记。

```
PRD v2 / 设计 v2 / 用例 v2  → 一致性矩阵 v2
```

---

## 五、与现有文件的引用关系

| 引用方 | 引用内容 | 引用位置 |
|--------|---------|---------|
| `SKILL.md`（主入口） | "所有产出文件路径详见 `hlpm/path-conventions.md`" | 「通用规则：文件输出路径」 |
| `hlpm/SKILL.md` | 引用产品交接清单 | 「11、12. 自检与打包」 |
| `hlpm/handoff-package.md` | 8 项交付清单 + 交付包总览 | 顶部交付清单 + 交付包总览段 |
| `hlpm/consistency-rules.md` | 设计稿 HTML 路径示例 | 「业务规则覆盖矩阵」 |
| `hldev/SKILL.md` | 6 项补充交付物路径 | 「交付文档清单（开发段补充）」 |

**维护原则**：本规范是**单一可信源**。如其他文件的路径与本规范冲突，**以本规范为准**；其他文件应在评审时同步更新。

---

## 六、变更管理

修改本规范需同步更新：
1. `SKILL.md`（如修改根级规则）
2. `hlpm/SKILL.md`（如修改产品段路径）
3. `hldev/SKILL.md`（如修改开发段路径）
4. `handoff-package.md`（如修改产品段交付清单）
5. `consistency-rules.md`（如修改设计稿命名）

变更记录：
- v8：新建本规范文档，解决"路径散落 3 文件 + 不完整 5 问题"
- v12：新增"零、版本目录管理"章节，每次产品段流程产出 8 项交付物到独立 `docs/vN/` 目录；启动时自动扫描历史未开发版本并询问用户。**所有 3 个引用方文件必须同步更新路径**（含 `{ver}` 占位符）
- v18：产品段交付物由 8 项扩为 9 项(新增"设计稿截图" `screenshot-<page-name>.png`,6b.5 触发)；交付物总数 14 → 15。**所有引用方文件同步更新计数与表格**
- v19：验收标准合并入一致性矩阵 §1"业务规则覆盖矩阵"的"验收方法"列,原独立文档 `acceptance-criteria.md` 取消；产品段交付物由 9 项减为 8 项(5 必出 + 3 条件出),交付物总数 15 → 14。**所有引用方文件同步更新计数与表格**
- v23：设计稿单文件化（单文件 .html + bl-marker 钉点）；接入时 `cp hlpm/templates/bl-marker/bl-marker.{css,js} docs/{ver}/design/`，`docs/{ver}/design/` 目录新增 `bl-marker.css` / `bl-marker.js` 两个资产文件
- v24：PRD 附录 A-G；附录 G 在 `prd.md` 内部，无新增文件，无路径影响
- v25：取消需求规模（轻量/标准/复杂）选择，一律按复杂需求标准；无路径影响
- v29：生成文档根 `docs/` → `knowledge/`,版本快照 `docs/vN/` → `knowledge/doc/vN/`;全局文档 `docs/{design,adr,user,qa}` → `knowledge/` 同名目录,`docs/tech-design.md` / `docs/rollback.md` → `knowledge/` 下;深度规则 ≤ 3 → ≤ 4(快照区多一层);0.2 扫描双读兼容老 `docs/v*/`,新写入只进 `knowledge/`;既有版本按原目录续写(§0.2.1)
- v31：PRD 附录 A-H;附录 H 信息架构在 `prd.md` 内部,无新增文件,无路径影响
- v32：知识库新增 `knowledge/pitfalls/`(踩坑记录,hlbug 步骤 14 强制)与 `knowledge/retro/v{N}.md`(版本复盘,hlpm 12.5 + hldev 15.5);两者归 hlkb 13 类总库,目录树同步
