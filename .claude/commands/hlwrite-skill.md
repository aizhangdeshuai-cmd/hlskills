---
description: hlskills 技能写作方法论(3 原则 / SKILL.md 结构 / 评审 checklist / user vs model invoked)。Use when 编写/编辑/评审 hlskills 子技能 SKILL.md。
---

# hlwrite-skill ── hlskills 技能写作方法论

加载 `hlwrite-skill` 子技能(SKILL.md 在 `hlskills/hlwrite-skill/SKILL.md`),按其规范写新技能或评审现有技能。

## 3 条核心原则(源 SKILL.md L10-19)

### 1. 可预测性 > 完整性

- 技能的目标是让 Agent **能预测**怎么行动
- 不写"视情况""综合考虑"这种不可预测措辞
- 每条规则具体到可执行(给具体判定规则 / 退出码 / 路径)

### 2. 小而可组合,不接管流程

- hlskills 的流程由 hlchain 编排
- 各技能只管自己那一段
- 不试图接管上下游(如 hlpm 不规定 hldev 怎么做)
- 通过交付物 + 交接段松耦合

### 3. 可验证(有检查项)

- 每个技能必须有"完成前自检"或"评审检查项"
- **机械可验证**(grep 能查 / 文件存在性 / 退出码)
- 纯叙事规则不可验证,Agent 会跳过

## SKILL.md 结构规范(源 SKILL.md L21-53)

```
1. frontmatter(必须)
   - name: 短横线连字符
   - description: 一句话定位 + Use when + 调用方式
2. 标题(必须)
3. > 属于 hlskills 技能系统(与其他技能的关系)
4. > ⚠️ 能力边界声明(先读)
   - 本技能的"硬性关卡"是文档纪律,非 runtime 强制
5. ## 角色(角色映射表)
6. ## 通用纪律(完成前验证 / 受阻停止)
7. ## 流程(分阶段 + 步骤编号)
   - 第零阶段:加载上下文
   - 第一阶段:...
   - 第N阶段:...
8. ## 硬性关卡汇总(步骤 / 关卡 / 触发后果)
9. ## 交接段(被 hlchain 编排时的衔接)
10. ## 不在本技能范围(边界)
```

## user-invoked vs model-invoked(源 SKILL.md L55-63)

| 类型 | 触发 | 职责 | 例子 |
|---|---|---|---|
| **user-invoked** | 用户显式 `/hlxxx` | 编排(调其他技能/agent) | hlchain / hlpm / hldev |
| **model-invoked** | 用户或 Agent 自动调 | 可复用纪律(单一职责) | hlcode / hlapi / hldesign |

- user-invoked **可调** model-invoked
- user-invoked **不可调**另一个 user-invoked(避免嵌套混乱)
- model-invoked 是"纪律载体",任何技能可引用

## 写作反模式(避免,源 SKILL.md L65-74)

| 反模式 | 问题 | 正确 |
|---|---|---|
| 过度抽象 | "视情况综合判断" → Agent 不可预测 | 给具体判定规则 |
| 接管流程 | 技能规定上下游怎么做 | 只管自己段,交付物 + 交接段 |
| 不可验证 | 纯叙事无检查项 | 加 grep/文件存在/退出码检查 |
| 重复定义 | 同一规则多处写 | 单一可信源,各处引用 |
| 绝对化措辞 | "必须阻塞"但无机制 | 加"靠 Agent 自觉"(能力边界声明) |
| 角色混淆 | user-invoked 调 user-invoked | model-invoked 才可被任意调 |

## 评审 checklist(写完技能自检,源 SKILL.md L76-87)

| # | 项 | 检查方法 |
|---|---|---|
| 1 | frontmatter 含 name + description + Use when | `head -10 SKILL.md` |
| 2 | 有能力边界声明 | `grep "能力边界" SKILL.md` |
| 3 | 角色映射表(角色 \| Agent) | `grep "^## 角色" SKILL.md` |
| 4 | 流程分阶段 + 步骤编号 | `grep "^## 流程" SKILL.md` |
| 5 | 硬性关卡汇总表 | `grep "^## 硬性关卡" SKILL.md` |
| 6 | 交接段(若被 hlchain 编排) | `grep "^## 交接段" SKILL.md` |
| 7 | 完成前自检(可机械验证) | `grep -E "^- \[ \]" SKILL.md` |
| 8 | 无重复定义(引用单一源) | `grep "详见" SKILL.md \| wc -l` |
| 9 | 措辞可预测(无"视情况") | `grep "视情况" SKILL.md` 应 0 命中 |
| 10 | user/model-invoked 归类清晰 | `grep "user-invoked\|model-invoked" SKILL.md` |

## 调用方式

- **无实参**: 走评审 checklist 检查现有 SKILL.md
- **有实参**(如 `/hlwrite-skill 新建 hltailwind 技能`): 进入新技能写作流程

详见 `hlskills/hlwrite-skill/SKILL.md` 完整规范(93 行)。