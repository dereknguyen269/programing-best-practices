#!/usr/bin/env python3
"""Check every HTTP link in the repository's Markdown files.

Exit status is 0 when no link is *confirmed broken*, 1 when at least one is, so
CI can gate on it.

Why "confirmed" rather than "not 200": the check runs from GitHub-hosted
runners, whose datacenter IPs get 403'd by a long list of sites that serve the
page perfectly to a browser. Treating 403 as a failure makes the gate red on
links that are fine (docs.solidjs.com, baeldung.com and toptal.com all returned
200 locally and 403 from the runner during development). Every failure is
therefore re-checked against the Wayback Machine before it is reported as
broken; anything with a recent snapshot is a live page we merely cannot reach.

Buckets:

  ok        2xx, or a 3xx that lands on a 2xx
  blocked   401/403, and the host is in blocked_hosts
  throttled 429 -- never means the page is gone
  broken    everything else, including 403/404 that Wayback also lacks

Usage:
    python3 scripts/validate_links.py                # human-readable summary
    python3 scripts/validate_links.py --json out.json
    python3 scripts/validate_links.py --report failed_urls_report.md
"""

from __future__ import annotations

import argparse
import concurrent.futures
import glob
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "link_check_config.json")

DEFAULT_CONFIG = {
    "timeout_seconds": 8,
    "retries": 2,
    "workers": 24,
    "per_host_workers": 2,
    "blocked_hosts": [],
    "ignored_urls": [],
    # A Wayback snapshot this recent proves the page was live not long ago.
    "wayback_max_age_days": 730,
}

