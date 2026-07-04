---
description: hlskills 测试全流程。Use when 需要测试用例编写、E2E 测试、健康评分。
---

# hltest ── hlskills 测试

加载 `hltest` 子技能(SKILL.md 在 `hlskills/hltest/SKILL.md`),按其流程执行。

**覆盖**: 测试用例 + E2E(Playwright + POM) + QA 三级(Quick / Standard / Exhaustive) + Diff-aware + 健康评分(8 类加权) + 响应式 + 注释截图 + a11y + CI/CD

**QA 三级**:

- **Quick**: 5 分钟健康度速查
- **Standard**: 完整用例覆盖
- **Exhaustive**: 加压 + 渗透式测试

无实参: 走 Quick 级,5 分钟速查当前项目
有实参(如 `/hltest E2E 标准级`): 指定级别和范围