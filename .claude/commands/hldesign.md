---
description: hlskills UI/UX 设计规范。Use when 需要设计规范、无障碍要点检查。
---

# hldesign ── hlskills UI/UX 设计

加载 `hldesign` 子技能(SKILL.md 在 `hlskills/hldesign/SKILL.md`),按其规范执行。

**覆盖**: 设计依据优先级(有设计文档严格遵循 vs 无设计文档先询问用户偏好 + 推导设计系统) + 5 态覆盖(默认 / 悬停 / 激活 / 聚焦 / 禁用) + 无障碍要点(详见 `hla11y`) + 行业→设计系统映射 + 反模式库 + DEV-NOT-FOR-PROD 白名单(单一可信源,设计与实现分离)

**与 hla11y 关系**: hldesign 包含通用设计规范;hla11y 专攻 WCAG 2.2 AA 无障碍

无实参: 询问用户需求类型 + 是否有现有设计文档
有实参(如 `/hldesign 设计登录页`): 进入设计 5 态检查