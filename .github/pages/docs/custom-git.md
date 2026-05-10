# Custom Git wrapper

A drop-in `git.cmd` that wraps the real `git.exe` and decorates your
prompt with **branch name** and **ahead/behind counts** after every
command. The vanilla `git status` already tells you this — but you have
to ask. The wrapper makes it ambient.

## How it works

`custom_git/git.cmd` shadows `git.exe` on `PATH`. Every git invocation
runs through it; after the underlying `git` finishes, the wrapper queries
`git rev-parse`, `git status --porcelain`, and `git rev-list --count`
to refresh the prompt with current state.

Display includes:

- Current branch name
- Commits ahead / behind the upstream
- Counts of added, modified, and deleted files (from porcelain output)

## Installation

There are two name pairs that do the same thing — pick either:

```bat
:: enable
enable-custom-git.cmd
:: or equivalently
activate-custom-git.cmd

:: disable
disable-custom-git.cmd
:: or equivalently
deactivate-custom-git.cmd
```

Each script prepends or removes `custom_git/` on `PATH` for the current
session.

## Source

[`custom_git/git.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/custom_git/git.cmd)
