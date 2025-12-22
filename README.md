# power-user-scripts

A curated, cross-platform toolbox of power-user scripts: shell wrappers, batch/PowerShell tools, tweaks and prompt templates for productivity.

# power-user-scripts

Curated toolbox of cross-platform power-user scripts, profiles, and prompts — batch, PowerShell, shell wrappers, tweaks, and utilities for productivity.

## What this repo is

A personal collection of small utilities: batch files, PowerShell modules and profiles, shell wrappers, registry snippets, and prompt templates. It started on Windows but is intentionally generic so it can grow into a cross-platform toolkit.

## Top-level layout

- Root: assorted batch/cmd utilities (startup, git helpers, logging, networking shortcuts)
- `powershell/`: PowerShell profiles, modules and deployment helpers
- `Hacks/`: experimental scripts, registry edits and small utilities
- `archieves/`: older archived scripts and backups
- `custom_git/`: git helpers and commit-template
- `Prompts/`: prompt templates and snippets for authoring
- `shcmd/`: small shell wrapper helpers

## Security note

This workspace contains absolute paths, usernames, emails, and company-specific project names. A detailed listing of all such instances is in `SENSITIVE_INSTANCES.txt`. Review and sanitize those entries before making this repo public.

## Quick start

1. Review `SENSITIVE_INSTANCES.txt` and decide which files to sanitize or exclude.
2. Choose `.gitignore` templates: recommended selections are `Windows`, `PowerShell`, and `VisualStudioCode`.
3. Add a license (recommended: MIT) and push to a private repo first for validation.

## Contributing

This is a personal collection. If you accept external contributions, clearly mark which scripts are safe to run and provide usage notes and tests. Avoid committing any credentials or organization-specific configuration.

## License

This repository is licensed under the MIT License (see `LICENSE`).
