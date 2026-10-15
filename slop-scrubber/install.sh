#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "🧹 Installing Slop Scrubber (Code Hygiene & Cruft Cleaner)"
echo "=========================================================="

GEMINI_SKILLS_DIR="$HOME/.gemini/config/skills/slop-scrubber"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills/slop-scrubber"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$GEMINI_SKILLS_DIR"
mkdir -p "$CLAUDE_SKILLS_DIR"
mkdir -p "$LOCAL_BIN_DIR"

chmod +x "$SCRIPT_DIR/scripts/scrub_slop.py"

# 1. Install skill to Antigravity / Gemini CLI
echo "📦 Installing skill to Antigravity (~/.gemini/config/skills/slop-scrubber)..."
cp "$SCRIPT_DIR/SKILL.md" "$GEMINI_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$GEMINI_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$GEMINI_SKILLS_DIR/"

# 2. Install skill to Claude Code
echo "📦 Installing skill to Claude Code (~/.claude/skills/slop-scrubber)..."
cp "$SCRIPT_DIR/SKILL.md" "$CLAUDE_SKILLS_DIR/SKILL.md"
cp -r "$SCRIPT_DIR/scripts" "$CLAUDE_SKILLS_DIR/"
cp -r "$SCRIPT_DIR/templates" "$CLAUDE_SKILLS_DIR/"

# 3. Create global CLI shortcut `slop-scrubber`
echo "⚡ Creating global CLI shortcut in $LOCAL_BIN_DIR/slop-scrubber..."
cat << 'EOF' > "$LOCAL_BIN_DIR/slop-scrubber"
#!/usr/bin/env bash
# Global shortcut for Slop Scrubber CLI

SOURCE_DIR="$HOME/.gemini/config/skills/slop-scrubber"

case "$1" in
    cursor)
        mkdir -p .cursor/rules
        cp "$SOURCE_DIR/templates/cursor_rule.mdc" .cursor/rules/slop-scrubber.mdc
        cp "$SOURCE_DIR/templates/.cursorrules" .cursorrules
        echo "✅ Installed Slop Scrubber Cursor rules into $(pwd)"
        ;;
    *)
        python3 "$SOURCE_DIR/scripts/scrub_slop.py" "$@"
        ;;
esac
EOF
chmod +x "$LOCAL_BIN_DIR/slop-scrubber"

echo ""
echo "=========================================================="
echo "✅ Installation Complete!"
echo "=========================================================="
echo ""
echo "How to use:"
echo "1. In Antigravity / Claude Code: Ask: 'Use slop-scrubber to sanitize my git diff before commit'"
echo "2. In Terminal:                  Run 'slop-scrubber scan', 'slop-scrubber clean', or 'slop-scrubber verify'"
echo "3. In Cursor:                    Run 'slop-scrubber cursor' to install rules to current project"
echo ""
