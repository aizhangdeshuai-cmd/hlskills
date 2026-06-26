---
name: hl-permission
description: 一键授权当前项目目录下所有文件改动（Edit/Write/Bash），免去逐条确认，窗口关闭后权限自然失效。Use when 不想每次文件改动都被询问授权、需要临时提升操作效率。通过 /hl-permission 调用，执行 /hl-permission --off 可恢复。
---

# 一键项目授权

> 属于 `hlskills` 技能系统。向当前项目目录添加权限白名单，免去逐条操作确认。

---

## 执行

```bash
# 检测项目根目录
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
echo "PROJECT_ROOT=$_ROOT"

# 确认 settings.local.json 存在
mkdir -p "$_ROOT/.claude"
[ ! -f "$_ROOT/.claude/settings.local.json" ] && echo '{}' > "$_ROOT/.claude/settings.local.json"
```

然后使用 Python 将权限追加到 `$_ROOT/.claude/settings.local.json`：

```python
import json, os, sys

root = os.environ.get('PROJECT_ROOT', os.getcwd)

settings_path = os.path.join(root, '.claude', 'settings.local.json')

with open(settings_path, 'r') as f:
    settings = json.load(f)

permissions = settings.setdefault('permissions', {})
allow = permissions.setdefault('allow', [])

new_allows = [
    f"Edit({root}/**)",
    f"Write({root}/**)",
    f"Bash(*:{root}*)",
    f"Read({root}/**)"
]

added = 0
for a in new_allows:
    if a not in allow:
        allow.append(a)
        added += 1
        print(f"+ {a}")

if added == 0:
    print("全部权限已存在，无需添加")

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"\n已授权 {added} 项权限 → {root}")
print("此权限在本次窗口关闭后随 settings.local.json 保留（不会被 git 追踪）")
```

---

## 关闭

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
echo "PROJECT_ROOT=$_ROOT"
```

```python
import json, os

root = os.environ['PROJECT_ROOT']
settings_path = os.path.join(root, '.claude', 'settings.local.json')

with open(settings_path, 'r') as f:
    settings = json.load(f)

allow = settings.get('permissions', {}).get('allow', [])
to_remove = [
    f"Edit({root}/**)", f"Write({root}/**)", f"Bash(*:{root}*)", f"Read({root}/**)"
]

removed = 0
for item in to_remove:
    if item in allow:
        allow.remove(item)
        removed += 1
        print(f"- {item}")

settings['permissions']['allow'] = allow
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"\n已移除 {removed} 项权限")
```

---

## 说明

- **权限范围**：当前 git 仓库根目录（或当前目录）下的所有文件 Edit / Write / Read + 目录相关的 Bash 命令
- **持久性**：写入项目 `.claude/settings.local.json`，该文件不会被 git 追踪
- **恢复**：执行 `/hl-permission --off` 或直接删除 `.claude/settings.local.json` 中的相应条目
- **安全**：仅授权当前项目，不影响其他项目的权限策略

> 这是临时提效工具，生产敏感项目请谨慎使用。

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
