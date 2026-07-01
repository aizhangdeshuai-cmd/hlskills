# 版本基线表的 commit 流程

> 本文件: `hlpm/disciplines/baseline-commit.md`
> 适用范围: hlpm 流程(版本交付物管理)

---

## 触发位置

PRD / 设计 / 测试用例任一基线版本 v1 登记到 `consistency-rules.md` 的版本基线表时,**必须 commit**。

---

## Commit 规范

- **提交方**: 主 agent 或 `planner` 执行(由 hldev/git-master 协作)
- **Commit 格式**: `docs(vX): baseline {PRD|design|test-cases} v1` (例:`docs(v1): baseline PRD v1`)
- **提交粒度**: 每个基线版本单独 commit, 不合并
- **附带内容**:
  - PRD 文档本身(`prd.md` / `design/*.html` / `test-cases.md`)
  - `consistency-rules.md` 版本基线表的对应行
  - 可选: `handoff-self-check.md` (步骤 11 才生成)
- **不应包含**: `.ts` / `.js` 等源代码(角色边界铁律)

---

## 示例

```bash
git add docs/v1/prd.md docs/v1/consistency-rules.md
git commit -m "docs(v1): baseline PRD v1" -m "由 analyst 主导生成,产品段第 4 步登记基线版本 v1。"
```

---

## 失败处理

- `consistency-rules.md` 缺失 → 阻塞 9.5 通过
- commit 失败(如 git 未初始化) → 警告但不阻塞(允许在交付物阶段手动补 commit)

---

## 项目级覆盖

如项目明确表示"ehr 本身不进 git" 等特殊情况,**允许跳过 commit**, 仅登记 `consistency-rules.md` 版本基线表(基线表本身作为流程记录), 不实际 commit。

---

## 关联

- SKILL.md: `./SKILL.md`
- 角色边界铁律: `./role-boundary.md`
- 完成前验证: `./completion-validation.md`