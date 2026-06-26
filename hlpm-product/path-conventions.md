---
name: hlpm-product-path-conventions
description: 交付文档目录规范中央文档（版本管理）。定义 14 项交付物的完整路径、版本目录结构、命名约定、深度限制、特殊情况处理。**v12 关键变更**: 每次产品段流程产出 8 项交付物到独立版本目录 `docs/vN/`,启动时自动扫描历史未开发版本。被 SKILL.md / hlpm-product / hlpm-dev 三个文件共同引用。Use when 用户询问"输出到哪"、"目录怎么组织"、"文件命名规则"。
---

# 交付文档完整目录规范

> 属于 `hlskills` 技能系统的**中央规范文档**。
> 被以下 3 个文件共同引用：
> - 主入口 `SKILL.md`（通用规则：文件输出路径）
> - `hlpm-product/SKILL.md`（产品段 8 项交付物）
> - `hlpm-dev/SKILL.md`（开发段 6 项补充交付物）
>
> **目的**：解决"路径规范散落 3 个文件 + 不完整（5 个问题）"的现状，作为单一可信源（single source of truth）。

---

## 零、版本目录管理(核心）

### 0.1 核心规则

> **每次产品段流程产出 8 项交付物到独立版本目录** `docs/vN/`，目录名直接显示版本号

- **版本号格式**：`vN`（N 为 1, 2, 3 ... 整数递增，从 v1 开始）
- **目录位置**：`docs/v1/` `docs/v2/` `docs/v3/` ...
- **目录内容**：8 项产品交付物**全部**放入版本目录
- **目录间关系**：版本目录之间**完全独立**，不共享文件，不软链

### 0.2 启动时版本扫描（阻塞点）

启动产品段时，**`analyst` 必须先扫描历史版本**：

```bash
# 扫描命令
ls -d docs/v*/ 2>/dev/null | sort -V
```

**扫描结果 3 种情况**：

#### 情况 A: 没有历史版本
- 直接创建 `docs/v1/`，所有 8 项交付物放 `docs/v1/`
- 不询问用户

#### 情况 B: 有历史版本，全部"已开发"
- 历史版本目录中存在 `docs/vN/.dev-completed` 标记文件
- 视为"该版本已交付且开发段已接手/发布"
- **直接创建新版本**（如 `docs/v3/`），不询问用户
- 命名规则：上一个版本号 + 1

#### 情况 C: 有"未开发"的历史版本（阻塞点）
- 历史版本目录中**没有** `docs/vN/.dev-completed` 标记文件
- 即"产品已交付但开发段未接手"
- **必须用 `AskUserQuestion` 询问用户**：

  ```
  问题：检测到以下未开发版本，请选择处理方式：
    - v1（[2026-06-20] PRD 8 条业务规则 / 3 页面 / 1 一致性矩阵未通过）
    - v2（[2026-06-24] PRD 3 条业务规则 / 1 页面 / 1 一致性矩阵未通过）

  选项:
    A. 在 [v1] 基础上修改（保留 v1 已有内容，叠加新需求，版本号仍为 v1）
    B. 在 [v2] 基础上修改
    C. 新建版本（v3 / v4...，与历史版本完全独立）
  ```

- 用户选择后：
  - 选 A/B → 当前版本号仍为选中的旧版本，**所有交付物更新到该旧版本目录**
  - 选 C → 新建版本目录，独立的 8 项交付物

### 0.3 标记文件约定

| 文件 | 位置 | 含义 | 何时创建 |
|------|------|------|---------|
| `.dev-completed` | `docs/vN/.dev-completed` | 该版本已交付 + 开发段已接手/发布 | `hlpm-dev` 步骤 13 "交付验证"通过时由 `verifier` 创建 |
| `.dev-rejected` | `docs/vN/.dev-rejected` | 该版本已被开发段拒收 | `hlpm-dev` 步骤 0 拒收时由 `executor` 创建（"未开发"状态保留,产品段需补齐后重发） |
| `.product-archived` | `docs/vN/.product-archived` | 产品段已主动归档该版本（不再开发） | 产品经理 `analyst` 主动创建 |

**重要**：标记文件是空文件（0 字节），仅作存在性检查。

### 0.4 完整目录结构（含版本目录）

