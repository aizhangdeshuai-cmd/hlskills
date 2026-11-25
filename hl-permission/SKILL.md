---
name: hl-permission
description: 一键授权当前项目目录下所有文件改动（Edit/Write/Bash），免去逐条确认。权限写入项目 .claude/settings.local.json 持久保留，不随窗口关闭失效，需手动执行 /hl-permission --off 或删除对应条目才能撤销。Use when 不想每次文件改动都被询问授权、需要临时提升操作效率。通过 /hl-permission 调用。
---

# 一键项目授权

> 属于 `hlskills` 技能系统。向当前项目目录添加权限白名单，免去逐条操作确认。

> ## ⚠️ 安全警告
>
> 本技能向项目配置写入 Edit、Write、Bash、Read 的 allow 匹配规则。实际免确认范围由宿主的规则匹配、拒绝规则和运行环境决定。宽泛授权涉及以下操作：
> - 可删除任意文件(包括 `git rm`/`rm`/`rm -rf`)
> - 可改写任意文件(包括 `.env` / 凭据 / 配置文件)
> - 可推送任意 commit / tag(包括 force push 到 main)
> - 可执行任意 Bash 命令(包括 `curl | bash`、`sudo`、`dd` 等)
>
> **风险场景**:
> - Agent 被 prompt injection(用户上传的截图/PDF 含恶意指令):此时 Agent 可能破坏仓库或泄露数据
> - 多人协作项目:同事 push 的代码若引入恶意逻辑,后续 Agent 行为不可控
> - CI / 生产环境脚本:Agent 可能改写部署配置导致线上事故
>
> **强烈建议**:
> 1. **配合 `hlhooks/SKILL.md` 的 hook 模板一起启用**(危险命令拦截 + 敏感文件保护 + force push 拦截)
> 2. **仅在临时任务中使用**,完成即 `--off`
> 3. **生产敏感项目**(凭据 / 客户数据 / 公开仓库)请**不要使用**
> 4. **多人协作项目**请改为**单步手动确认**,不要一键放开

---

## 开启与撤销

从目标项目（含子目录）调用本技能同目录的 `permissions.py`。使用加载的技能文件所在目录解析脚本路径。两次调用均从 Git 查询根目录，非 Git 目录使用当前工作目录。

```bash
python3 "/实际技能目录/hl-permission/permissions.py"
python3 "/实际技能目录/hl-permission/permissions.py" --off
```

第一条开启项目的四条匹配规则，第二条撤销。状态保存在项目的 `.claude/.hl-permission.json`，用于保留启用前已有的同名权限。旧版没有该记录，直接执行 `--off` 时沿用旧版行为，移除本项目的四条精确匹配规则。

## 说明

- **权限范围**：当前 git 仓库根目录（或当前目录）下的所有文件 Edit / Write / Read + 目录相关的 Bash 命令
- **持久性**：写入项目 `.claude/settings.local.json`，建议将本地设置和授权状态文件加入项目的 Git 忽略规则
- **恢复**：执行 `/hl-permission --off` 或直接删除 `.claude/settings.local.json` 中的相应条目
- **安全**：仅授权当前项目，不影响其他项目的权限策略

> 这是临时提效工具，生产敏感项目请谨慎使用。

---

> **路径规范**：本文件涉及的 `knowledge/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
