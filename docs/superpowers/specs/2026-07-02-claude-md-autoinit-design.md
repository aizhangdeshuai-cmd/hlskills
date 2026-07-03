# 设计:项目约束文件自动初始化(CLAUDE.md / AGENTS.md)

> 日期:2026-07-02
> 状态:已确认,待写实施计划
> 背景:hlkb 的"知识库同步铁律"按需加载(SKILL.md),非常驻上下文,Agent 改代码时常忘同步。ehr 已在 CLAUDE.md 写了铁律,但因铁律是声明性的(无核对动作),仍发生指标三处并写漂移(PRD §1.13 `P95<500ms` vs NFR 文档 `P95<2s`)。本设计把铁律提升为**项目级常驻约束文件**,并加"完成前自检"把声明变核对动作,防漂移。

## 目标与非目标

**目标**
- 下次使用任意 hlskills 子技能时,自动为项目创建/补全 AI 约束文件(CLAUDE.md / AGENTS.md / .cursor/rules),作为知识沉淀的常驻载体。
- 把 hlkb 铁律从"按需加载"提升为"每次会话常驻"。
- 加"完成前自检"段,把声明性铁律变成可执行核对项,防漂移。

**非目标**
- 不做 hook/pre-commit 机制级阻断(属 hlhooks 范畴,本期不动)。
- 不内嵌项目详情(角色表/字段表/技术栈明细)——那些在 `knowledge/` 与 `.hl/memory/`,约束文件只放铁律+自检+指针,避免成为新漂移源。
- 不改 ehr 现有 CLAUDE.md(下次技能跑 ehr 时自动补缺)。

## 决策汇总

| 决策点 | 选择 |
|--------|------|
| ① 谁负责写 | 所有子技能步骤 0(加载项目上下文)都加检测+创建/补全 |
| ② 写哪个文件 | 检测当前 IDE:Claude Code→`CLAUDE.md` / Codex→`AGENTS.md` / Cursor→`.cursor/rules/*.mdc`;检测不出或多 IDE → 都写 |
| ③ 模板内容 | 铁律 + 检查项(不写死具体命令,跨 Java/Go/Python 可移植) |
| ④ 已存在时 | 校验是否含"完成前自检"段,缺则追加该段,不重写其他内容 |
| ⑤ 与 hlkb/hlmemory 边界 | 极简:一句话定位 + 铁律 + 完成前自检 + 指针(不内嵌详情) |

## 架构:共享定义 + 各技能引用(方案 A)

采用 hlskills 既有的"中央规范 + 各处引用"模式(同 path-conventions.md / consistency-rules.md):

- **模板 + 检测逻辑定义在一处**:`hlkb/templates/claude-md.template.md`
- **各子技能 step 0 加一条引用指令**:不内联完整逻辑,只引用模板路径
- **理由**:单一可信源,改模板只改一处。若各技能内联完整逻辑,会形成重复定义 = 漂移源,与本设计目标自相矛盾。

## 组件

### 组件 1:模板文件 `hlkb/templates/claude-md.template.md`

新建。与 hlkb 既有 9 个知识库模板(api/db/er-diagram/adr/state-machine/enum/error-code/dependency/env-var)并列。

内容(极简 4 段):

```markdown
# CLAUDE.md · {项目名}

> 项目级 AI 助手常驻约束。与代码同 commit 维护。
> 本文件极简:只放铁律 + 完成前自检 + 指针。详情见 knowledge/ 与 docs/ 与 .hl/memory/。

## 项目定位(一句话)
{技术栈一句话} · {项目类型} · 当前版本 {vN}

## AI 助手必读(进来先看)
1. 读本文件了解约束铁律
2. 读 `docs/master-prd.md` 了解当前所有功能
3. 读 `knowledge/` 了解工程现实(接口/数据库/决策/状态机/枚举/错误码/依赖/环境变量)
4. 读 `.hl/memory/` 了解跨会话项目记忆
5. 不许从 src/ 反推架构——查知识库或问用户

## 知识库同步铁律
任何代码/接口/数据/配置/决策变更,必须同步 `knowledge/` 对应条目,与代码同 commit 提交。详见 `hlkb` 技能 SKILL.md §同步触发表。

## 🚨 完成前自检(声明"完成"前必跑)
- [ ] 改了 src/ 代码 → 确认本次 diff 涉及的表/接口/枚举,在 `knowledge/` 对应文件已更新
- [ ] 涉及指标数字(性能/容量/QPS)→ 确认该数字在 PRD/NFR 文档/一致性矩阵三处一致,只允许一处定义
- [ ] 涉及枚举/错误码/依赖/环境变量变更 → 确认 `knowledge/{enums,error-codes,dependencies,env-vars}/` 同步
- [ ] 涉及架构决策 → 确认 `knowledge/adr/` 有对应 ADR
- [ ] 证据先于断言:上述核对有证据方可声明"完成"
```

设计要点:
- "完成前自检"5 项是**检查项**(描述要查什么),不写死 `grep`/`git diff` 命令——跨 Java/Go/Python 可移植,Agent 自决怎么查。
- 不内嵌角色表/字段表/技术栈明细——那些在 `knowledge/` 与 `.hl/memory/`,约束文件只放指针,避免详情变化时约束文件也成为需同步的漂移源。
- "项目定位"只一句话(技术栈/类型/版本),最小化内嵌信息。

### 组件 2:各子技能 step 0 加引用指令

在每个子技能的"步骤 0 加载项目上下文"里加一条(措辞统一):

