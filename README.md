# hlskills

> HL 项目开发技能合集 — 33 项子技能 + 19 个 Agent,覆盖产品→开发→测试→发布→部署全流程

## 5 分钟快速上手

**第一次用?** 先跑 `Skill hlquickstart` —— 5 分钟内用 2 个 mock 场景让你**实际看到** AI 按文档一步步做事是什么体验,而不是读 33 项 SKILL.md 想象。详见 [`hlquickstart/SKILL.md`](./hlquickstart/SKILL.md)。

### 我该用哪个? — 5 字口诀

| 场景 | 用什么 |
|------|--------|
| 演示/学习 hlskills 怎么用 | `Skill hlquickstart` (5 分钟) |
| 单人/小团队, 想自己跑完一条需求 | `Skill hl-flow` (按范围执行，UI 变更核对设计与浏览器行为，CLI/API 验证命令或接口，含发布部署) |
| 产品+开发分工, 先产品段产 PRD/设计 | `Skill hlpm`（可只写 PRD、增加可演示原型或准备完整交接包），完整包由 `Skill hldev` 接手 |
| 一次跑完需求→开发→测试→发布→部署 | `Skill hlchain` (编排 6 阶段, Agent 按顺序自觉加载) |
| 改代码/修 bug | `Skill hldev` (接手 knowledge/) 或 `Skill hlbug` (14 步排查) |

