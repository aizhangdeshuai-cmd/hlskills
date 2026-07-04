#!/usr/bin/env bash
# hlkb-hooks ── 一键安装脚本
# 把"知识库强同步"hooks 装进当前项目 .claude/settings.local.json
#
# 用法:bash install.sh [--uninstall] [--dry-run] [--preset=default|java]
set -e

# ---- 0. 参数 ----
UNINSTALL=0
DRY_RUN=0
PRESET="default"
for arg in "$@"; do
  case "$arg" in
    --uninstall) UNINSTALL=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --preset=*)  PRESET="${arg#--preset=}" ;;
    -h|--help)
      cat <<'EOF'
用法: bash install.sh [--uninstall] [--dry-run] [--preset=default|java]

  --uninstall        卸载 hooks(删 .hlskills + 从 settings.local.json 移除 hooks 节)
  --dry-run          模拟跑一遍,不真改文件
  --preset=DEFAULT   default: src/api|controllers|routes 标准 Web 项目
  --preset=JAVA      java:    Spring Boot + Controller.java + Mapper.java + migrations
  --preset=文件路径   也支持自定义 preset JSON 文件绝对路径

EOF
      exit 0
      ;;
  esac
done

# ---- 1. 定位项目根 ----
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
echo "📁 项目根: $_ROOT"
cd "$_ROOT"

SENTINEL="$_ROOT/.hlskills"
SETTINGS="$_ROOT/.claude/settings.local.json"
BACKUP="$_ROOT/.claude/settings.local.json.hlkb-hooks.bak"
HOOKS_DATA="$_ROOT/.claude/.hlkb-hooks-data.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRESETS_FILE="$SCRIPT_DIR/presets.json"

# 自定义 preset 文件支持
if [ -f "$PRESET" ]; then
  PRESETS_FILE="$PRESET"
  echo "  · 使用自定义 preset: $PRESET"
fi

if [ ! -f "$PRESETS_FILE" ]; then
  echo "❌ 找不到 presets.json: $PRESETS_FILE"
  exit 1
fi

# ---- 2. 卸载 ----
if [ "$UNINSTALL" = "1" ]; then
  echo "🗑️  卸载 hlkb-hooks"
  [ -f "$SENTINEL" ] && { [ "$DRY_RUN" = "1" ] || rm -f "$SENTINEL"; echo "  ✓ 删 .hlskills"; } || echo "  · .hlskills 不存在,跳过"
  if [ -f "$SETTINGS" ]; then
    [ "$DRY_RUN" = "1" ] || python3 -c "
import json, pathlib
p = pathlib.Path('$SETTINGS')
d = json.loads(p.read_text())
if 'hooks' in d:
    del d['hooks']
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
    print('  ✓ 从 settings.local.json 删 hooks 节')
else:
    print('  · settings.local.json 无 hooks 节,跳过')
"
    [ -f "$BACKUP" ] && { [ "$DRY_RUN" = "1" ] || { rm -f "$BACKUP"; echo "  ✓ 删备份 $BACKUP"; }; }
  fi
  [ -f "$HOOKS_DATA" ] && { [ "$DRY_RUN" = "1" ] || rm -f "$HOOKS_DATA"; echo "  ✓ 删中间文件 $HOOKS_DATA"; }
  echo "✅ 卸载完成"
  exit 0
fi

# ---- 3. 装 .hlskills 哨兵 ----
if [ -f "$SENTINEL" ]; then
  echo "  · .hlskills 哨兵已存在,跳过"
else
  [ "$DRY_RUN" = "1" ] || touch "$SENTINEL"
  echo "  ✓ 放 .hlskills 哨兵"
fi

# ---- 4. 备份 settings.local.json ----
mkdir -p "$(dirname "$SETTINGS")"
if [ -f "$SETTINGS" ]; then
  [ "$DRY_RUN" = "1" ] || cp "$SETTINGS" "$BACKUP"
  echo "  ✓ 备份原 settings 到 $(basename "$BACKUP")"
else
  [ "$DRY_RUN" = "1" ] || echo "{}" > "$SETTINGS"
  echo "  ✓ 创建空 settings.local.json"
fi

