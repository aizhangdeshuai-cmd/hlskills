---
description: hlskills 技能写作方法论。Use when 编写/编辑/评审 hlskills 子技能 SKILL.md。
---

# hlwrite-skill ── hlskills 技能写作方法论

加载 `hlwrite-skill` 子技能(SKILL.md 在 `hlskills/hlwrite-skill/SKILL.md`),按其规范写新技能。

**3 条核心原则**:

1. **可预测性 > 完整性**(具体到可执行,不写"视情况")
2. **小而可组合,不接管流程**(只管自己段 + 交接段)
3. **可验证**(grep / 文件存在 / 退出码检查)

**结构规范**: frontmatter(name + description + Use when) → 能力边界声明 → 角色映射 → 流程步骤 → 硬性关卡 → 不在本技能范围 → 验收 checklist

**10 项评审 checklist**: 见 SKILL.md §评审 checklist

无实参: 走评审 checklist 检查现有 SKILL.md
有实参(如 `/hlwrite-skill 新建 hltailwind 技能`): 进入新技能写作流程