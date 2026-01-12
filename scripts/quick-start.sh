#!/bin/bash

# ============================================================================
# Programming Best Practices - Quick Start Setup Script
# ============================================================================
#
# This script automates the initial setup of the Programming Best Practices
# repository, including:
#   - Dependency installation
#   - Python virtual environment setup
#   - Optional content crawling
#   - AI summary generation
#
# Usage:
#   ./scripts/quick-start.sh [OPTIONS]
#
# Options:
#   --full          Full setup including crawling all resources
#   --minimal       Minimal setup (dependencies only, no crawling)
#   --crawl-only    Only run the crawler (skip dependency check)
#   --limit N       Crawl only N resources (for testing)
#   --category CAT  Crawl only specific category
#   --help          Show this help message
#
# Examples:
#   ./scripts/quick-start.sh --minimal
#   ./scripts/quick-start.sh --full
#   ./scripts/quick-start.sh --limit 20
#   ./scripts/quick-start.sh --category python
#
# ============================================================================

set -e

# Default options
SETUP_MODE="interactive"
CRAWL_LIMIT=""
CRAWL_CATEGORY=""
SKIP_DEPS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Emoji support
CHECK_MARK="✓"
CROSS_MARK="✗"
ROCKET="🚀"
PACKAGE="📦"
SPIDER="🕷️"
BRAIN="🤖"
SPARKLES="✨"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "=============================================================================="
    echo "  $1"
    echo "=============================================================================="
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${CYAN}${BOLD}▶ $1${NC}\n"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    printf "%bProgramming Best Practices - Quick Start Setup%b\n\n" "${BOLD}" "${NC}"
    printf "%bUSAGE:%b\n" "${BOLD}" "${NC}"
    printf "    ./scripts/quick-start.sh [OPTIONS]\n\n"
    printf "%bOPTIONS:%b\n" "${BOLD}" "${NC}"
    printf "    --full              Full setup including crawling all resources (~10-15 min)\n"
    printf "    --minimal           Minimal setup (dependencies only, no crawling)\n"
    printf "    --crawl-only        Only run the crawler (skip dependency check)\n"
    printf "    --limit N           Crawl only N resources (for testing)\n"
    printf "    --category CAT      Crawl only specific category (e.g., python, javascript)\n"
    printf "    --help              Show this help message\n\n"
    printf "%bEXAMPLES:%b\n" "${BOLD}" "${NC}"
    printf "    %b# Interactive setup (recommended for first-time users)%b\n" "${CYAN}" "${NC}"
    printf "    ./scripts/quick-start.sh\n\n"
    printf "    %b# Quick minimal setup%b\n" "${CYAN}" "${NC}"
    printf "    ./scripts/quick-start.sh --minimal\n\n"
    printf "    %b# Full setup with all content%b\n" "${CYAN}" "${NC}"
    printf "    ./scripts/quick-start.sh --full\n\n"
    printf "    %b# Test with limited crawling%b\n" "${CYAN}" "${NC}"
    printf "    ./scripts/quick-start.sh --limit 20\n\n"
    printf "    %b# Crawl only Python resources%b\n" "${CYAN}" "${NC}"
    printf "    ./scripts/quick-start.sh --category python\n\n"
    printf "%bCATEGORIES:%b\n" "${BOLD}" "${NC}"
    printf "    python, javascript, ruby, go, java, php, rust, typescript,\n"
    printf "    react, vue, angular, docker, kubernetes, aws, and more...\n\n"
    exit 0
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            SETUP_MODE="full"
            shift
            ;;
        --minimal)
            SETUP_MODE="minimal"
            shift
            ;;
        --crawl-only)
            SETUP_MODE="crawl-only"
            SKIP_DEPS=true
            shift
            ;;
        --limit)
            CRAWL_LIMIT="$2"
            shift 2
            ;;
        --category)
            CRAWL_CATEGORY="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# Main Setup
# ============================================================================

print_header "${ROCKET} Programming Best Practices - Quick Start Setup"

echo -e "${BOLD}Welcome!${NC} This script will help you set up the repository.\n"

# ============================================================================
# Step 1: Check System Requirements
# ============================================================================

