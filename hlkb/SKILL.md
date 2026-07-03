---
name: hlkb
description: 项目知识库(9 类:接口/数据库/ADR/状态机/枚举/错误码/依赖/环境变量/测试覆盖)。项目内 `knowledge/` 目录是"工程现实单一可信源",与 src/ 代码同 commit 维护。AI 助手/新开发者进入项目看文档就能 5 分钟理解项目,不用从代码反推。Use when 需要新建/更新项目知识库条目,或调用 hlskills 其他技能时需要检查"该次变更是否需要同步知识库"。
---

# hlkb · 项目知识库

> **项目级"工程现实单一可信源"**。仓库即文档。代码改了,知识库必同步。

---

## 🚨 硬性纪律(先读再启动)

> **本节是 hlkb 的最高约束,优先级高于下面所有维护规则**

> ⚠️ **能力边界声明**:本节所说的"阻塞""必须同步""不存在某状态"等是**文档纪律**,不是 Claude Code runtime 强制。hlkb 没有 hook / 状态机 / 编排器——所谓"同步触发""发布前阻塞"全靠加载本技能的 Agent **自觉遵守 + 用户手动把关**。想要真实的"缺失即阻断",需自行在 `hlhooks` 里配置对应 hook 并实测。

### 三条铁律

1. **仓库即文档**: `knowledge/` 与 `src/` 同 commit 维护。代码变了知识库必须同步,反之亦然。**不分离提交**。
2. **同步触发**: 调用 `hlskills` 任意技能(`hlpm` / `hldev` / `hldb` / `hlapi` / `hlbug` / `hladr` / `hllegacy` / `hlrefactor` 等),如果涉及"代码/接口/数据/配置/决策"变更, **应同步 `knowledge/` 对应条目**。
3. **同步失败 = 应阻塞**: 自检不通过应视为阻塞交付/发布的信号,由 Agent/用户把关补齐——目标是不留"代码写完但知识库没更新"的状态(靠自觉,非机制强制)。

### 与版本管理的关系

| 文档类型 | 跟版本走? | 存放位置 | 说明 |
|---|---|---|---|
| PRD / 设计稿 / 测试用例(单版本) | ✅ 是 | `docs/v{N}/` | 版本基线,固定不变 |
| **知识库(api/db/adr/...)** | **❌ 否(跨版本)** | **`knowledge/`** | **持续维护的工程资产,跨版本共用** |
| 总 PRD / 总测试用例(跨版本汇总) | ❌ 否 | `docs/master-prd.md` / `docs/master-test-cases.md` | 每次版本交付后追加章节 |
| CLAUDE.md | ❌ 否 | 项目根 | 项目元信息,持续维护 |
| 评审记录 / 自检报告 | ✅ 是 | `docs/v{N}/` | 单版本产物 |

> 知识库**不跟版本走**——v2 加的接口在 v3 仍存在,接口知识库条目是持续维护的,不是 v2 版本快照。

---

## 何时使用 hlkb

### 主动调用场景

1. **新建项目** → 初始化 `knowledge/` 整套(9 类目录)
2. **跑 hllegacy 旧项目分析** → 把现状反推沉淀到知识库
3. **查接口/数据库/枚举的定义** → 已有知识库,直接 Read
4. **生成 CLAUDE.md / master-prd.md** → 汇总知识库

### 被动触发场景(其他技能约定调用 hlkb — 靠 Agent 自觉,非自动 hook)

> ⚠️ 下表为 hlkb **建议**的触发点。其中 `hlpm`/`hllegacy` 当前**未在其 SKILL.md 内对接**本技能(待后续补齐),实际触发由本项目 Agent/用户手动把关;`hldev`/`hldb`/`hlapi`/`hladr` 已在其各自 SKILL.md 内引用 hlkb。

| 技能 | 何时触发 hlkb(建议) | 更新什么 | 对方已对接? |
|---|---|---|---|
| `hlpm` 版本交付自检 | 版本交付完成 | `docs/master-prd.md` / `docs/master-test-cases.md` 追加本版本章节 | ❌ 待对接 |
| `hldev` 步骤 4.5 PRD 走查 | 代码实现后 commit | `knowledge/api/` / `knowledge/db/` 追加对应条目 | ✅ |
| `hldev` 步骤 12.7 发布前自检 | 发布前 | 知识库完整性自检(9 类齐全, 缺则应补齐后再发布) | ✅ |
| `hldb` 数据库迁移 | 任何 DDL | `knowledge/db/{table}.md` + ER 图 | ✅ |
| `hlapi` 接口设计/新增 | 任何接口契约 | `knowledge/api/{module}.md` | ✅ |
| `hlbug` Bug 修复 | 涉及字段/接口/配置变化 | 同步知识库 | ✅ |
| `hladr` 架构决策 | 任何决策 | `knowledge/adr/{NNNN}-{slug}.md` | ✅ |
| `hllegacy` 旧项目分析 | 知识沉淀阶段 | 初始化整套知识库 | ❌ 待对接 |

