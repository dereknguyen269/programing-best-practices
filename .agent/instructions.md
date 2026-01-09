# Programming Best Practices Knowledge Base

## About This Repository

This repository is a **curated knowledge base** containing programming best practices, style guides, and coding standards for 30+ programming languages and frameworks. It is designed to serve as a reference for developers and AI coding assistants.

## Repository Structure

```
programing-best-practices/
├── README.md              # Main knowledge base (all resources organized by category)
├── CLAUDE.md              # Instructions for Claude Code
├── AGENTS.md              # General AI agent instructions
├── contributing.md        # How to contribute
├── LICENSE                # CC0 1.0 Universal
├── .agent/
│   ├── config.json        # Repository metadata
│   └── instructions.md    # This file
├── .kiro/
│   └── project.md         # Kiro-specific instructions
└── .github/
    └── FUNDING.yml
```

## How to Use This Knowledge Base

### When Asked About Best Practices

1. **Identify the Topic**: Determine if the question is about:
   - A specific programming language
   - A framework or library
   - System design/architecture
   - Security
   - Performance
   - DevOps/Cloud

2. **Navigate README.md**: The main document is organized with these sections:
   - 🔹 Backend Development
   - 🎨 Frontend Development
   - 🗄️ Database & Data
   - 📱 Mobile Development
   - ☁️ DevOps & Infrastructure
   - 🤖 AI & Data Science
   - 🛠️ Development Tools & Practices

3. **Provide Resources**: 
   - Cite the specific links from README.md
   - Prioritize "Featured Resources" for must-know guides
   - Include context about who created the resource (e.g., Airbnb, Google, Uber)

### Response Guidelines

- **Be Specific**: Point to exact resources and links
- **Cite Sources**: Include the original source links
- **Prioritize Quality**: Start with well-known, trusted sources
- **Consider Context**: Adapt recommendations to user's skill level
- **Stay Organized**: Follow the repository's category structure

### Featured Resources Quick Reference

| Category | Top Resource |
|----------|-------------|
| JavaScript | [Airbnb Style Guide](https://github.com/airbnb/javascript) |
| Clean Code | [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript) |
| System Design | [System Design 101](https://github.com/ByteByteGoHq/system-design-101) |
| Cloud Native | [12 Factor App](https://12factor.net/) |
| Security | [OWASP Top 10](https://owasp.org/www-project-top-ten/) |
| Go | [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) |
| Ruby | [bbatsov Ruby Style Guide](https://github.com/bbatsov/ruby-style-guide) |
| Design Patterns | [Refactoring.Guru](https://refactoring.guru/design-patterns) |

## Contribution Notes

When users ask about contributing:
- Direct them to `contributing.md`
- Encourage adding resources via Pull Requests
- Remind about quality standards (mainstream sources, active maintenance)

## Crawled Content

If the `content/` directory exists, it contains crawled versions of external resources:

```
content/
├── index.json          # Index of all crawled resources
├── metadata.yaml       # Crawl statistics
├── backend_development/
├── frontend_development/
└── ...
```

### Using Crawled Content

1. **Load index**: Read `content/index.json` to find relevant resources
2. **Read content**: Load specific markdown files for detailed information
3. **Use summaries**: Check `summaries/` for condensed category overviews

### Index Format

```json
{
  "resource_id": {
    "title": "Resource Title",
    "url": "https://original-source.com",
    "category": "Backend Development",
    "subcategory": "Python Best Practices",
    "file": "content/backend_development/abc123.md",
    "crawled_at": "2024-01-03T10:30:00"
  }
}
```

## Maintenance

This repository is actively maintained with regular updates:
- New resources are added as they emerge
- Outdated links are removed
- Organization is improved based on community feedback
- Content can be re-crawled with `python scripts/crawler/crawl.py --update`
