#!/usr/bin/env bash
# hlkb-hooks verify-paths ── 知识库路径合规性检查
# 用途:在项目里跑这个脚本,验证文档没有用错路径(常见 .hl/knowledge/ 笔误等)
#
# 触发场景:
#   - 团队成员首次接入 hlkb 时跑一次(确认项目合规)
#   - 提交 PR 前跑一次(确认没引入新笔误)
#   - 跨季度审计(团队 git log 排查历史笔误)
#
# 用法:
#   bash hlkb-hooks/verify-paths.sh             # 当前目录
#   bash hlkb-hooks/verify-paths.sh /path/to/project   # 指定项目
#   bash hlkb-hooks/verify-paths.sh --strict    # 严格模式:任何违规 exit 1
set -e

ROOT="${1:-$(pwd)}"
STRICT=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
  esac
done

# 切到项目根
cd "$ROOT"

EXIT_CODE=0
VIOLATIONS_TOTAL=0

# ---- 1. 检查 .hl/knowledge/ 笔误 ----
# 排除:本 ADR 文件本身(若存在)、引用 ADR 索引的 README
echo ""
echo "===检查 1:.hl/knowledge/ 笔误==="
echo "(排除 ADR-0002 自身 + adr/README.md 索引行 + CLAUDE.md 注释行)"
echo ""

