#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "🧐 Installing Loop Engineer (Human-Proxy Auditor) Skill"
echo "=========================================================="

GEMINI_SKILLS_DIR="$HOME/.gemini/config/skills/loop-engineer"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills/loop-engineer"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$GEMINI_SKILLS_DIR"
mkdir -p "$CLAUDE_SKILLS_DIR"
mkdir -p "$LOCAL_BIN_DIR"

chmod +x "$SCRIPT_DIR/scripts/audit_trajectory.py"

# 1. Install skill to Antigravity / Gemini CLI
echo "📦 Installing skill to Antigravity (~/.gemini/config/skills/loop-engineer)..."
cp "$SCRIPT_DIR/SKILL.md" "$GEMINI_SKILLS_DIR/SKILL.md"

# 2. Install skill to Claude Code
echo "📦 Installing skill to Claude Code (~/.claude/skills/loop-engineer)..."
cp "$SCRIPT_DIR/SKILL.md" "$CLAUDE_SKILLS_DIR/SKILL.md"

# 3. Create global CLI shortcut `loop-engineer`
echo "⚡ Creating global CLI shortcut in $LOCAL_BIN_DIR/loop-engineer..."
cat << 'EOF' > "$LOCAL_BIN_DIR/loop-engineer"
#!/usr/bin/env bash
# Global shortcut for Loop Engineer Trajectory Auditor

SOURCE_DIR="$(dirname "$(realpath "$0")")/../../Desktop/MY RAN IDEAS/loop-engineer"
if [ ! -d "$SOURCE_DIR" ]; then
    SOURCE_DIR="$HOME/Desktop/MY RAN IDEAS/loop-engineer"
fi

case "$1" in
    cursor)
        mkdir -p .cursor/rules
        cp "$SOURCE_DIR/templates/cursor_rule.mdc" .cursor/rules/loop-engineer.mdc
        cp "$SOURCE_DIR/templates/.cursorrules" .cursorrules
        echo "✅ Installed Loop Engineer Cursor rules into $(pwd)"
        ;;
    audit|scan|check|*)
        shift || true
        python3 "$SOURCE_DIR/scripts/audit_trajectory.py" "$@"
        ;;
esac
EOF
chmod +x "$LOCAL_BIN_DIR/loop-engineer"

# 4. Also update ~/.local/bin/autopilot to support audit command
if [ -f "$LOCAL_BIN_DIR/autopilot" ]; then
    sed -i '/case "\$1" in/a \    audit)\n        shift\n        python3 "'"$SCRIPT_DIR"'/scripts/audit_trajectory.py" "$@"\n        ;;\n' "$LOCAL_BIN_DIR/autopilot" 2>/dev/null || true
fi

echo ""
echo "=========================================================="
echo "✅ Installation Complete!"
echo "=========================================================="
echo ""
echo "How to use:"
echo "1. In Antigravity / Claude Code: Ask: 'Use loop-engineer to audit the agent work and verify if we are on the right track'"
echo "2. In Terminal:                  Run 'loop-engineer' or 'autopilot audit' to scan current diffs for stubs, cheats, or errors"
echo "3. In Cursor:                    Run 'loop-engineer cursor' to add the rule to your project"
echo ""
