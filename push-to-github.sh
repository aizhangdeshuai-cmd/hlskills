#!/usr/bin/env bash
# 一键推送到 GitHub 仓库
# 用法: ./push-to-github.sh
# 前提: 本机已配置 git 凭据(SHH key 或 credential helper)

set -e

REPO_DIR="/Users/zhangdanyang/.agents/skills/hlskills"
REMOTE_URL="https://github.com/aizhangdeshuai-cmd/hlskills.git"
BRANCH="main"

echo "=========================================="
echo "  hlskills 推送到 GitHub"
echo "=========================================="
echo ""
echo "仓库目录: $REPO_DIR"
echo "远程地址: $REMOTE_URL"
echo "分支:     $BRANCH"
echo ""

cd "$REPO_DIR"

# 1. 确认 remote 已配置
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "[1/4] 添加远程仓库..."
  git remote add origin "$REMOTE_URL"
else
  current_url=$(git remote get-url origin)
  if [ "$current_url" != "$REMOTE_URL" ]; then
    echo "[1/4] 更新远程仓库 URL..."
    git remote set-url origin "$REMOTE_URL"
  else
    echo "[1/4] 远程仓库已配置: $current_url"
  fi
fi

# 2. 确认当前分支
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "(无分支)")
if [ "$current_branch" != "$BRANCH" ]; then
  echo "[2/4] 切换到 $BRANCH 分支..."
  git branch -M "$BRANCH"
else
  echo "[2/4] 当前分支: $current_branch"
fi

# 3. 推送
echo ""
echo "[3/4] 推送到 GitHub..."
if git push -u origin "$BRANCH"; then
  echo ""
  echo "=========================================="
  echo "  ✅ 推送成功!"
  echo "=========================================="
  echo ""
  echo "访问: https://github.com/aizhangdeshuai-cmd/hlskills"
  echo ""
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

# 4. 显示远程信息
echo "[4/4] 远程信息:"
git remote -v
echo ""
git log --oneline -5
