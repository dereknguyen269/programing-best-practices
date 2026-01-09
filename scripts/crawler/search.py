#!/usr/bin/env python3
"""
Search the crawled knowledge base content.

Usage:
    python search.py "javascript style guide"
    python search.py "python best practices" --category python
    python search.py "security" --top 5
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
INDEX_PATH = CONTENT_DIR / "index.json"


def load_index() -> dict:
    """Load the content index."""
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run 'python crawl.py' first.")
        return {}
    
    with open(INDEX_PATH, 'r') as f:
        return json.load(f)


def search_content(
    query: str,
    category: Optional[str] = None,
    top: int = 10
) -> list[dict]:
    """Search the knowledge base content."""
    index = load_index()
    
    if not index:
        return []
    
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()
    
    for id, item in index.items():
        # Filter by category
        if category and category.lower() not in item["category"].lower():
            continue
        
        score = 0
        
        # Check title
        title_lower = item["title"].lower()
        for word in query_words:
            if word in title_lower:
                score += 10
        
        # Check category
        if query_lower in item["category"].lower():
            score += 5
        
        # Check subcategory
        if query_lower in item.get("subcategory", "").lower():
            score += 3
        
        # Read file content for deeper search
        file_path = PROJECT_ROOT / item["file"]
        if file_path.exists() and score == 0:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for word in query_words:
                        if word in content:
                            score += 1
            except:
                pass
        
        if score > 0:
            results.append({
                **item,
                "id": id,
                "score": score
            })
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:top]


def format_results(results: list[dict]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."
    
    output = []
    for i, r in enumerate(results, 1):
        output.append(f"""
{i}. {r['title']}
   Category: {r['category']} > {r.get('subcategory', 'General')}
   URL: {r['url']}
   File: {r['file']}
   Score: {r['score']}
""")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search the programming best practices knowledge base"
    )
    parser.add_argument(
        "query",
        help="Search query"
    )
    parser.add_argument(
        "--category", "-c",
        help="Filter by category"
    )
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=10,
        help="Number of results to show (default: 10)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    results = search_content(
        args.query,
        category=args.category,
        top=args.top
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n🔍 Search Results for: '{args.query}'")
        print("=" * 50)
        print(format_results(results))


if __name__ == "__main__":
    main()
