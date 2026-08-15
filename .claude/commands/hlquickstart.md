---
description: hlskills 5 分钟快速上手演示(看一眼 + Mock Bug + Mock 需求)。Use when 第一次用 hlskills、给团队成员培训、或想快速看 AI 按文档一步步做事是什么体验。
---

# hlquickstart ── hlskills 5 分钟上手

加载 `hlquickstart` 子技能(SKILL.md 在 `hlskills/hlquickstart/SKILL.md`),按其 3 步演示。

## 流程结构(源 SKILL.md,完整版)

### 第 1 步:看一眼(30 秒)

- 走读 hlskills 主入口 SKILL.md
- 列出 26 个子技能 / 19 个 Agent
- 强调能力边界(无 runtime 强制,靠 Agent 自觉)

### 第 2 步:Mock Bug 演示 hlbug(2 分钟)

演示走 7 步(简化自 hlbug 14 步):

1. **加载已有文档** — 跳过(无 `.hl/memory/`)
2. **Bug 分析** — 用 `debugger` agent 角色扮演,描述"白屏可能原因:JS 错误 / 网络失败 / 路由错误 / 状态管理 bug"
3. **根因定位** — `debugger` 主导,提供"证据收集 → 根因分析 → 假设验证"四阶段框架
4. **修复方案** — `debugger` + `architect` 给出 3 个候选方案,每个含预期工作量 + 风险

### 第 3 步:Mock 需求演示 hlpm 前 7 步(2.5 分钟)

演示走 7 步(简化自 hlpm 13 步):

1. **加载已有文档** — 跳过
2. **需求分析** — 用 `analyst` 角色,梳理"导出 CSV"涉及的:筛选条件、分页、列选择、文件名规则
3. **竞品分析** — 用 `AskUserQuestion` 问你"是否有参考产品?"
4. **PRD 编写** — 生成一份 5-10 行的 mock PRD(不写完整 6 大模块,只为演示)
5. **PRD 评审** — 5 方角色扮演(analyst/architect/designer/test-engineer/executor)各给 1 段意见
6. **UI/UX 设计** — 生成一份 mock HTML 设计稿(灰度布局,只要 1 个区块)
7. **用户确认设计** — **停在硬性关卡**,等你说"确认"

## 演示结束后:5 分钟感受总结

复盘你看到的:
- AI 真的**按文档一步步做**,不是"看起来聪明地乱做"
- 多 Agent 协作:每个角色只负责自己那段(analyst 不写代码、designer 不写 PRD)
- 阻塞点:**真等用户确认**(不在背后偷偷决定)
- 文档纪律:**每一步都有产出**,可追溯

## 不做的事(源 SKILL.md L113-124)

- 不替代任何子技能(只演示前 7 步/前 4 步)
- 不写实际代码、不修改 knowledge/ 或老 docs/
- 不评估你的项目质量
- 不配置 hooks(那是 hlkb-hooks 的事)

## 调用方式

- **无实参**: 启动 5 分钟演示(按 3 步走)
- **真用这个库第一次必跑**

详见 `hlskills/hlquickstart/SKILL.md` 完整规范。