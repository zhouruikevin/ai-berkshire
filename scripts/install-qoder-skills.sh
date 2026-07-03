#!/usr/bin/env bash
set -euo pipefail

# 项目内使用无需安装：用 Qoder 打开本仓库即自动加载 .qoder/skills（项目级）。
# 本脚本用于把技能安装到用户级目录，供跨项目使用。

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${QODER_HOME:-$HOME/.qoder}/skills"

python3 "$ROOT/scripts/sync-qoder-skills.py"
mkdir -p "$DEST"

for skill_dir in "$ROOT"/.qoder/skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  rm -rf "$DEST/$name"
  cp -R "$skill_dir" "$DEST/$name"
done

chmod +x "$ROOT"/tools/*.py "$ROOT"/tools/*.sh 2>/dev/null || true

echo "Installed Qoder skills to $DEST"
echo "项目内使用无需安装：用 Qoder 打开本仓库即自动加载 .qoder/skills（项目级）。"
echo "Restart Qoder to pick up user-level skills."
