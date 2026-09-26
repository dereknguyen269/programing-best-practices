import re
import glob
import os
import urllib.request
import urllib.error
import concurrent.futures
import socket

socket.setdefaulttimeout(4)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

links = set()
for md in glob.glob(os.path.join(REPO_ROOT, "**", "*.md"), recursive=True):
    with open(md, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        found = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", content)
        for text, url in found:
            url = url.rstrip(')"\'>')
            links.add(url)

print(f"Found {len(links)} unique URLs across markdown files.")

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Compatible; LinkChecker/1.0)"})
        with urllib.request.urlopen(req) as resp:
            return (url, resp.getcode(), "OK")
    except urllib.error.HTTPError as e:
        return (url, e.code, f"HTTP Error: {e.reason}")
    except urllib.error.URLError as e:
        return (url, 0, f"URL Error: {e.reason}")
    except Exception as e:
        return (url, 0, f"Error: {str(e)}")

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    future_to_url = {executor.submit(check_url, url): url for url in links}
    for future in concurrent.futures.as_completed(future_to_url):
        results.append(future.result())

success = sum(1 for r in results if r[1] == 200)
redirects = sum(1 for r in results if r[1] in [301, 302, 307, 308])
failed = len(results) - success - redirects

print(f"\n--- Link Validation Summary ---")
print(f"Total Unique Links: {len(results)}")
print(f"Successful (200 OK): {success}")
print(f"Redirects: {redirects}")
print(f"Failed / Errors: {failed}")

print("\n--- Failed or Problematic Links ---")
for url, status, msg in sorted(results):
    if status != 200:
        print(f"[{status}] {url} -> {msg}")
