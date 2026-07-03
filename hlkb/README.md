---
name: hlkb-readme
description: hlkb 技能使用说明(README)。面向"第一次在本项目跑 hlkb"的人。聚焦"11 类知识库怎么填、怎么同步、怎么查",不重复 SKILL.md 硬性规则。Use when 用户问"hlkb 怎么用"/"知识库怎么填"/"怎么同步代码和文档"。
---

# hlkb 项目知识库使用说明

> **仓库即文档**: 与 `src/` 代码同 commit 维护。
> 完整规范见 [`SKILL.md`](./SKILL.md),概念速读见 [`INTRO.md`](./INTRO.md)

---

## 这是什么?

`hlkb` 是 hlskills 的"**项目知识库**"技能——仓库里 `knowledge/` 目录是"项目总文件库"(跨版本累计单一可信源),11 类文档覆盖 PRD/术语表/接口/数据库/ADR/状态机/枚举/错误码/依赖/环境变量/总测试库。

**触发式同步**: 任何代码/接口/数据/配置/决策变更, **必须同步知识库对应条目**, 与代码同 commit 提交。

---

## 什么时候用

✅ **适合用 hlkb**:
- 长期维护的项目(> 6 个月)
- 多人/AI Agent 协作
- 需要 onboarding 新人 / AI 5 分钟理解项目

❌ **不适合**(改用其他技能):
- 临时 demo / 一次性脚本(用 hl-flow / hlbug)
- 已有的 hl-prd / hldev 流程跑完仍缺知识库(用 hlkb 补)

---

## 5 分钟决策树:怎么用 hlkb?

```
我接手项目,接下来怎么办?
│
├─ 项目已经有 knowledge/
│  │
│  ├─ 想知道接口契约 → 读 knowledge/api/{module}.md
│  ├─ 想知道表结构 → 读 knowledge/db/{table}.md
│  ├─ 想知道 v3 为啥选方案 C → 读 knowledge/adr/{NNNN}-{slug}.md
│  ├─ 想知道状态机流转 → 读 knowledge/state-machines/{entity}.md
│  ├─ 想知道枚举/错误码 → 读 knowledge/{enums,error-codes}/
│  └─ 想知道技术栈/环境变量 → 读 knowledge/{dependencies,env-vars}/
│
└─ 项目还没有 knowledge/ (新项目 / 接手旧项目)
   │
   ├─ 新项目 + 跑 hlpm → 建议在版本交付自检时触发初始化(hlpm 未对接,需手动)
   │
   ├─ 接手旧项目 → 跑 hllegacy 知识沉淀阶段建议生成 knowledge/README.md + 初始反推(hllegacy 未对接,需手动)
   │
   └─ 自己手动初始化 → 看下面"手动初始化"
```

---

## 手动初始化(项目还没有 `knowledge/`)

```bash
# 1. 创建 9 个目录 + 1 个总 PRD 文件(可少建, 没内容的类别不建)
mkdir -p knowledge/{api,db,adr,state-machines,enums,error-codes,dependencies,env-vars,tests}
touch knowledge/prd.md  # 总 PRD(hlpm 步骤 11 追加累计,初始空)
touch knowledge/glossary.md  # 术语表(通用语言,hlpm 步骤 1 梳理时追加)

# 2. 写总目录
# 复制 templates/ 任意模板到 knowledge/README.md 改写

# 3. 接口文档(按模块拆分)
cp templates/api.md knowledge/api/blacklist.md
# 在里面填接口(URL/Method/入参/出参/错误码/权限)

# 4. 数据库文档(按表拆分, 加全局 ER 图)
cp templates/db-table.md knowledge/db/blacklist.md
cp templates/er-diagram.md knowledge/db/er-diagram.md  # 全局跨表关系图(mermaid)

# 5. ADR(每次决策新建一个, 编号 0001+)
cp templates/adr.md knowledge/adr/0001-{slug}.md

# 6. 状态机(按实体拆分)
cp templates/state-machine.md knowledge/state-machines/blacklist.md

# 7. 枚举 / 错误码(各放一文件)
cp templates/enum.md knowledge/enums/blacklist-status.md
cp templates/error-code.md knowledge/error-codes/README.md

# 8. 依赖 / 环境变量
cp templates/dependency.md knowledge/dependencies/README.md
cp templates/env-var.md knowledge/env-vars/README.md

# 9. 总测试库(按模块,验收用例 hlpm 产出 + 代码层用例 hldev 沉淀)
cp templates/code-tests.md knowledge/tests/blacklist.md

# 9. 同 commit 提交(代码 + 知识库)
git add knowledge/
git commit -m "docs(kb): 初始化项目知识库 - 11 类"
```