```
{项目根目录}/
├── docs/
│   ├── v1/                                 # 版本 1
│   │   ├── prd.md
│   │   ├── test-cases.md
│   │   ├── acceptance-criteria.md
│   │   ├── non-functional-requirements.md
│   │   ├── consistency-matrix.md
│   │   ├── handoff-self-check.md
│   │   ├── design/
│   │   │   └── *.html
│   │   ├── analysis/
│   │   │   └── competitive-analysis.md
│   │   ├── .dev-completed                  # 标记文件(空文件）
│   │   ├── .dev-rejected                   # 标记文件(空文件）
│   │   └── .product-archived               # 标记文件(空文件）
│   ├── v2/                                 # 版本 2（独立）
│   │   └── ... （同 v1 结构）
│   ├── design/                             # 全局设计规范（与版本无关）
│   │   ├── spec.md
│   │   ├── SKILL.md
│   │   └── *.md
│   ├── adr/                                # 全局 ADR（与版本无关）
│   │   └── NNNN-slug.md
│   ├── user/                               # 全局用户文档
│   │   ├── manual.md
│   │   └── help.md
│   ├── tech-design.md                      # 全局技术设计（开发段输出,与最新版本对齐）
│   ├── rollback.md                         # 全局回滚方案
│   └── qa/                                 # 全局测试报告
│       └── *.md
├── CHANGELOG.md                            # 根目录（业界惯例）
├── DESIGN.md                               # 根目录（跨目录兜底）
└── .hl/memory/                             # 项目记忆
    ├── project.md
    └── ...
```

### 0.5 与"文档深度 ≤ 3 层"规则的关系

**版本目录不增加深度**：

- 旧路径：`docs/prd.md`（深度 2）
- 新路径：`docs/v1/prd.md`（深度仍为 2，因为 v1 是单层目录名）
- 设计稿：`docs/v1/design/order-detail.html`（深度 3，**符合 ≤ 3 限制**）

如果未来版本目录嵌套（如 `docs/v1/release-a/`），需要重新审视深度限制。

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
| 路径深度 | **≤ 3 层**（如 `docs/design/order-detail.html`） | 无 |
| 文件后缀 | `.md`（文档） / `.html`（设计稿） | 无 |
| 目录名 | **小写 + 复数**（如 `docs/design/` / `docs/adr/`） | 无 |

### 1.3 特殊根目录文件（不在 `docs/` 下）

| 文件 | 路径 | 原因 |
|------|------|------|
| `CHANGELOG.md` | 项目根目录 | 业界惯例（GitHub / npm / Cargo 等都放根目录） |
| `DESIGN.md` | 项目根目录 | 6a.1 步骤的跨目录兜底（项目级而非文档级） |
| `.hl/memory/` | 项目根目录 | hlskills 体系约定的项目记忆目录 |

---

## 二、完整目录结构

```
{项目根目录}/
├── docs/                                    # 文档根目录
│   ├── prd.md                               # 产品段：PRD
│   ├── acceptance-criteria.md               # 产品段：验收标准
│   ├── non-functional-requirements.md       # 产品段：非功能需求
│   ├── test-cases.md                        # 产品段：测试用例
│   ├── consistency-matrix.md                # 产品段：一致性矩阵
│   ├── handoff-self-check.md                # 产品段：自检报告
│   ├── tech-design.md                       # 开发段：技术设计
│   ├── rollback.md                          # 开发段：回滚方案
│   ├── design/                              # 设计相关
│   │   ├── spec.md                          # 项目设计规范（6a.1 优先查找 #1）
│   │   ├── SKILL.md                         # 项目设计规范（6a.1 优先查找 #2）
│   │   └── *.html                           # 设计稿（kebab-case，单数）
│   ├── analysis/                            # 分析相关
│   │   └── competitive-analysis.md          # 产品段：竞品分析报告
│   ├── adr/                                 # 架构决策记录
│   │   └── NNNN-slug.md                     # 开发段：单个 ADR（编号 + 短横线描述）
│   ├── user/                                # 用户文档
│   │   ├── manual.md                        # 开发段：用户操作手册
│   │   └── help.md                          # 开发段：帮助文档
│   └── qa/                                  # 测试报告（来自主入口规范）
│       └── *.md                             # 测试报告、健康评分、审计报告
├── CHANGELOG.md                             # 开发段：变更日志（根目录特例）
├── DESIGN.md                                # 项目设计规范（6a.1 跨目录兜底 #4）
└── .hl/memory/                              # 项目记忆（来自 hlmemory 技能）
    ├── project.md                           # 项目概述
    ├── techstack.md                         # 技术栈
    ├── architecture.md                      # 架构
    ├── conventions.md                       # 约定
    └── working.md                           # 工作记忆
```

---

## 三、14 项交付物完整路径映射

### 3.1 产品段交付物（8 项，v12 起全部进版本目录 `docs/vN/`）

| # | 交付物 | 路径 | Agent | 步骤 |
|---|--------|------|-------|------|
| 1 | 竞品分析报告 | `docs/{ver}/analysis/competitive-analysis.md` | `analyst` 生成 → 写入文件 | 2b/2c |
| 2 | PRD 文档 | `docs/{ver}/prd.md` | `analyst` 生成 → 写入文件 | 4 |
| 3 | 设计稿 | `docs/{ver}/design/<page-name>.html` | `designer` | 6b |
| 4 | 测试用例 | `docs/{ver}/test-cases.md` | `test-engineer` | 8 |
| 5 | 验收标准 | `docs/{ver}/acceptance-criteria.md` | `analyst` 生成 → 写入文件 | 10 |
| 6 | 非功能需求 | `docs/{ver}/non-functional-requirements.md` | `analyst` 生成 → 写入文件 | 10 |
| 7 | 一致性矩阵 | `docs/{ver}/consistency-matrix.md` | `analyst` 生成 + `verifier` 验证 | 9.5 |
| 8 | 自检报告 | `docs/{ver}/handoff-self-check.md` | `analyst` 生成 → 写入文件 | 11 |

