# hlskills

> HL 项目开发技能合集 — 25 项子技能 + 19 个 Agent,覆盖产品→开发→测试→发布→部署全流程

## 简介

`hlskills` 是面向 AI 编码 Agent(如 Claude Code / Codex / Cursor)的**结构化开发工作流技能库**,把"从需求到上线"的完整流程拆解为可执行的子技能。每个子技能都按"阶段 + 评审 + 产出物"的方式组织,适合单人小团队或多角色协作场景。

## 核心特性

- **25 项子技能**:需求分析、PRD、设计、开发、测试、发布、部署、Git 规范、API 设计、数据库迁移、错误处理、编码标准、无障碍、ADR 等
- **19 个 Agent**:analyst / executor / code-reviewer / security-reviewer / verifier / designer / test-engineer 等专业角色
- **多角色协作**:`hlpm-product` (产品段 23 步) + `hlpm-dev` (开发段 15 步),支持"产品+开发"分工 + 重量评审会签 + 三项强同步 + 拒收机制
- **一体化保障**:5 项交付物 + 7 个一致性矩阵(业务规则 / 状态机 / 权限 / 非功能 / 代码实现追踪),确保 PRD 100% 实现

## 子技能速览

| 场景 | 技能 | 命令 |
|------|------|------|
| 新功能/新项目开发 | `hlpm` | `/hlpm` (28 步) |
| 新项目 0→1 全流程 | `hlpmnew` | `/hlpmnew` (41 步) |
| 多角色协作-产品段 | `hlpm-product` | `/hlpm-product` (23 步,含 3 场重量评审) |
| 多角色协作-开发段 | `hlpm-dev` | `/hlpm-dev` (15 步,含 4 维防御) |
| 项目分析/重构/Bug 修复 | `hlnew` / `hllegacy` / `hlrefactor` / `hlbug` | — |
| 设计/审查/无障碍 | `hldesign` / `hlreview` / `hla11y` | — |
| 测试/发布/部署 | `hltest` / `hlrelease` / `hldeploy` | — |
| Git/API/DB/错误/编码 | `hlgit` / `hlapi` / `hldb` / `hlerror` / `hlcode` | — |
| 基础设施 | `hlsetup` / `hlhooks` / `hlPermission` / `hlmemory` | — |
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
- **v13**:评审模式可选(联合评审 / 3 合 1 集中评审)
- **v14**:设计规范硬性约束 + 已有页面微调 diff 规范
- **v15**(当前):多平台诚实声明 + 清理断链外部依赖 + agent 字段健康化(面向公开发布)

## 平台支持分级

> ⚠️ **三平台能力不对等**。本合集在不同平台下支持范围不同，请按所用平台对号入座：

### Claude Code(完整支持)

支持全部能力：25 项子技能 + 19 个 role agent(含 `disallowedTools` 工具隔离、`model` 模型分级、`effort` 等原生 frontmatter 字段) + slash 命令(`/hlpm` 等通过 `Skill` 工具或路由触发) + 可选外部技能(`videodb` / `market-research`)调用。

### Codex CLI(降级支持)

Codex 没有 per-agent 文件 + frontmatter 机制,定制方式是 `AGENTS.md` 纯 markdown 提示词拼进上下文,模型在 `~/.codex/config.toml` 全局配置。

- ✅ **可用**:全部子技能的流程纪律、步骤、产出物规范 → 合并进 `~/.codex/AGENTS.md` 或项目 `AGENTS.md` 使用;agent 角色设定(`agents/*.md` 正文) → 作为提示词内容粘贴进 `AGENTS.md` 使用
- ❌ **不生效**:agent frontmatter 中的 `disallowedTools` / `model` / `level` 字段(Codex 不解析);角色工具隔离改由"提示词自觉 + 主调用方负责写文件"实现
- ❌ **无入口**:`/hlpm` 等 slash 命令(改用"在对话中指明调用某子技能名称"触发);`Skill` 工具调用外部技能(如 `videodb`)

### Cursor(降级支持)

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
