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
- **v10**(当前):4 维防御机制
  - 步骤 4.5:PRD 逐项勾选(拦截漏实现 A 类)
  - 步骤 7.5:PRD 走查(拦截错误实现 B + 范围越界 D)
  - 步骤 12.5:PRD 覆盖率审计(拦截非功能漏实现 C + 兜底 A/B/D)
  - 第 5 矩阵:代码实现追踪矩阵(含 4 类偏离状态)
  - v11 自动化规划:Git Hook / CI/CD 集成(未来工作)

## 安装

```bash
# 复制到 Claude Code skills 目录
cp -r hlskills ~/.claude/skills/

# 或 Codex
cp -r hlskills ~/.codex/skills/
```

## 许可证

私有项目,未授权不得复制或商用。
