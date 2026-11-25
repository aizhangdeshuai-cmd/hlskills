---
name: hlrelease
description: 将版本、变更日志、通过的 CI 与 Git 标签绑定到同一提交，核实远端发布结果并交给部署。Use when 用户需要发布版本、推送标签或核对发布记录时调用。
---

# 发布流程

1. **确定发布目标。** 从项目配置和最近一次发布确定版本（不兼容改动升主版本、兼容功能升次版本、兼容修复升补丁）。确认目标仓库、允许发布的分支、版本来源和远端。沿用 [hldev](../hldev/SKILL.md) 交付的候选提交及未结风险。
2. **形成候选提交。** 更新项目版本与 CHANGELOG，核对本次新增条目和实际变更，把发布文件纳入提交。以 `git rev-parse HEAD` 记录完整 SHA；用 `git show "$RELEASE_SHA:CHANGELOG.md"` 核对该提交的本次发布条目。分支合并、冲突处理、改版本或补日志产生了新 SHA 时，针对新 SHA 重新取得必需测试、CI 和适用的 UAT 结果。核对适用的数据库迁移与回滚、未解决的严重审查意见。
3. **验证候选。** 在业务仓库根运行本技能的 [verify-release.py](verify-release.py)。从项目必需的 CI 工作流读取实际运行记录，逐个核对工作流名称和证据链接是否覆盖发布策略。脚本读取一个记录或记录数组；每项应含真实的 `headSha`、`status` 和 `conclusion`。GitHub Actions 可用 `gh run view "$RUN_ID" --json workflowName,headSha,status,conclusion,url` 导出，其他平台从其运行结果映射等价字段。按项目发布策略逐个传入 `--require-workflow`；以下示例假设只有一个必需工作流。每个必需名称应只对应候选 SHA 的一份最终结果。重跑时取最近一次尝试；同名但不同的必需任务以配置路径或任务 ID 作为唯一名称，同时将导出的 workflowName 映射成该标识。CI 缺失、失败、仍在运行或与候选 SHA 不符即暂停。可在已验证的候选工作树中使用以下命令，各变量取本次实际值。

   ```sh
   python3 "$HLRELEASE_DIR/verify-release.py" --tag "$TAG" --commit "$RELEASE_SHA" \
     --version-file "$VERSION_FILE" --ci "$CI_EVIDENCE" --require-workflow "$REQUIRED_WORKFLOW"
   ```

   脚本读取候选提交中的文件，支持 package.json、pyproject.toml 的 project.version（Python 3.11+）及纯文本版本文件。使用其他格式或动态版本的项目，从指向候选提交的干净工作树运行项目已有版本命令，将其真实输出作为 `--source-version`；已有上一发布时带上 `--previous-tag "$PREVIOUS_TAG"` 检查本次日志确有改动；首次发布时直接核对首个条目。CHANGELOG 位于其他路径时使用 `--changelog`。

   默认识别 Markdown 版本标题（如 `## [1.2.3] - 日期` 或 `# Release v1.2.3`）。项目使用其他版本标题格式时，可传入完整行模板，例如 `--changelog-entry '发布 {tag}'`。对于版本及说明同处一行的格式，将实际说明标成 `{note}`，例如 `--changelog-entry '{tag} | {note}'`。纯标题模板读取其下的正文。空勾选、TODO、TBD 等独立占位会被标为缺失。

   在本版章节内写清用户可见的变更，项目允许空发布时写明具体原因及可追溯依据。检查器会核对当前章节有正文，跳过分类标题、注释、链接定义和代码示例。发布者对照实际改动核实说明及依据，并核对 CI 记录来源与必需工作流清单。
4. **给候选打标签。** 确认第 3 步成功后执行 `git tag -a "$TAG" "$RELEASE_SHA" -m "Release $TAG"`。重复发布时，先核对已有标签的对象和提交。仅在完全吻合时复用；发现同名冲突就报告并停止。
5. **推送与交接。** 向用户展示远端、版本、完整 SHA、日志摘要和必需 CI 结果，按对应授权推送该标签。已获授权的部分可直接执行。

   ```sh
   TAG_OBJECT=$(git rev-parse --verify "refs/tags/$TAG") &&
     test "$(git rev-parse --verify "$TAG_OBJECT^{commit}")" = "$RELEASE_SHA" &&
     git push -- "$REMOTE" "$TAG_OBJECT:refs/tags/$TAG" &&
     python3 "$HLRELEASE_DIR/verify-release.py" --tag "$TAG" --commit "$RELEASE_SHA" \
       --version-file "$VERSION_FILE" --ci "$CI_EVIDENCE" --require-workflow "$REQUIRED_WORKFLOW" --remote "$REMOTE"
   ```

   两次检查使用相同的版本与日志参数。发布由标签触发时，继续核对该提交的发布任务成功、预期产物存在；失败或未结束时记为发布未完成。同名远端标签冲突需人工决定，禁止强推覆盖。记录远端、标签、完整 SHA、CI 与发布记录，以及存在构建产物时的不可变标识（如镜像摘要）。由 [hlchain](../hlchain/SKILL.md) 或用户将这份记录交给 [hldeploy](../hldeploy/SKILL.md)。
