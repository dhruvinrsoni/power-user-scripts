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

SET GITPROMPT=$E[1;34;1;32m$C!GITBRANCH!$F$E[0m$$$_$G$S
if "!GITBRANCH!" == "" (
    prompt !MYPROMPT! 
) else (
    prompt !MYPROMPT_FORCUSTOMGIT!!GITPROMPT!
)
exit /b 0