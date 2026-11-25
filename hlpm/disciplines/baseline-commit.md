# 交付物基线登记

仅交 PRD 或 PRD 与原型时，在已交文档记录版本、确认范围和实际评审状态。完整交接复用这些记录，在步骤 0.6 选定的版本目录创建或更新 `{version_dir}/consistency-rules.md`，从[一致性规则](../consistency-rules.md)取“版本基线表”表头。PRD、设计和用例首次定稿分别登记基线 v1，修订记录关联交付物、基线版本、步骤与证据。

## 项目使用 Git 时

完整交接中，主代理或指定执行者按项目授权为每个交付物基线单独提交一次。提交本次定稿的文档及项目基线表，设计基线包含页面及实际依赖的本地资源。步骤 11 的自检已生成且属于同次变更时也可附上。提交仅包含本基线的文件。

以下为 PRD 首次定稿的示例，`PROJECT` 为业务项目根目录，`VERSION_DIR` 为本次所选版本的绝对路径。示例同样适用于旧目录 `docs/v7`。

```bash
git -C "$PROJECT" add -- "$VERSION_DIR/prd.md" "$VERSION_DIR/consistency-rules.md"
git -C "$PROJECT" commit --only -m "docs(${VERSION_DIR##*/}): baseline PRD v1" -- "$VERSION_DIR/prd.md" "$VERSION_DIR/consistency-rules.md"
```

设计和用例基线使用同样的方式，明确列出本次提交的文件，标题项分别为 `design` 和 `test-cases`。重复执行前先核对表中同一交付物、基线和提交，已有记录直接复用。

## 未能登记或提交

- 基线表缺失或与交付物不一致时，修复记录再通过步骤 9.5。
- 项目明确在 Git 之外管理时只登记项目表，备注管理方式。
- 项目使用 Git 但提交失败时，记录错误及待补动作，保留文档基线和实际提交状态。

[产品流程](../SKILL.md) · [角色边界](role-boundary.md) · [完成前验证](completion-validation.md)
