#!/bin/bash
#
# setup-qoder.sh — 一键同步 Qoder 本地环境
#
# 将 git-tracked 的 skills/*.md 和 CLAUDE.md 同步到 .qoder/ 目录。
# Qoder 不跟随软链接，因此使用 cp 拷贝方式。
#
# 用法：
#   bash setup-qoder.sh          # 同步全部
#   bash setup-qoder.sh --watch  # 监听变更自动同步（需 fswatch）
#
# 修改 skills/*.md 或 CLAUDE.md 后重新运行即可同步到 Qoder。
#

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

SKILLS=(
  bottleneck-hunter deep-company-series dyp-ask earnings-review earnings-team
  financial-data industry-funnel industry-research investment-checklist
  investment-research investment-team management-deep-dive news-pulse
  portfolio-review private-company-research quality-screen thesis-tracker
  wechat-article
)

sync_skills() {
  echo "📦 同步 Skills..."
  for skill in "${SKILLS[@]}"; do
    SOURCE="skills/$skill.md"
    TARGET_DIR=".qoder/skills/$skill"
    TARGET="$TARGET_DIR/SKILL.md"

    if [ ! -f "$SOURCE" ]; then
      echo "   ⚠️  $SOURCE 不存在，跳过"
      continue
    fi

    mkdir -p "$TARGET_DIR"
    # 删除旧的（可能是软链接或旧文件）
    rm -f "$TARGET"
    cp "$SOURCE" "$TARGET"
    echo "   ✅ $skill"
  done
}

sync_rules() {
  echo "📋 同步 Rules..."
  mkdir -p .qoder/rules
  rm -f .qoder/rules/project-rules.md
  cp CLAUDE.md .qoder/rules/project-rules.md
  echo "   ✅ project-rules.md"
}

# ─── 主逻辑 ───

if [ "$1" = "--watch" ]; then
  # 监听模式
  if ! command -v fswatch &> /dev/null; then
    echo "❌ --watch 模式需要 fswatch，请运行: brew install fswatch"
    exit 1
  fi
  echo "👀 监听模式启动（Ctrl+C 退出）"
  echo "   修改 skills/*.md 或 CLAUDE.md 会自动同步到 .qoder/"
  echo ""
  # 初次同步
  sync_skills
  sync_rules
  echo ""
  # 监听变更
  fswatch -o skills/ CLAUDE.md | while read; do
    echo "$(date '+%H:%M:%S') 检测到变更，同步中..."
    sync_skills
    sync_rules
    echo ""
  done
else
  # 单次同步模式
  echo "🔧 同步 Qoder 本地环境"
  echo "   项目根目录: $PROJECT_ROOT"
  echo ""
  sync_skills
  echo ""
  sync_rules
  echo ""
  echo "🎉 完成！"
  echo ""
  echo "   维护方式："
  echo "   - 编辑 skills/*.md 或 CLAUDE.md"
  echo "   - 运行 bash setup-qoder.sh 同步到 Qoder"
  echo "   - 或用 bash setup-qoder.sh --watch 自动同步"
  echo "   - 新机器克隆后运行一次即可"
fi
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