---

## 目录结构(9 类知识库)

```
knowledge/
├── README.md                       # 知识库总目录(进入后第一眼看到的索引)
├── api/                            # 类别 1: HTTP 接口
│   ├── README.md                   # 接口总览
│   └── {module}.md                 # 单个模块的接口
├── db/                             # 类别 2: 数据库表 + ER 图
│   ├── README.md                   # 数据库总览
│   ├── {table}.md                  # 单个表
│   └── er-diagram.md               # ER 关系图(全局跨表关系,可嵌入 mermaid)
├── adr/                            # 类别 3: 架构决策记录
│   ├── README.md                   # ADR 索引
│   └── {NNNN}-{slug}.md            # 单个 ADR(Michael Nygard 格式)
├── state-machines/                 # 类别 4: 实体状态机
│   ├── README.md
│   └── {entity}.md
├── enums/                          # 类别 5: 枚举字典
│   ├── README.md
│   └── {enum}.md
├── error-codes/                    # 类别 6: 错误码字典
│   └── README.md
├── dependencies/                   # 类别 7: 第三方依赖
│   └── README.md
├── env-vars/                       # 类别 8: 环境变量
│   └── README.md
└── tests/                          # 类别 9: 总测试库(验收用例+代码层用例)
    ├── README.md                   # 测试覆盖总览
    └── {module}.md                 # 单个模块的代码层测试点 ↔ AC ↔ 测试代码路径
```

> 9 类不一定都用,新项目至少要建:`README.md` + 实际有内容的类别(无内容的类别不建目录,避免空文件夹)。

---

## 9 类知识库模板

模板在 `templates/` 目录,复制后填充:

| 类别 | 模板文件 | 用途 |
|---|---|---|
| API 接口 | `templates/api.md` | URL / Method / 入参 / 出参 / 错误码 / 权限 / 调用方 |
| 数据库表 | `templates/db-table.md` | 字段 / 类型 / 索引 / 外键 / 索引策略 |
| ER 关系图 | `templates/er-diagram.md` | 全局跨表关系 / mermaid 图 / 关键约束 |
| 架构决策 | `templates/adr.md` | 上下文 / 决策 / 后果 / 备选方案 |
| 状态机 | `templates/state-machine.md` | 状态列表 / 转移图 / 转移条件 |
| 枚举字典 | `templates/enum.md` | 枚举值 / 含义 / 来源 / 写入方 |
| 错误码 | `templates/error-code.md` | 错误码 / HTTP / 含义 / 触发场景 |
| 第三方依赖 | `templates/dependency.md` | 库名 / 版本 / 许可证 / 升级计划 |
| 环境变量 | `templates/env-var.md` | 名称 / 含义 / 默认值 / 环境差异 |
| 总测试库 | `templates/code-tests.md` | 验收用例(黑盒)/ 代码层用例(白盒)/ 交叉追溯 / 测试代码路径 |

详见 `templates/` 目录各文件。

---

## 维护规则

### 谁负责

| 角色 | 维护内容 |
|---|---|
| 后端开发(`executor`) | `api/`, `db/`, `enums/`, `error-codes/`, `dependencies/`, `env-vars/` |
| 架构师(`architect`) | `adr/`, `state-machines/` |
| 产品经理(`analyst`) | 跨版本 master 文档(`docs/master-prd.md` / `docs/master-test-cases.md`) |
| AI 助手(项目) | `CLAUDE.md` (项目根) |

### 何时更新

