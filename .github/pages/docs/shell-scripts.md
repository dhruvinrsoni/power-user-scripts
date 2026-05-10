# Shell scripts

POSIX-side companions to the Windows utilities.

## scripts/init-bash.sh

A WSL bootstrap script. Configures `/etc/wsl.conf` (systemd + DNS),
creates a `~/.bash_aliases` file with 30+ common aliases (cd, ls
variants, disk and file helpers, Maven/Java tools, git navigation), logs
every action, and backs up existing files before overwriting.

```bash
sh ./scripts/init-bash.sh
```

Source: [`scripts/init-bash.sh`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/scripts/init-bash.sh)

## shcmd/sh.cmd

A hybrid shell/batch script template. Interleaves Bash and `cmd.exe`
commands in a single file using labeled blocks, so the same file runs on
both Linux and Windows. Useful as a starting point for cross-platform
utilities.

Source: [`shcmd/sh.cmd`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/shcmd/sh.cmd)
