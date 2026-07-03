---
name: hlwrite-skill
description: hlskills 技能写作方法论,定义技能结构(SKILL.md frontmatter + 段落规范)、user-invoked vs model-invoked 区分、可预测性原则、避免常见反模式(过度抽象/接管流程/不可验证)。Use when 编写/编辑/评审 hlskills 子技能 SKILL.md。通过 /hlwrite-skill 调用。
---

# hlskills 技能写作方法论

> 属于 `hlskills` 技能系统。吸收 mattpocock/skills 的 `writing-great-skills` 理念:技能要**可预测**(Agent 读了知道怎么做)、**小而可组合**(不接管流程)、**可验证**(有检查项)。

## 核心原则

### 1. 可预测性 > 完整性
技能的目标不是写满所有情况,而是让 Agent 读了能**预测**该怎么行动。每条规则要具体到可执行,不要"视情况而定""综合考虑"这种不可预测的措辞。

### 2. 小而可组合,不接管流程
hlskills 的流程由 hlchain 编排,各技能只管自己那一段。技能不要试图接管上下游(如 hlpm 不要规定 hldev 怎么做,只产出交付物 + 交接段)。技能间通过交付物 + 交接段松耦合。

### 3. 可验证(有检查项)
每个技能必须有"完成前自检"或"评审检查项"——能机械验证的清单(grep 能查 / 文件存在性 / 退出码)。纯叙事规则不可验证,Agent 会跳过。

## 技能结构(hlskills SKILL.md 规范)

```markdown
---
name: hlxxx
description: 一句话定位 + Use when 触发条件 + 通过 /hlxxx 调用。
---

# 技能标题

> 属于 hlskills 技能系统。(与其他技能的关系)

> ## ⚠️ 能力边界声明(先读)
> 本技能的"硬性关卡"是文档纪律,非 runtime 强制。靠 Agent 自觉 + 用户打断。

## 角色(角色映射表)
| 角色 | Agent |
|------|-------|
| ... | ... |

## 通用纪律(完成前验证 / 受阻停止)

## 流程(分阶段 + 步骤编号)
### 第零阶段:加载上下文(含项目约束文件初始化)
### 第一阶段:...
### 第N阶段:...

## 硬性关卡汇总(步骤 / 关卡 / 触发后果)

## 交接段(被 hlchain 编排时的衔接)

## 不在本技能范围(边界)
```

## user-invoked vs model-invoked

| 类型 | 触发 | 职责 | 例子 |
|------|------|------|------|
| user-invoked | 用户显式 `/hlxxx` | 编排(调其他技能/agent) | hlchain / hlpm / hldev |
| model-invoked | 用户或 Agent 自动调 | 可复用纪律(单一职责) | hlcode / hlapi / hldesign |

- user-invoked 可调 model-invoked,**不可调另一个 user-invoked**(避免编排嵌套混乱)
- model-invoked 是"纪律载体",任何技能可引用

## 写作反模式(避免)

| 反模式 | 问题 | 正确 |
|--------|------|------|
| 过度抽象 | "视情况综合判断"→ Agent 不可预测 | 给具体判定规则 |
| 接管流程 | 技能规定上下游怎么做 | 只管自己段,交付物 + 交接段 |
| 不可验证 | 纯叙事无检查项 | 加 grep/文件存在/退出码检查 |
| 重复定义 | 同一规则多处写 | 单一可信源,各处引用 |
| 绝对化措辞 | "必须阻塞"但无机制 | 加"靠 Agent 自觉"(能力边界声明) |
| 角色混淆 | user-invoked 调 user-invoked | model-invoked 才可被任意调 |

## 评审 checklist(写完技能自检)

- [ ] frontmatter 含 name + description + Use when
- [ ] 有能力边界声明(承认靠自觉,非 runtime)
- [ ] 角色映射表(角色 | Agent)
- [ ] 流程分阶段 + 步骤编号
- [ ] 硬性关卡汇总表
- [ ] 交接段(若被 hlchain 编排)
- [ ] 完成前自检(可机械验证)
- [ ] 无重复定义(引用单一源)
- [ ] 措辞可预测(无"视情况")
- [ ] user/model-invoked 归类清晰

## 关联

- hlskills 现有技能:见根 `SKILL.md` 技能清单
- 技能写作参考:mattpocock/skills `writing-great-skills`
- 模板:本文件即可作为新技能 SKILL.md 的起点
