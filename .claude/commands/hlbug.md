---
description: hlskills Bug 修复(14 步)。Use when 用户报 Bug、线上排查、系统调试。
---

# hlbug ── hlskills Bug 修复

加载 `hlbug` 子技能(SKILL.md 在 `hlskills/hlbug/SKILL.md`),按其 14 步流程。

**14 步**: 定位 → Git 工作区 → 修复 → 审查 → 回归 → 验证 → 分支 → 交付
**融合**: gstack `/investigate` 四阶段(Investigation / Analysis / Hypotheses / Implementation)

无实参: 走第 0 步定位(需要用户描述 Bug 现象)
有实参(如 `/hlbug 用户反馈登录页 500`)按实参作为 Bug 报告输入