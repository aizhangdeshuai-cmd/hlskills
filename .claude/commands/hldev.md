---
description: hlskills 开发段(多角色 15 步)。Use when 产品交付物已就绪开发即将启动、或调用 hlskills 复杂流程。
---

# hldev ── hlskills 开发段

加载 `hldev` 子技能(SKILL.md 在 `hlskills/hldev/SKILL.md`),按其 15 步执行。

**前置**: 产品段 hlpm 已交付 8 项产物(5 必出 + 3 条件出)
**15 步**: 版本一致性验证 + 拒收检查 → Git → 开发 → 审查 → 联调 → 测试 → 审计 → 发布 → 部署
**与 hlpm 关系**: 必须 hlpm 先有产物,hldev 才能启动

无实参: 读取产品段 `docs/v{N}/` 交付物
有实参(如 `/hldev 开始开发 docs/v1/ 里的 8 项交付物`)按实参指定文档路径