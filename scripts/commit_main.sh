#!/usr/bin/env bash
# Commit result directories to main from inside GitHub Actions, retrying if another
# workflow pushed first. Pushes made with GITHUB_TOKEN do not trigger further runs.
#   bash scripts/commit_main.sh "scans ledger data" "desk: scan 2026-10-16T01:00:00Z"
set -euo pipefail
DIRS="$1"
MSG="$2"
git config user.name "desk-bot"
git config user.email "desk-bot@users.noreply.github.com"
for d in $DIRS; do
  [ -e "$d" ] && git add -A "$d"
done
if git diff --cached --quiet; then
  echo "nothing to commit"; exit 0
fi
git commit -qm "$MSG"
for i in 1 2 3 4 5; do
  if git push origin HEAD:main; then exit 0; fi
  echo "push rejected, rebasing (attempt $i)"
  git pull --rebase -q origin main
done
echo "could not push after 5 attempts" >&2
exit 1
