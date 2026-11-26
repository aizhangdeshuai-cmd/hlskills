---
name: hlgit
description: Git规范，覆盖Conventional Commits格式（feat/fix/docs/refactor/test/chore/perf）、OMC提交协议（Constraint/Rejected/Confidence/Scope-risk/Not-tested）、分支命名规范（feature/fix/hotfix/release）。Use when 用户需要遵循 Git 规范（Conventional Commits/分支命名/OMC 协议）时调用。
---

# Git 规范

项目已有的分支模型、提交规范和 hooks 优先；与本技能默认值冲突时，沿用项目约定并在交接中注明。

---

## 提交信息格式（Conventional Commits）

```
<type>(<scope>): <subject>

[body]

[OMC trailers]
```

### Type 类型

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug修复 |
| `docs` | 文档变更 |
| `refactor` | 重构（不改变行为） |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖 |
| `style` | 格式（不影响逻辑） |
| `perf` | 性能优化 |
| `ci` | CI/CD变更 |

### 规则
- 主题行使用祈使语气，首字母小写，不超过 50 字符，**不加句号**
- 正文解释 **为什么** 做这个变更，而非做了什么
- 一个提交只做一件事

---

## OMC 提交协议（保留决策上下文）

在提交信息尾部添加以下标记：

```
Constraint: <活跃约束>
Rejected: <备选方案 | 原因>
Confidence: high | medium | low
Scope-risk: narrow | moderate | broad
Not-tested: <已知验证缺口>
```

示例：
```
feat(auth): add OAuth2 login flow

Constraint: Must support both Google and GitHub providers
Rejected: Custom JWT-only approach | increases maintenance burden
Confidence: high
Scope-risk: narrow
Not-tested: Token refresh with expired provider tokens
```

---

## 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 新功能 | `feature/<描述>` | `feature/user-authentication` |
| Bug修复 | `fix/<描述>` | `fix/login-redirect-loop` |
| 紧急修复 | `hotfix/<描述>` | `hotfix/critical-security-patch` |
| 发布 | `release/<版本>` | `release/1.2.0` |

---

## 禁止事项

- **禁止**直接提交到 main 分支
- **禁止**对已推送的共享分支执行 rebase
- 强制推送使用 `--force-with-lease`
- **禁止**跳过 Git hooks（`--no-verify`、`--no-gpg-sign`）
- 建议配置 `/hlhooks` 中的 force push 拦截 hook，自动阻止 `git push --force` 到 main/master

---

## 相关技能
- [hlrelease](../hlrelease/SKILL.md) — 发布流程
- [hlreview](../hlreview/SKILL.md) — 代码审查

## 核对待推历史

用户指定排除范围时，先核实目标远端分支的提交和候选 SHA，再在仓库根目录检查候选差异以及远端基线之后的全部可达提交。下例假设本次排除 tests/ 和所有 ZIP，实际路径按本次授权替换。

```sh
git diff --name-status --no-renames "$remote_sha" "$candidate_sha" -- tests/ ':(glob)**/*.zip'
git log --full-history -m --root --no-renames --format='commit %H' --name-status "$remote_sha..$candidate_sha" -- tests/ ':(glob)**/*.zip'
```

命令成功后读取其输出。新增、修改或改名移入被排除路径的内容，都应定位到首次出现的提交；仅删除远端已存在文件的记录，按本次范围核对。新分支没有远端基线时，以候选 SHA 检查其全部可达历史。发现不该发布的内容时，保留本地工作，基于已确认的基线重新准备候选，再核查和验证。已进入共享历史的内容沿用项目的处理决定。

---

> **路径规范**：本文件涉及的 `knowledge/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
