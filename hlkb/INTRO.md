---
name: hlkb-intro
description: hlkb 技能说明(概览版)。5 分钟读懂"项目知识库"是什么、为什么需要、8 类怎么管。Use when 用户问"知识库是什么"/"hlkb 怎么用"/"为什么需要知识库"。
---

# hlkb 项目知识库(概览)

> **5 分钟读懂项目知识库**
> 完整规范见 [`SKILL.md`](./SKILL.md),日常使用见 [`README.md`](./README.md)

---

## 一句话定义

**hlkb** 是 hlskills 体系中的"**项目知识库**"——仓库里 `.hl/knowledge/` 目录是"工程现实单一可信源",与 `src/` 代码同 commit 维护,8 类文档(接口 / 数据库 / ADR / 状态机 / 枚举 / 错误码 / 依赖 / 环境变量)。

---

## 解决什么问题?

### 没有知识库时,新人 onboarding 的痛苦

```
新人 / AI Agent 进入项目
   │
   ├─ 想找"POST /blacklist/restore/{id} 接口契约"
   │  └─ 去 .java 源码 grep 半天, 找 Controller, 看 @PostMapping / @RequestBody 注解
   │     └─ 没有出参示例, 没有错误码定义, 没有权限约束说明
   │
   ├─ 想找"blacklist 表有几个索引?"
   │  └─ 去 schema.sql grep, 看 CREATE INDEX, 推断哪些查询走哪个索引
   │
   ├─ 想找"v3 为啥选方案 C 而不是方案 B?"
   │  └─ 翻 git log, 找 commit message, 试图逆向推理
   │
   └─ 想了解项目用了哪些技术栈
      └─ 翻 package.json + pom.xml + 各种 README
```

**典型痛点**:
- 接口契约散落在 Controller, 没有单一文档
- 表结构变更看 git diff 看不出来, 索引策略靠猜
- 架构决策没有记录, 后来人不知道为啥这样设计
- 枚举值 / 错误码 / 环境变量全靠 grep
- onboarding 一个新人或 AI Agent 需要 1-2 周熟悉项目

### 有了知识库后

```
新人 / AI Agent 进入项目
   │
   ├─ 打开 .hl/knowledge/api/{module}.md
   │  └─ 所有接口契约一目了然(URL / 入参 / 出参 / 错误码 / 权限)
   │
   ├─ 打开 .hl/knowledge/db/{table}.md + er-diagram.md
   │  └─ 表结构 + 索引策略 + ER 图
   │
   ├─ 打开 .hl/knowledge/adr/{NNNN}-{slug}.md
   │  └─ 所有架构决策 + 备选方案 + 选中理由
   │
   ├─ 打开 .hl/knowledge/state-machines/{entity}.md
   │  └─ 实体状态机流转图
   │
   ├─ 打开 .hl/knowledge/enums/{enum}.md + error-codes/
   │  └─ 全局枚举值 + 错误码字典
   │
   └─ 打开 .hl/knowledge/{dependencies,env-vars}/
      └─ 技术栈 + 环境变量
```

**核心改变**:
- ✅ 新人/AI onboarding **从 1-2 周缩到 1 小时**
- ✅ 接口契约 / 表结构 / 决策有单一可信源
- ✅ 代码改了, 知识库必同步(同 commit 触发)
- ✅ AI Agent 可独立读知识库做决策,不靠记忆

---

## 核心机制(3 大支柱)

### 1. 仓库即文档(同步触发)

代码改了 → 知识库必同步,**同 commit 提交**:
- 新增接口 → `api/{module}.md` 加条目
- 表结构变 → `db/{table}.md` + `er-diagram.md` 更新
- 架构决策 → `adr/{NNNN}-{slug}.md` 新建
- 状态机变化 → `state-machines/{entity}.md` 更新

**触发技能矩阵**:

| 技能 | 触发 hlkb | 更新 |
|---|---|---|
| `hlpm` 步骤 11 自检 | 版本交付完成 | `docs/master-prd.md` / `master-test-cases.md` |
| `hldev` 步骤 4.5 走查 | 代码实现后 | `api/` / `db/` |
| `hldb` 数据库迁移 | 任何 DDL | `db/` |
| `hlapi` 接口设计 | 任何契约 | `api/` |
| `hladr` 架构决策 | 任何决策 | `adr/` |
| `hlbug` Bug 修复 | 涉及字段/接口 | 同步知识库 |
| `hllegacy` 旧项目 | 第 12 步沉淀 | 初始化整套 |

