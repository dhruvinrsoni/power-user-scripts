# Atomic Git Commits

Git commits created by the agent must be atomic — one commit equals one complete, verified, logical change. If any step fails, nothing gets committed.

## Before Committing

1. Run `git status` and `git diff --staged` to review exactly what will be committed.
2. Verify every staged file is relevant to the current task. Never include unrelated changes.
3. Run the project's lint, compile, or build step (e.g., `mvn compile`, `npm run lint`, `tsc --noEmit`) to confirm the change doesn't break the codebase. If it fails, fix first, then commit.
4. Never stage or commit files that likely contain secrets: `.env`, `credentials.json`, `**/secrets/**`, `*.pem`, `*.key`. Warn the user if they specifically ask to commit those files.

## Commit Rules

- One logical change per commit. Don't bundle unrelated fixes, refactors, or features.
- Write the commit message as a concise summary of **why**, not what. Use past tense or imperative mood consistently with the repo's existing style. Check `git log --oneline -10` to match conventions.
- For multi-line commit messages, use `git commit -m "line 1" -m "line 2"` (multiple `-m` flags). This works in all shells — PowerShell, bash, and cmd. Example:
  ```
  git commit -m "feat: add user validation" -m "Validate email format and check for duplicates before saving."
  ```
- For single-line messages, a simple `git commit -m "message"` is fine.
- Never use HEREDOC syntax (`<<'EOF'`) — it is not supported in PowerShell.
- Never commit with `--allow-empty`, `--no-verify`, or `--no-gpg-sign` unless the user explicitly asks.

## After a Failed Commit

If the commit fails (pre-commit hook rejection, merge conflict, etc.):

- Fix the root cause.
- Create a **new** commit. Never `git commit --amend` on a failed commit.

## Amend Restrictions

Only use `--amend` when **all** of these are true:

1. The user explicitly requested an amend, or the commit succeeded but a pre-commit hook auto-modified files that need including.
2. The HEAD commit was created by the agent in this conversation (verify with `git log -1 --format='%an %ae'`).
3. The commit has not been pushed to remote (verify: `git status` shows "Your branch is ahead").

If any condition is false, create a new commit instead.

## Forbidden Operations (always ask the user)

- `git add .` or `git add -A` (stages everything blindly — stage specific files instead)
- `git commit` without reviewing `git diff --staged` first
- `git push` (never push unless the user explicitly asks)
- `git push --force` or `git push --force-with-lease` (warn if targeting main/master)
- `git reset --hard`
- `git rebase -i` (requires interactive input)
- `git stash drop` or `git stash clear`
- Any git config changes
