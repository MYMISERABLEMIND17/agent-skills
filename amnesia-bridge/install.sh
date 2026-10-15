#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "🧠 Installing Amnesia Bridge (Negative Knowledge Ledger)"
echo "=========================================================="

GEMINI_SKILLS_DIR="$HOME/.gemini/config/skills/amnesia-bridge"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills/amnesia-bridge"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$GEMINI_SKILLS_DIR"
mkdir -p "$CLAUDE_SKILLS_DIR"
mkdir -p "$LOCAL_BIN_DIR"

chmod +x "$SCRIPT_DIR/scripts/failure_ledger.py"

# 1. Install skill to Antigravity / Gemini CLI
echo "📦 Installing skill to Antigravity (~/.gemini/config/skills/amnesia-bridge)..."
cp "$SCRIPT_DIR/SKILL.md" "$GEMINI_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$GEMINI_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$GEMINI_SKILLS_DIR/"

# 2. Install skill to Claude Code
echo "📦 Installing skill to Claude Code (~/.claude/skills/amnesia-bridge)..."
cp "$SCRIPT_DIR/SKILL.md" "$CLAUDE_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$CLAUDE_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$CLAUDE_SKILLS_DIR/"

# 3. Create global CLI shortcut `amnesia-bridge`
echo "⚡ Creating global CLI shortcut in $LOCAL_BIN_DIR/amnesia-bridge..."
cat << 'EOF' > "$LOCAL_BIN_DIR/amnesia-bridge"
#!/usr/bin/env bash
# Global shortcut for Amnesia Bridge Ledger CLI

SOURCE_DIR="$HOME/.gemini/config/skills/amnesia-bridge"

case "$1" in
    cursor)
        mkdir -p .cursor/rules
        cp "$SOURCE_DIR/templates/cursor_rule.mdc" .cursor/rules/amnesia-bridge.mdc
        cp "$SOURCE_DIR/templates/.cursorrules" .cursorrules
        echo "✅ Installed Amnesia Bridge Cursor rules into $(pwd)"
        ;;
    *)
        python3 "$SOURCE_DIR/scripts/failure_ledger.py" "$@"
        ;;
esac
EOF
chmod +x "$LOCAL_BIN_DIR/amnesia-bridge"

echo ""
echo "=========================================================="
echo "✅ Installation Complete!"
echo "=========================================================="
echo ""
echo "How to use:"
echo "1. In Antigravity / Claude Code: Ask: 'Use amnesia-bridge to check if this fix was tried before'"
echo "2. In Terminal:                  Run 'amnesia-bridge check <query>' or 'amnesia-bridge record ...'"
echo "3. In Cursor:                    Run 'amnesia-bridge cursor' to install rules to current project"
echo ""
