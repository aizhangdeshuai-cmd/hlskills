---
name: hlskills
description: HL 项目开发技能合集总入口,内嵌 19 个角色 agent 与 25 项子技能,覆盖需求→开发→测试→发布→部署全流程。Use when 用户提到开发流程、PRD、需求评审、设计评审、Bug 修复、代码审查、API 设计、数据库迁移、发布部署、编码规范、无障碍等任意关键词时自动路由到对应子技能。通过 Skill 工具调用。
---
![hlpm-product](https://img.shields.io/badge/hlpm--product-v15-blue) ![review](https://img.shields.io/badge/review-3%20in%201-green)

> 当前版本: **v15** | 评审模式: **3 合 1(可选择)** | 原版 hlpm / hlpmnew 一字不改
> ⚠️ 多平台能力不对等:Claude Code 完整支持;Codex / Cursor 降级支持(详见 README「平台支持分级」)
# HL 项目开发技能合集

## 子技能索引

根据用户意图自动路由到对应技能：

| 意图 | 技能 | 命令 | 内容 |
|------|------|------|------|
| 新功能/新项目开发 | `hlpm` | `/hlpm` | 28步：加载上下文→需求→竞品→PRD→设计→确认→测试→Git工作区→计划→ADR→开发→审查→联调→自测→分支→安全→测试→浏览器→审计→交付→用户确认发布→用户确认部署 |
| 新项目0→1全流程 | `hlpmnew` | `/hlpmnew` | 41步：市场分析→可行性→风险评估→Go/No-Go→完整PRD→风格设计→确认→全部页面→开发→测试→交付→上线 |
| **多角色协作-产品段** | `hlpm-product` | `/hlpm-product` | **23步基础 + 6 条件路径：第 0.5 步评估规模(轻量/标准/复杂)和是否涉及设计；设计阶段(6/7)是条件性执行(纯后端/接口/状态机/规则可跳过)。仅产出文档(PRD/用例/验收/非功能),绝不修改代码。配套 hlpm-dev 使用** |
| **多角色协作-开发段** | `hlpm-dev` | `/hlpm-dev` | **15步：验证5项交付物（含版本一致性+一致性矩阵）→Git→开发→审查→联调→测试→审计→发布→部署。配套 hlpm-product 使用** |
| 新项目分析 | `hlnew` | `/hlnew` | 18步：市场分析→可行性→风险评估→Go/No-Go决策→启动准备→衔接hlpm |
| 旧项目分析 | `hllegacy` | `/hllegacy` | 12步：项目扫描→架构理解→质量基线→知识沉淀（含前端设计规范提取） |
| 旧项目重构 | `hlrefactor` | `/hlrefactor` | 21步：代码分析→策略→测试护城河→逐模块重构→回归→文档→上线 |
| Bug修复/线上排查 | `hlbug` | `/hlbug` | 14步：定位→Git工作区→修复→审查→回归→验证→分支→交付（融合 /investigate 四阶段调试） |
| 代码/安全/生产审查 | `hlreview` | `/hlreview` | PRD/设计/代码/安全/生产审查 + 结构性问题检测 + /cso 安全 + /codex 第二意见 |
| UI/UX 设计 | `hldesign` | `/hldesign` | 设计依据优先级 + 交互状态覆盖 + 无障碍检查 |
| **无障碍规范** | `hla11y` | `/hla11y` | **WCAG 2.2 AA 规范，覆盖设计→开发→测试三阶段** |
| 架构决策记录 | `hladr` | `/hladr` | ADR 格式、记录时机、取代规则 |
| 测试全流程 | `hltest` | `/hltest` | 用例编写 + E2E（Playwright）+ QA三级 + Diff-aware + 健康评分 + 响应式 + 仅报告模式 |
| 浏览器实时QA | `hlbrowse` | `/hlbrowse` | 70+命令：导航/交互/快照/截图/Cookie导入（集成 gstack 浏览器引擎） |
| 发布上线 | `hlrelease` | `/hlrelease` | 版本号→变更日志→预发布清单→标签→推送 |
| 部署运维 | `hldeploy` | `/hldeploy` | CI/CD + 部署策略 + Docker + 健康检查 + 金丝雀监控 + 回滚 |
| Git 规范 | `hlgit` | `/hlgit` | Conventional Commits + OMC协议 + 分支命名 |
| API 设计 | `hlapi` | `/hlapi` | URL命名 + 状态码 + 分页 + 错误格式 + 版本控制 |
| 数据库迁移 | `hldb` | `/hldb` | 安全清单 + 零停机策略 + 禁止事项 |
| 错误处理 | `hlerror` | `/hlerror` | 类型化错误 + 重试断路器 + 错误边界 |
| 编码标准 | `hlcode` | `/hlcode` | 命名 + 不可变性 + 文件组织 + 代码味道清单 |
| 项目记忆 | `hlmemory` | `/hlmemory` | 跨会话持久化（项目/技术栈/架构/约定/工作记忆） |
| 安装部署 | `hlsetup` | `/hlsetup` | 一键安装到 Claude Code / Codex / Cursor |
| Hooks 配置 | `hlhooks` | `/hlhooks` | 安全/质量/自动化 hooks 模板 |
| 一键授权 | `hl-permission` | `/hl-permission` | 当前项目目录 Edit/Write/Bash 全免授权，`--off` 恢复 |

---

## 使用场景选择

| 场景 | 推荐技能 | 原因 |
|------|---------|------|
| **单人或小团队**（一人跑完全流程） | `hlpm` / `hlpmnew` | 流程紧凑，28/41 步串行执行 |
| **多角色协作**（产品 + 开发分工） | `hlpm-product` + `hlpm-dev` | 23 + 15 步分工,角色边界铁律(产品不写代码)+ 6 条件路径(按规模和设计需求)+ 重量评审会签、三项强同步、拒收机制 |

**原 `hlpm` / `hlpmnew` 一字不改，新技能作为变体并存，按需选用。**

---

## 角色与 Agent 映射（全局）

| 角色 | Agent |
|------|-------|
| 产品经理 | `analyst` / `planner` |
| UI/UX设计师 | `designer` |
| 前端开发 | `executor` |
| 后端开发 | `architect` / `executor` |
| 代码审查 | `code-reviewer` |
| 安全审查 | `security-reviewer` |
| 测试 | `test-engineer` / `qa-tester` |
| 验证 | `verifier` |
| 用户（我） | — 关键节点确认者 |

### Agent 使用方式

所有 Agent 定义文件位于 `hlskills/agents/` 目录。使用某个 Agent 时，先读取对应的定义文件（如 `agents/analyst.md`），按其中的角色设定和指令执行任务。

| Agent | 文件 | 模式 |
|-------|------|------|
| `analyst` | `agents/analyst.md` | 需求分析、PRD评审（只读） |
| `planner` | `agents/planner.md` | 制定可执行工作计划 |
| `designer` | `agents/designer.md` | UI/UX 视觉设计 |
| `executor` | `agents/executor.md` | 代码实现与重构 |
| `architect` | `agents/architect.md` | 系统架构、根因分析（只读） |
| `code-reviewer` | `agents/code-reviewer.md` | 代码质量审查（只读） |
| `security-reviewer` | `agents/security-reviewer.md` | 安全漏洞审查（只读） |
| `test-engineer` | `agents/test-engineer.md` | 测试策略与用例编写 |
| `qa-tester` | `agents/qa-tester.md` | 交互式测试执行 |
| `verifier` | `agents/verifier.md` | 基于证据的完成验证 |
| — | — | — |
| `explore` | `agents/explore.md` | 快速代码库搜索与映射（只读） |
| `debugger` | `agents/debugger.md` | 根因分析与故障诊断 |
| `tracer` | `agents/tracer.md` | 证据驱动的因果追踪（只读） |
| `writer` | `agents/writer.md` | 文档与内容生成 |
| `git-master` | `agents/git-master.md` | 原子提交策略与历史管理 |
| `scientist` | `agents/scientist.md` | 数据分析与统计推理（只读） |
| `code-simplifier` | `agents/code-simplifier.md` | 保持行为的代码简化（只读） |
| `critic` | `agents/critic.md` | 计划/设计的多角度挑战评审（只读） |
| `document-specialist` | `agents/document-specialist.md` | SDK/API/框架文档查找（只读） |

---

## 通用纪律：完成前验证

**任何阶段标记"完成"前，必须执行以下验证规则：**

- 识别能证明该阶段完成的验证命令，完整运行该命令
- 读取完整输出并检查退出码，确认通过后方可声明完成
- **绝对禁止**："应该通过了"、"看起来正确"、"之前检查过了"、"应该没问题"
- 证据先于断言，无一例外

## 通用能力：文件与图片读取

- **优先使用当前模型的多模态能力**：如果当前 AI 模型原生支持图片识别（如 Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5），直接让模型分析图片内容
- **降级使用 Read 工具**：如果当前模型**不支持**图片识别（如通过 API 调用且 provider 未启用多模态），则使用 Read 工具读取图片文件（支持 PNG / JPG / WebP / PDF），Read 工具返回的图片内容可供分析
- 需求分析、设计规范提取、Bug分析等场景中，如输入文件包含图片，**必须分析图片内容**，不能只读文本
- 图片内容与文本内容同等重要，合并分析形成完整理解

## 通用规则：文件输出路径

**所有产出文件必须保存到对应的项目目录下。**

- **项目地址已知**（`.hl/memory/` 存在 或 用户已指定） → 输出到项目根目录的对应子目录：
  ```
  {项目根目录}/
  ├── docs/           ← 需求文档/PRD/技术设计/ADR/测试用例
  ├── docs/design/    ← 设计规范文档/设计HTML
  ├── docs/analysis/  ← 市场分析/竞品分析/可行性报告
  ├── docs/qa/        ← 测试报告/健康评分/审计报告
  ├── docs/user/      ← 用户操作手册/帮助文档
  └── .hl/memory/     ← 项目记忆文件
  ```
- **项目地址未知** → 🚨 **立即向用户提问**："请指定项目根目录地址"，用户回复后再输出文件
- **严禁**将文件输出到 `/tmp`、`~` 等临时或个人目录
- **完整目录规范**：详见 `hlpm-product/path-conventions.md`（中央规范文档，定义 15 项交付物路径、命名约定、深度限制、特殊情况处理）

---

## 问题升级机制

- 各阶段遇到问题，由**产品经理**（`analyst`）组织会议讨论
- 会议中无法达成一致的问题，**立即向用户提问**，不得自行裁决
- 直至所有参与方无异议后，方可进入下一阶段

---

## 变更传播规则

- 设计变更 → 需求文档、PRD、设计规范、设计HTML、测试用例、技术设计文档 **同步更新**
- Bug修复涉及逻辑变更 → 接口文档、数据库设计、测试用例、用户操作手册、帮助文档 **同步更新**
- 架构决策被取代 → 原 ADR 标记"已取代"，不删除历史
- 产品经理负责追踪，确保所有文档一致性

---

## 交付文档清单

1. 需求文档
2. 竞品分析报告（新项目必须）
3. PRD文档
4. 设计规范文档
5. 设计HTML
6. 技术设计文档（接口文档 + 数据库设计 + 逻辑架构图）
7. 架构决策记录（`docs/adr/`）
8. 测试用例
9. 用户操作手册
10. 帮助文档
11. 变更日志（CHANGELOG）
12. 回滚方案

---

## 可独立使用的 gstack 技能

以下 gstack 技能未纳入 hlskills 体系，但可作为独立技能使用。在终端执行 `Skill gstack <技能名>` 加载：

### 规划与决策
| 技能 | 用途 |
|------|------|
| **office-hours** | 产品头脑风暴 / YC Office Hours 创业诊断 |
| **plan-ceo-review** | CEO 视角方案评审，重新思考问题边界 |
| **plan-eng-review** | 工程视角方案评审，锁定执行计划 |
| **autoplan** | 自动评审流水线（CEO → 设计 → 工程 → DX） |
| **retro** | 工程周回顾：分析提交历史、工作模式、代码质量 |

### 设计与视觉
| 技能 | 用途 |
|------|------|
| **design-consultation** | 从零构建设计系统（美学/字体/颜色/布局/动效），产出 DESIGN.md |
| **design-review** | 线上网站视觉审计 + 修复循环 |
| **design-shotgun** | 生成多个 AI 设计变体，对比板，结构化反馈 |

### 工程与性能
| 技能 | 用途 |
|------|------|
| **benchmark** | 性能回归检测（页面加载/Core Web Vitals/资源大小） |
| **land-and-deploy** | 合并 + 部署 + 金丝雀验证一体化 |
| **document-generate** | 从零生成文档（Diataxis 框架：教程/指南/参考/解释） |
| **document-release** | 发布后文档同步更新 |
| **scrape** | 网页数据提取 |

### 工具与实用
| 技能 | 用途 |
|------|------|
| **make-pdf** | Markdown → 出版质量 PDF |
| **setup-deploy** | 配置项目部署平台 |
| **learn** | 管理项目跨会话学习成果 |

**使用方式**：在终端执行 `Skill gstack office-hours`（或任何上述技能名）加载对应技能。加载后可独立使用，不影响 hlskills 工作流。
