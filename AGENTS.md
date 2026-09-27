# AGENTS.md

Repository-specific notes for automated maintenance.

## Link maintenance pipeline

Two GitHub Actions workflows own link health. `scripts/auto_maintenance_pr.sh`
was removed — it ran on one developer machine with hardcoded `/home/ubuntu/repo`
paths and opened a PR every week even when nothing changed.

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `.github/workflows/link-check.yml` | PRs and pushes touching `*.md`, plus Mondays 06:00 UTC | Fails the build on genuinely broken links |
| `.github/workflows/weekly-maintenance.yml` | Mondays 04:00 UTC, or manual | Applies `fix_links.py`, opens one PR if anything real changed |

Both run `scripts/validate_links.py`, which is stdlib-only and exits non-zero
only when a link is actually broken.

### Link status buckets

`validate_links.py` sorts every URL into four buckets. Only `broken` fails CI.

- `ok` — 2xx, or a 3xx that lands on a 2xx
- `blocked` — 401/403 that a recent Wayback snapshot proves is still live, or
  from a host in `blocked_hosts`. The page is fine; we just cannot reach it.
- `throttled` — 429. Never means the page is gone; our own parallel workers can
  trigger it. `per_host_workers` caps concurrency per domain to reduce this.
- `broken` — 404/410, 5xx after retries, DNS/TLS failure, timeout, or a 403/404
  that Wayback has no recent snapshot of

### Why the Wayback cross-check matters

The check runs from GitHub-hosted runners, whose datacenter IPs get 403'd by a
long list of sites that serve the page perfectly to a browser. During
development `docs.solidjs.com`, `baeldung.com` and `toptal.com` all returned
**200 locally and 403 from the runner**. Treating 403 as broken made the gate
red on healthy links, and allowlisting every CDN-fronted site does not scale.

So before any non-200 is called broken, it is checked against
`http://archive.org/wayback/available`. A snapshot younger than
`wayback_max_age_days` (default 730) means the page is live and merely
unreachable from CI, so it is classified `blocked`. That is what keeps the gate
meaningful: it fails on pages that are actually gone.

### When a link fails

1. The validator already does the browser-UA and Wayback checks for you —
   re-read its output. A `broken` entry has no recent Wayback snapshot, which
   is strong evidence the page is really gone.
2. If it is a real 404, find a current replacement and add a rule to the
   `replacements` dict in `scripts/fix_links.py` so future runs stay fixed.
3. For retired-but-valuable content, wrap in
   `https://web.archive.org/web/2024/<original-url>`.
4. Only add a host to `blocked_hosts` when it throttles or blocks us but Wayback
   has no snapshot to prove it is alive. Toptal is the existing example: its
   article URLs return 429 while `/python` and `/` return 200.

### Gotchas

- `fix_links.py` must stay idempotent. It matches whole URL tokens, longest
  rule first, because plain substring replacement re-matches archive.org
  wrappers (which still contain the original URL) and prefix URLs like
  `/router` inside `/routers`. Run it twice after editing `replacements` and
  confirm the second run reports 0 updates.
- The weekly workflow force-pushes the fixed `chore/weekly-maintenance` branch.
  That branch is owned solely by the workflow, so never push to it by hand.
- A timestamp-only `maintenance_log.txt` diff is explicitly excluded from
  change detection, so a run with no link fixes does not open a PR.

## Repo conventions

- Default branch is `master`.
- Discussions is disabled on this repository; link to Issues instead.
- Markdown resource lists live in `README.md` under `### <Technology> Best
  Practices` headings, with a matching entry in the Table of Contents. Update
  both when adding a resource.