| 触发场景 | 同步哪些文件 |
|---|---|
| 新增/修改/删除 HTTP 接口 | `api/{module}.md` |
| 新增/修改/删除数据库表 | `db/{table}.md` + `db/er-diagram.md` |
| 新增/修改字段 | `db/{table}.md`(同表) + `db/er-diagram.md`(如外键变化) |
| 任何架构决策 | `adr/{NNNN}-{slug}.md` |
| 状态机变化 | `state-machines/{entity}.md` |
| 新增枚举/错误码/依赖/环境变量 | 对应类目文件 |
| 版本交付完成 | `docs/master-prd.md` + `docs/master-test-cases.md` 追加本版本章节 |
| 项目元信息变化(技术栈/架构) | `CLAUDE.md` |

### 同步时机(铁律)

- **同 commit**: 代码/接口/数据变更 与 知识库条目 **必须同一次 commit 提交**。不允许"代码已 commit,知识库下次再说"。
- **同 PR**: 如果用 PR 流程,知识库条目与代码变更**同 PR** 提交,不分离。
- **同 review**: PR review 阶段必须同时检查代码与知识库条目。

### 自检规则(发布前)

`hldev` 步骤 12.7 发布前自检,逐项检查:

- [ ] `api/` 目录覆盖所有 v{N} 文档里引用的接口
- [ ] `db/` 目录覆盖所有数据库表
- [ ] `adr/` 目录含本版本所有重大决策(如本版本新增了 1 个 BL-12 方案 C, 必有 0001-bl12-restore-strategy.md)
- [ ] `state-machines/` 覆盖所有跨功能状态机
- [ ] `enums/` 覆盖所有 `ENUM` 字段
- [ ] `error-codes/` 覆盖所有自定义错误码
- [ ] `dependencies/` 与 `pom.xml` / `package.json` 一致
- [ ] `env-vars/` 覆盖所有 `.env` / `application-{profile}.yml` 变量
- [ ] `tests/` 覆盖本版本所有模块(验收用例 + 代码层用例,每个新增/修改的 Service/API 有测试点 + 对应 AC + 测试代码路径,交叉追溯无 ⚠️ 待补)
- [ ] `docs/master-prd.md` 包含当前最新版本章节
- [ ] `docs/master-test-cases.md` 包含当前最新版本章节
- [ ] `CLAUDE.md` 反映最新项目元信息

**任一缺失 → 应补齐后再发布**(靠 Agent/用户把关,非机制强制阻断)。

---

## 引用规范

### 其他文档如何引用知识库

| 引用场景 | 格式 |
|---|---|
| PRD 引用接口 | `见 knowledge/api/blacklist.md §新增接口` |
| ADR 引用决策 | `详见 knowledge/adr/0001-bl12-restore-strategy.md` |
| 状态机引用 | `见 knowledge/state-machines/blacklist.md` |
| master 文档引用 | `详见 docs/v{N}/prd.md §{N}` |

### 知识库条目如何引用代码

- 引用类文件: `src/main/java/.../BlacklistController.java#L42`
- 引用接口: `/blacklist/restore/{id}`(接口路径)
- 引用 SQL 迁移: `migrations/v3_001_restore_field.sql`

### 知识库条目如何引用版本

- 引入版本: `**v3 引入**`(标注首次出现的版本)
- 废弃版本: `**v3 起废弃**(v2 仍使用)`
- 跨版本: 写明"v2 已实现, v3 扩展(新增 5 字段)"

---

## 项目约束文件(CLAUDE.md / AGENTS.md)

> 约束文件是 hlkb 同步铁律的**常驻上下文版**——hlkb SKILL.md 按需加载(调 Skill hlkb 才进场),约束文件每次会话常驻(AI 工具启动即读)。ehr 实证:纯声明性铁律会漂移,需"完成前自检"把声明变核对动作。

- **模板**:`templates/claude-md.template.md`(与 9 类知识库模板并列)
- **内容**:极简 4 段——项目定位(一句话) + AI 助手必读(指针) + 知识库同步铁律 + 🚨 完成前自检(5 项检查项)。不内嵌角色表/字段表/技术栈明细(那些在 `knowledge/` 与 `.hl/memory/`),避免成为新漂移源。
- **初始化/补全**:由各子技能 step 0 检测并按模板创建(不存在)或补"完成前自检"段(已存在缺该段)。详见各子技能 step 0。
- **IDE 适配**:Claude Code→`CLAUDE.md` / Codex→`AGENTS.md` / Cursor→`.cursor/rules/*.mdc`;检测不出或多 IDE → 都写。
- **校验锚点**:已存在文件用 `## 🚨 完成前自检` 段标题判断是否合规,缺则追加该段(不重写其他内容)。

---

