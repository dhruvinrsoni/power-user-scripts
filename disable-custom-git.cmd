@ECHO off
REM SETLOCAL EnableDelayedExpansion

SET CURRENT_DIR=%~dp0
SET CUSTOM_GIT_DIR=!CURRENT_DIR!custom_git

ECHO where git output:
where git
ECHO.
ECHO Current Path
ECHO %PATH%

SET $line=%path%
SET $line=%$line: =#%
SET $line=%$line:;= %
SET $line=%$line:)=^^)%

SET CUSTOM_GIT_DIR=%CUSTOM_GIT_DIR: =#%
SET CUSTOM_GIT_DIR=%CUSTOM_GIT_DIR:;= %
SET CUSTOM_GIT_DIR=%CUSTOM_GIT_DIR:)=^^)%

SET NEWPATH=

FOR %%a IN (%$line%) DO (ECHO "%%a"|find "!CUSTOM_GIT_DIR!">nul || SET NEWPATH=!NEWPATH!;"%%a")

SET NEWPATH=!NEWPATH:#= !
ECHO.
ECHO New Path
ECHO !NEWPATH:#= !
SET PATH=%NEWPATH:"=%

REM SET PATH=%TEMP_PATH%
REM ECHO. !PATH!
REM @ECHO. !PATH!|find "!CUSTOM_GIT_DIR!"

ECHO.
ECHO where git output:
where git

SET GITPROMPT=
call doskeys
prompt !MYPROMPT!!GITPROMPT!

EXIT /B 0
