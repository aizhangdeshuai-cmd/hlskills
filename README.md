# hlskills

> HL 项目开发技能合集 — 25 项子技能 + 19 个 Agent,覆盖产品→开发→测试→发布→部署全流程

## 5 分钟快速上手

**第一次用?** 先跑 `Skill hlquickstart` —— 5 分钟内用 2 个 mock 场景让你**实际看到** AI 按文档一步步做事是什么体验,而不是读 25 项 SKILL.md 想象。详见 [`hlquickstart/SKILL.md`](./hlquickstart/SKILL.md)。

## 🚨 v16 子技能改名迁移说明

> **重要**:v16 起子技能改名为三件套。如果你是老用户,请对照下表更新引用:

| 旧名 (≤v15) | 新名 (v16+) | 变化 |
|--------------|------------|------|
| `hlpm` (28 步单人全流程) | **`hl-flow`** | 改名,流程不变(28 步单人自跑) |
| `hlpmnew` (0→1 41 步) | **(删除)** | 功能与 `hl-flow` 重复,移除 |
| `hlnew` (新项目分析 18 步) | **(删除)** | 功能由 `hlbug` / `hl-flow` 覆盖,移除 |
| `hlpm-product` (23 步产品段) | **`hlpm`** | 改名(原 hlpm 删除后,占这个名字) |
| `hlpm-dev` (15 步开发段) | **`hldev`** | 改名 |

**新三件套**:
- **`hl-flow`**:单人/小团队自跑全流程(28 步)
- **`hlpm`**:产品段(多角色,23 步,产出 PRD/设计/用例给开发)
- **`hldev`**:开发段(15 步,从产品段接手到部署上线)

**典型调用示例**:

```text
# 单人跑全流程
Skill hl-flow "为登录功能加短信验证码"

# 产品+开发分工
Skill hlpm "为订单列表加导出 CSV"
# 评审通过后,产品段产物交接给开发段:
Skill hldev "开始开发 docs/v1/ 里的 8 项交付物"

# 一次跑完全链路 (自动按顺序加载 hlpm→hldev→hlrelease→hldeploy, 中间可调 hlbug/hltest)
Skill hlchain "为订单列表加导出 CSV"
```

**如果有团队已有引用旧名的脚本/AGENTS.md**:把 `/hlpm` → `/hl-flow`、`/hlpm-product` → `/hlpm`、`/hlpm-dev` → `/hldev` 即可。`/hlpmnew` 和 `/hlnew` 没有对应新名,删掉。

## ⚠️ 能力边界声明(请先读)

`hlskills` **本质是一份写得扎实的开发工作流 SOP 手册(以 Markdown 文本形式存在),而不是一套带 hook / runtime / 编排器的运行时**。了解这一点对正确使用本库至关重要:

- ✅ **流程纪律是文本**:28/23/15/14 步流程、"硬性关卡"、"三项强同步"、"角色边界铁律"——这些都是 Markdown 文档,**Claude Code 不会机械地强制执行**。它们靠 Agent 加载后**自觉遵守**。
- ✅ **角色工具隔离靠 frontmatter 字段**:只读 agent 的 `disallowedTools: Write, Edit` 字段是 Claude Code 原生支持的,会被 harness 强制执行——这是仓库**真实生效**的工具隔离。
- ❌ **"会签""门禁""阶段门禁"等是文档语言**:仓库没有 hook / 状态机 / 编排器强制 Agent 走完某一步才能进入下一步。"5 角色会签"是 5 个 Agent 角色**在同一个 LLM 会话里被 prompt 提示**(你看到的"5 方评审意见"实际是同一个 LLM 在扮演)。
- ❌ **代码覆盖率审计靠一致性矩阵**:靠人工对照 `docs/consistency-matrix.md` 第 5 矩阵逐行核对实现状态(已在前次 v15 修复 grep 正则审计方案)。
- ⚠️ **hooks 模板需自测**:`hlhooks/SKILL.md` 提供的 hook 模板已对齐 Claude Code 真实协议,但启用后请按模板"验证"段实测一次,确认真的生效。

**对你的实际影响**:
- 你能让 Agent **照着文档一步步做**,但 Agent 不会因为漏一步就"无法进入下一步"
- 你能用 `hl-permission` **真实放宽**项目目录权限,这是唯一操作 Claude Code 真实 API 的子技能
- 你的"角色隔离"在只读类 agent(analyst/architect 等)是**真生效**,在写类 agent(executor/designer 等)**靠自觉**
- 多角色协作(`hlpm` + `hldev`)适合流程引导,**不适合把多 Agent 协作当流水线调度器**

## 简介

