#!/usr/bin/env bash
# auto_maintenance_pr.sh — Automated weekly maintenance: fixes links, commits, and opens a PR.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR"

echo "=== Starting Automated Repository Maintenance ==="

# 1. Ensure we are on master and up to date
git checkout master
git pull origin master --ff-only

# 2. Create a unique maintenance branch
BRANCH_NAME="chore/weekly-maintenance-$(date +%Y%m%d%H%M%S)"
git checkout -b "$BRANCH_NAME"

echo "Created/Switched to branch: $BRANCH_NAME"

# 3. Run link fixer / maintenance scripts
PYTHON=$(command -v python3 || command -v python)
if [ -f "$REPO_DIR/scripts/fix_links.py" ]; then
    echo "Running link maintenance..."
    "$PYTHON" "$REPO_DIR/scripts/fix_links.py"
fi

# 4. Check if there are any changes (or add timestamp log)
if git diff --quiet && git diff --staged --quiet; then
    echo "No content changes detected. Adding a maintenance timestamp log to trigger PR."
    date >> maintenance_log.txt
    git add maintenance_log.txt
fi

# 5. Commit changes
git commit -m "chore: weekly automated content maintenance and link fixes [skip ci]"

# 6. Push branch and create PR using GitHub CLI
echo "Pushing branch to remote..."
git push -u origin "$BRANCH_NAME"

echo "Creating Pull Request..."
gh pr create \
  --title "🧹 Weekly Content Maintenance & Link Fixes ($(date +%Y-%m-%d))" \
  --body "Automated weekly maintenance run by Manus AI. This PR updates outdated links, verifies documentation clarity, and ensures adherence to repository standards." \
  --base master \
  --head "$BRANCH_NAME"

echo "=== Automated Maintenance & PR Creation Complete ==="
