#!/usr/bin/env bash
# git-push-retry.sh - 重试式 git push，专治国内网络 curl 52/55 连接重置、443 超时
# 用法:
#   ./git-push-retry.sh                 # 默认 origin/main, 10 次
#   ./git-push-retry.sh upstream dev    # 指定远程/分支
#   ./git-push-retry.sh origin main 15 5  # 15 次, 间隔 5s
set -u

REMOTE="${1:-origin}"
BRANCH="${2:-main}"
MAX_TRIES="${3:-10}"
DELAY="${4:-3}"

# 国内网络常见修复：强制 HTTP/1.1 + 放大缓冲，避免中途重置
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000

i=1
while [ "$i" -le "$MAX_TRIES" ]; do
  echo "=== try $i / $MAX_TRIES ==="
  if git push "$REMOTE" "$BRANCH"; then
    echo "PUSH OK"
    exit 0
  fi
  echo "retry in ${DELAY}s..."
  sleep "$DELAY"
  i=$((i + 1))
done
echo "FAILED after $MAX_TRIES tries"
exit 1
