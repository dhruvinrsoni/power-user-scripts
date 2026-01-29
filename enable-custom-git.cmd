@echo off
REM SETLOCAL EnableDelayedExpansion

SET CURRENT_DIR=%~dp0
SET CUSTOM_GIT_DIR=!CURRENT_DIR!custom_git

ECHO. 
ECHO Current Path 
ECHO %PATH%
ECHO.
ECHO where git output:
where git

SET PATH=!CUSTOM_GIT_DIR!;!PATH!

ECHO. 
ECHO New Path 
ECHO %PATH%
ECHO.
ECHO %PATH%|find "!CUSTOM_GIT_DIR!"
ECHO.
ECHO where git output:
where git
ECHO.
ECHO Calling git.cmd at !CUSTOM_GIT_DIR!
call git.cmd

exit /B 0
