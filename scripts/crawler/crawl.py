#!/usr/bin/env python3
"""
Programming Best Practices Crawler

This script crawls external links from README.md and saves the content locally
for use by AI coding editors as a knowledge base.

Usage:
    python crawl.py                    # Crawl all links
    python crawl.py --category python  # Crawl only Python-related links
    python crawl.py --limit 10         # Crawl only first 10 links
    python crawl.py --update           # Update existing content
"""

import os
import re
import json
import ssl
import hashlib
import argparse
import asyncio
import certifi
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Optional

try:
    import aiohttp
    import aiofiles
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
    from tqdm import tqdm
    import yaml
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    exit(1)


# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
README_PATH = PROJECT_ROOT / "README.md"
CONTENT_DIR = PROJECT_ROOT / "content"
INDEX_PATH = CONTENT_DIR / "index.json"
METADATA_PATH = CONTENT_DIR / "metadata.yaml"

# Rate limiting
MAX_CONCURRENT_REQUESTS = 5
REQUEST_DELAY = 1  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds

# User agent
USER_AGENT = "ProgrammingBestPractices-Crawler/1.0 (Knowledge Base Builder)"


class ContentCrawler:
    """Crawls and stores content from external links."""

    def __init__(self, max_concurrent: int = MAX_CONCURRENT_REQUESTS):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.index: dict = {}
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        self.failed_urls = []  # Track failed URLs with details

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        
        # Create SSL context that works on macOS
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            # Fallback: disable SSL verification (not recommended for production)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            print("⚠️  Warning: SSL verification disabled")
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": USER_AGENT}
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    def extract_links_from_readme(self) -> list[dict]:
        """Extract all external links from README.md with context."""
        if not README_PATH.exists():
            print(f"ERROR: README.md not found at {README_PATH}")
            return []

        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        links = []
        current_category = "General"
        current_subcategory = ""

        # Pattern for markdown links: [text](url)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        # Pattern for headers
        h2_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)
        h3_pattern = re.compile(r'^###\s+(.+)$', re.MULTILINE)

        lines = content.split('\n')
        
        for line in lines:
            # Check for category headers
            h2_match = h2_pattern.match(line)
            h3_match = h3_pattern.match(line)
            
            if h2_match:
                current_category = self._clean_header(h2_match.group(1))
                current_subcategory = ""
            elif h3_match:
                current_subcategory = self._clean_header(h3_match.group(1))

            # Find links in this line
            for match in link_pattern.finditer(line):
                text = match.group(1)
                url = match.group(2)

                # Skip internal links and badges
                if url.startswith('#') or url.startswith('./'):
                    continue
                if 'badge' in url.lower() or 'shields.io' in url:
                    continue
                if 'img.shields.io' in url or 'licensebuttons' in url:
                    continue

                # Filter for actual resource links
                if self._is_valid_resource_url(url):
                    links.append({
                        "title": text,
                        "url": url,
                        "category": current_category,
                        "subcategory": current_subcategory,
                        "id": self._generate_id(url)
                    })

        return links

    def _clean_header(self, header: str) -> str:
        """Remove emojis and extra characters from headers."""
        # Remove emojis and special characters
        cleaned = re.sub(r'[^\w\s&/-]', '', header)
        return cleaned.strip()

    def _is_valid_resource_url(self, url: str) -> bool:
        """Check if URL is a valid resource to crawl."""
        # Skip certain domains
        skip_domains = [
            'github.com/dereknguyen269',  # Own repo
            'twitter.com',
            'linkedin.com',
            'reddit.com',
            'star-history.com',
            'contrib.rocks',
            'creativecommons.org'
        ]
        
        for domain in skip_domains:
            if domain in url:
                return False
        
        # Must be http/https
        if not url.startswith(('http://', 'https://')):
            return False

        return True

    def _generate_id(self, url: str) -> str:
        """Generate a unique ID for a URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    async def fetch_content(self, url: str) -> Optional[dict]:
        """Fetch and process content from a URL."""
        async with self.semaphore:
            error_msg = None
            try:
                # Handle GitHub repos specially
                if 'github.com' in url and '/blob/' not in url:
                    result = await self._fetch_github_readme(url)
                    if not result:
                        error_msg = "GitHub README not found (tried main/master branches)"
                    return result
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        error_msg = f"HTTP {response.status} - {response.reason}"
                        return None

                    content_type = response.headers.get('content-type', '')
                    
                    if 'text/html' in content_type:
                        html = await response.text()
                        return self._process_html(html, url)
                    elif 'text/markdown' in content_type or url.endswith('.md'):
                        markdown = await response.text()
                        return {
                            "type": "markdown",
                            "content": markdown,
                            "url": url
                        }
                    else:
                        error_msg = f"Unsupported content type: {content_type}"
                        return None

            except asyncio.TimeoutError:
                error_msg = "Request timeout"
                return None
            except aiohttp.ClientError as e:
                error_msg = f"Network error: {str(e)}"
                return None
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                return None
            finally:
                # Store error if one occurred
                if error_msg:
                    self.failed_urls.append({
                        "url": url,
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
                    })
                await asyncio.sleep(REQUEST_DELAY)

    async def _fetch_github_readme(self, url: str) -> Optional[dict]:
        """Fetch README from a GitHub repository."""
        # Convert github.com URL to raw content URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            owner, repo = path_parts[0], path_parts[1]
            
            # Try different README filenames
            readme_names = ['README.md', 'readme.md', 'README.rst', 'README']
            
            for readme in readme_names:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{readme}"
                
                try:
                    async with self.session.get(raw_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            return {
                                "type": "markdown",
                                "content": content,
                                "url": url,
                                "source": "github_readme"
                            }
                except:
                    pass
                
                # Try master branch
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{readme}"
                try:
                    async with self.session.get(raw_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            return {
                                "type": "markdown",
                                "content": content,
                                "url": url,
                                "source": "github_readme"
                            }
                except:
                    pass
        
        return None

    def _process_html(self, html: str, url: str) -> dict:
        """Process HTML content and convert to markdown."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # Try to find main content
        main_content = None
        for selector in ['article', 'main', '.content', '.post-content', '.markdown-body', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Convert to markdown
        markdown_content = md(str(main_content), heading_style="ATX")
        
        # Get title
        title = ""
        if soup.title:
            title = soup.title.string or ""
        elif soup.h1:
            title = soup.h1.get_text()
        
        # Get description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        return {
            "type": "html",
            "content": markdown_content,
            "title": title,
            "description": description,
            "url": url
        }

    async def crawl_link(self, link: dict, update: bool = False) -> bool:
        """Crawl a single link and save content."""
        link_id = link["id"]
        content_path = CONTENT_DIR / link["category"].lower().replace(' ', '_')
        file_path = content_path / f"{link_id}.md"

        # Skip if already exists and not updating
        if file_path.exists() and not update:
            self.stats["skipped"] += 1
            return True

        # Fetch content
        result = await self.fetch_content(link["url"])
        
        if not result:
            self.stats["failed"] += 1
            # Add link details to failed URLs if not already added by fetch_content
            if not any(f["url"] == link["url"] for f in self.failed_urls):
                self.failed_urls.append({
                    "url": link["url"],
                    "title": link["title"],
                    "category": link["category"],
                    "subcategory": link["subcategory"],
                    "error": "Failed to fetch content",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Update existing entry with link details
                for f in self.failed_urls:
                    if f["url"] == link["url"]:
                        f["title"] = link["title"]
                        f["category"] = link["category"]
                        f["subcategory"] = link["subcategory"]
            return False

        # Create directory
        content_path.mkdir(parents=True, exist_ok=True)

        # Create markdown file with frontmatter
        frontmatter = {
            "title": link["title"],
            "url": link["url"],
            "category": link["category"],
            "subcategory": link["subcategory"],
            "crawled_at": datetime.now().isoformat(),
            "source_type": result.get("source", result["type"])
        }

        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

# {link["title"]}

> Source: [{link["url"]}]({link["url"]})

---

{result["content"]}
"""

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)

        # Update index
        self.index[link_id] = {
            "title": link["title"],
            "url": link["url"],
            "category": link["category"],
            "subcategory": link["subcategory"],
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "crawled_at": datetime.now().isoformat()
        }

        self.stats["success"] += 1
        return True

    async def crawl_all(
        self, 
        category: Optional[str] = None,
        limit: Optional[int] = None,
        update: bool = False
    ):
        """Crawl all links from README.md."""
        print("📚 Extracting links from README.md...")
        links = self.extract_links_from_readme()
        
        if category:
            links = [l for l in links if category.lower() in l["category"].lower()]
            print(f"   Filtered to category: {category}")
        
        if limit:
            links = links[:limit]
            print(f"   Limited to {limit} links")

        self.stats["total"] = len(links)
        print(f"   Found {len(links)} links to crawl\n")

        # Load existing index
        if INDEX_PATH.exists():
            with open(INDEX_PATH, 'r') as f:
                self.index = json.load(f)

        # Crawl with progress bar
        print("🕷️  Crawling content...")
        tasks = []
        for link in links:
            tasks.append(self.crawl_link(link, update))
        
        # Process with progress bar
        for i, task in enumerate(tqdm(asyncio.as_completed(tasks), total=len(tasks))):
            await task

        # Save index
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        with open(INDEX_PATH, 'w') as f:
            json.dump(self.index, f, indent=2)

        # Save metadata
        metadata = {
            "last_crawl": datetime.now().isoformat(),
            "total_resources": len(self.index),
            "categories": list(set(v["category"] for v in self.index.values())),
            "stats": self.stats
        }
        with open(METADATA_PATH, 'w') as f:
            yaml.dump(metadata, f)

        # Generate failure report if there are failed URLs
        if self.failed_urls:
            report_path = CONTENT_DIR / "failed_urls_report.md"
            with open(report_path, 'w') as f:
                f.write("# Failed URLs Report\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Failed: {len(self.failed_urls)}\n\n")
                f.write("---\n\n")
                
                # Group by category
                by_category = {}
                for failed in self.failed_urls:
                    category = failed.get('category', 'Unknown')
                    if category not in by_category:
                        by_category[category] = []
                    by_category[category].append(failed)
                
                for category, failures in sorted(by_category.items()):
                    f.write(f"## {category}\n\n")
                    for failed in failures:
                        f.write(f"### {failed.get('title', 'Unknown Title')}\n\n")
                        f.write(f"- **URL**: {failed['url']}\n")
                        f.write(f"- **Error**: {failed.get('error', 'Unknown error')}\n")
                        if failed.get('subcategory'):
                            f.write(f"- **Subcategory**: {failed['subcategory']}\n")
                        f.write(f"- **Timestamp**: {failed.get('timestamp', 'N/A')}\n")
                        f.write("\n")
            
            print(f"\n⚠️  Failed URLs report saved to: {report_path}")

        # Print summary
        print("\n📊 Crawl Summary:")
        print(f"   ✅ Success: {self.stats['success']}")
        print(f"   ⏭️  Skipped: {self.stats['skipped']}")
        print(f"   ❌ Failed:  {self.stats['failed']}")
        if self.failed_urls:
            print(f"\n📋 Failed URLs Report: {CONTENT_DIR / 'failed_urls_report.md'}")
        print(f"\n📁 Content saved to: {CONTENT_DIR}")


async def main():
    parser = argparse.ArgumentParser(
        description="Crawl programming best practices resources"
    )
    parser.add_argument(
        "--category", "-c",
        help="Filter by category (e.g., 'python', 'javascript')"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Limit number of links to crawl"
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Update existing content"
    )
    
    args = parser.parse_args()

    print("=" * 50)
    print("  Programming Best Practices Crawler")
    print("=" * 50)
    print()

    async with ContentCrawler() as crawler:
        await crawler.crawl_all(
            category=args.category,
            limit=args.limit,
            update=args.update
        )


if __name__ == "__main__":
    asyncio.run(main())
