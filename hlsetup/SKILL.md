---
name: hlsetup
description: hlskills 一键安装与部署，支持 Claude Code / Codex / Cursor 等 IDE 的技能分发，将 hlskills 目录安装到目标工具的技能系统。Use when 重新安装 hlskills、在新机器部署、或切换 IDE。通过 /hlsetup 调用。
---

# hlskills 安装与部署

> 属于 `hlskills` 技能系统。一键将 hlskills 安装到目标 AI 编程工具。

---

## 从指定 checkout 安装

从用户选定的 hlskills 仓库根运行 `python3 hlsetup/install.py <平台>`，平台取 `claude`、`codex`、`cursor` 或 `all`。安装器以自身所在 checkout 为来源。Claude 的技能、命令、角色分别链接到 `~/.claude/{skills,commands,agents}`。Codex 使用用户技能目录 `~/.agents/skills/`。Cursor 使用 `~/.cursor/skills/`。[Codex 官方技能目录](https://developers.openai.com/codex/skills/)

```bash
python3 hlsetup/install.py claude
python3 hlsetup/install.py claude --check
```

`--check` 检查缺失、来源冲突和随版本退役的已安装入口，发现问题即返回非零。更新本 checkout 后再次安装即可补新入口并清理旧名。旧版若在宿主专属目录同时保留了指向本 checkout 的总链接与子技能链接，安装器可以接管同名、同源的旧链接。Codex 迁移时先建立共享入口，再撤下 `~/.codex/skills/` 中原属本库的链接。发现其他 checkout 的同名副本时先核对其本地修改，需保留的副本移出发现目录再重试。

运行记录按宿主和 checkout 存于 `~/.local/state/hlskills/`。安装前已有的同源共享入口可直接复用。重新打开宿主的技能列表，核对 `hlpm` 和总入口的实际来源，再按需读取同一 checkout 的角色。

## 卸载

```bash
python3 hlsetup/install.py claude --uninstall
```

卸载会复核归属并移除该宿主已登记且仍指向本 checkout 的链接，包含源文件已删除的旧名。用户替换的文件和借用的共享入口保留。卸载其他平台时替换平台参数。

## 候选包验收

维护者可将候选归档解到空目录，在独立的宿主账户中从解包目录执行上面的安装和 `--check`。检查输出的“技能来源”是否为该解包目录，再重开宿主，核对 `hlskills` 和 `hlpm` 的来源路径。任一入口缺失或指向其他副本时，记录宿主、候选路径和安装器诊断后复验。

## 启用项目知识库 hook

在业务项目目录运行所选 checkout 中的安装脚本：

```bash
bash "/实际仓库路径/hlkb-hooks/install.sh" --dry-run
bash "/实际仓库路径/hlkb-hooks/install.sh" --preset=default
```

安装器按条目合并到项目的 `.claude/settings.local.json`。撤销方法、旧版备份和提交检查范围见 [hlkb-hooks](../hlkb-hooks/SKILL.md)。
