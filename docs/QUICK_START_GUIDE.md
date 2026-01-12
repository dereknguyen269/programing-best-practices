# Quick Start Setup Script

## Overview

The `quick-start.sh` script automates the initial setup of the Programming Best Practices repository. It handles dependency installation, Python virtual environment setup, content crawling, and AI summary generation.

## Features

- ✅ **Interactive Mode** - Guided setup with multiple options
- ✅ **Automated Dependency Checking** - Verifies Python, pip, and Git
- ✅ **Virtual Environment Management** - Creates and activates Python venv
- ✅ **Flexible Crawling Options** - Full, partial, or category-specific
- ✅ **AI Summary Generation** - Creates condensed summaries for AI assistants
- ✅ **Beautiful CLI Output** - Color-coded, emoji-enhanced interface

## Setup Process Flow

![Quick Start Setup Process](images/quick-start-flowchart.png)


## Quick Start

### Interactive Setup (Recommended)

```bash
./scripts/quick-start.sh
```

This will present you with 4 options:

1. **Minimal Setup** (~1 minute)
   - Install Python dependencies only
   - No content crawling
   - Best for: Browsing README, using as reference

2. **Test Setup** (~2-3 minutes)
   - Install dependencies
   - Crawl 20 sample resources
   - Best for: Testing the crawler, trying it out

3. **Full Setup** (~10-15 minutes)
   - Install dependencies
   - Crawl all 150+ resources
   - Generate AI summaries
   - Best for: Offline access, AI integration

4. **Custom Setup** (Varies)
   - Choose specific category to crawl
   - Best for: Focused learning on specific technologies

## Command-Line Options

### Basic Options

```bash
# Show help message
./scripts/quick-start.sh --help

# Minimal setup (dependencies only)
./scripts/quick-start.sh --minimal

# Full setup (everything)
./scripts/quick-start.sh --full

# Crawler only (skip dependency check)
./scripts/quick-start.sh --crawl-only
```

### Advanced Options

```bash
# Crawl limited number of resources
./scripts/quick-start.sh --limit 20
./scripts/quick-start.sh --limit 50

# Crawl specific category
./scripts/quick-start.sh --category python
./scripts/quick-start.sh --category javascript
./scripts/quick-start.sh --category react

# Combine options
./scripts/quick-start.sh --category ruby --limit 10
```

## Available Categories

The `--category` option supports the following categories:

### Backend Languages
- `python`
- `ruby`
- `rails`
- `php`
- `laravel`
- `java`
- `kotlin`
- `scala`
- `go`
- `rust`
- `elixir`
- `nodejs`
- `nestjs`

### Frontend Technologies
- `javascript`
- `typescript`
- `html`
- `css`
- `sass`
- `react`
- `vue`
- `angular`
- `nextjs`
- `nuxt`

### Mobile Development
- `flutter`
- `dart`
- `swift`
- `react-native`

### DevOps & Cloud
- `aws`
- `docker`
- `kubernetes`
- `microservices`

### Databases
- `sql`
- `postgresql`
- `mysql`
- `nosql`

### Other
- `security`
- `performance`
- `system-design`

## System Requirements

The script checks for the following dependencies:

- **Python 3.x** - Required for running the crawler
- **pip3** - Python package manager
- **Git** - Version control (usually already installed)

If any are missing, the script will provide installation links.

## What Gets Created

After running the setup, you'll have:

```
programing-best-practices/
├── .venv/                      # Python virtual environment
├── content/                    # Crawled content (if crawling enabled)
│   ├── index.json              # Master index
│   ├── metadata.yaml           # Crawl statistics
│   └── [categories]/           # Content by category
├── summaries/                  # AI summaries (full mode only)
│   ├── SUMMARY.md              # Master overview
│   └── [category].md           # Category summaries
└── scripts/
    └── crawler/
        └── requirements.txt    # Installed dependencies
```

## Troubleshooting

### Script Won't Run

```bash
# Make sure it's executable
chmod +x scripts/quick-start.sh

# Run with bash explicitly
bash scripts/quick-start.sh
```

### Python Not Found

```bash
# Check Python installation
python3 --version

# Install Python 3
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3
# Windows: Download from python.org
```

### Virtual Environment Issues

```bash
# Manually create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r scripts/crawler/requirements.txt
```

### Crawler Errors

The crawler may encounter errors with some websites (rate limiting, timeouts, etc.). This is normal and the script will continue with other resources.

**Failed URLs Report:**

After crawling, if any URLs failed, a detailed report will be generated at:
```
content/failed_urls_report.md
```

This report includes:
- **URL**: The failed link
- **Error**: Specific error message (HTTP status, timeout, etc.)
- **Category**: Which section of README.md it belongs to
- **Subcategory**: More specific categorization
- **Timestamp**: When the failure occurred

Use this report to:
1. Identify broken or moved links in README.md
2. Update outdated URLs
3. Remove dead resources
4. Find alternative sources

To retry failed resources:
```bash
python3 scripts/crawler/crawl.py --retry-failed
```

## Post-Setup Commands

After setup, you can use these commands:

```bash
# Search crawled content
python3 scripts/crawler/search.py "javascript best practices"

# Update content (re-crawl)
python3 scripts/crawler/crawl.py

# Re-generate summaries
python3 scripts/crawler/generate_summaries.py

# Crawl new category
python3 scripts/crawler/crawl.py --category golang
```

## Integration with AI Editors

After setup, your AI coding editor will automatically detect the configuration files:

| Editor | Config File | Location |
|--------|-------------|----------|
| Claude Code | `CLAUDE.md` | Root directory |
| Antigravity | `instructions.md` | `.agent/` |
| Kiro | `project.md` | `.kiro/` |
| Cursor | `.cursorrules` | Root directory |
| Windsurf | `.windsurfrules` | Root directory |

No additional configuration needed!

## Examples

### Example 1: First-Time User

```bash
# Clone the repo
git clone https://github.com/dereknguyen269/programing-best-practices.git
cd programing-best-practices

# Run interactive setup
./scripts/quick-start.sh

# Choose option 2 (Test Setup) to try it out
```

### Example 2: Python Developer

```bash
# Clone and setup for Python only
git clone https://github.com/dereknguyen269/programing-best-practices.git
cd programing-best-practices

# Setup with Python resources only
./scripts/quick-start.sh --category python
```

### Example 3: Full Offline Access

```bash
# Clone the repo
git clone https://github.com/dereknguyen269/programing-best-practices.git
cd programing-best-practices

# Full setup with everything
./scripts/quick-start.sh --full

# Wait 10-15 minutes for all content to download
# Now you have complete offline access!
```

### Example 4: Quick Test

```bash
# Just want to test the crawler?
./scripts/quick-start.sh --limit 5

# This will crawl only 5 resources to see how it works
```

## Performance Tips

1. **Start Small** - Use `--limit 20` first to test
2. **Use Categories** - Crawl only what you need with `--category`
3. **Run Overnight** - Full setup takes 10-15 minutes, perfect for overnight
4. **Virtual Environment** - Always use venv to avoid dependency conflicts
5. **Update Regularly** - Re-run crawler monthly to get latest content

## Contributing

Found a bug or want to improve the script? 

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](../contributing.md) for more details.

## License

This script is part of the Programming Best Practices repository and is licensed under the same terms. See [LICENSE](../LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/dereknguyen269/programing-best-practices/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dereknguyen269/programing-best-practices/discussions)
- **Documentation**: [Main README](../README.md)
