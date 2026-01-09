#!/bin/bash

# ============================================================================
# Setup Programming Best Practices Knowledge Base for Your Project
# ============================================================================
#
# This script helps you integrate the Programming Best Practices knowledge base
# into your existing project.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/dereknguyen269/programing-best-practices/main/scripts/setup-kb.sh | bash
#
# Or download and run:
#   chmod +x setup-kb.sh
#   ./setup-kb.sh
#
# ============================================================================

set -e

REPO_URL="https://github.com/dereknguyen269/programing-best-practices"
TEMPLATES_URL="https://raw.githubusercontent.com/dereknguyen269/programing-best-practices/main/templates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=============================================="
echo "  Programming Best Practices - KB Setup"
echo "=============================================="
echo -e "${NC}"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Warning: Not in a git repository root.${NC}"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo "Exiting."
        exit 1
    fi
fi

echo ""
echo "How would you like to integrate the knowledge base?"
echo ""
echo "  1) Git Submodule (keeps KB updated with repo)"
echo "  2) Copy Templates Only (static, no dependency)"
echo "  3) Add References to Existing Config"
echo ""
read -p "Choose an option (1-3): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Setting up as Git Submodule...${NC}"
        
        # Create .kb directory if it doesn't exist
        mkdir -p .kb
        
        # Add submodule
        git submodule add $REPO_URL .kb/best-practices
        
        echo -e "${GREEN}✓ Submodule added at .kb/best-practices${NC}"
        echo ""
        echo "To update the knowledge base later, run:"
        echo "  git submodule update --remote .kb/best-practices"
        ;;
        
    2)
        echo -e "\n${GREEN}Copying Templates...${NC}"
        
        # Create directories
        mkdir -p .agent
        mkdir -p .kiro
        
        # Download templates
        echo "Downloading CLAUDE.md template..."
        curl -sSL "$TEMPLATES_URL/CLAUDE.template.md" -o CLAUDE.md
        
        echo "Downloading .agent templates..."
        curl -sSL "$TEMPLATES_URL/agent/instructions.template.md" -o .agent/instructions.md
        curl -sSL "$TEMPLATES_URL/agent/config.template.json" -o .agent/config.json
        
        echo "Downloading .kiro template..."
        curl -sSL "$TEMPLATES_URL/kiro/project.template.md" -o .kiro/project.md
        
        echo "Downloading .cursorrules template..."
        curl -sSL "$TEMPLATES_URL/cursorrules.template" -o .cursorrules
        
        echo -e "${GREEN}✓ Templates copied${NC}"
        echo ""
        echo "Please edit the following files and replace placeholders:"
        echo "  - CLAUDE.md"
        echo "  - .agent/instructions.md"
        echo "  - .agent/config.json"
        echo "  - .kiro/project.md"
        echo "  - .cursorrules"
        ;;
        
    3)
        echo -e "\n${GREEN}Adding References...${NC}"
        
        # Create or append to CLAUDE.md
        if [ -f "CLAUDE.md" ]; then
            echo "" >> CLAUDE.md
            echo "## Best Practices Reference" >> CLAUDE.md
            echo "" >> CLAUDE.md
            echo "This project follows the [Programming Best Practices](https://github.com/dereknguyen269/programing-best-practices) knowledge base." >> CLAUDE.md
            echo "" >> CLAUDE.md
            echo "Key resources:" >> CLAUDE.md
            echo "- Code Style: Check language-specific sections" >> CLAUDE.md
            echo "- Security: API Security and DevSecOps sections" >> CLAUDE.md
            echo "- Architecture: System Design section" >> CLAUDE.md
            echo -e "${GREEN}✓ Added reference to existing CLAUDE.md${NC}"
        else
            echo "## Best Practices Reference" > CLAUDE.md
            echo "" >> CLAUDE.md
            echo "This project follows the [Programming Best Practices](https://github.com/dereknguyen269/programing-best-practices) knowledge base." >> CLAUDE.md
            echo "" >> CLAUDE.md
            echo "Key resources:" >> CLAUDE.md
            echo "- Code Style: Check language-specific sections" >> CLAUDE.md
            echo "- Security: API Security and DevSecOps sections" >> CLAUDE.md
            echo "- Architecture: System Design section" >> CLAUDE.md
            echo -e "${GREEN}✓ Created CLAUDE.md with reference${NC}"
        fi
        ;;
        
    *)
        echo -e "${RED}Invalid option. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=============================================="
echo "  Setup Complete!"
echo "==============================================${NC}"
echo ""
echo "Knowledge Base Repository:"
echo "  $REPO_URL"
echo ""
echo "Documentation:"
echo "  https://github.com/dereknguyen269/programing-best-practices/blob/main/docs/INTEGRATION.md"
echo ""
