# 随库角色

按实际任务选择角色。每个角色的职责、工具范围和交付要求见链接。

| 角色定义 | 职责 |
|---|---|
| [analyst](../agents/analyst.md) | 需求分析、PRD 起草与评审（只读） |
| [planner](../agents/planner.md) | 按验收结果规划复用、修改和新增，交付可实施步骤 |
| [designer](../agents/designer.md) | 新视觉探索、可操作原型及确认设计的还原 |
| [executor](../agents/executor.md) | 实施代码变更并按 AC 移交验证结果和未完成项 |
| [architect](../agents/architect.md) | 系统架构、根因分析（只读） |
| [code-reviewer](../agents/code-reviewer.md) | 代码质量审查（只读） |
| [security-reviewer](../agents/security-reviewer.md) | 安全漏洞审查（只读） |
| [test-engineer](../agents/test-engineer.md) | 测试策略与用例编写 |
| [qa-tester](../agents/qa-tester.md) | 浏览器、API、CLI 验收执行及逐用例证据 |
| [verifier](../agents/verifier.md) | 按阶段验证交付证据，区分通过、失败与待验证 |
| [explore](../agents/explore.md) | 追踪定义与调用，交接可跨 checkout 核对的源码证据（只读） |
| [debugger](../agents/debugger.md) | 根因分析与故障诊断 |
| [tracer](../agents/tracer.md) | 对照竞争解释和反证，移交能区分原因的下一步核验（只读） |
| [writer](../agents/writer.md) | 文档与内容生成 |
| [git-master](../agents/git-master.md) | 原子提交策略与历史管理 |
| [scientist](../agents/scientist.md) | 数据分析与统计推理（只读） |
| [code-simplifier](../agents/code-simplifier.md) | 简化指定代码，按相同输入复验前后行为 |
| [critic](../agents/critic.md) | 计划/设计的多角度挑战评审（只读） |
| [document-specialist](../agents/document-specialist.md) | SDK/API/框架文档查找（只读） |

## 什么情况下交给下一个人

- **需求到实现。** 业务结果有两个合理解释，由 analyst 给出能区分它们的具体输入、结果和决定人。业务规则已确认，planner 交可实施的变更和验证方法，executor 交实际实现及证据。小改动可由当前执行者直接完成已获委派的工作。
- **设计到验收。** designer 交同一版本上可重放的页面、状态和操作。test-engineer 将确认结果写成断言，qa-tester 在候选上操作并交原始读数，verifier 对同版证据作结论。有现成用例时可直接交给执行者。
- **故障定位。** debugger 接可复现的问题并保留现场。若多个原因能解释同一症状，tracer 交能区分它们的下一项观察。观察指向模块边界或共享契约时，architect 再判断设计取舍。
- **代码审查。** code-reviewer 核对变更与需求，涉及身份、数据或凭证时可把相应范围交 security-reviewer。需要独立签核时，写入者登记复核者针对该版本给出的结论。
