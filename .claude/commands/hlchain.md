---
description: hlskills 全流程编排(6 阶段,Agent 自觉顺序)。Use when 一次跑完需求→开发→测试→发布→部署全链路,而不是手动一次次调各技能。
---

# hlchain ── hlskills 全链路编排

加载 `hlchain` 子技能(SKILL.md 在 `hlskills/hlchain/SKILL.md`),按其编排 6 个子技能跑完整链路。

## 编排的 6 个子技能

| 阶段 | 子技能 | 角色 | 何时调 |
|---|---|---|---|
| 1 | `hlpm` | 产品段 13 步 + 4 子阶段 | 需求开始 |
| 2 | `hldev` | 开发段 15 步 | hlpm 产物交接后 |
| 3 | `hlrelease` | 版本号/CHANGELOG/标签 | hldev 交付后 |
| 4 | `hldeploy` | CI/CD + 部署 + 金丝雀 | hlrelease 后 |
| 5 | `hlbug` | Bug 修复 14 步 | **任一阶段发现问题** 都可触发 |
| 6 | `hltest` | 独立测试 | 与 hldev 步骤 10 并行 |

## 执行模式(源 SKILL.md L31-40)

### 模式 C(默认,A+B 结合):Agent 自觉顺序 + 显式交接段

- **A: Agent 自觉顺序** — Agent 按文档顺序自动加载下一阶段,不需用户手动 Skill
- **B: 显式交接段** — 每个子技能末尾加"## 交接段"标注下一阶段预期产出

## Agent 加载本技能后的执行规范(4 步)

1. **第零步** 项目约束文件初始化(检测 Claude Code/Codex/Cursor,创建 CLAUDE.md/AGENTS.md)
2. **第一步** 用 `AskUserQuestion` 问 3 个问题(规模/设计需求/评审模式,同 hlpm 0.5)
3. **第二步** 按用户回答展开链路(顺序加载 hlpm → hldev → hlrelease → hldeploy)
4. **第三步** 每阶段完成后检查输出物(8 项交付物是否齐全)
5. **第四步** 每阶段完成后询问用户是否继续(避免 Agent 自动推进过深)

## 强制约束(4 条,源 SKILL.md L148-153)

1. **不修改任何子技能的核心流程** — hlpm/hldev/hlrelease/hldeploy/hltest/hlbug 的步骤不变
2. **不做覆盖** — hlchain 不替代上述 6 个技能,只是顺序加载它们
3. **所有"自动门禁"靠 Agent 自觉** — Agent 不会因 hlchain 缺失某阶段而拒绝继续
4. **失败处理** — 任一阶段失败(如 hlpm 被拒收),hlchain 应建议回到前一阶段或终止

## 与其他子技能的关系

| 子技能 | 关系 |
|---|---|
| `hl-flow` | hlchain 是多角色版(产品/开发接力);hl-flow 是单人版(全跑) |
| `hlpm` + `hldev` | hlchain 自动串起;手动 `hlpm` + `hldev` 是手动版 |
| `hlrelease` / `hldeploy` | 仅 hlchain 编排;手动需单独 Skill 调 |
| `hlbug` / `hltest` | 任一阶段都可中断触发 |

## 调用方式

- **有实参**(如 `/hlchain 为登录加短信验证码`): 实参作为整链路需求
- **无实参**: 走第零步需求确认
- **典型耗时**: 半天-3 天(完整从需求到部署)

详见 `hlskills/hlchain/SKILL.md` 完整规范。