# 收集所有 .md 文件
ALL_MD=$(find . -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/target/*" 2>/dev/null | sort)

# 过滤:在 ADR 文件里引用 `.hl/knowledge/` 是合法的(讲决策本身)
filtered_count=0
suspect_files=()

while IFS= read -r md; do
  [ -z "$md" ] && continue
  # 跳过 ADR 文件自身(决策内容必然包含旧路径做证据)
  if [[ "$md" =~ ^\./knowledge/adr/[0-9]+- ]]; then
    continue
  fi
  # 跳过 adr/README.md(索引含 ADR 标题)
  if [[ "$md" == "./knowledge/adr/README.md" ]]; then
    continue
  fi
  # 跳过 CLAUDE.md(架构图或注释可能引用历史路径)
  if [[ "$md" == "./CLAUDE.md" ]] || [[ "$md" == "./AGENTS.md" ]]; then
    continue
  fi
  # 跳过所有"讲知识库路径规范"的文档
  # 反模式表必然含错误路径作反例;这是规范文档的设计属性,不是真笔误
  # 适用文件: hlkb/SKILL.md + hlkb-hooks/SKILL.md(任何讲路径的规范文档)
  if [[ "$md" =~ ^\./hlkb(-hooks)?/SKILL\.md$ ]]; then
    continue
  fi
  # 跳过 verify-paths.sh 自身(脚本输出含路径名)
  if [[ "$md" == *"/hlkb-hooks/verify-paths.sh" ]]; then
    continue
  fi

  # 在合法文件里搜 .hl/knowledge/ 引用 → 笔误
  matches=$(grep -n "\.hl/knowledge" "$md" 2>/dev/null || true)
  if [ -n "$matches" ]; then
    suspect_files+=("$md")
    while IFS= read -r line; do
      echo "  ❌ $md:$line"
    done <<< "$matches"
    filtered_count=$((filtered_count + 1))
  fi
done <<< "$ALL_MD"
if [ "$filtered_count" -eq 0 ]; then
  echo "  ✅ 无 .hl/knowledge/ 笔误"
  VIOLATIONS_TOTAL=$((VIOLATIONS_TOTAL + 0))
else
  echo ""
  echo "  ⚠️  共发现 $filtered_count 个文件含 .hl/knowledge/ 笔误"
  VIOLATIONS_TOTAL=$((VIOLATIONS_TOTAL + filtered_count))
  EXIT_CODE=1
fi

# ---- 2. 检查 src/knowledge/ 笔误 ----
echo ""
echo "===检查 2:src/knowledge/ 笔误==="
SRC_KNOW_VIOLATIONS=$(grep -rn "src/knowledge" --include="*.md" --include="*.java" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" . 2>/dev/null | grep -v "^./knowledge/adr/" | grep -vE "^./hlkb(-hooks)?/SKILL\.md" || true)
if [ -z "$SRC_KNOW_VIOLATIONS" ]; then
  echo "  ✅ 无 src/knowledge/ 笔误"
else
  echo "$SRC_KNOW_VIOLATIONS" | while IFS= read -r line; do
    echo "  ❌ $line"
  done
  SRC_KNOW_COUNT=$(echo "$SRC_KNOW_VIOLATIONS" | wc -l | tr -d ' ')
  VIOLATIONS_TOTAL=$((VIOLATIONS_TOTAL + SRC_KNOW_COUNT))
  EXIT_CODE=1
fi

# ---- 3. 检查 docs/knowledge/ 笔误 ----
echo ""
echo "===检查 3:docs/knowledge/ 笔误==="
DOCS_KNOW_VIOLATIONS=$(grep -rn "docs/knowledge" --include="*.md" . 2>/dev/null | grep -v "^./knowledge/adr/" | grep -vE "^./hlkb(-hooks)?/SKILL\.md" || true)
if [ -z "$DOCS_KNOW_VIOLATIONS" ]; then
  echo "  ✅ 无 docs/knowledge/ 笔误"
else
  echo "$DOCS_KNOW_VIOLATIONS" | while IFS= read -r line; do
    echo "  ❌ $line"
  done
  DOCS_KNOW_COUNT=$(echo "$DOCS_KNOW_VIOLATIONS" | wc -l | tr -d ' ')
  VIOLATIONS_TOTAL=$((VIOLATIONS_TOTAL + DOCS_KNOW_COUNT))
  EXIT_CODE=1
fi

# ---- 4. 检查 .knowledge/ 笔误 ----
echo ""
echo "===检查 4:.knowledge/ 笔误(npm 风格误用)==="
DOT_KNOW_VIOLATIONS=$(grep -rn "\.knowledge/" --include="*.md" --include="*.json" --include="*.yml" --include="*.yaml" . 2>/dev/null | grep -v "^./knowledge/adr/" | grep -vE "^./hlkb(-hooks)?/SKILL\.md" | grep -v "knowledge/" | head -10 || true)
if [ -z "$DOT_KNOW_VIOLATIONS" ]; then
  echo "  ✅ 无 .knowledge/ 笔误"
else
  echo "$DOT_KNOW_VIOLATIONS" | while IFS= read -r line; do
    echo "  ❌ $line"
  done
fi

# ---- 5. 验证真路径存在 ----
echo ""
echo "===检查 5:knowledge/ 真路径存在==="
if [ -d "knowledge" ]; then
  KNOW_FILES=$(find knowledge -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "  ✅ knowledge/ 存在(包含 $KNOW_FILES 个 .md 文件)"
  # 抽查 knowledge/README.md(总目录)
  if [ ! -f "knowledge/README.md" ]; then
    echo "  ⚠️  knowledge/README.md 缺失(建议创建知识库总目录索引)"
  fi
else
  echo "  ⚠️  knowledge/ 目录不存在(项目可能未启用 hlkb 体系)"
fi

# ---- 6. 验证 .hl/memory/ 没被误伤 ----
echo ""
echo "===检查 6:.hl/memory/ 项目记忆(应保留)==="
if [ -d ".hl/memory" ]; then
  MEMORY_FILES=$(find .hl/memory -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "  ✅ .hl/memory/ 存在(包含 $MEMORY_FILES 个 .md 文件,属 hlmemory 管理)"
else
  echo "  · .hl/memory/ 不存在(项目可能没用 hlmemory,属正常)"
fi

# ---- 7. 汇总 ----
echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
  echo "🎉 知识库路径检查全部通过"
elif [ $EXIT_CODE -eq 1 ] && [ $STRICT -eq 0 ]; then
  echo "⚠️  发现 $VIOLATIONS_TOTAL 处路径笔误(详见上方)"
  echo ""
  echo "修复建议:"
  echo "  - .hl/knowledge/X.md → knowledge/X.md"
  echo "  - src/knowledge/X     → knowledge/X"
  echo "  - docs/knowledge/X    → knowledge/X"
  echo ""
  echo "项目内知识库必须在项目根的 knowledge/(详见 hlkb/SKILL.md §路径约定)"
  echo ""
  echo "如需强制失败(返回 exit 1)防止引入新笔误,加 --strict 标志"
  echo "或者在 PR 检查/CI 里跑: bash verify-paths.sh --strict"
fi
echo "================================================"

exit $EXIT_CODE