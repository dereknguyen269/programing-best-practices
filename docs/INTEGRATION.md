# 🔗 Integrating This Knowledge Base Into Your Projects

This guide explains how to use the Programming Best Practices knowledge base with your existing projects and AI coding assistants.

---

## 📋 Integration Methods

### Method 1: Git Submodule (Recommended)

Add this repository as a submodule in your existing project:

```bash
# Navigate to your project root
cd /path/to/your-project

# Add as submodule
git submodule add https://github.com/dereknguyen269/programing-best-practices.git .kb/best-practices

# Commit the change
git commit -m "Add programming best practices knowledge base"
```

**Structure after integration:**
```
your-project/
├── src/
├── .kb/
│   └── best-practices/        # Knowledge base
│       ├── README.md
│       ├── CLAUDE.md
│       └── ...
├── CLAUDE.md                  # Your project's AI config (references .kb/)
└── ...
```

---

### Method 2: Reference in AI Configuration

Add a reference to this knowledge base in your project's AI configuration files:

#### For Claude Code (`CLAUDE.md`)

```markdown
# Your Project Name

## Knowledge Base Reference

This project uses best practices from:
- **Repository**: https://github.com/dereknguyen269/programing-best-practices
- **Local Path**: .kb/best-practices/ (if using submodule)

When reviewing code or suggesting improvements, reference the appropriate
language-specific best practices from the knowledge base.

## Project-Specific Guidelines

[Your project's specific guidelines here...]
```

#### For Antigravity (`.agent/instructions.md`)

```markdown
## External Knowledge Base

Reference programming best practices from:
- https://github.com/dereknguyen269/programing-best-practices

Use this for:
- Code style guidance
- Architecture decisions
- Security best practices
- Performance optimization
```

---

### Method 3: Symbolic Link

Create a symbolic link to a local clone:

```bash
# Clone the knowledge base (once)
git clone https://github.com/dereknguyen269/programing-best-practices.git ~/knowledge-bases/programming-best-practices

# In each project, create a symbolic link
cd /path/to/your-project
ln -s ~/knowledge-bases/programming-best-practices .kb/best-practices
```

---

### Method 4: Copy Configuration Templates

Copy the relevant AI configuration templates to your project:

```bash
# Clone or download the repository
git clone https://github.com/dereknguyen269/programing-best-practices.git /tmp/bp

# Copy the templates you need
cp /tmp/bp/templates/project-claude.md your-project/CLAUDE.md
cp -r /tmp/bp/templates/agent your-project/.agent
cp /tmp/bp/templates/cursorrules your-project/.cursorrules

# Clean up
rm -rf /tmp/bp
```

---

## 🛠️ Project Templates

### Template: CLAUDE.md for Your Project

```markdown
# [Your Project Name]

## Project Overview
[Brief description of your project]

## Tech Stack
- **Language**: [e.g., TypeScript, Python, Go]
- **Framework**: [e.g., Next.js, FastAPI, Gin]
- **Database**: [e.g., PostgreSQL, MongoDB]

## Coding Standards

Follow the best practices from:
- **[Language]**: https://github.com/dereknguyen269/programing-best-practices#[language]-best-practices
- **[Framework]**: https://github.com/dereknguyen269/programing-best-practices#[framework]-best-practices

## Project-Specific Rules
[Your project's specific guidelines]
```

### Template: .agent/instructions.md for Your Project

```markdown
# [Your Project Name] - Agent Instructions

## Project Type
[e.g., Web Application, CLI Tool, API Service]

## Technology Stack
- Language: [language]
- Framework: [framework]
- Database: [database]

## Best Practices Reference

Use the Programming Best Practices knowledge base for:
- Code style: https://github.com/dereknguyen269/programing-best-practices#[language]-best-practices
- Architecture: https://github.com/dereknguyen269/programing-best-practices#system-design-best-practices
- Security: https://github.com/dereknguyen269/programing-best-practices#api-security-best-practices

## Project Structure
[Describe your project structure]

## Key Guidelines
[Your project-specific guidelines]
```

---

## 🔄 Keeping Updated

### If Using Submodule

```bash
# Update the knowledge base
cd your-project
git submodule update --remote .kb/best-practices
git commit -m "Update knowledge base"
```

### If Using Symbolic Link

```bash
# Update the local clone
cd ~/knowledge-bases/programming-best-practices
git pull origin main
```

---

## 📚 Quick Reference Links

Use these direct links in your project documentation:

| Topic | Link |
|-------|------|
| JavaScript | `#javascript-best-practices` |
| TypeScript | `#typescript-best-practices` |
| Python | `#python-best-practices` |
| Go | `#go-golang-best-practices` |
| Ruby | `#ruby-best-practices` |
| Rails | `#rails-best-practices` |
| React | `#reactjs-best-practices` |
| Node.js | `#nodejs-best-practices` |
| SQL | `#sql-best-practices` |
| System Design | `#system-design-best-practices` |
| API Security | `#api-security-best-practices` |
| Code Review | `#code-review-best-practices` |

---

## 💡 Example Use Cases

### 1. Setting Up a New TypeScript Project

```markdown
# CLAUDE.md

## Coding Standards
Follow TypeScript best practices from the knowledge base:
https://github.com/dereknguyen269/programing-best-practices#typescript-best-practices

Key guides to follow:
- Airbnb JavaScript Style Guide (for JavaScript patterns)
- Clean Code JavaScript principles
```

### 2. Adding to a Python API Project

```markdown
# .agent/instructions.md

## Best Practices
- Python style: Follow PEP 8 and BOBP Guide
- API security: Reference OWASP Top 10 and API Security Checklist
- Database: Follow PostgreSQL best practices for queries

Reference: https://github.com/dereknguyen269/programing-best-practices
```

### 3. Ruby on Rails Application

```markdown
# CLAUDE.md

## Rails Best Practices
Follow the guides from:
- Rails Style Guide (@bbatsov)
- RSpec Best Practices
- Production Rails guide

Full reference: https://github.com/dereknguyen269/programing-best-practices#rails-best-practices
```