> **`{ver}` = 当前版本号**（如 `v1` / `v2` / `v3`），由 0.5 步骤的版本扫描决定
> 例：当前产品段流程在 v2，则 PRD 写到 `docs/v2/prd.md`

### 3.2 开发段交付物（6 项，hlpm-dev 步骤 13 输出）

| # | 文档 | 路径 | 负责 Agent | 步骤 |
|---|------|------|-----------|------|
| 9 | 技术设计文档 | `docs/tech-design.md` | `architect` | 3 |
| 10 | 架构决策记录 | `docs/adr/NNNN-<slug>.md` | `architect` | 3 |
| 11 | 用户操作手册 | `docs/user/manual.md` | `writer` | 13 |
| 12 | 帮助文档 | `docs/user/help.md` | `writer` | 13 |
| 13 | 变更日志 | `CHANGELOG.md`（根目录） | `planner` | 13 |
| 14 | 回滚方案 | `docs/rollback.md` | `architect` | 13 |

### 3.3 项目记忆（1 项，可选，由 hlmemory 技能管理）

| # | 文档 | 路径 | 负责 Agent |
|---|------|------|-----------|
| 15 | 项目记忆文件 | `.hl/memory/*.md` | 详见 hlmemory 技能 |

---

## 四、关键路径的细化规则

### 4.1 设计稿命名（docs/design/*.html）

**kebab-case + 单数**，示例（来自 `consistency-rules.md` 矩阵）：

```
docs/design/order-detail.html
docs/design/refund.html
docs/design/cart.html
docs/design/register.html
docs/design/login.html
```

**反例（不允许）**：
- `docs/design/order_detail.html`（下划线）
- `docs/design/orders.html`（复数）
- `docs/design/pages/order-detail.html`（路径深度 > 3）

### 4.2 设计规范文件查找优先级（6a.1 步骤）

按以下顺序查找项目设计规范，**找到第一个即用**：

```
1. docs/design/spec.md       ← 主规范
2. docs/design/SKILL.md      ← 次规范
3. docs/design/ 下任意 .md    ← 兜底
4. 项目根目录 DESIGN.md       ← 跨目录兜底
```

如全部未找到，输出"未发现设计规范"报告，继续后续步骤。

### 4.3 ADR 命名（docs/adr/NNNN-*.md）

**NNNN = 4 位顺序编号**（如 `0001-use-postgresql.md` / `0002-adopt-microservices.md`）

- 编号递增，不重用
- 删除 ADR 不重排编号（保留历史）
- 取代时新建 ADR 并在旧 ADR 中标注"已被 NNNN 取代"

### 4.4 一致性矩阵版本号（docs/consistency-matrix.md）

**文件内版本号 ≠ 文件路径**：路径始终是 `consistency-matrix.md`（无版本号），版本号在文件内部标记。

```
PRD v2 / 设计 v2 / 用例 v2  → 一致性矩阵 v2
```

---

## 五、与现有文件的引用关系

| 引用方 | 引用内容 | 引用位置 |
|--------|---------|---------|
| `SKILL.md`（主入口） | "所有产出文件路径详见 `hlpm-product/path-conventions.md`" | 第 112-127 行"通用规则：文件输出路径" |
| `hlpm-product/SKILL.md` | 8 项交付物路径表 | 第 277-285 行"交付文档清单" |
| `hlpm-product/handoff-package.md` | 7 项交付清单 + 交付包总览 | 第 9-16 行 + 第 117-118 行 |
| `hlpm-product/consistency-rules.md` | 设计稿 HTML 路径示例 | 第 48-67 行 |
| `hlpm-dev/SKILL.md` | 6 项补充交付物路径 | 第 204-211 行 |

**维护原则**：本规范是**单一可信源**。如其他文件的路径与本规范冲突，**以本规范为准**；其他文件应在评审时同步更新。

---

## 六、变更管理

修改本规范需同步更新：
1. `SKILL.md`（如修改根级规则）
2. `hlpm-product/SKILL.md`（如修改产品段路径）
3. `hlpm-dev/SKILL.md`（如修改开发段路径）
4. `handoff-package.md`（如修改产品段交付清单）
5. `consistency-rules.md`（如修改设计稿命名）

变更记录：
- v8：新建本规范文档，解决"路径散落 3 文件 + 不完整 5 问题"
- v12：新增"零、版本目录管理"章节，每次产品段流程产出 8 项交付物到独立 `docs/vN/` 目录；启动时自动扫描历史未开发版本并询问用户。**所有 3 个引用方文件必须同步更新路径**（含 `{ver}` 占位符）