# ---- 5. 渲染 hook command(从 preset)----
echo "  · preset: $PRESET"

[ "$DRY_RUN" = "1" ] || python3 - "$PRESETS_FILE" "$PRESET" "$HOOKS_DATA" <<'PYEOF'
import json, pathlib, sys

presets_file = pathlib.Path(sys.argv[1])
preset_name = sys.argv[2]
data_file = pathlib.Path(sys.argv[3])

presets = json.loads(presets_file.read_text())
if preset_name not in presets:
    available = ', '.join(presets.keys())
    print(f'  ❌ preset "{preset_name}" 不存在,可选: {available}')
    sys.exit(1)

p = presets[preset_name]['patterns']

# 渲染 PreToolUse command
pre_cmd = (
    "jq -r '.tool_input.command' | grep -qE '^[[:space:]]*git commit' || exit 0; "
    "jq -r '.tool_input.command' | grep -qE 'no-verify|\\[skip-kb-sync\\]' && exit 0; "
    "([ -f .hlskills ] || [ -d knowledge ]) || exit 0; "
    "CHANGED=$(git diff --cached --name-only); "
    f"echo \"$CHANGED\" | grep -qE '^({p['root_dirs']})/' || exit 0; "
    "MISS=''; "
    "for f in $CHANGED; do "
    "  case \"$f\" in "
    f"    {p['api_globs']}) "
    f"echo \"$CHANGED\" | grep -qE '^({p['sync_api_dir']})/' || MISS=\"$MISS api:$f\";; "
    f"    {p['db_globs']}) "
    f"echo \"$CHANGED\" | grep -qE '^({p['sync_db_dir']})/' || MISS=\"$MISS db:$f\";; "
    f"    {p['enum_globs']}) "
    f"echo \"$CHANGED\" | grep -qE '^({p['sync_enum_dir']})/' || MISS=\"$MISS enum:$f\";; "
    f"    {p['error_globs']}) "
    f"echo \"$CHANGED\" | grep -qE '^({p['sync_error_dir']})/' || MISS=\"$MISS err:$f\";; "
    f"    {p['test_globs']}) "
    f"echo \"$CHANGED\" | grep -qE '^({p['sync_test_dir']})/' || MISS=\"$MISS test:$f\";; "
    "  esac; "
    "done; "
    "[ -z \"$MISS\" ] && exit 0; "
    "echo '🚨 知识库未同步:' >&2; "
    "echo \"$MISS\" >&2; "
    "echo '' >&2; "
    "echo '请同步 knowledge/ 或 git commit --no-verify / commit message 加 [skip-kb-sync]' >&2; "
    "exit 2"
)

# PostToolUse 渲染辅助:把每类 glob 转成 case 分支模板
# 例如 'src/api/*|*controllers/*' → '*src/api*|*controllers*'
def to_case_patterns(globs):
    parts = globs.split('|')
    out = []
    for part in parts:
        # */controllers/* → *controllers*(任意位置出现即可)
        if part.endswith('/*'):
            out.append(f"*{part[:-2]}*")
        elif '*' in part:
            out.append(part)
        else:
            out.append(f"*{part}*")
    return '|'.join(out)

# 渲染 PostToolUse command
post_cmd = (
    "F=$(jq -r '.tool_input.file_path'); "
    "([ -f .hlskills ] || [ -d knowledge ]) || exit 0; "
    "case \"$F\" in "
    f"    {to_case_patterns(p['api_globs'])}) echo '🔔 接口文件变更,若涉及契约请同步 knowledge/api/';;"
    f"    {to_case_patterns(p['db_globs'])}) echo '🔔 数据库/架构变更,请同步 knowledge/db/ 或新建 ADR';; "
    f"    {to_case_patterns(p['enum_globs'])}) echo '🔔 枚举变更,请同步 knowledge/enums/';; "
    f"    {to_case_patterns(p['error_globs'])}) echo '🔔 错误码变更,请同步 knowledge/error-codes/';; "
    f"    {to_case_patterns(p['test_globs'])}) echo '🔔 测试变更,请同步 knowledge/tests/';; "
    "esac; exit 0"
)

