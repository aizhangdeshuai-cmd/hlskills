#!/usr/bin/env bash
set -eu
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"
python3 "$script_dir/configure.py" "$@"
for arg in "$@"; do
  case "$arg" in --dry-run|--uninstall|--help|-h) exit 0 ;; esac
done
if ! bash "$script_dir/verify-paths.sh" "$root"; then
  echo "⚠️ 路径检查发现问题，请核对上方输出。" >&2
fi
