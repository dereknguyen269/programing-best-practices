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
- `blocked` — 401/403 from a host in `blocked_hosts`. The page is live but
  rejects automated clients, so these must never fail the build.
- `throttled` — 429. Never means the page is gone; our own parallel workers can
  trigger it. `per_host_workers` caps concurrency per domain to reduce this.
- `broken` — 404/410, 5xx after retries, DNS/TLS failure, timeout

### When a link fails

1. Check whether it is a real 404 or just bot protection. A real browser UA
   still getting 403, plus a recent 200 snapshot from
   `http://archive.org/wayback/available?url=<url>`, means the host blocks bots
   — add the host to `blocked_hosts`, do not "fix" the link.
2. For real 404s, find a current replacement and add a rule to the
   `replacements` dict in `scripts/fix_links.py` so future runs stay fixed.
3. For retired-but-valuable content, wrap in
   `https://web.archive.org/web/2024/<original-url>`.

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
