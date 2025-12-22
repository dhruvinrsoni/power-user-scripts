@ECHO off
echo Welcome to the GitUtility - a wrapper on top of git to avoid writing "git" again and again...:P
FOR /f %%i IN ('ECHO prompt $E^| cmd') DO SET "ESC=%%i"
ECHO Type "e/q/exit/quit" to leave this utility.
call doskeys delete
IF NOT ["%*"]==[""] (SET GIT_CMD=%* && GOTO :RunGitCommand)

:GetGitBranch
REM for /f "usebackq tokens=*" %%i in (`git rev-parse --abbrev-ref HEAD 2^>nul`) do set GITBRANCH=%%i
for /f "usebackq tokens=*" %%i in (`cmd /D /C "git rev-parse --abbrev-ref HEAD 2>nul"`) do (set GITBRANCH=%%i)
REM for /f "tokens=*" %%i in ('bash -c "git rev-parse --abbrev-ref HEAD 2>/dev/null"') do (set GITBRANCH=%%i)
IF "!GITBRANCH!" == "" (SET PROMPT=!MYPROMPT![!GITBRANCH!]$$$S) ELSE (SET PROMPT=!MYPROMPT!)
SET GIT_CMD=
SET "COLOR_PROMPT=%ESC%[93m%ESC%[41m%ESC%[1m !DATE! %ESC%[93m%ESC%[102m%ESC%[1m !TIME! %ESC%[97m%ESC%[44m%ESC%[4m !CD!%ESC%[0m%ESC%[1;34;1;32m"
SET "MY_GIT_PROMPT=(!GITBRANCH!)%ESC%[0m^> "

call git status
ECHO.

ECHO !COLOR_PROMPT! && (ECHO|SET /p="!MY_GIT_PROMPT!")
:::  ECHO|SET /p="!MY_GIT_PROMPT!!COLOR_PROMPT!"
SET /p "GIT_CMD=git "

IF /i "!GIT_CMD!"=="E" GOTO exit0
IF /i "!GIT_CMD!"=="EXIT" GOTO exit0
IF /i "!GIT_CMD!"=="Q" GOTO exit0
IF /i "!GIT_CMD!"=="QUIT" GOTO exit0

:RunGitCommand
call git %GIT_CMD%
ECHO. 
GOTO :GetGitBranch

:exit0
ECHO.
SET GITBRANCH=
TITLE C:\WINDOWS\system32\cmd.exe
ECHO Thank You for Using the Git Utility. Exiting...
DOSKEY resetdoskeys= && CALL doskeys
exit /B 0