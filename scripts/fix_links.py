import glob
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

replacements = {
    "https://docs.anthropic.com/en/docs/build-with-claude/agentic": "https://docs.anthropic.com/en/docs/build-with-claude",
    "https://docs.anthropic.com/en/docs/build-with-claude/develop-with-claude": "https://docs.anthropic.com/en/docs/build-with-claude",
    "https://docs.deno.com/runtime/fundamentals/best-practices/": "https://docs.deno.com/",
    "https://docs.deno.com/runtime/fundamentals/style-guide/": "https://docs.deno.com/",
    "https://bun.sh/docs/install": "https://bun.sh/docs",
    "https://bun.sh/docs/runtime/best-practices": "https://bun.sh/docs",
    "https://svelte.dev/docs/kit/best-practices": "https://svelte.dev/docs",
    "https://svelte.dev/docs/svelte/guide": "https://svelte.dev/docs",
    "https://svelte.dev/docs/svelte/performance": "https://svelte.dev/docs",
    "https://svelte.dev/docs/svelte/rules": "https://svelte.dev/docs",
    "https://nuxt.com/docs/guide/conventions": "https://nuxt.com/docs",
    "https://docs.solidjs.com/guides/best-practices": "https://docs.solidjs.com/",
    "https://docs.solidjs.com/guides/style-guide": "https://docs.solidjs.com/",
    "https://docs.solidjs.com/solid-start/best-practises": "https://docs.solidjs.com/",
    # 2026-09 maintenance pass — dead links replaced with verified targets
    "https://www.baeldung.com/java-coding-standards-and-best-practices": "https://www.baeldung.com/java-clean-code",
    "https://www.oracle.com/java/technologies/performance-tuning.html": "https://docs.oracle.com/en/java/javase/21/performance/",
    "https://github.com/JackyAndroid/kotlin-best-practices": "https://kotlinlang.org/docs/coding-conventions.html",
    "https://github.com/abinoda/rspec-best-practices": "https://web.archive.org/web/2024/https://github.com/abinoda/rspec-best-practices",
    "https://blog.carbonfive.com/rails-database-best-practices/": "https://web.archive.org/web/2024/https://blog.carbonfive.com/rails-database-best-practices/",
    "https://escape.tech/blog/graphql-security-best-practices-guide/": "https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html",
    "https://products.golangdojo.com/golang-cheat-sheet-by-golang-dojo": "https://github.com/a8m/golang-cheat-sheet",
    "https://www.codeproject.com/Tips/666578/HTML-and-Some-CSS-Best-Practice": "https://web.archive.org/web/2024/https://www.codeproject.com/Tips/666578/HTML-and-Some-CSS-Best-Practice",
    "https://jstherightway.org/": "https://github.com/braziljs/js-the-right-way",
    "https://learnvue.co/2020/01/12-vuejs-best-practices-for-pro-developers/": "https://learnvue.co/articles/vue-best-practices",
    "https://masteringnuxt.com/blog/nuxt-3-best-practices": "https://masteringnuxt.com/blog",
    "https://www.heroku.com/podcasts/codeish/72-beyond-the-12-factor-app": "https://12factor.net/",
    "https://martinfowler.com/articles/2024-evaluating-code-gen-tools.html": "https://martinfowler.com/articles/exploring-gen-ai.html",
    "https://expeditor.chef.io/docs/patterns/bash-scripts/": "https://google.github.io/styleguide/shellguide.html",
    "https://turbo.build/repo/docs/guides/migration": "https://turborepo.com/docs/guides/migrating-from-nx",
    "https://nx.dev/concepts/decisions/architecture": "https://nx.dev/concepts/decisions/overview",
    "https://nx.dev/resources/migration/turbo": "https://nx.dev/docs/kb/nx-vs-turborepo",
    "https://about.gitlab.com/remote/": "https://about.gitlab.com/company/culture/all-remote/",
    "https://auth0.com/blog/ten-things-you-should-know-about-tokens/": "https://auth0.com/blog/ten-things-you-should-know-about-tokens-and-cookies/",
    "https://biomejs.dev/guides/convert-eslint-prettier/": "https://biomejs.dev/guides/migrate-eslint-prettier/",
    "https://biomejs.dev/linter/rules/": "https://biomejs.dev/linter/",
    "https://nodejs.org/en/docs/guides/security/": "https://nodejs.org/en/learn/getting-started/security-best-practices",
    "https://trpc.io/docs/server/router": "https://trpc.io/docs/server/routers",
    "https://www.prisma.io/docs/orm/prisma-client/performance": "https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance",
    "https://snyk.io/blog/devsecops-best-practices/": "https://snyk.io/learn/devsecops/",
    "https://github.com/palantir/gradle-baseline/blob/develop/docs/best-practices/code-reviews/README.md": "https://github.com/palantir/gradle-baseline/blob/develop/docs/best-practices/code-reviews/readme.md",
}

updated_files = 0
for md in glob.glob(os.path.join(REPO_ROOT, "**", "*.md"), recursive=True):
    with open(md, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    modified = False
    # Longest first so a shorter rule can't partially match a longer one.
    for old_url, new_url in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
        # Match the URL as a whole token. Plain substring replacement is not
        # idempotent: an archive.org wrapper still contains the original URL,
        # and ".../router" is a prefix of ".../routers", so a second run would
        # re-match and corrupt already-fixed links.
        pattern = re.compile(
            r"(?<![A-Za-z0-9/_.\-])" + re.escape(old_url) + r"(?![A-Za-z0-9/_.\-])"
        )
        content, count = pattern.subn(lambda m: new_url, content)
        if count:
            modified = True

    if modified:
        with open(md, "w", encoding="utf-8") as f:
            f.write(content)
        updated_files += 1

print(f"Total files updated: {updated_files}")