if [ "$SKIP_DEPS" = false ]; then
    print_section "${PACKAGE} Step 1: Checking System Requirements"

    MISSING_DEPS=false

    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_info "Python version: $PYTHON_VERSION"
    else
        MISSING_DEPS=true
    fi

    # Check pip
    if check_command pip3; then
        PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
        print_info "pip version: $PIP_VERSION"
    else
        MISSING_DEPS=true
    fi

    # Check git
    if check_command git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_info "Git version: $GIT_VERSION"
    else
        MISSING_DEPS=true
    fi

    if [ "$MISSING_DEPS" = true ]; then
        echo ""
        print_error "Some required dependencies are missing."
        print_info "Please install the missing dependencies and try again."
        echo ""
        echo "Installation guides:"
        echo "  - Python 3: https://www.python.org/downloads/"
        echo "  - pip: Usually comes with Python"
        echo "  - Git: https://git-scm.com/downloads"
        exit 1
    fi

    print_success "All system requirements met!"
fi

# ============================================================================
# Step 2: Interactive Mode Selection
# ============================================================================

if [ "$SETUP_MODE" = "interactive" ]; then
    print_section "${SPARKLES} Step 2: Choose Setup Mode"

    printf "Select your setup preference:\n\n"
    printf "  %b1)%b %bMinimal Setup%b (Fast, ~1 minute)\n" "${BOLD}" "${NC}" "${GREEN}" "${NC}"
    printf "     - Install Python dependencies only\n"
    printf "     - No content crawling\n"
    printf "     - Good for: Browsing the README, using as reference\n\n"
    
    printf "  %b2)%b %bTest Setup%b (Medium, ~2-3 minutes)\n" "${BOLD}" "${NC}" "${YELLOW}" "${NC}"
    printf "     - Install dependencies\n"
    printf "     - Crawl 20 sample resources\n"
    printf "     - Good for: Testing the crawler, trying it out\n\n"
    
    printf "  %b3)%b %bFull Setup%b (Slow, ~10-15 minutes)\n" "${BOLD}" "${NC}" "${BLUE}" "${NC}"
    printf "     - Install dependencies\n"
    printf "     - Crawl all 150+ resources\n"
    printf "     - Generate AI summaries\n"
    printf "     - Good for: Offline access, AI integration\n\n"
    
    printf "  %b4)%b %bCustom Setup%b\n" "${BOLD}" "${NC}" "${MAGENTA}" "${NC}"
    printf "     - Choose specific category to crawl\n\n"
    
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            SETUP_MODE="minimal"
            ;;
        2)
            SETUP_MODE="test"
            CRAWL_LIMIT="20"
            ;;
        3)
            SETUP_MODE="full"
            ;;
        4)
            SETUP_MODE="custom"
            echo ""
            echo "Available categories:"
            echo "  python, javascript, ruby, rails, go, java, php, rust,"
            echo "  typescript, react, vue, angular, docker, kubernetes, aws"
            echo ""
            read -p "Enter category name: " CRAWL_CATEGORY
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# ============================================================================
# Step 3: Setup Python Virtual Environment
# ============================================================================

if [ "$SKIP_DEPS" = false ]; then
    print_section "${PACKAGE} Step 3: Setting Up Python Environment"

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source .venv/bin/activate

    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r scripts/crawler/requirements.txt

    print_success "Python environment ready!"
fi

# ============================================================================
# Step 4: Run Crawler (if needed)
# ============================================================================

if [ "$SETUP_MODE" != "minimal" ]; then
    print_section "${SPIDER} Step 4: Crawling Best Practices Content"

    # Build crawler command
    CRAWLER_CMD="python3 scripts/crawler/crawl.py"

    if [ -n "$CRAWL_LIMIT" ]; then
        CRAWLER_CMD="$CRAWLER_CMD --limit $CRAWL_LIMIT"
        print_info "Crawling $CRAWL_LIMIT resources..."
    elif [ -n "$CRAWL_CATEGORY" ]; then
        CRAWLER_CMD="$CRAWLER_CMD --category $CRAWL_CATEGORY"
        print_info "Crawling $CRAWL_CATEGORY resources..."
    else
        print_info "Crawling all resources (this may take 10-15 minutes)..."
    fi

    # Run crawler
    if $CRAWLER_CMD; then
        print_success "Content crawling completed!"
        
        # Check for failed URLs report
        if [ -f "content/failed_urls_report.md" ]; then
            echo ""
            print_warning "Some URLs failed to crawl. See report for details:"
            print_info "content/failed_urls_report.md"
        fi
    else
        print_warning "Crawler encountered some errors, but continued"
    fi
