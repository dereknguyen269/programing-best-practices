#!/usr/bin/env python3
"""
Regenerate docs/<category>.md from data/resources.csv.

Usage:
    python3 scripts/generate_docs.py

This is the ONE place that turns the CSV (source of truth) into the
markdown pages people actually read. Never hand-edit files under docs/
for an existing resource — edit the CSV row and rerun this script.
Adding a new resource: add a row to data/resources.csv, run this, commit both.
"""
import csv
import os
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "resources.csv")
DOCS_DIR = os.path.join(ROOT, "docs")

TITLES = {
    "backend": "Backend Best Practices",
    "frontend": "Frontend Best Practices",
    "database": "Database & Data Best Practices",
    "mobile": "Mobile Development Best Practices",
    "devops": "DevOps & Infrastructure Best Practices",
    "ai-ml": "AI & Data Science Best Practices",
    "tools": "Development Tools & Practices",
}


def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group(rows):
    by_category = defaultdict(lambda: OrderedDict())
    for row in rows:
        cat = row["category"]
        topic = row["language_or_topic"]
        by_category[cat].setdefault(topic, []).append(row)
    return by_category


def render(category, sections):
    lines = [f"# {TITLES.get(category, category.title())}", ""]
    for topic, links in sections.items():
        lines.append(f"## {topic}")
        lines.append("")
        for row in links:
            org = f" — *{row['org']}*" if row["org"] else ""
            lines.append(f"- [{row['title']}]({row['url']}){org}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    rows = load_rows()
    by_category = group(rows)
    for category, sections in by_category.items():
        out_path = os.path.join(DOCS_DIR, f"{category}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render(category, sections))
        print(f"wrote {out_path} ({sum(len(v) for v in sections.values())} links)")
    print(f"\n{len(rows)} total resources across {len(by_category)} categories.")


if __name__ == "__main__":
    main()