`hlskills` 是面向 AI 编码 Agent(如 Claude Code / Codex / Cursor)的**结构化开发工作流技能库**,把"从需求到上线"的完整流程拆解为可执行的子技能。每个子技能都按"阶段 + 评审 + 产出物"的方式组织,适合单人小团队或多角色协作场景。

## 核心特性

- **25 项子技能**(含 `hlquickstart` 快速上手 + `hlchain` 全流程编排):需求分析、PRD、设计、开发、测试、发布、部署、Git 规范、API 设计、数据库迁移、错误处理、编码标准、无障碍、ADR 等
- **19 个 Agent**:analyst / executor / code-reviewer / security-reviewer / verifier / designer / test-engineer 等专业角色
- **多角色协作**:`hlpm` (产品段 23 步) + `hldev` (开发段 15 步),支持"产品+开发"分工 + 重量评审会签 + 三项强同步 + 拒收机制
- **全流程编排**:`hlchain` 一次跑完 hlpm → hldev → hlrelease → hldeploy 全链路(中间可调 hlbug/hltest), 不必手动一次次调各技能
- **一体化保障**:8 项产品交付物 + 7 个一致性矩阵(业务规则 / 状态机 / 权限 / 非功能 / 代码实现追踪),确保 PRD 100% 实现

## 子技能速览

| 场景 | 技能 | 命令 |
|------|------|------|
| 一次跑完全链路（自动按顺序加载 6 阶段） | `hlchain` | `/hlchain` (编排 hlpm→hldev→hlrelease→hldeploy + hlbug/hltest) |
| 新功能/新项目开发（单人跑） | `hl-flow` | `/hl-flow` (28 步) |
| 多角色协作-产品段 | `hlpm` | `/hlpm` (23 步,含 5 角色评审) |
| 多角色协作-开发段 | `hldev` | `/hldev` (15 步,含 4 维防御) |
| 旧项目分析/重构/Bug 修复 | `hllegacy` / `hlrefactor` / `hlbug` | — |
| 设计/审查/无障碍 | `hldesign` / `hlreview` / `hla11y` | — |
| 测试/发布/部署 | `hltest` / `hlrelease` / `hldeploy` | — |
| Git/API/DB/错误/编码 | `hlgit` / `hlapi` / `hldb` / `hlerror` / `hlcode` | — |
| 基础设施 | `hlsetup` / `hlhooks` / `hl-permission` / `hlmemory` | — |
| 浏览器实时 QA | `hlbrowse` | `/hlbrowse` (70+ 命令) |
| 架构决策记录 | `hladr` | — |

## 详细说明

主入口见 [`SKILL.md`](./SKILL.md)。

## 版本演进

- **v1-v4**:基础工作流(单技能 `hlpm`)
- **v5**:三项强同步(PRD/设计/用例) + 一致性矩阵
- **v6**:非功能需求细分(性能/安全/兼容 3 个子表) + 自检报告模板
- **v7-v9**:微调
- **v10**:4 维防御机制(步骤 4.5 PRD 逐项勾选 / 7.5 PRD 走查 / 12.5 PRD 覆盖率审计 / 第 5 矩阵代码实现追踪)
- **v11**:角色边界铁律(产品不写代码) + 6 条件路径
- **v12**:版本目录管理(`docs/vN/`) + 开发完成/拒收标记文件
- **v13**:评审模式可选(分阶段评审 / 集中评审)
- **v14**:设计规范硬性约束 + 已有页面微调 diff 规范
- **v15**:多平台诚实声明 + 清理断链外部依赖 + agent 字段健康化(面向公开发布)
- **v16**(当前):评审模式改名(联合评审 → 分阶段评审 / 3 合 1 → 集中评审) + 集中评审补全 5 角色(补回 architect/executor 视角)

## 平台支持分级

> ⚠️ **三平台能力不对等**。本合集在不同平台下支持范围不同，请按所用平台对号入座：

### Claude Code(完整支持)

支持全部能力：25 项子技能 + 19 个 role agent(含 `disallowedTools` 工具隔离、`model` 模型分级、role-only 行为约束写入 agent 正文) + Skill 工具调用(如 `Skill hlpm`) + 可选外部技能(`videodb` / `market-research`)调用。

### Codex CLI(降级支持)

> ⚠️ **Codex 用户注意**: 你**不能**直接调用 `/hlpm` 等子技能——Codex 没有 Skill 工具也没有 slash 命令入口。实际使用方式: **手动复制 `hlpm/SKILL.md` 全文到 `~/.codex/AGENTS.md` 或项目 `AGENTS.md` 当提示词**,然后在对话中"指明调用某子技能名"让 Codex 按提示词行事。**这是降级路径,不是同等待遇**。

