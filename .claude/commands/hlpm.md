---
description: hlskills 产品段(多角色协作 27 步流程)。Use when 用户提出新需求且产品/开发是两角色、或调用 hlskills 复杂流程。
---

# hlpm ── hlskills 产品段

加载 `hlpm` 子技能(SKILL.md 在 `hlskills/hlpm/SKILL.md`),按其 27 步流程处理用户需求。

**Claude Code 实际触发方式**(本文件只是 /hlpm slash 的入口薄壳):

1. **优先**: 检测本命令后的实参(如 `/hlpm 为登录加短信验证码`),把它作为需求传入 hlpm 子技能的第 0 步
2. **无实参**: 走 hlpm 第 0 步项目上下文加载 → 第 0.5 步规模评估(轻量/标准/复杂)
3. **跨平台降级**: Codex / Cursor 见 hlskills README "平台支持分级"

**关键约束**(取自 hlpm 子技能铁律):

- 产品段**绝不修改代码**,仅产出文档(PRD/用例/验收/非功能)
- 与 `hldev` 配套使用:产品交付物评审通过后交接开发
- 集中评审模式含 5 角色:analyst / planner / architect / designer / executor

详见 `hlskills/hlpm/SKILL.md` + `hlskills/SKILL.md` 索引。
