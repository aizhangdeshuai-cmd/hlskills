---
name: hlrelease
description: 发布流程规范，覆盖版本号确定（语义化版本）、变更日志生成、预发布清单（CI绿/测试通过/版本号/变更日志/无严重问题）、标签创建与推送。Use when 用户需要发布版本（版本号/变更日志/预发布清单/标签推送）时调用。
---

# 发布流程

> 属于 `project-dev-workflow` 技能系统的一部分。参考 `release` 技能。

## 通用纪律

每个步骤完成后必须验证，证据先于断言。

🚨 **发布前用户确认（硬性关卡）**
- 步骤1-4（版本号→变更日志→清单→标签）可自动执行
- **步骤5（推送发布）前必须等待用户确认**，向用户展示：
  - 版本号（vX.Y.Z）
  - 变更日志摘要
  - 预发布清单检查结果
  - 当前分支
- 用户确认后方可执行 git push，**严禁自动推送**

---

## 发布流程

### 1. 版本号确定
按语义化版本（MAJOR.MINOR.PATCH）自动检测版本源：
- `package.json` → `version` 字段
- `pyproject.toml` → `[project] version`
- 其他语言/框架对应文件

升级规则：
- **MAJOR** — 不兼容的 API 变更
- **MINOR** — 向后兼容的功能新增
- **PATCH** — 向后兼容的 Bug 修复

### 2. 变更日志生成
从 Git 提交历史（Conventional Commits）自动生成 CHANGELOG，按类型分组：feat / fix / refactor / perf 等。

### 3. 预发布清单
全部通过后方可发布：
- [ ] CI 全部绿色
- [ ] 全部测试通过（单元+集成+E2E）
- [ ] 版本号已应用到所有文件
- [ ] 变更日志已更新
- [ ] 无未解决的严重/重要审查问题
- [ ] 数据库迁移已测试且可回滚

### 4. 创建标签
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 5. 推送发布
```bash
# 安全检查：确认在正确分支上
BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ] && echo "⚠️ 当前不在 main/master 分支（当前：$BRANCH）"

git push origin vX.Y.Z
```
推送标签触发 CI 发布流程。

---

## 关联命令
- `/hldeploy` — 部署规范
- `/hlreview` — 审查机制
- `/hlgit` — Git规范

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