Codex 没有 per-agent 文件 + frontmatter 机制,定制方式是 `AGENTS.md` 纯 markdown 提示词拼进上下文,模型在 `~/.codex/config.toml` 全局配置。

- ✅ **可用**:全部子技能的流程纪律、步骤、产出物规范 → 合并进 `~/.codex/AGENTS.md` 或项目 `AGENTS.md` 使用;agent 角色设定(`agents/*.md` 正文) → 作为提示词内容粘贴进 `AGENTS.md` 使用
- ❌ **不生效**:agent frontmatter 中的 `disallowedTools` / `model` / `level` 字段(Codex 不解析);角色工具隔离改由"提示词自觉 + 主调用方负责写文件"实现
- ❌ **无入口**:`/hlpm` 等 slash 命令(改用"在对话中指明调用某子技能名称"触发);`Skill` 工具调用外部技能(如 `videodb`)

### Cursor(降级支持)

> ⚠️ **Cursor 用户注意**: 与 Codex 类似,你**不能**用 `/hlpm` 启动流程或用 Skill 工具调用外部技能。实际使用方式: **将所需子技能 SKILL.md 转为 `.cursor/rules/*.mdc` 规则文件**,通过文件触发(`globs` 匹配)或常驻(`alwaysApply`)挂载。**功能大幅缩水**,不适合完整跑 23/28 步流程。

Cursor rules(`.cursor/rules/*.mdc`)frontmatter 只认 `description` / `alwaysApply` / `globs`,控制"何时挂载",不认工具/模型限制;模型和工具开关在 Cursor app 设置里配置。

- ✅ **可用**:子技能作为 `.mdc` 规则挂载(按 `globs` 匹配文件触发或 `alwaysApply`);流程纪律 + 产出物规范作为规则内容使用
- ❌ **不生效**:agent frontmatter 的工具/模型/level 字段;per-agent 文件机制
- ❌ **无入口**:slash 命令、`Skill` 工具

## 安装

### Claude Code

```bash
cp -r hlskills ~/.claude/skills/
```

安装后通过 `Skill hlskills` 调用主入口,或在对话中提"开发流程 / PRD / Bug 修复"等关键词自动路由到对应子技能。各 role agent 位于 `hlskills/agents/`,Claude Code 会按 `disallowedTools` / `model` frontmatter 强制执行工具隔离与模型分级。

**调用语法示例**:

```text
# 加载主入口(SKILL.md 的 description 触发自动路由)
Skill hlskills

# 直接调用某个子技能(Skill 工具传 args)
Skill hlpm "为登录功能启动 28 步流程"

# 子技能内部按 frontmatter 描述自动派发 role agent(无需你手动调)
# 例如 analyst (Opus, 只读) / executor (Sonnet, 可改) / verifier (Sonnet) 等
```

> 注意:本文档表格中的 `/hlpm` / `/hlpm` 等写法是**子技能名称简写**,实际调用使用 Claude Code 的 `Skill` 工具(如 `Skill hlpm`)而非终端 `/` 斜杠命令。Codex CLI / Cursor 无此入口,改用各自平台的常规方式触发(详见各平台章节)。

### Codex CLI

```bash
# Codex 无 per-agent 机制,请将主入口与所需子技能合并进 AGENTS.md
# 1) 复制子技能正文
cp -r hlskills ~/.codex/skills/   # 作为参考文档留存
# 2) 在 ~/.codex/AGENTS.md(全局) 或项目 AGENTS.md 中引用你需要的流程:
#    将 ~/.codex/skills/hlskills/SKILL.md 与各 hl*/SKILL.md 内容直接粘贴/引入到 AGENTS.md
# 3) 全局模型在 ~/.codex/config.toml 设置: model = "..."
```

> Codex 下 agent 的工具限制、模型分级、level 字段不生效,角色隔离靠提示词自觉;`/hlpm` 等命令改用对话中指明子技能名触发。

### Cursor

```bash
# 将所需子技能的 SKILL.md 转为 .cursor/rules/*.mdc 规则文件
# 示例:把 hlskills/hlpm/SKILL.md 内容放进 .cursor/rules/hlpm.mdc
```

```yaml
# .cursor/rules/*.mdc frontmatter 仅支持以下字段:
---
description: 新需求开发流程
alwaysApply: false
globs: "src/**"   # 匹配到这些文件时挂载
---
(此处粘贴对应子技能 SKILL.md 正文)
```

> Cursor 下 per-agent 工具/模型限制、slash 命令、Skill 工具均不适用。

## 许可证

私有项目,未授权不得复制或商用。
