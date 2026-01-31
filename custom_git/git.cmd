@echo off
REM echo %CMDCMDLINE%
echo %CMDCMDLINE%| find "/c">nul || echo Using Wrapper Script - "%~dpnx0"
echo.

IF NOT "%*"=="" (
	git.exe %*
)

set GITBRANCH=
for /f "tokens=2" %%I in ('git.exe branch 2^> NUL ^| findstr /b "* "') do set GITBRANCH=%%I

SET MYPROMPT_FORCUSTOMGIT=!MYPROMPT:~0,-6!
REM echo MYPROMPT_FORCUSTOMGIT=!MYPROMPT_FORCUSTOMGIT!

if "!GITBRANCH!" == "" (
    prompt !MYPROMPT! 
) else (
    REM --- START: Custom code for commit (ahead/behind) status ---
    set AHEAD=
    set BEHIND=
    REM This command will only succeed if an upstream branch is configured.
    for /f "tokens=1,2" %%A in ('git.exe rev-list --left-right --count @{u}...HEAD 2^>NUL') do (
        set BEHIND=%%A
        set AHEAD=%%B
    )

    set "COMMIT_STATUS_STRING="
    REM Only build the string if the command was successful and values are non-zero.
    if defined AHEAD (
        if !AHEAD! GTR 0 (
            if !BEHIND! GTR 0 (
                set "COMMIT_STATUS_STRING=^^!AHEAD! ^<!BEHIND!"
            ) else (
                set "COMMIT_STATUS_STRING=^^!AHEAD!"
            )
        ) else (
            if !BEHIND! GTR 0 (
                set "COMMIT_STATUS_STRING=^<!BEHIND!"
            )
        )
    )

    if defined COMMIT_STATUS_STRING (
        REM Add color (magenta) and formatting. Note the space before the closing brace.
        set "COMMIT_STATUS_STRING=$E[1;35m{!COMMIT_STATUS_STRING!}$E[0m"
    )
    REM --- END: Custom code for commit status ---

    REM --- START: Custom code to get file status counts ---
    set ADDED=0
    set MODIFIED=0
    set DELETED=0
    REM Use 'git status --porcelain' which is fast and made for scripts.
    REM Count untracked ('??') as "added".
    for /f %%C in ('git.exe status --porcelain ^| findstr /b /c:"??" ^| find /c /v ""') do set ADDED=%%C
    REM Count modified (' M') in the working directory.
    for /f %%C in ('git.exe status --porcelain ^| findstr /c:" M" ^| find /c /v ""') do set MODIFIED=%%C
    REM Count deleted (' D') in the working directory.
    for /f %%C in ('git.exe status --porcelain ^| findstr /c:" D" ^| find /c /v ""') do set DELETED=%%C

    set "STATUS_STRING="
    REM Build the string, but only include non-zero counts.
    if !ADDED! NEQ 0 set "STATUS_STRING=!STATUS_STRING!+!ADDED! "
    if !MODIFIED! NEQ 0 set "STATUS_STRING=!STATUS_STRING!~!MODIFIED! "
    if !DELETED! NEQ 0 set "STATUS_STRING=!STATUS_STRING!-!DELETED! "

    REM If we added anything, format it and add color (yellow).
    if defined STATUS_STRING (
        REM Remove the trailing comma.
        set STATUS_STRING=!STATUS_STRING:~0,-1!
        REM Add brackets, color, and a leading space.
        set "STATUS_STRING=$E[1;33m[!STATUS_STRING!]"
        set "STATUS_STRING=!STATUS_STRING!$E[0m"
    )
    REM --- END: Custom code ---

    REM SET GITPROMPT=$E[1;34;1;32m$C!GITBRANCH!$F!COMMIT_STATUS_STRING!!STATUS_STRING!$E[0m$$$_$G$S
    SET "GITPROMPT=$E[1;34;1;32m $C!GITBRANCH!$F !COMMIT_STATUS_STRING! !STATUS_STRING! $E[0m$$$_$G$S"
    prompt !MYPROMPT_FORCUSTOMGIT!!GITPROMPT!
)

exit /b 0