data = {
    'PreToolUse': {'matcher': 'Bash', 'command': pre_cmd},
    'PostToolUse': {'matcher': 'Write|Edit|MultiEdit', 'command': post_cmd}
}
data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print(f'  ✓ 渲染 hook command 完成 ({len(pre_cmd)} + {len(post_cmd)} 字节)')
PYEOF

# ---- 6. 把渲染结果注入 settings.local.json ----
[ "$DRY_RUN" = "1" ] || python3 - "$SETTINGS" "$HOOKS_DATA" <<'PYEOF'
import json, pathlib, sys
settings_path = pathlib.Path(sys.argv[1])
data_path = pathlib.Path(sys.argv[2])
d = json.loads(settings_path.read_text() or '{}')
hooks_data = json.loads(data_path.read_text())
d.setdefault('hooks', {})
d['hooks']['PreToolUse'] = [{
    'matcher': hooks_data['PreToolUse']['matcher'],
    'hooks': [{'type': 'command', 'command': hooks_data['PreToolUse']['command']}]
}]
d['hooks']['PostToolUse'] = [{
    'matcher': hooks_data['PostToolUse']['matcher'],
    'hooks': [{'type': 'command', 'command': hooks_data['PostToolUse']['command']}]
}]
settings_path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('  ✓ hooks 已写入 settings.local.json')
PYEOF

[ "$DRY_RUN" = "1" ] || rm -f "$HOOKS_DATA"

# ---- 7. 验证 JSON 合法 + 节点齐全 ----
echo ""
echo "🔍 验证..."
if [ "$DRY_RUN" = "1" ]; then
  echo "  · dry-run 模式,跳过 JSON 内容验证(只跑了备份/哨兵步骤)"
  exit 0
fi
python3 -m json.tool "$SETTINGS" > /dev/null && echo "  ✓ JSON 格式合法"
python3 -c "
import json
d = json.load(open('$SETTINGS'))
h = d.get('hooks', {})
assert 'PreToolUse' in h, 'PreToolUse 缺失'
assert 'PostToolUse' in h, 'PostToolUse 缺失'
assert h['PreToolUse'][0]['matcher'] == 'Bash'
assert h['PostToolUse'][0]['matcher'] == 'Write|Edit|MultiEdit'
print('  ✓ PreToolUse matcher :', h['PreToolUse'][0]['matcher'])
print('  ✓ PostToolUse matcher:', h['PostToolUse'][0]['matcher'])
print('  ✓ PreToolUse cmd     :', len(h['PreToolUse'][0]['hooks'][0]['command']), '字节')
print('  ✓ PostToolUse cmd    :', len(h['PostToolUse'][0]['hooks'][0]['command']), '字节')
"
[ -f "$SENTINEL" ] && echo "  ✓ .hlskills 哨兵已放"
[ -f "$BACKUP" ] && echo "  ✓ 备份存在: $(basename "$BACKUP")"

# ---- 8. 路径合规检查(不阻断,仅警告) ----
echo ""
echo "🔎 路径合规检查(verify-paths.sh)..."
if [ -f "$SCRIPT_DIR/verify-paths.sh" ]; then
  # verify-paths 退出码:0=全过,1=有笔误. 不阻断 hook 安装,只警告
  bash "$SCRIPT_DIR/verify-paths.sh" "$_ROOT" 2>&1 | tail -30 || true
  VERIFY_EXIT=${PIPESTATUS[0]}
  if [ "$VERIFY_EXIT" -ne 0 ]; then
    echo ""
    echo "  ⚠️  路径检查发现笔误,见上方(不阻断 hook 安装)"
    echo "  建议修复后定期跑: bash hlkb-hooks/verify-paths.sh --strict"
  else
    echo ""
    echo "  ✅ 路径合规检查通过(knowledge/ 路径规范)"
  fi
else
  echo "  · verify-paths.sh 不在脚本同目录,跳过"
fi

echo ""
echo "✅ 安装完成。"
echo ""
echo "📚 完整文档:hlkb-hooks/SKILL.md"
echo "🧪 真实拦截测试:"
echo "   echo test > <改任意被识别文件> && git add && git commit -m test"
echo "   (预期:harness 输出 🚨 知识库未同步,commit 失败)"