---

## 日常维护规则

### 新增接口

```bash
# 1. 编写代码 (Controller)
# 2. 更新接口文档(knowledge/api/{module}.md)
vi knowledge/api/blacklist.md  # 加 1 行接口总览 + 1 段详细说明
# 3. 同 commit 提交
git add src/main/java/.../BlacklistController.java knowledge/api/blacklist.md
git commit -m "feat(api): 新增 POST /blacklist/restore/{id} 接口"
```

### 新增字段

```bash
# 1. 编写迁移 SQL (hldb 强制)
# 2. 更新表结构文档
vi knowledge/db/{table}.md  # 加字段 + 更新索引
# 3. 更新 ER 图(如有外键变化)
vi knowledge/db/er-diagram.md
# 4. 同 commit 提交
git add migrations/v3_001_*.sql knowledge/db/{table}.md knowledge/db/er-diagram.md
git commit -m "feat(db): blacklist 表加 restored_* 字段"
```

### 重大决策

```bash
# 1. 写 ADR(必须先 ADR 后代码)
cp templates/adr.md knowledge/adr/0002-{slug}.md
# 编辑 ADR(状态=Proposed)
# 2. 集中评审(找用户拍板)
# 3. 评审通过 → ADR 状态改 Accepted
# 4. 才可写代码
# 5. 关联代码 commit message 引用 ADR 编号
git commit -m "feat(api): 实现 BL-12 恢复接口(ADR 0001)"
```

---

## 11 类知识库填充示例

详见 `templates/` 目录的 11 个模板文件:
- `templates/api.md` (接口)
- `templates/db-table.md` (数据库表)
- `templates/er-diagram.md` (全局 ER 关系图)
- `templates/adr.md` (决策记录)
- `templates/state-machine.md` (状态机)
- `templates/enum.md` (枚举)
- `templates/error-code.md` (错误码)
- `templates/dependency.md` (依赖)
- `templates/env-var.md` (环境变量)
- `templates/code-tests.md` (总测试库:验收+代码层)
- `templates/glossary.md` (术语表:通用语言)

---

## 自检清单(发布前必跑)

`hldev` 步骤 12.7 发布前自动跑, 你也可以手动跑:

```bash
# 检查 11 类是否齐全(prd.md + glossary.md + 9 目录 README)
ls knowledge/prd.md knowledge/glossary.md knowledge/{api,db,adr,state-machines,enums,error-codes,dependencies,env-vars,tests}/README.md

# 检查 API 文档覆盖所有接口
grep -oE "(GET|POST|PUT|DELETE) /[a-z]" knowledge/api/*.md | sort -u

# 检查 ADR 数量
ls knowledge/adr/*.md | wc -l

# 检查数据库表文档 + ER 图
ls knowledge/db/*.md
```

**任一缺失 → 应补齐后再发布**(靠 Agent/用户把关,非机制强制阻断;与 SKILL.md 能力边界声明一致)。

---

## 与 hlskills 其他技能的关系

| 技能 | 触发 hlkb 的位置 | 对方已对接? |
|---|---|---|
| `hlpm` 版本交付自检 | 建议追加 `knowledge/prd.md` / `knowledge/tests/` | ❌ 待对接 |
| `hldev` 步骤 4.5 走查 | 代码实现后同步 `api/` `db/` | ✅ |
| `hldev` 步骤 12.7 发布前 | 自检 11 类知识库完整性, 缺则应补齐 | ✅ |
| `hldb` 数据库迁移 | 任何 DDL 强约束同步 `db/` | ✅ |
| `hlapi` 接口设计 | 任何契约强约束同步 `api/` | ✅ |
| `hladr` 架构决策 | 输出直接写到 `adr/` | ✅ |
| `hlbug` Bug 修复 | 涉及字段/接口/配置时同步 | ✅ |
| `hllegacy` 知识沉淀 | 建议初始化整套知识库(从现状反推) | ❌ 待对接 |

---

## 关键约定(牢记)

- **同 commit**: 代码 + 知识库条目**必须同次提交**, 不分离
- **同 PR**: 如果用 PR 流程, 也必须同 PR
- **知识库不跟版本走**: 不放在 `docs/v{N}/`, 跨版本共用
- **编号永不重置**: ADR 编号从 0001 起, 不删除, 只标 Deprecated / Superseded
- **README.md 必填**: 每个 `knowledge/{类别}/` 目录都有 README.md 当索引

---

## 维护者

本技能是 `hlskills` 体系的一部分,版本 v1(2026-07-01)。
反馈 / 改进建议 → 主仓库开 issue。