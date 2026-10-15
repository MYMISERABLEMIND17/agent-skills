#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "🚀 Installing Overnight Autopilot Skill & Tooling"
echo "=========================================================="

# 1. Ensure directories exist
GEMINI_SKILLS_DIR="$HOME/.gemini/config/skills/overnight-autopilot"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills/overnight-autopilot"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$GEMINI_SKILLS_DIR"
mkdir -p "$CLAUDE_SKILLS_DIR"
mkdir -p "$LOCAL_BIN_DIR"

# 2. Make scripts executable
chmod +x "$SCRIPT_DIR/scripts/autopilot_init.py"
chmod +x "$SCRIPT_DIR/scripts/overnight_loop.py"

# 3. Install skill to Antigravity / Gemini CLI
echo "📦 Installing skill to Antigravity (~/.gemini/config/skills/overnight-autopilot)..."
cp "$SCRIPT_DIR/SKILL.md" "$GEMINI_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$GEMINI_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$GEMINI_SKILLS_DIR/"

# 4. Install skill to Claude Code
echo "📦 Installing skill to Claude Code (~/.claude/skills/overnight-autopilot)..."
cp "$SCRIPT_DIR/SKILL.md" "$CLAUDE_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$CLAUDE_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$CLAUDE_SKILLS_DIR/"

# 5. Create global CLI shortcut `autopilot` in ~/.local/bin
echo "⚡ Creating global CLI shortcut in $LOCAL_BIN_DIR/autopilot..."
cat << 'EOF' > "$LOCAL_BIN_DIR/autopilot"
#!/usr/bin/env bash
# Global shortcut for Overnight Autopilot

SOURCE_DIR="$HOME/.gemini/config/skills/overnight-autopilot"

case "$1" in
    init)
        shift
        python3 "$SOURCE_DIR/scripts/autopilot_init.py" "$@"
        ;;
    run|loop|start)
        shift
        python3 "$SOURCE_DIR/scripts/overnight_loop.py" "$@"
        ;;
    cursor)
        mkdir -p .cursor/rules
        cp "$SOURCE_DIR/templates/cursor_rule.mdc" .cursor/rules/overnight-autopilot.mdc
        cp "$SOURCE_DIR/templates/.cursorrules" .cursorrules
        echo "✅ Installed Cursor rules in $(pwd) (.cursor/rules/overnight-autopilot.mdc and .cursorrules)"
        ;;
    *)
        echo "🌙 Overnight Autopilot CLI"
        echo ""
        echo "Usage:"
        echo "  autopilot init '<Objective>' [task 1] [task 2]...  - Initialize progress ledger & git branch"
        echo "  autopilot run [--agent claude|agy]                 - Run the continuous overnight execution loop"
        echo "  autopilot cursor                                  - Install Cursor rules into current project"
        echo ""
        echo "Direct Agent Chat Commands:"
        echo "  Claude Code / Antigravity: Ask: 'Use the overnight-autopilot skill to build X'"
        ;;
esac
EOF
chmod +x "$LOCAL_BIN_DIR/autopilot"

echo ""
echo "=========================================================="
echo "✅ Installation Complete!"
echo "=========================================================="
echo ""
echo "How to use:"
echo "1. In Claude Code:     claude --dangerously-skip-permissions"
echo "                       Then say: 'Use the overnight-autopilot skill to build <feature>'"
echo "2. In Antigravity:     Simply prompt: 'Activate overnight-autopilot and build <feature>'"
echo "3. In Cursor:          Run 'autopilot cursor' inside your project, or paste templates/.cursorrules"
echo "4. Autonomous Loop:    Run 'autopilot init \"My Feature\"' followed by 'autopilot run'"
echo ""
