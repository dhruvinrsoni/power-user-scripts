# CMD utilities

Root-level `.cmd` shortcuts. Install by adding the repo root to your
`PATH`, or call them by full path. Most are Windows `cmd.exe` only;
PowerShell can invoke them but won't always inherit aliases.

## Git & GitHub

| File | Purpose | Notes |
|---|---|---|
| [`gitinit.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/gitinit.cmd) | Initialize global git config: shell, pager, GPG, editor, merge tools. | Run once per machine |
| [`gh.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/gh.cmd) | GitHub CLI token-injection shim with per-repo local git config. | Per-repo tokens |
| [`gu.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/gu.cmd) | Interactive git utility wrapper with colored prompt and status display. | Interactive |
| [`enable-custom-git.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/enable-custom-git.cmd) / [`activate-custom-git.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/activate-custom-git.cmd) | Prepend `custom_git/` to PATH so the wrapper takes over `git`. | Aliases of each other |
| [`disable-custom-git.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/disable-custom-git.cmd) / [`deactivate-custom-git.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/deactivate-custom-git.cmd) | Remove `custom_git/` from PATH; restore default `git`. | Aliases of each other |

See [Custom Git wrapper](custom-git.md) for what `enable`/`activate` flips on.

## API & network monitoring

| File | Purpose | Notes |
|---|---|---|
| [`pingserver.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/pingserver.cmd) | Continuously ping a server/IP with status logging and optional alerts. | Configurable interval |
| [`checkapi.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/checkapi.cmd) | Monitor an API endpoint's availability with timeout and logging. | Configurable interval |
| [`grepapi.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/grepapi.cmd) | Monitor an API endpoint and match a keyword in the response. | Keyword search |

## Terminal & productivity

| File | Purpose | Notes |
|---|---|---|
| [`doskeys.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/doskeys.cmd) | DOS macros, prompt colors, command-prompt settings. | `cmd.exe` only |
| [`get.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/get.cmd) | Menu-driven utility for window sizing, system apps, misc tasks. | Menu-based |
| [`logger.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/logger.cmd) | Log timestamped work activities to a file with hourly reminder pings. | Requires admin |

## Admin

| File | Purpose | Notes |
|---|---|---|
| [`admincmd.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/admincmd.cmd) | Run commands as administrator via the `cmd-as-admin` scheduled task. | Requires admin task pre-set |
| [`admin.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/admin.cmd) | Empty placeholder. | — |
