---
description: 一键授权当前项目目录下所有文件改动(Edit/Write/Bash/Read),免去逐条确认。⚠️ 等效 --dangerously-skip-permissions(仅本项目)。Use when 不想每次文件改动都被询问授权。
---

# hl-permission ── 一键项目授权

加载 `hl-permission` 子技能(SKILL.md 在 `hlskills/hl-permission/SKILL.md`),向**当前项目**的 `.claude/settings.local.json` 加 4 条权限白名单。

## 加的 4 条权限

| 权限 | 作用 |
|---|---|
| `Edit(<项目根>/**)` | 编辑当前项目任意文件,免确认 |
| `Write(<项目根>/**)` | 写入当前项目任意文件,免确认 |
| `Bash(*:<项目根>*)` | 在当前项目目录执行任意 Bash,免确认 |
| `Read(<项目根>/**)` | 读当前项目任意文件,免确认 |

## ⚠️ 安全警告(必读)

**等效 Claude Code 项目级 `--dangerously-skip-permissions`**。启用后,Agent 在你**当前项目**任意操作不再询问:

- ❌ 可删除任意文件(`git rm`/`rm`/`rm -rf`)
- ❌ 可改写任意文件(`.env` / 凭据 / 配置)
- ❌ 可 force push main
- ❌ 可跑 `curl | bash` / `sudo` / `dd`

**强烈建议**:
1. **配合 hlkb-hooks 一起用** — `bash hlskills/hlkb-hooks/install.sh`(危险命令拦截 + 敏感文件保护 + force push 拦截)
2. 仅临时任务用,完成即 `--off`
3. 生产敏感项目(凭据 / 客户数据 / 公开仓库)**不要用**
4. 多人协作项目改单步手动确认,**不要一键放开**

## 调用方式

- **开启**:`/hl-permission` → 4 条权限写入 `~/.claude/settings.local.json`,**持久保留**
- **关闭**:`/hl-permission --off` → 删 4 条权限
- **手改**:编辑 `<项目根>/.claude/settings.local.json`,删 `Edit/Write/Bash/Read` 记录

## 关键诚实点

按 CLAUDE.md #12 标注:hl-permission 的 `--dangerously-skip-permissions` 行为**没运行时强制**(跟 hlskills 所有纪律一样),需要 Agent 自觉 + 用户手动打断。**配合 hlkb-hooks 装是当前最稳组合**(已在你 ehr 项目实装)。

详见 `hlskills/hl-permission/SKILL.md` 完整规范。