# 交付物基线登记

在已交文档登记版本、确认范围、参与者和实际结论。正式交接使用所选目录的 `consistency-rules.md` [版本基线表](../consistency-rules.md)，分别登记 PRD、设计和测试材料的首次定稿及修订。

| 基线 | 本次提交应包含的变更 |
|---|---|
| PRD | 正文、基线表及本次定稿的全部产品文档。按附录逐项选取真实文件，例如已选的数据或接口分册。 |
| 原型 | 本轮页面、实际依赖的本地资源、实测记录、更新过的 PRD 引用和基线表。 |
| 测试 | 实际生成的验收标准和用例，以及补上 TC、附录链接的正文和基线表。客户固定目录在约定位置更新验收索引。 |

项目授权 Git 提交时逐一列出本轮定稿文件。例如，仅选了数据分册的 PRD 基线可用以下命令。若同时选了接口分册，在同一份文件清单加入该文件。项目另有已选产品文档也按实际清单追加。

```bash
files=("$VERSION_DIR/prd.md" "$VERSION_DIR/data-requirements.md" "$VERSION_DIR/consistency-rules.md")
git -C "$PROJECT" add -- "${files[@]}"
git -C "$PROJECT" commit --only -m "docs(${VERSION_DIR##*/}): baseline PRD v1" -- "${files[@]}"
```

提交前核对实际差异，重交前核对已有基线。使用其他版本管理方式时登记实际位置。记录或提交失败时保留错误和待补动作，补齐后再确认交接。