> **项目约束文件初始化**:检测项目根是否有 AI 约束文件——Claude Code→`CLAUDE.md` / Codex→`AGENTS.md` / Cursor→`.cursor/rules/*.mdc`(检测不出当前 IDE 或检测到多个 IDE,则都写)。不存在 → 按 `hlkb/templates/claude-md.template.md` 创建;已存在 → 校验是否含 `## 🚨 完成前自检` 段,缺则追加该段(不重写其他内容)。

涉及子技能 step 0(~10 个文件,加同一句引用):
- `hl-flow/SKILL.md`
- `hlpm/SKILL.md`(步骤 0 加载已有文档)
- `hldev/SKILL.md`(步骤 0 验证版本目录)
- `hlbug/SKILL.md`(第零阶段加载项目上下文)
- `hllegacy/SKILL.md`(步骤 1 项目全景扫描前)
- `hlchain/SKILL.md`(编排入口,前置检查)
- `hldb/SKILL.md`
- `hlapi/SKILL.md`
- `hladr/SKILL.md`
- `hlrefactor/SKILL.md`

注:`hlkb` 自身不加(它是约束文件的**定义源**,不是"首次接触项目"的入口);`hltest`/`hlrelease`/`hldeploy` 等后续阶段技能不加(它们进入时项目已被前面技能初始化过,加引用冗余)。

### 组件 3:hlkb/SKILL.md 补"项目约束文件"职责段

在 hlkb/SKILL.md 的"与 hlskills 其他技能的关系"段附近,加一小段说明:

> ### 项目约束文件(CLAUDE.md / AGENTS.md)
> 约束文件是 hlkb 同步铁律的**常驻上下文版**——hlkb SKILL.md 按需加载,约束文件每次会话常驻。
> - 模板:`templates/claude-md.template.md`
> - 初始化/补全:由各子技能 step 0 检测并按模板创建(不存在)或补"完成前自检"段(已存在缺该段)
> - 内容:极简(铁律 + 完成前自检 + 指针),不内嵌详情,避免成为新漂移源

并在 hlkb 模板表(`## 9 类知识库模板` 段)补一行:

| 项目约束文件 | `templates/claude-md.template.md` | 铁律 + 完成前自检 + 指针(极简) |

## 数据流

```
用户跑任意 hlskills 子技能(如 hlpm)
  → 子技能 step 0 "加载项目上下文"
  → 检测项目根 AI 约束文件
     ├─ 不存在 → Read hlkb/templates/claude-md.template.md
     │           → 填充项目定位(从 .hl/memory 或项目扫描)
     │           → Write 到 CLAUDE.md/AGENTS.md/.cursor/rules
     └─ 已存在 → grep "## 🚨 完成前自检"
                  ├─ 含该段 → 跳过(已合规)
                  └─ 不含   → 追加该段到文件末尾(不重写其他)
  → 继续子技能正常流程
```

后续每次会话:AI 工具自动读约束文件(常驻上下文),铁律 + 自检始终在场。Agent 声明"完成"前,读自检段逐项核对。

## 错误处理 / 边界

- **IDE 检测不出**:都写(CLAUDE.md + AGENTS.md + .cursor/rules)。冗余但绝不漏。
- **模板路径找不到**:子技能 step 0 若 `Read hlkb/templates/claude-md.template.md` 失败 → 跳过初始化,不阻塞主流程(约束文件是增强项,非阻塞项),在输出中提示"未能初始化约束文件"。
- **已存在文件且无"完成前自检"段**:只追加该段,不动其他内容(尊重项目既有约定)。
- **已存在文件且有"完成前自检"段**:跳过,不做任何修改。
- **项目无 `knowledge/` 与 `.hl/memory/`**:约束文件仍创建(指针指向的目录可能暂不存在,指针本身有效;后续 hlkb/hllegacy 跑时会建目录)。

## 测试 / 验证

- **新项目场景**:在空目录跑 hl-flow/hlpm → 确认生成 CLAUDE.md(或对应 IDE 文件),内容含 4 段,定位一句话已填。
- **ehr 现有项目场景**:跑任意子技能 → 确认检测到 ehr/CLAUDE.md 已存在 → 确认其当前无"## 🚨 完成前自检"段 → 确认追加该段,其他内容不动。
- **Codex 场景**:在 Codex 环境跑 → 确认生成 AGENTS.md(非 CLAUDE.md)。
- **多 IDE 场景**:同时有 .claude 和 .codex 配置 → 确认 CLAUDE.md + AGENTS.md 都写。
- **防漂移回归**:改一个字段后声明完成 → 确认 Agent 读自检段第 1 项 → 确认核对 knowledge/db/ 已更新。

## 实施清单

1. 新建 `hlkb/templates/claude-md.template.md`(组件 1)
2. 改 `hlkb/SKILL.md`:加"项目约束文件"段 + 模板表补一行(组件 3)
3. 改 10 个子技能 step 0 加引用指令(组件 2):
   hl-flow / hlpm / hldev / hlbug / hllegacy / hlchain / hldb / hlapi / hladr / hlrefactor

## 非目标再确认(防范围蔓延)

- ❌ 不做 hook/pre-commit 机制(hlhooks 范畴)
- ❌ 不内嵌项目详情(角色/字段/技术栈明细)
- ❌ 不强制改 ehr 现有 CLAUDE.md(自动补缺即可)
- ❌ 不给 hltest/hlrelease/hldeploy 等后续技能加(冗余)
- ❌ 不写死自检命令(跨语言可移植)