## 与 hlskills 其他技能的关系

| 技能 | 关系 |
|---|---|
| `hlpm` | 版本交付自检建议追加 `docs/master-prd.md` / `docs/master-test-cases.md`(对方未对接,待补) |
| `hldev` | 步骤 4.5 走查同步 `api/` `db/`; 步骤 12.7 自检知识库完整性 |
| `hldb` | 任何 DDL 应同步 `db/` |
| `hlapi` | 任何接口契约同步 `api/` |
| `hlbug` | 涉及字段/接口/配置变化同步知识库 |
| `hladr` | 决策直接写入 `knowledge/adr/`,不独立存(可视为 hladr 与 hlkb 合并) |
| `hllegacy` | 旧项目分析建议初始化整套知识库(对方未对接,待补) |
| `hlrefactor` | 重构涉及字段/接口 → 同步知识库 |
| `hlrelease` | 发布前最后一道自检(由 hldev 步骤 12.7 触发) |

---

## 启动检查清单(第 0 阶段必读)

启动 hlkb 之前,确认以下 4 件事:
- [ ] 确认项目根存在 `.hl/` 目录(已有 memory 在 `.hl/memory/`)
- [ ] 确认本次是"新建知识库"还是"更新现有知识库"
- [ ] 确认涉及哪几个类别(9 类中的几个)
- [ ] 确认 git 已配置(知识库与代码同 commit)

---

## 知识库条目清单(本技能不交付,只触发同步)

> 下表与"9 类知识库"一一对应(总目录 + 9 类内容类别 = 10 行)。依赖与环境变量分开列。

| 编号 | 文档 | 路径 | 触发技能 | 状态 |
|---|---|---|---|---|
| 0 | 知识库总目录 | `knowledge/README.md` | hlkb / hllegacy | ✅ 项目元信息(初始化) |
| 1 | 接口文档 | `knowledge/api/*.md` | hlapi / hldev | ✅ 接口契约(每次新增/修改) |
| 2 | 数据库文档 | `knowledge/db/*.md` | hldb / hldev | ✅ DDL(每次迁移) |
| 3 | ADR | `knowledge/adr/*.md` | hladr / hlpm | ✅ 决策(每次重大决策) |
| 4 | 状态机 | `knowledge/state-machines/*.md` | hlpm / hldev | ✅ 状态机变化 |
| 5 | 枚举字典 | `knowledge/enums/*.md` | hldev | ✅ 新增 ENUM 字段 |
| 6 | 错误码 | `knowledge/error-codes/*.md` | hldev | ✅ 新增错误码 |
| 7 | 依赖 | `knowledge/dependencies/*.md` | hldev | ✅ 升级/新增 |
| 8 | 环境变量 | `knowledge/env-vars/*.md` | hldev | ✅ 新增/修改 |
| 9 | 总测试库 | `knowledge/tests/*.md` | hlpm(验收用例沉淀)+ hldev(代码层用例) | ✅ hlpm 步骤8 产出 + hldev 步骤10 沉淀 |

---

## 通用纪律:完成前验证

**任何知识库条目写完前,必须执行验证规则:**
- 识别能证明该条目完整的验证命令, 完整运行
- 读取完整输出并检查退出码, 确认通过后方可声明完成
- **绝对禁止**:"应该通过了"、"看起来正确"、"可能没问题"
- **铁律**: 证据先于断言, 无一例外

### 受阻停止纪律

- 任何步骤遇到阻塞, **立即停止**, 不得猜测或强行绕过
- 向 `analyst` 报告阻塞情况
- `analyst` 无法解决时, 立即向用户提问
- 3 次修复/驳回尝试失败 = 质疑方案, 升级到用户决策
- **单项条目最多驳回 3 轮**, 超出升级用户决策

---

## 不在本技能范围

- ❌ 任何源代码的修改 — 用 `hldev`
- ❌ 数据库迁移 SQL 编写 — 用 `hldb`
- ❌ 接口契约设计 — 用 `hlapi`
- ❌ 架构决策制定 — 用 `hladr`(本技能只负责存储)
- ❌ 项目初始化(0 → 1) — 用 `hl-flow` 或 `hlchain`
- ❌ 跨会话的"产品 AI + 开发 AI"自动协作 — 本期不实现编排器

---

## 维护者

本技能是 `hlskills` 体系的一部分,版本 v1 (2026-07-01)。
反馈 / 改进建议 → 主仓库开 issue。