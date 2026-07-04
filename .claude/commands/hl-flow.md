---
description: hlskills 单人/小团队全流程(28 步自跑)。Use when 新需求开发、单人跑完整流程。
---

# hl-flow ── hlskills 单人全流程

加载 `hl-flow` 子技能(SKILL.md 在 `hlskills/hl-flow/SKILL.md`),按其 28 步单人全流程跑完整路径(加载上下文 → 需求 → 竞品 → PRD → 设计 → 确认 → 测试 → Git → 计划 → ADR → 开发 → 审查 → 联调 → 自测 → 分支 → 安全 → 测试 → 浏览器 → 审计 → 交付 → 用户确认发布 → 用户确认部署)。

**与 hlpm + hldev 对比**:

- `hl-flow` = 单人/小团队(一次性跑完)
- `hlpm` + `hldev` = 多角色协作(产品段 + 开发段接力)
- `hlchain` = 跨阶段编排(Agent 按文档顺序自动加载 hlpm → hldev → hlrelease → hldeploy)

无实参走第 0 步加载上下文,有实参(如 `/hl-flow 为登录加短信验证码`)作为需求输入。