---
description: hlskills 全流程编排(6 阶段)。Use when 一次跑完需求→开发→测试→发布→部署全链路,而不是手动一次次调各技能。
---

# hlchain ── hlskills 全链路编排

加载 `hlchain` 子技能(SKILL.md 在 `hlskills/hlchain/SKILL.md`),按其 6 阶段跑完整链路。

**6 阶段**:

1. `hlpm`(产品段 27 步)
2. `hldev`(开发段 15 步)
3. `hlrelease`(发布)
4. `hldeploy`(部署)
5. 过程中调 `hlbug`(Bug 修复)
6. 过程中调 `hltest`(独立测试)

**优势**: Agent 自动按文档顺序加载各技能,无需手动一次次调用
**适合**: 新需求从 0 到上线完整跑一遍;而不是"我只想单独跑某段"

无实参: 走第 0 步需求确认
有实参(如 `/hlchain 为登录加短信验证码`)作为整链路的需求输入