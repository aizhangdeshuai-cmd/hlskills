---
description: hlskills 开发段(15 步,5 阶段,多角色)。Use when 产品交付物已就绪开发即将启动、或调用 hlskills 复杂流程。
---

# hldev ── hlskills 开发段

加载 `hldev` 子技能(SKILL.md 在 `hlskills/hldev/SKILL.md`),按其 5 阶段 15 步执行。

## 流程结构(源 SKILL.md L53-274,完整版)

### 第零阶段:交付物验证(1 步,阻塞点)

- **0** ★ **验证版本目录 + 8 项交付物 + 一致性矩阵**(`executor` 主导)
  - 验证版本一致性(版本号对齐)
  - 验证 8 项交付物齐全(PRD/用例/非功能/矩阵/自检 必出 + 竞品/设计/设计稿 条件出)
  - 验证一致性矩阵(业务规则/状态机/权限/非功能/代码实现追踪 5 矩阵)
  - 缺项 → **拒收**(进入拒收流程,不进入开发)

### 第一阶段:Git 与开发准备(3 步)

- **1** Git 工作区准备(隔离工作区)
- **2** 开发计划(`planner`,任务粒度 = 单步 2-5 分钟)
- **3** 架构决策记录(`architect`,→ knowledge/adr/NNNN-slug.md)

### 第二阶段:开发与审查(4 步)

- **4** 开发(`executor`,TDD 覆盖率 ≥80%)
- **5** 代码审查(`code-reviewer`,按严重/重要/次要分级)
- **6** 前后端联调
- **7** 前后端自测(`executor`)

### 第三阶段:分支收尾(1 步)

- **8** 分支完成(4 选项:本地合并 / 推 PR / 保持原样 / 丢弃;执行 → 清理)

### 第四阶段:测试与审计(4 步)

- **9** 安全审查(`security-reviewer`)
- **10** 测试用例编写(代码层) + 执行 + 总库沉淀 → `knowledge/tests/{module}.md`(`test-engineer` + `qa-tester`)
- **11** 浏览器验证(`qa-tester`)
- **12** 生产审计(`verifier`)

### 第五阶段:交付与发布(3 步)

- **13** 交付验证(`verifier` 创建完成标记,如 knowledge/doc/v{N}/.dev-completed)
- **14** 发布(`hlrelease` 子技能)
- **15** 部署(`hldeploy` 子技能)

## 关键铁律

- **必前置**:hlpm 8 项交付物 + 一致性矩阵(否则步骤 0 拒收)
- **拒收纪律**:版本不一致 / 缺交付物 / 矩阵漏项 → 不进入开发,返回 hlpm 修补
- **TDD + 覆盖率 ≥ 80%**
- **跨版本一致性**:knowledge/doc/{ver}/ 版本快照 + knowledge/ 跨版本累计 双写
- **代码层用例沉淀**:hldev 步骤 10 把验收用例(来自 hlpm)+ 代码层用例合并 → knowledge/tests/{module}.md

## 调用方式

- **无实参**: 走第 0 步读取产品段 `knowledge/doc/v{N}/` 交付物
- **有实参**(如 `/hldev 开始开发 knowledge/doc/v1/ 里的 8 项交付物`): 按实参指定文档路径
- **典型耗时**: 半天-2 天(看交付物复杂度)

详见 `hlskills/hldev/SKILL.md` 完整规范(369 行,含拒收纪律、自检报告模板)。