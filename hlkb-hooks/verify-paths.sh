#!/usr/bin/env bash
# 用法：bash verify-paths.sh [项目目录] [--strict]
# 默认报告路径笔误并返回 0；--strict 命中笔误返回 1。参数或扫描错误返回 2。
set -eu
set -o pipefail

root=
strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -*) echo "用法: verify-paths.sh [项目目录] [--strict]" >&2; exit 2 ;;
    *) if [[ -n "$root" ]]; then echo "只接受一个项目目录" >&2; exit 2; fi
       root=$arg ;;
  esac
done
cd -- "${root:-.}" || exit 2

# 路径经 find -exec 作为独立参数传递。awk 批量读取每份文件一次，
# 只将每批命中次数写入临时文件，诊断直接输出到终端。
counts=$(mktemp "${TMPDIR:-/tmp}/hlkb-path-counts.XXXXXXXX") || exit 2
trap 'rm -f -- "$counts"' EXIT
if ! find . -name .git -prune -o -type f \
    \( -name '*.md' -o -name '*.java' -o -name '*.ts' -o -name '*.tsx' \
       -o -name '*.js' -o -name '*.py' -o -name '*.json' -o -name '*.yml' -o -name '*.yaml' \) \
    ! -path './CLAUDE.md' ! -path './AGENTS.md' ! -path './knowledge/adr/README.md' \
    ! -path './hlkb/SKILL.md' ! -path './hlkb-hooks/SKILL.md' \
    -exec env LC_ALL=C awk -v counts="$counts" '
      function hit(rule) {
        print "  " FILENAME ":" FNR "  " rule
        total++
      }
      FILENAME ~ /^\.\/knowledge\/adr\/[0-9][0-9][0-9][0-9]-[^\/]+\.md$/ { next }
      {
        md = FILENAME ~ /\.md$/
        code = FILENAME ~ /\.(java|ts|tsx|js|py)$/
        config = FILENAME ~ /\.(json|yml|yaml)$/
        if (md && FILENAME !~ /\/(node_modules|target)\// && /(^|[^[:alnum:]_.-])\.hl\/knowledge([^[:alnum:]_.-]|$)/) hit(".hl/knowledge/")
        if ((md || code) && /(^|[^[:alnum:]_.-])src\/knowledge([^[:alnum:]_.-]|$)/) hit("src/knowledge/")
        if (md && /(^|[^[:alnum:]_.-])docs\/knowledge([^[:alnum:]_.-]|$)/) hit("docs/knowledge/")
        if ((md || config) && /(^|[^[:alnum:]_.-])\.knowledge\//) hit(".knowledge/")
      }
      END { if (total) print total >> counts }
    ' {} +; then
  echo "路径扫描未完成，请检查上方的目录遍历或文件读取错误。" >&2
  exit 2
fi
hits=$(awk '{ n += $1 } END { print n + 0 }' "$counts") || exit 2

for directory in knowledge .hl/memory; do
  if [[ -d "$directory" ]]; then
    # Count records without depending on newlines in filenames.
    files=$(find "$directory" -type f -name '*.md' -exec printf '.%.0s' {} + | wc -c) || exit 2
    echo "$directory/ 存在（$((files)) 个 Markdown 文件）"
    if [[ "$directory" == knowledge && ! -f knowledge/README.md ]]; then
      echo "提示：knowledge/README.md 总目录索引缺失"
    fi
  elif [[ "$directory" == knowledge ]]; then
    echo "提示：尚未创建 knowledge/ 目录"
  else
    echo "提示：未使用 .hl/memory/ 项目记忆"
  fi
done

if (( hits )); then
  echo "发现 $hits 处知识库路径笔误，请核对上方文件与行号，使用项目根目录下的 knowledge/。"
  if (( strict )); then exit 1; fi
else
  echo "知识库路径检查通过。"
fi
