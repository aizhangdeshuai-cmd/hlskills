---
name: hlhooks
description: Claude Code hooks 配置模板，提供推荐的安全/质量/自动化 hooks 配置（提交前检查/危险命令拦截/工具调用后验证）。Use when 配置 hooks、添加自动化检查、或提到"hooks"、"自动化"、"提交前检查"。通过 /hlhooks 调用。
---

# Hooks 配置模板

> 属于 `hlskills` 技能系统。提供推荐的 Claude Code `settings.json` hooks 配置。

> ⚠️ **重要：以下模板遵循 Claude Code 真实 hooks 协议**。每条 hook 都是 `{ matcher, hooks: [{type: "command", command}] }` 结构,阻断靠 exit code 2 + stderr 反馈,**不是 JSON 输出**。

---

## 配置位置

- 用户级：`~/.claude/settings.json`
- 项目级：`.claude/settings.local.json`

项目级优先于用户级。

---

## Claude Code hooks 协议(真实)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "<shell 命令, stdin 接收 JSON 上下文>"
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "Stop": [...],
    "SubagentStop": [...],
    "Notification": [...]
  }
}
```

**关键协议**:
- matcher 仅匹配工具名(`Bash` / `Write` / `Edit` / `Read` 等),不接受组合
- command 通过 stdin 接收 JSON,字段含 `tool_name` / `tool_input` / `tool_output`
- **阻断方式**:exit code `2` + stderr 输出 → Claude 收到反馈但不执行工具
- **非阻断**:exit code `0` + stdout 输出 JSON(可选)
- **PreToolUse matcher** 也支持带前缀的 `mcp__*` 或 `mcp__server__*`

---

## 推荐配置

### 1. 危险命令拦截(Bash)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE 'rm -rf /|rm -rf ~|git push --force origin (main|master)|DROP TABLE|DROP DATABASE|shutdown|reboot|chmod 777 /|> /dev/sda|mkfs|dd if=/dev/zero' && { echo '🚨 危险命令已拦截:不允许执行 rm -rf /, force push main, DROP TABLE 等' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

**协议说明**:
- `jq -r '.tool_input.command'` 从 stdin JSON 提取 Bash 命令内容
- 命中危险模式 → exit 2 + stderr → Claude 收到拦截反馈
- 不命中 → exit 0 → Claude 正常执行

### 2. 环境变量保护(Write)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -qE '\\.(env|secret|pem|key|p12|pfx|credentials)$|credentials\\.json$|secrets\\.yaml$' && { echo '🚨 禁止写入敏感文件' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

**协议说明**:与上面相同,jq 从 `tool_input.file_path` 提取路径。

### 3. 提交前提醒(Bash,仅提示,不阻断)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE '^git commit' && { echo '⚠️ 提交前请确认:1. 测试通过? 2. 代码审查通过? 3. 提交信息符合规范?'; exit 0; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

**协议说明**:仅 stdout 提示,exit 0 不阻断——提交仍然执行,用户自行确认。

### 4. Bash 错误关键词提醒(PostToolUse,仅提示)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_output' | grep -q 'error\\|Error\\|fatal\\|FATAL\\|permission denied' && echo '⚠️ 输出中发现错误关键词,请检查' || exit 0"
          }
        ]
      }
    ]
  }
}
```

---

## 完整模板(防御型,推荐直接使用)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE 'rm -rf /|rm -rf ~|git push --force origin (main|master)|DROP TABLE|DROP DATABASE|shutdown|reboot|chmod 777 /|> /dev/sda|mkfs|dd if=/dev/zero' && { echo '🚨 危险命令已拦截' >&2; exit 2; } || exit 0"
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -qE '\\.(env|secret|pem|key|p12|pfx|credentials)$|credentials\\.json$|secrets\\.yaml$' && { echo '🚨 禁止写入敏感文件' >&2; exit 2; } || exit 0"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE '^git commit' && { echo '⚠️ 提交前请确认:1. 测试通过? 2. 代码审查通过? 3. 提交信息符合规范?'; exit 0; } || exit 0"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_output' | grep -q 'error\\|Error\\|fatal\\|FATAL\\|permission denied' && echo '⚠️ 输出中发现错误关键词' || exit 0"
          }
        ]
      }
    ]
  }
}
```

---

## 与 hlskills 集成

| 技能 | 推荐 hook | 阻断/提示 |
|------|---------|-----------|
| `hlpm` | 提交前检查 | 提示 |
| `hlbug` | 修复提交前检查 | 提示 |
| `hlrefactor` | 每次模块变更后跑全量测试 | 提示(用户手动跑) |
| `hltest` | PostToolUse 验证测试输出 | 提示 |
| `hlgit` | Bash 拦截 force push main | **阻断** |
| `hldb` | Bash 拦截 DROP TABLE/DATABASE | **阻断** |
| `hldeploy` | 部署前检查 CI 通过 | 提示 |

---

## 验证 hooks 是否生效

启用 hooks 后,**实测一次**确保配置生效:

```bash
# 1. 语法检查
cat ~/.claude/settings.json | python3 -m json.tool > /dev/null && echo "✅ JSON 格式正确"

# 2. 列出当前 hooks
cat ~/.claude/settings.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('hooks',{}), indent=2))"

# 3. 实测阻断:尝试一次危险命令,确认 hook 真的拦截(Claude 应收到反馈且不执行)
# 例:让 Claude 跑 'echo test' → 应该正常执行
# 让 Claude 跑 'rm -rf /tmp/test-dir' → 应该被 hook 拦截,Claude 收到反馈
```

⚠️ **如果实测时 hook 未拦截**:说明 hooks 未生效。常见原因:
- JSON 格式错误(用 step 1 检查)
- matcher 拼错(如 `Bash` 写成 `bash`)
- command 路径错误(确认 `jq` 已安装)
- 配置文件路径错误(用户级 vs 项目级)

---

> **路径规范**:本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。