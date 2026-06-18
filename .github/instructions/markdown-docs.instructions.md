---
description: "Use when editing Markdown files, repository documentation, docs-adjacent text files, or markdownlint settings in JSON or JSONC config. Covers code fence language tags, line-length policy, and ordered-list numbering conventions."
applyTo: "**/*.md, .vscode/**/*.json, .vscode/**/*.jsonc, LICENSE"
---

# Markdown And Markdownlint Guidelines

- Keep fenced code blocks language-tagged. Do not disable `MD040` globally; if a block is intentionally plain text, handle that case locally instead of relaxing the repo-wide rule.
- Keep line-length linting enabled with explicit limits. Prefer configuring `MD013` over disabling it, and exclude noisy cases such as tables or fenced code blocks when needed.
- Prefer `MD029` style `one` so ordered lists can use `1.` repeatedly and avoid renumbering churn in diffs.
- When changing markdownlint settings, preserve readability and reviewability for docs before optimizing for editor convenience.
