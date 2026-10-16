#!/usr/bin/env bash
# Fetch sports-method at the pinned commit (its devig/fees/metrics/matcher are the
# arithmetic the desk reuses) and, unless "code-only" is passed, a shallow copy of
# its data branch (Polymarket US quotes, Pinnacle odds, histories). Run from the
# repo root; reads the pin from config/desk.yaml.
set -euo pipefail
MODE="${1:-full}"
REPO="$(python3 -c 'import yaml;print(yaml.safe_load(open("config/desk.yaml"))["reference"]["sports_method_repo"])')"
SHA="$(python3 -c 'import yaml;print(yaml.safe_load(open("config/desk.yaml"))["reference"]["sports_method_sha"])')"
BRANCH="$(python3 -c 'import yaml;print(yaml.safe_load(open("config/desk.yaml"))["reference"]["data_branch"])')"

mkdir -p vendor
if [ ! -d vendor/sports-method/.git ]; then
  git init -q vendor/sports-method
  git -C vendor/sports-method remote add origin "$REPO"
fi
git -C vendor/sports-method fetch -q --depth 1 origin "$SHA"
git -C vendor/sports-method checkout -q FETCH_HEAD
echo "sports-method code at $(git -C vendor/sports-method rev-parse --short HEAD)"

if [ "$MODE" != "code-only" ]; then
  rm -rf vendor/sports-method-data
  git clone -q --depth 1 --branch "$BRANCH" "$REPO" vendor/sports-method-data
  echo "sports-method data branch at $(git -C vendor/sports-method-data rev-parse --short HEAD): $(find vendor/sports-method-data/data -type f | wc -l) files"
fi