fi

# ============================================================================
# Step 5: Generate AI Summaries (full mode only)
# ============================================================================

if [ "$SETUP_MODE" = "full" ]; then
    print_section "${BRAIN} Step 5: Generating AI Summaries"

    print_info "Creating condensed summaries for AI assistants..."
    
    if python3 scripts/crawler/generate_summaries.py; then
        print_success "AI summaries generated!"
    else
        print_warning "Summary generation encountered errors"
    fi
fi

# ============================================================================
# Final Summary
# ============================================================================

print_header "${SPARKLES} Setup Complete!"

echo -e "${GREEN}${BOLD}Congratulations!${NC} Your Programming Best Practices repository is ready.\n"

# Show what was set up
echo -e "${BOLD}What's been set up:${NC}"
if [ "$SKIP_DEPS" = false ]; then
    echo "  ${CHECK_MARK} Python virtual environment (.venv)"
    echo "  ${CHECK_MARK} Crawler dependencies installed"
fi

if [ "$SETUP_MODE" != "minimal" ]; then
    echo "  ${CHECK_MARK} Content crawled to ./content/"
    
    if [ -f "content/metadata.yaml" ]; then
        # Try to show crawl stats if available
        CRAWLED_COUNT=$(grep -c "url:" content/metadata.yaml 2>/dev/null || echo "N/A")
        echo "  ${CHECK_MARK} Resources crawled: $CRAWLED_COUNT"
    fi
fi

if [ "$SETUP_MODE" = "full" ]; then
    echo "  ${CHECK_MARK} AI summaries generated in ./summaries/"
fi

echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo "  ${CYAN}1. Browse the Knowledge Base${NC}"
echo "     Open README.md to explore 30+ languages and frameworks"
echo ""
echo "  ${CYAN}2. Search Locally${NC}"
if [ "$SETUP_MODE" != "minimal" ]; then
    echo "     python3 scripts/crawler/search.py \"your search term\""
else
    echo "     (Run crawler first to enable local search)"
fi
echo ""
echo "  ${CYAN}3. Use with AI Coding Editors${NC}"
echo "     Your AI editor will auto-detect:"
echo "     - Claude Code (CLAUDE.md)"
echo "     - Antigravity (.agent/instructions.md)"
echo "     - Kiro (.kiro/project.md)"
echo "     - Cursor (.cursorrules)"
echo "     - Windsurf (.windsurfrules)"
echo ""
echo "  ${CYAN}4. Integrate into Your Projects${NC}"
echo "     ./scripts/setup-kb.sh"
echo ""

if [ "$SETUP_MODE" = "minimal" ]; then
    echo -e "${YELLOW}${BOLD}Want offline access?${NC}"
    echo "  Run: ./scripts/quick-start.sh --full"
    echo ""
fi

echo -e "${BOLD}Useful Commands:${NC}"
echo ""
echo "  # Activate virtual environment first"
echo "  source .venv/bin/activate"
echo ""
echo "  # Update crawled content"
echo "  python3 scripts/crawler/crawl.py --update"
echo ""
echo "  # Search for content"
echo "  python3 scripts/crawler/search.py \"javascript best practices\""
echo ""
echo "  # Crawl specific category"
echo "  python3 scripts/crawler/crawl.py --category python"
echo ""
echo "  # Re-generate summaries"
echo "  python3 scripts/crawler/generate_summaries.py"
echo ""

echo -e "${GREEN}${BOLD}Happy Coding! ${ROCKET}${NC}"
echo ""
echo "Documentation: https://github.com/dereknguyen269/programing-best-practices"
echo "Issues: https://github.com/dereknguyen269/programing-best-practices/issues"
echo ""