详细对比见下方 [子技能速览](#子技能速览)。

## 🚨 v16 子技能改名迁移说明

> **重要**:v16 起子技能改名为三件套。如果你是老用户,请对照下表更新引用:

| 旧名 (≤v15) | 新名 (v16+) | 变化 |
|--------------|------------|------|
| `hlpm` (28 步单人全流程) | **`hl-flow`** | 改名,流程不变(28 步单人自跑) |
| `hlpmnew` (0→1 41 步) | **(删除)** | 功能与 `hl-flow` 重复,移除 |
| `hlnew` (新项目分析 18 步) | **(删除)** | 功能由 `hllegacy`(旧项目分析)/ `hl-flow` 覆盖,移除 |
| `hlpm-product` (23 步产品段) | **`hlpm`** | 改名(原 hlpm 删除后,占这个名字) |
| `hlpm-dev` (15 步开发段) | **`hldev`** | 改名 |

**新三件套**:
- **`hl-flow`**:单人/小团队自跑全流程(28 步)
- **`hlpm`**:产品段（按本次目标交付 PRD、可演示原型或开发测试交接包）
- **`hldev`**:开发段(15 步,从产品段接手到部署上线)

**典型调用示例**:

```text
# 单人跑全流程
Skill hl-flow "为登录功能加短信验证码"

# 产品+开发分工
Skill hlpm "为订单列表加导出 CSV"
# 评审通过后,产品段产物交接给开发段:
Skill hldev "开始开发 knowledge/doc/v1/ 里的适用交付物（5 项必出，3 项按条件）"

# 一次跑完全链路 (由 Agent 按文档顺序自觉加载 hlpm→hldev→hlrelease→hldeploy, 中间可调 hlbug/hltest)
Skill hlchain "为订单列表加导出 CSV"

# 跨会话查项目知识
Skill hlkb "上次为什么调整退款重试？找出现行规则和证据位置"
```

**如果有团队已有引用旧名的脚本/AGENTS.md**:把 `/hlpm` → `/hl-flow`、`/hlpm-product` → `/hlpm`、`/hlpm-dev` → `/hldev` 即可。`/hlpmnew` 和 `/hlnew` 没有对应新名,删掉。

## ⚠️ 能力边界声明(请先读)

`hlskills` **本质是一份写得扎实的开发工作流 SOP 手册(以 Markdown 文本形式存在),而不是一套带 hook / runtime / 编排器的运行时**。了解这一点对正确使用本库至关重要:

- ✅ **流程纪律是文本**:产品、开发与缺陷修复流程、"硬性关卡"、"三项强同步"、"角色边界铁律"——这些都是 Markdown 文档,**Claude Code 不会机械地强制执行**。它们靠 Agent 加载后**自觉遵守**。
- **角色权限**。Claude 原生角色声明的 `disallowedTools: Write, Edit` 限制这两种工具。Bash 构建或测试仍可能写入文件，执行只读评审时应使用隔离副本或临时输出目录。其他宿主遵循其实际工具权限。
- **评审记录**。按实际参与者写明独立委派、人工签核或同一会话的多个视角。只有实际发生的独立审查才能登记为独立签核。
- **需求验收**：产品交接核对已确认约束、AC、TC 和适用原型；开发从同一计划核对候选测试报告。有指定竞品时，可从参考画面或实际操作建立基线，把采用的交互及品牌差异关联到原型和候选测试。[竞品 UI 还原](hlpm/competitor-ui.md)
- ⚠️ **hooks 模板需自测**:`hlhooks/SKILL.md` 提供的 hook 模板已对齐 Claude Code 真实协议,但启用后请按模板"验证"段实测一次,确认真的生效。

**对你的实际影响**:
- 你能让 Agent **照着文档一步步做**,但 Agent 不会因为漏一步就"无法进入下一步"
- `hl-permission` 写入项目权限；安装 `hlkb-hooks` 后，Claude Code 可在提交前按暂存路径检查知识库同步。内容质量仍需评审。
- 单独调用产品、开发或测试技能时，按本次 checkout 加载所需角色，角色出处可在交接中复核。[角色加载方式](SKILL.md#agent-使用方式)
- 多角色协作(`hlpm` + `hldev`)适合流程引导,**不适合把多 Agent 协作当流水线调度器**

## 简介

`hlskills` 是面向 AI 编码 Agent(如 Claude Code / Codex / Cursor)的**结构化开发工作流技能库**,把"从需求到上线"的完整流程拆解为可执行的子技能。每个子技能都按"阶段 + 评审 + 产出物"的方式组织,适合单人小团队或多角色协作场景。

## 核心特性

- **33 项子技能**(含 `hlquickstart` 快速上手 + `hlchain` 全流程编排 + `hlkb` 项目知识库):需求分析、PRD、设计、开发、测试、发布、部署、Git 规范、API 设计、数据库迁移、错误处理、编码标准、无障碍、ADR 等
- **19 个 Agent**:analyst / executor / code-reviewer / security-reviewer / verifier / designer / test-engineer 等专业角色
- **多角色协作**:`hlpm` （产品段，含交付后复盘） + `hldev` (开发段 15 步),支持"产品+开发"分工 + 重量评审会签 + 三项强同步 + 拒收机制
- **全流程编排**:`hlchain` 由 Agent 按文档顺序自觉加载 hlpm → hldev → hlrelease → hldeploy 全链路(中间可调 hlbug/hltest), 不必手动一次次调各技能(无真编排器 runtime, 靠 Agent 自觉 + 用户手动打断)
- **一体化保障**:按条件核对产品交付物，通过一致性矩阵追踪业务规则、状态机、权限、非功能要求与代码实现

## 子技能速览

**`hl-flow` vs `hlchain` 边界**：
- **`hl-flow`** = 单人/小团队自跑全流程（28 步已含发布部署）。**全流程能力内置**。
- **`hlchain`** = 编排器，**依次调 `hlpm → hldev → hlrelease → hldeploy`** 6 阶段。**主价值是多角色分工 + 阶段间停下评审/发布**。

**单人项目**用 `hl-flow`(一条龙跑完)。**多角色分工**用 `hlpm` + `hldev`(产品段产 PRD 后停下,开发段接手,阶段间自己把控节奏)。**想一次编排跑完全链路**用 `hlchain`(内部按顺序串 hlpm→hldev→hlrelease→hldeploy,少手动切换)。

| 场景 | 技能 | 命令 |
|------|------|------|
| 全流程编排（Agent 按文档顺序自觉加载 6 阶段） | `hlchain` | `Skill hlchain` (编排 hlpm→hldev→hlrelease→hldeploy + hlbug/hltest) |
| 新功能/新项目开发（单人跑, 28 步自含发布部署） | `hl-flow` | `Skill hl-flow` (28 步) |
| 多角色协作-产品段 | `hlpm` | `Skill hlpm` （各文档分别询问是否进行 5 角色评审） |
| 多角色协作-开发段 | `hldev` | `Skill hldev` (15 步, 含 4 维防御) |
| 旧项目分析/重构/Bug 修复 | `hllegacy` / `hlrefactor` / `hlbug` | — |
| UI 设计与指定竞品还原 | [hldesign](./hldesign/SKILL.md) | `/hldesign` |
| 审查/无障碍 | `hlreview` / `hla11y` | — |
| 代码质量与性能专项审查 | [hlquality](./hlquality/SKILL.md) | `Skill hlquality` |
| 硬编码凭证专项扫描 | [hlsecrets](./hlsecrets/SKILL.md) | `Skill hlsecrets` |
| 测试/发布/部署 | `hltest` / `hlrelease` / `hldeploy` | — |
| Git/API/DB/错误/编码 | `hlgit` / `hlapi` / `hldb` / `hlerror` / `hlcode` | — |
| 基础设施 | `hlsetup` / `hlhooks` / `hl-permission` / `hlmemory` / `hlkb` | — |
| 浏览器实时 QA | [hlbrowse](./hlbrowse/SKILL.md) | 仓库内命令行工具，支持页面交互、证据截图与性能检查 |
| 市场与竞品调研 | [hlresearch](./hlresearch/SKILL.md) | `Skill hlresearch` |
| 录屏分析与演示交付 | [hlmedia](./hlmedia/SKILL.md) | `Skill hlmedia` |
| 规划、基准测试与文档等 16 项专项流程 | [hltoolbox](./hltoolbox/SKILL.md) | `Skill hltoolbox` |
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
- **v16**:评审模式改名(联合评审 → 分阶段评审 / 3 合 1 → 集中评审) + 集中评审补全 5 角色(补回 architect/executor 视角)

- **hlpm v31**：该版引入信息架构附录。当前版本的 PRD 选型和启动分工见[产品段入口](./hlpm/SKILL.md#启动与选版)。

- **hlpm v32–v33**：增加踩坑记录、版本复盘和跨需求的全局约束去重。五项必交、三项按条件交付的校验规则见 [hlpm](./hlpm/handoff-package.md)。

本库内含各项流程、19 份角色定义和浏览器工具。浏览器自动化需要 Playwright 和 Chromium，本地视频抽帧和剪辑需要 FFmpeg。上游及采用范围见[升级记录](./docs/upstreams.md)。

## 平台支持分级与安装

在要使用的 **hlskills 仓库根目录** 运行对应命令。安装器从自身所在的 checkout 建立链接，并打印实际来源；修改这个 checkout 后链接随之更新。

| 平台 | 安装命令 | 入口与能力 |
|------|----------|------------|
| Claude Code | `python3 hlsetup/install.py claude` | 安装技能、命令文件和角色定义。项目权限与知识库 hook 单独启用。 |
| Codex | `python3 hlsetup/install.py codex` | 安装到 `~/.agents/skills/`，从同一 checkout 读取所需角色。旧版专属目录的同源安装会迁移。 |
| Cursor | `python3 hlsetup/install.py cursor` | 从链接的技能目录读取同源角色。项目规则可写入 `.cursor/rules/`。 |

安装后用同一命令加 `--check` 核对入口的来源、缺失和退役情况。更新后重跑安装会补齐新入口并清理本库旧链接。来源冲突、卸载及候选归档验证步骤见 [hlsetup](./hlsetup/SKILL.md)。

## 许可证

本项目自有内容沿用原授权限制。第三方角色文件及其衍生内容保留[上游 MIT 许可](./agents/LICENSE-OMC)。
