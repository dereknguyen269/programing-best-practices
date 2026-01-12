#!/usr/bin/env python3
"""
Generate AI-ready summaries from crawled content.

This script creates condensed summaries optimized for AI coding assistants,
organized by category for quick context loading.

Usage:
    python generate_summaries.py              # Generate all summaries
    python generate_summaries.py --category python  # Generate for specific category
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Run: pip install pyyaml")
    exit(1)


SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
SUMMARIES_DIR = PROJECT_ROOT / "summaries"
INDEX_PATH = CONTENT_DIR / "index.json"


def load_index() -> dict:
    """Load the content index."""
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run 'python crawl.py' first.")
        return {}
    
    with open(INDEX_PATH, 'r') as f:
        return json.load(f)


def extract_key_points(content: str, max_points: int = 10) -> list[str]:
    """Extract key points from markdown content."""
    points = []
    
    # Look for headers
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    
    # Look for list items
    list_items = re.findall(r'^\s*[-*]\s+(.+)$', content, re.MULTILINE)
    
    # Look for numbered items
    numbered = re.findall(r'^\s*\d+\.\s+(.+)$', content, re.MULTILINE)
    
    # Combine and dedupe
    all_items = headers[:5] + list_items[:10] + numbered[:10]
    
    seen = set()
    for item in all_items:
        item_clean = item.strip()[:200]  # Limit length
        if item_clean and item_clean not in seen:
            seen.add(item_clean)
            points.append(item_clean)
            if len(points) >= max_points:
                break
    
    return points


def generate_category_summary(category: str, items: list[dict]) -> str:
    """Generate a summary for a category."""
    summary_parts = [
        f"# {category} Best Practices Summary",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d')}",
        f"> Sources: {len(items)} resources",
        "",
        "---",
        ""
    ]
    
    for item in items:
        file_path = PROJECT_ROOT / item["file"]
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove frontmatter
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    content = content[end + 3:]
            
            key_points = extract_key_points(content)
            
            if key_points:
                summary_parts.append(f"## {item['title']}")
                summary_parts.append(f"> Source: {item['url']}")
                summary_parts.append("")
                
                for point in key_points[:5]:
                    summary_parts.append(f"- {point}")
                
                summary_parts.append("")
        except Exception as e:
            print(f"  Warning: Could not process {file_path}: {e}")
    
    return "\n".join(summary_parts)


def generate_master_summary(index: dict) -> str:
    """Generate a master summary of all content."""
    categories = {}
    
    for id, item in index.items():
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    summary_parts = [
        "# Programming Best Practices - Quick Reference",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d')}",
        f"> Total Resources: {len(index)}",
        f"> Categories: {len(categories)}",
        "",
        "---",
        "",
        "## Table of Contents",
        ""
    ]
    
    for cat in sorted(categories.keys()):
        anchor = cat.lower().replace(' ', '-').replace('&', 'and')
        summary_parts.append(f"- [{cat}](#{anchor}) ({len(categories[cat])} resources)")
    
    summary_parts.append("")
    summary_parts.append("---")
    summary_parts.append("")
    
    for cat in sorted(categories.keys()):
        summary_parts.append(f"## {cat}")
        summary_parts.append("")
        
        for item in categories[cat][:10]:  # Top 10 per category
            summary_parts.append(f"- **[{item['title']}]({item['url']})**")
            if item.get('subcategory'):
                summary_parts.append(f"  - Subcategory: {item['subcategory']}")
        
        summary_parts.append("")
    
    return "\n".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-ready summaries from crawled content"
    )
    parser.add_argument(
        "--category", "-c",
        help="Generate summary for specific category only"
    )
    
    args = parser.parse_args()
    
    print("📝 Generating Summaries...")
    print()
    
    index = load_index()
    if not index:
        return
    
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Group by category
    categories = {}
    for id, item in index.items():
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({**item, "id": id})
    
    # Filter if category specified
    if args.category:
        categories = {
            k: v for k, v in categories.items()
            if args.category.lower() in k.lower()
        }
        if not categories:
            print(f"No category matching '{args.category}'")
            return
    
    # Generate category summaries
    for cat, items in categories.items():
        print(f"  Generating: {cat}...")
        summary = generate_category_summary(cat, items)
        
        # Sanitize filename: replace slashes and other problematic characters
        filename = cat.lower().replace(' ', '_').replace('&', 'and').replace('/', '_') + ".md"
        filepath = SUMMARIES_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
    
    # Generate master summary
    if not args.category:
        print("  Generating: Master Summary...")
        master = generate_master_summary(index)
        
        with open(SUMMARIES_DIR / "SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(master)
    
    print()
    print(f"✅ Summaries saved to: {SUMMARIES_DIR}")


if __name__ == "__main__":
    main()
