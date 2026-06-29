---
name: hlrelease
description: 发布流程规范，覆盖版本号确定（语义化版本）、变更日志生成、预发布清单（CI绿/测试通过/版本号/变更日志/无严重问题）、标签创建与推送。Use when 用户需要发布版本（版本号/变更日志/预发布清单/标签推送）时调用。
---

# 发布流程

> ## ⚠️ 流程纪律的执行机制
>
> 本流程的"硬性关卡""返回上一步""强同步规则"是 markdown 文本纪律,Claude Code 不会机械地强制执行。Agent 加载后会**自觉遵守**,但如 Agent 模型弱或 prompt 冲突,关卡可能失效。
>
> **真实约束**:文档本身 + Agent 自觉 + 用户手动打断。
> **不是**:Claude Code runtime hook 拦截 + 状态机门禁。
>
> 如发现 Agent 在第 X 步没停下来等你确认 / 直接跳过第 Y 步 / 没返回上一步重做,请**手动打断**让它重读 SKILL.md 对应章节。
>
> 详细能力边界见仓库 `README.md` 「⚠️ 能力边界声明」段。

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

## 交接段

> 本技能被 `hlchain` 编排为"全流程第 3 阶段 (可选)"。完成本技能后, Agent 应:
>
> 1. 验证 `CHANGELOG.md` 已更新 + git tag 已推送
> 2. 询问用户: "发布完成, 是否部署到生产 (hldeploy)?"
> 3. 用户确认后, 调 `Skill hldeploy "..."` 进入下一阶段
>
> **hldev 步骤 14 已内置 tag 推送**, 所以单独调用 hlrelease 仅在需要补 changelog 时有必要。hldev + hlrelease 二选一即可。
>
> 如果用户是**单独调用本技能**, 此交接段不触发, 由用户决定下一步。

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