### 2. 8 类知识库(覆盖工程现实)

| 类别 | 路径 | 维护角色 | 何时更新 |
|---|---|---|---|
| API 接口 | `api/{module}.md` | 后端 | 新增/修改/删除接口 |
| 数据库 | `db/{table}.md` + `er-diagram.md` | 后端 + DBA | DDL 变更 |
| ADR | `adr/{NNNN}-{slug}.md` | 架构师 | 重大决策 |
| 状态机 | `state-machines/{entity}.md` | 架构师 + 后端 | 状态机变化 |
| 枚举 | `enums/{enum}.md` | 后端 | 新增 ENUM 字段 |
| 错误码 | `error-codes/README.md` | 后端 | 新增错误码 |
| 依赖 | `dependencies/README.md` | 前端 + 后端 | 升级 |
| 环境变量 | `env-vars/README.md` | 后端 + 运维 | 新增/修改 |

### 3. 跨版本不跟版本走

```
docs/v{N}/                  ← 版本基线(快照), 不会变
.hl/knowledge/              ← 跨版本共用, 持续维护
CLAUDE.md                   ← 项目元信息, 持续维护
docs/master-prd.md         ← 跨版本汇总, 每次版本交付后追加
```

---

## 适用 vs 不适用

### ✅ 适用项目

- 长期维护的项目(> 6 个月)
- 多人协作(> 2 人)或 AI Agent 协作
- 涉及多模块 / 多接口 / 多数据库表的中型以上项目
- 需要合规审计 / 决策追溯

### ❌ 不适用项目

- 临时 demo / PoC / 一次性脚本
- 个人极简小项目(只有 1 个文件 / 1 个接口)
- 项目初始阶段(< 1 周就完成)

---

## 3 个关键设计决策

### 决策 1: 知识库放 `.hl/knowledge/`,不进 `docs/`

- **理由**: 知识库跨版本共用, 不是某版本的快照
- 代价**: 不在版本基线检查范围内(consistency-rules.md 不跟踪)

### 决策 2: 触发式同步, 而非"完整文档"

- **理由**: 没人会维护完整 1000 页文档, 只有触发式的同步才能保持鲜活
- 代价**: 需要 hlskills 各技能配套升级(本任务核心)

### 决策 3: 同 commit, 不同 PR

- **理由**: 文档/代码分离提交 = 文档过期
- 代价**: 单个 commit 内容更杂(但原子性强)

---

## 关键数字

| 指标 | 值 |
|---|---|
| 知识库类别数 | 8(完整) / < 项目实际数量(可少建) |
| ADR 编号格式 | 4 位顺序号(0001-9999, 永不重置) |
| 同步触发点 | hlpm 1 处 / hldev 2 处 / hldb 强约束 / hlapi 强约束 / hladr 直接写 |
| 单 commit 包含 | 代码 + 知识库条目 + ADR(如重大) + 测试 |
| onboarding 时间 | 1-2 周 → **1 小时** |

---

## 它和谁配套

| 技能 | 关系 |
|---|---|
| `hlpm` | 步骤 11 触发 master 文档追加 |
| `hldev` | 步骤 4.5 + 12 触发 API/DB 同步 + 完整性自检 |
| `hldb` | 任何 DDL 强约束同步 db/ |
| `hlapi` | 任何接口契约强约束同步 api/ |
| `hladr` | 输出直接写到 adr/ |
| `hlbug` | 涉及字段/接口变化时同步 |
| `hllegacy` | 第 12 步初始化整套知识库 |
| `hlprd` | 文档合成时引用知识库 |

**核心配套**: 项目知识库 = 8 个模板 + 同步触发规则 + 自检清单。

---

## 下一步

- 想知道"目录结构长啥样" → 看 [`structure.md`](./structure.md)
- 想"具体怎么用" → 看 [`README.md`](./README.md)
- 想"看真实 ehr 项目知识库" → 看 `/Users/zhangdanyang/ehr/.hl/knowledge/`

---

## 维护者

本技能是 `hlskills` 体系的一部分,版本 v1(2026-07-01)。
反馈 / 改进建议 → 主仓库开 issue。