@echo off
setlocal EnableDelayedExpansion
REM ──────────────────────────────────────────────────────────────────────
REM  gh.cmd — Per-repo GitHub CLI token injection shim
REM
REM  The cmd.exe equivalent of the PowerShell `function gh` in powershell.psm1
REM
REM  How it works:
REM    1. setlocal creates a scoped copy of the environment
REM    2. If the current git repo has `gh.token` in local config, it
REM       overrides GH_TOKEN in the scoped environment
REM    3. gh.exe runs with the correct token (or no override if none set)
REM    4. When the script exits, setlocal auto-restores the parent
REM       environment — the token never leaks
REM
REM  This is the standard "shim" pattern used by Scoop, Chocolatey,
REM  nvm-windows, and pyenv-win. It works in interactive cmd, batch
REM  scripts, and any tool that shells out to cmd.
REM
REM  Setup:
REM    Ensure this file's directory appears in PATH BEFORE the directory
REM    containing gh.exe (e.g., C:\root\ProgramFiles\GitHub CLI\).
REM
REM  Per-repo token:
REM    git config --local gh.token ghp_YourPersonalAccessToken
REM ──────────────────────────────────────────────────────────────────────

for /f "usebackq delims=" %%T in (`git config --local gh.token 2^>nul`) do set "GH_TOKEN=%%T"

gh.exe %*
exit /b !ERRORLEVEL!
