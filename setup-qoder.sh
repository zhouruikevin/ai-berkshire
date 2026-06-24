#!/bin/bash
#
# setup-qoder.sh — 一键配置 Qoder 本地环境
#
# 将 git-tracked 的 skills/*.md 和 CLAUDE.md 通过软链接映射到 .qoder/ 目录，
# 实现单一数据源：修改 skills/*.md 或 CLAUDE.md 一处，Claude Code 和 Qoder 同时生效。
#
# 用法：bash setup-qoder.sh
# 可重复运行，已存在的软链接会被安全替换。
#

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "🔧 配置 Qoder 本地环境（软链接模式）"
echo "   项目根目录: $PROJECT_ROOT"
echo ""

# ─── 1. Skills 软链接 ───
echo "📦 创建 Skills 软链接..."

SKILLS=(
  bottleneck-hunter deep-company-series dyp-ask earnings-review earnings-team
  financial-data industry-funnel industry-research investment-checklist
  investment-research investment-team management-deep-dive news-pulse
  portfolio-review private-company-research quality-screen thesis-tracker
  wechat-article
)

for skill in "${SKILLS[@]}"; do
  SOURCE="skills/$skill.md"
  TARGET_DIR=".qoder/skills/$skill"
  TARGET="$TARGET_DIR/SKILL.md"

  if [ ! -f "$SOURCE" ]; then
    echo "   ⚠️  $SOURCE 不存在，跳过"
    continue
  fi

  # 创建目标目录
  mkdir -p "$TARGET_DIR"

  # 如果已存在（文件或软链接），先删除
  if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    rm "$TARGET"
  fi

  # 创建软链接（相对路径，便于项目目录整体移动）
  ln -s "../../../$SOURCE" "$TARGET"
  echo "   ✅ $skill → $SOURCE"
done

echo ""

# ─── 2. Rules 软链接 ───
echo "📋 创建 Rules 软链接..."

RULES_DIR=".qoder/rules"
mkdir -p "$RULES_DIR"

RULES_TARGET="$RULES_DIR/project-rules.md"
if [ -e "$RULES_TARGET" ] || [ -L "$RULES_TARGET" ]; then
  rm "$RULES_TARGET"
fi
ln -s "../../CLAUDE.md" "$RULES_TARGET"
echo "   ✅ project-rules.md → CLAUDE.md"

echo ""
echo "🎉 完成！Qoder 环境已配置。"
echo ""
echo "   维护方式："
echo "   - 修改 Skill → 编辑 skills/*.md"
echo "   - 修改项目规则 → 编辑 CLAUDE.md"
echo "   - 两处修改对 Claude Code 和 Qoder 同时生效，无需额外操作"
echo "   - 新机器克隆后运行 bash setup-qoder.sh 即可"
