---
name: hlsetup
description: hlskills 一键安装与部署，支持 Claude Code / Codex / Cursor 等 IDE 的技能分发，将 hlskills 目录安装到目标工具的技能系统。Use when 重新安装 hlskills、在新机器部署、或切换 IDE。通过 /hlsetup 调用。
---

# hlskills 安装与部署

> 属于 `hlskills` 技能系统。一键将 hlskills 安装到目标 AI 编程工具。

---

## 安装流程

```bash
# 1. 检测当前环境
echo "=== 检测环境 ==="
echo "OS: $(uname -s)"
echo "Shell: $SHELL"

# 2. 检测已安装的 AI 工具
CLAUDE_SKILLS=""
CODEX_SKILLS=""
CURSOR_SKILLS=""
[ -d ~/.claude/skills ] && CLAUDE_SKILLS=~/.claude/skills && echo "✅ Claude Code"
[ -d ~/.codex/skills ] && CODEX_SKILLS=~/.codex/skills && echo "✅ Codex CLI"
[ -d ~/.cursor/skills ] && CURSOR_SKILLS=~/.cursor/skills && echo "✅ Cursor"
```

---

## 项目级 hooks 一键安装(知识库强同步)

**`hlskills` 安装到工具** ≠ **项目用上 hooks**。要把"代码改动→knowledge/ 同步"机械化,需要在目标项目里跑:

```bash
cd <目标项目根>          # 比如 ~/work/my-app
bash <hlskills 仓库>/hlkb-hooks/install.sh              # 通用 Web 项目
# 或
bash <hlskills 仓库>/hlkb-hooks/install.sh --preset=java  # Java/Spring Boot 项目
```

详见 `hlkb-hooks/SKILL.md`。安装后:

- **PreToolUse**: `git commit` 漏同步时 harness 真实 exit 2 阻断
- **PostToolUse**: 改完接口/db/枚举/错误码/测试立即 stdout 提示
- **哨兵 `.hlskills`**: 只对 hlskills 涉及的项目生效(其他项目零干扰)
- **可绕过**: `git commit --no-verify` 或 commit message 加 `[skip-kb-sync]`

> 注:本节先于"Claude Code 安装"展示,是因为**装到项目**比**装到 IDE** 优先级更高 ── 没有 hooks 强行同步,`hlkb` 知识库很易漂。

---

## Claude Code 安装

```bash
# 创建 hlskills 技能符号链接
HL_SRC=~/.agents/skills/hlskills

for skill_dir in "$HL_SRC"/hl*/; do
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] && \
    ln -sf "$skill_dir" ~/.claude/skills/"$name"
done

# 总入口
ln -sf "$HL_SRC" ~/.claude/skills/hlskills

# slash commands(让 /hlpm /hldev /hlchain 等真能用)
mkdir -p ~/.claude/commands
if [ -d "$HL_SRC/.claude/commands" ]; then
  cp "$HL_SRC"/.claude/commands/*.md ~/.claude/commands/ 2>/dev/null && \
    echo "✅ slash commands: $(ls ~/.claude/commands/hl*.md 2>/dev/null | wc -l) 个(/hlpm /hldev /hlchain /hlquickstart /hlbug ...)"
fi

echo "✅ Claude Code 安装完成: $(ls ~/.claude/skills/hl* | wc -l) 个技能"
```

---

## Codex CLI 安装

```bash
# Codex 使用相同技能目录格式
HL_SRC=~/.agents/skills/hlskills

mkdir -p ~/.codex/skills

for skill_dir in "$HL_SRC"/hl*/; do
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] && \
    ln -sf "$skill_dir" ~/.codex/skills/"$name"
done

ln -sf "$HL_SRC" ~/.codex/skills/hlskills
echo "✅ Codex CLI 安装完成"
```

---

## Cursor 安装

```bash
# Cursor 使用 .cursorrules 和 .cursor/skills/
HL_SRC=~/.agents/skills/hlskills

mkdir -p ~/.cursor/skills

for skill_dir in "$HL_SRC"/hl*/; do
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] && \
    ln -sf "$skill_dir" ~/.cursor/skills/"$name"
done

ln -sf "$HL_SRC" ~/.cursor/skills/hlskills
echo "✅ Cursor 安装完成"
```

---

## 一键全部安装

```bash
#!/bin/bash
HL_SRC=~/.agents/skills/hlskills

# Claude Code
if [ -d ~/.claude/skills ]; then
  for d in "$HL_SRC"/hl*/; do
    n=$(basename "$d")
    [ -f "$d/SKILL.md" ] && ln -sf "$d" ~/.claude/skills/"$n"
  done
  ln -sf "$HL_SRC" ~/.claude/skills/hlskills
  echo "✅ Claude Code: $(ls ~/.claude/skills/hl* 2>/dev/null | wc -l) skills"
fi

# Codex
if [ -d ~/.codex ]; then
  mkdir -p ~/.codex/skills
  for d in "$HL_SRC"/hl*/; do
    n=$(basename "$d")
    [ -f "$d/SKILL.md" ] && ln -sf "$d" ~/.codex/skills/"$n"
  done
  ln -sf "$HL_SRC" ~/.codex/skills/hlskills
  echo "✅ Codex: $(ls ~/.codex/skills/hl* 2>/dev/null | wc -l) skills"
fi
```

---

## 卸载

```bash
for dir in ~/.claude/skills/hl* ~/.codex/skills/hl* ~/.cursor/skills/hl*; do
  rm -f "$dir" 2>/dev/null
done
echo "✅ hlskills 已卸载"
```

---

## 验证

安装后执行：

```bash
# 确保 hlskills 总入口可用
ls ~/.claude/skills/hlskills/SKILL.md && echo "✅ 总入口就绪"

# 确保至少核心技能可用
for skill in hlpm hldev hlbug hllegacy hlrefactor hltest; do
  [ -L ~/.claude/skills/$skill ] && echo "✅ $skill" || echo "❌ $skill"
done

# 确保 Agent 目录存在
ls ~/.agents/skills/hlskills/agents/ | wc -l | xargs echo "Agent 数量:"
```

---

## 一键安装(Claude Code)实际效果

```bash
$ cd <目标项目根>
$ bash <hlskills 仓库>/hlkb-hooks/install.sh --preset=java
📁 项目根: <目标项目根>
  ✓ 放 .hlskills 哨兵
  ✓ 备份原 settings 到 settings.local.json.hlkb-hooks.bak
  · preset: java
  ✓ 渲染 hook command 完成 (1731 + 861 字节)
  ✓ hooks 已写入 settings.local.json
🔍 验证...
  ✓ JSON 格式合法
  ✓ PreToolUse matcher : Bash
  ✓ PostToolUse matcher: Write|Edit|MultiEdit
  ✓ PreToolUse cmd     : 1731 字节
  ✓ PostToolUse cmd    : 861 字节
  ✓ .hlskills 哨兵已放
  ✓ 备份存在: settings.local.json.hlkb-hooks.bak
✅ 安装完成。
```

---

> **路径规范**：本文件涉及的 `knowledge/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
