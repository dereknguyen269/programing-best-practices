# Knowledge Base Crawler

This directory contains scripts for crawling and processing the external links from the Programming Best Practices knowledge base.

## Setup

```bash
# Install dependencies
cd scripts/crawler
pip install -r requirements.txt
```

## Usage

### 1. Crawl All Resources

```bash
# Crawl all external links from README.md
python crawl.py

# Crawl only Python-related resources
python crawl.py --category python

# Crawl first 10 links only (for testing)
python crawl.py --limit 10

# Update existing content
python crawl.py --update
```

### 2. Search the Knowledge Base

```bash
# Search for JavaScript content
python search.py "javascript style guide"

# Search within a category
python search.py "best practices" --category python

# Get top 5 results
python search.py "security" --top 5

# Output as JSON
python search.py "design patterns" --json
```

### 3. Generate AI-Ready Summaries

```bash
# Generate summaries for all categories
python generate_summaries.py

# Generate for specific category
python generate_summaries.py --category javascript
```

## Output Structure

After crawling, the following directories are created:

```
programing-best-practices/
├── content/                    # Crawled content
│   ├── index.json              # Index of all resources
│   ├── metadata.yaml           # Crawl metadata
│   ├── backend_development/    # Content by category
│   │   ├── abc123.md
│   │   └── ...
│   ├── frontend_development/
│   └── ...
└── summaries/                  # AI-ready summaries
    ├── SUMMARY.md              # Master summary
    ├── backend_development.md
    ├── frontend_development.md
    └── ...
```

## Content Format

Each crawled file includes YAML frontmatter and extracted content:

```markdown
---
title: Airbnb JavaScript Style Guide
url: https://github.com/airbnb/javascript
category: Frontend Development
subcategory: JavaScript Best Practices
crawled_at: 2024-01-03T10:30:00
source_type: github_readme
---

# Airbnb JavaScript Style Guide

> Source: [https://github.com/airbnb/javascript](https://github.com/airbnb/javascript)

---

[Extracted content here...]
```

## How AI Assistants Use This

After crawling, AI coding assistants can:

1. **Load the index**: Read `content/index.json` to find relevant resources
2. **Search content**: Use the search script or read files directly
3. **Use summaries**: Load category-specific summaries for quick context
4. **Reference sources**: All content includes original URLs for attribution

## Notes

- Crawling respects rate limits (1 second between requests)
- GitHub repositories fetch README.md automatically
- HTML pages are converted to markdown
- Content is cached locally to avoid re-crawling
