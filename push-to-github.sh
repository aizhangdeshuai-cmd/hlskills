#!/usr/bin/env bash
# 一键推送到 GitHub 仓库
# 用法: ./push-to-github.sh [分支名]   默认 main
# 前提: 本机已配置 git 凭据(SSH key 或 credential helper) + 已用 `git remote add origin ...` 配好远程

set -e

BRANCH="${1:-main}"

echo "=========================================="
echo "  hlskills 推送到 GitHub"
echo "=========================================="
echo ""

# 1. 自动检测仓库根(不再硬编码绝对路径)
REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_DIR" ]; then
  echo "❌ 错误:当前目录不在 git 仓库内"
  echo "   请在仓库根目录运行此脚本,或先 `git init`"
  exit 1
fi
cd "$REPO_DIR"
echo "仓库目录: $REPO_DIR"

# 2. 读取(而非改写)已配的远程地址
REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$REMOTE_URL" ]; then
  echo ""
  echo "❌ 错误:未配置 origin 远程仓库"
  echo "   请先手动配置: git remote add origin <你的仓库地址>"
  echo "   例如:          git remote add origin git@github.com:<你的用户名>/hlskills.git"
  exit 1
fi
echo "远程地址: $REMOTE_URL (已配置,不会改写)"
echo "分支:     $BRANCH"
echo ""

# 3. 确认当前分支
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ "$current_branch" != "$BRANCH" ]; then
  echo "⚠️  当前分支 '$current_branch' 与目标分支 '$BRANCH' 不一致"
  echo "   本脚本不会自动 rename,先 `git checkout $BRANCH` 再跑"
  exit 1
fi
echo "当前分支: $current_branch ✅"

# 4. 推送前预览:显示未推送的 commit + 文件改动统计
echo ""
echo "[推送前预览]"
behind=$(git rev-list --count origin/"$BRANCH"..HEAD 2>/dev/null || echo "?")
ahead=$(git rev-list --count HEAD..origin/"$BRANCH" 2>/dev/null || echo "?")
echo "本地领先远程: $behind 个 commit"
echo "远程领先本地: $ahead 个 commit"
if [ "$behind" = "0" ]; then
  echo "⚠️  本地无新 commit 可推,退出"
  exit 0
fi
echo ""
echo "--- 待推送 commit ---"
git log --oneline origin/"$BRANCH"..HEAD
echo ""
echo "--- 文件改动统计 ---"
git diff --stat origin/"$BRANCH"..HEAD | tail -10
echo ""

# 5. 用户确认
echo "将推送到: $REMOTE_URL ($BRANCH 分支)"
read -r -p "确认推送? 输入 yes 继续,其他取消: " confirm
if [ "$confirm" != "yes" ]; then
  echo "已取消"
  exit 0
fi

# 6. 推送
echo ""
echo "[推送中]..."
if git push origin "$BRANCH"; then
  echo ""
  echo "=========================================="
  echo "  ✅ 推送成功"
  echo "=========================================="
else
  echo ""
  echo "=========================================="
  echo "  ❌ 推送失败"
  echo "=========================================="
  echo ""
  echo "可能原因:"
  echo "  1. 未配置 GitHub 凭据 (SSH key 或 PAT)"
  echo "  2. 远程仓库不存在或无写权限"
  echo "  3. 网络问题"
  echo ""
  echo "诊断命令:"
  echo "  git remote -v                    # 检查远程仓库"
  echo "  ssh -T git@github.com            # 测试 SSH 连接"
  echo "  git config --global credential.helper    # 检查凭据 helper"
  echo ""
  exit 1
fi