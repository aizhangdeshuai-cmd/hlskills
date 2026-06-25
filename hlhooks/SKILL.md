---
name: hlhooks
description: Claude Code hooks 配置模板，提供推荐的安全/质量/自动化 hooks 配置（提交前检查/危险命令拦截/工具调用后验证）。Use when 配置 hooks、添加自动化检查、或提到"hooks"、"自动化"、"提交前检查"。通过 /hlhooks 调用。
---

# Hooks 配置模板

> 属于 `hlskills` 技能系统。提供推荐的 Claude Code `settings.json` hooks 配置。

---

## 配置位置

- 用户级：`~/.claude/settings.json`
- 项目级：`.claude/settings.local.json`

项目级优先于用户级。

---

## 推荐配置

### 安全 Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": "danger-commands",
        "description": "拦截危险命令"
      },
      {
        "matcher": "Write",
        "hook": "env-file-protect",
        "description": "防止覆盖 .env 文件"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hook": "verify-output",
        "description": "命令执行后验证输出"
      }
    ]
  }
}
```

### 危险命令拦截

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf /|git push --force origin main|DROP TABLE|DROP DATABASE|shutdown -h now' && echo '🚨 危险命令已拦截' && exit 1 || exit 0",
        "description": "拦截危险 Bash 命令"
      }
    ]
  }
}
```

### 提交前检查

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '^git commit' && (echo '⚠️ 提交前请确认：' && echo '  1. 测试通过？' && echo '  2. 代码审查通过？' && echo '  3. 提交信息符合规范？')",
        "description": "提交前提醒检查"
      }
    ]
  }
}
```

### 环境变量保护

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '\\.env$|\\.env\\.local$|\\.env\\.production$|credentials\\.json$|secrets\\.yaml$' && echo '🚨 禁止覆盖敏感文件' && exit 1 || exit 0",
        "description": "防止写入敏感文件"
      }
    ]
  }
}
```

### 工具调用后验证

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "command": "exit_code=$(echo \"$CLAUDE_TOOL_OUTPUT\" | tail -1 | grep -o 'exit code: [0-9]*' | cut -d' ' -f3); [ \"$exit_code\" != \"0\" ] && echo '⚠️ 命令返回非零退出码，请检查'",
        "description": "Bash 非零退出码提醒"
      }
    ]
  }
}
```

---

## 安全 Hooks 模板（完整版）

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "input=\"$CLAUDE_TOOL_INPUT\"; patterns=\"rm -rf /|rm -rf ~|rm -rf .|git push --force origin main|git push --force origin master|DROP TABLE|DROP DATABASE|shutdown|reboot|chmod 777 /|> /dev/sda|mkfs|dd if=/dev/zero\" && echo \"$input\" | grep -qE \"$patterns\" && echo '{\"hook_status\": \"blocked\", \"reason\": \"危险命令已拦截\"}' && exit 1 || exit 0",
        "description": "拦截危险命令"
      },
      {
        "matcher": "Write",
        "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '\\.(env|secret|pem|key|p12|pfx|credentials)(\\.|$)' && echo '{\"hook_status\": \"blocked\", \"reason\": \"禁止写入敏感文件\"}' && exit 1 || exit 0",
        "description": "防止写入敏感文件"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "command": "echo \"$CLAUDE_TOOL_OUTPUT\" | grep -q 'error\\|Error\\|ERROR\\|fatal\\|FATAL\\|permission denied\\|Permission denied' && echo '⚠️ 输出中发现错误' || true",
        "description": "错误关键词提醒"
      }
    ]
  }
}
```

---

## 与 hlskills 集成

| 技能 | 推荐 hook |
|------|---------|
| `hlpm` | 提交前检查 + 测试通过验证 |
| `hlbug` | 修复提交前检查回归测试 |
| `hlrefactor` | 每次模块变更后跑全量测试 |
| `hltest` | PostToolUse 验证测试输出 |
| `hlgit` | 禁止 force push main |
| `hldb` | 禁止 DROP TABLE/DATABASE |
| `hldeploy` | 部署前检查 CI 通过 |

---

## 验证

```bash
# 检查 hooks 配置语法
cat ~/.claude/settings.json | python3 -m json.tool > /dev/null && echo "✅ JSON 格式正确"

# 列出当前 hooks
cat ~/.claude/settings.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('hooks',{}), indent=2))"
```

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