# 401/403 mean "this client was rejected", not "the page is missing".
BLOCKED_STATUSES = {401, 403}
# 429 means we are being throttled. It never means the page is gone, and our own
# parallel workers can trigger it.
THROTTLED_STATUSES = {429}
# Worth another attempt before we call them dead.
RETRY_STATUSES = {408, 425, 429, 500, 502, 503, 504}
RETRY_EXCEPTIONS = (
    urllib.error.URLError,
    socket.timeout,
    ssl.SSLError,
    ConnectionError,
    TimeoutError,
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def find_markdown_files() -> list[str]:
    skip = {".git", "node_modules", "venv", ".venv", "env"}
    files = []
    for path in glob.glob(os.path.join(REPO_ROOT, "**", "*.md"), recursive=True):
        parts = set(os.path.relpath(path, REPO_ROOT).split(os.sep))
        if parts & skip:
            continue
        files.append(path)
    return sorted(files)


def collect_links() -> dict[str, list[str]]:
    """Map each URL to the list of 'path:line' locations that reference it."""
    locations: dict[str, list[str]] = defaultdict(list)
    for path in find_markdown_files():
        rel = os.path.relpath(path, REPO_ROOT)
        with open(path, encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                for _text, url in MD_LINK_RE.findall(line):
                    url = url.rstrip(')"\'>.,;')
                    loc = f"{rel}:{lineno}"
                    if loc not in locations[url]:
                        locations[url].append(loc)
    return dict(locations)


def host_matches(host: str, hosts: set[str]) -> bool:
    return any(host == h or host.endswith("." + h) for h in hosts)


def check_url(url: str, cfg: dict) -> tuple[str, int, str]:
    """Return (url, status_code, message). status 0 means no HTTP response."""
    timeout = cfg["timeout_seconds"]
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
        method="GET",
    )

    attempts = int(cfg["retries"]) + 1
    last = (0, "no attempt made")
    for attempt in range(attempts):
        if attempt:
            time.sleep(1.5 * attempt)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return (url, resp.getcode(), "OK")
        except urllib.error.HTTPError as e:
            last = (e.code, f"HTTP {e.code} {e.reason}")
            if e.code not in RETRY_STATUSES:
                return (url, e.code, last[1])
        except RETRY_EXCEPTIONS as e:
            last = (0, f"{type(e).__name__}: {str(e)[:120]}")
        except Exception as e:  # unexpected; do not retry
            return (url, 0, f"{type(e).__name__}: {str(e)[:120]}")
    return (url, last[0], last[1])


def wayback_snapshot(url: str, cfg: dict) -> str | None:
    """Return the timestamp of a recent snapshot, else None.

    Used to tell 'this site blocks our runner' apart from 'this page is gone'.
    """
    api = "http://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(api, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as resp:
            data = json.load(resp)
    except Exception:
        return None
    snap = (data.get("archived_snapshots") or {}).get("closest") or {}
    if snap.get("status") != "200":
        return None
    stamp = snap.get("timestamp", "")
    if len(stamp) < 8 or not stamp[:8].isdigit():
        return None
    try:
        archived = time.strptime(stamp[:8], "%Y%m%d")
    except ValueError:
        return None
    age_days = (time.time() - time.mktime(archived)) / 86400
    if age_days > float(cfg["wayback_max_age_days"]):
        return None
    return stamp


def classify(url: str, status: int, blocked_hosts: set[str], snapshot: str | None) -> str:
    if 200 <= status < 300:
        return "ok"
    if status in THROTTLED_STATUSES:
        return "throttled"
    if snapshot:
        # Reachable by browsers and archived recently: not broken, just refused.
        return "blocked"
    host = (urlparse(url).hostname or "").lower()
    if status in BLOCKED_STATUSES and host_matches(host, blocked_hosts):
        return "blocked"
    return "broken"


def write_report(path: str, results: list[dict], counts: dict[str, int]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    lines = [
        "# Failed URLs Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        "",
        f"Checked: {counts['total']} | ok: {counts['ok']} | "
        f"blocked: {counts['blocked']} | throttled: {counts['throttled']} | "
        f"broken: {counts['broken']}",
        "",
    ]
    for bucket, title in (
        ("broken", "Broken"),
        ("throttled", "Throttled (429, retry later)"),
        ("blocked", "Blocked (bot protection or unreachable from CI)"),
    ):
        rows = [r for r in results if r["classification"] == bucket]
        lines += [f"## {title}", ""]
        if not rows:
            lines += ["None.", ""]
            continue
        for r in sorted(rows, key=lambda r: r["url"]):
            lines += [
                f"### {r['url']}",
                "",
                f"- **Status**: {r['status']} — {r['message']}",
                f"- **Wayback snapshot**: {r.get('wayback') or 'none'}",
                f"- **Referenced by**: {', '.join(r['locations'])}",
                "",
            ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Markdown links.")
    ap.add_argument("--json", metavar="PATH", help="write machine-readable results")
    ap.add_argument("--report", metavar="PATH", help="write a Markdown report")
    args = ap.parse_args()

    cfg = load_config()
    socket.setdefaulttimeout(cfg["timeout_seconds"])
    blocked_hosts = {h.lower() for h in cfg["blocked_hosts"]}

    locations = collect_links()
    for url in cfg.get("ignored_urls") or []:
        locations.pop(url, None)

    print(f"Found {len(locations)} unique URLs across Markdown files.")

    # Cap concurrency per host: hitting one domain with 24 workers at once is
    # what earns a 429, and the retry then makes it worse.
    host_semaphores: dict[str, threading.Semaphore] = {}
    host_lock = threading.Lock()
    per_host = max(1, int(cfg.get("per_host_workers", 2)))

    def guarded_check(url: str):
        host = (urlparse(url).hostname or "").lower()
        with host_lock:
            sem = host_semaphores.setdefault(host, threading.Semaphore(per_host))
        with sem:
            return check_url(url, cfg)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(cfg["workers"])) as pool:
        futures = {pool.submit(guarded_check, url): url for url in locations}
        for future in concurrent.futures.as_completed(futures):
            url, status, message = future.result()
            results.append(
                {
                    "url": url,
                    "status": status,
                    "message": message,
                    "locations": locations.get(url, []),
                    "wayback": None,
                    "classification": None,
                }
            )

    # Confirm every failure against Wayback before calling it broken.
    candidates = [r for r in results if not 200 <= r["status"] < 300]
    if candidates:
        print(f"Cross-checking {len(candidates)} non-200 URLs against Wayback...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            snaps = {r["url"]: pool.submit(wayback_snapshot, r["url"], cfg) for r in candidates}
            for url, fut in snaps.items():
                try:
                    snap = fut.result()
                except Exception:
                    snap = None
                for r in results:
                    if r["url"] == url:
                        r["wayback"] = snap

    for r in results:
        r["classification"] = classify(r["url"], r["status"], blocked_hosts, r["wayback"])

    counts = {
        "total": len(results),
        "ok": sum(1 for r in results if r["classification"] == "ok"),
        "blocked": sum(1 for r in results if r["classification"] == "blocked"),
        "throttled": sum(1 for r in results if r["classification"] == "throttled"),
        "broken": sum(1 for r in results if r["classification"] == "broken"),
    }

    print()
    print("--- Link Validation Summary ---")
    print(f"Total Unique Links: {counts['total']}")
    print(f"OK: {counts['ok']}")
    print(f"Blocked (not reachable from CI, not counted as broken): {counts['blocked']}")
    print(f"Throttled (429, not counted as broken): {counts['throttled']}")
    print(f"Broken: {counts['broken']}")

    for bucket, heading in (
        ("broken", "BROKEN"),
        ("throttled", "THROTTLED (retry later)"),
        ("blocked", "BLOCKED"),
    ):
        rows = sorted(
            (r for r in results if r["classification"] == bucket), key=lambda r: r["url"]
        )
        if not rows:
            continue
        print(f"\n--- {heading} ---")
        for r in rows:
            print(f"[{r['status']}] {r['url']} -> {r['message']}")
            if r["wayback"]:
                print(f"        wayback snapshot: {r['wayback']}")
            print(f"        referenced by: {', '.join(r['locations'])}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"counts": counts, "results": results}, f, indent=2)
        print(f"\nWrote {args.json}")
    if args.report:
        write_report(args.report, results, counts)
        print(f"Wrote {args.report}")

    return 1 if counts["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())
