@ECHO Off
@REM echo %~0 is called with params [%*]
@REM IF "%1"=="delete" ( 
@REM     ECHO Deleting all doskey macros from %DOSFILE%
@REM 	FOR /F "usebackq delims== tokens=1" %%f in (`type "%DOSFILE%"`) do (DOSKEY %%f=)
@REM 	REM GOTO :EOF
@REM    exit /B 0
@REM )

@REM :: --- Guard Check: Check if the 'resetdoskeys' macro already exists --- 
@REM :: We try to run the macro definition into 'find'. If it finds "resetdoskeys", errorlevel is 0 (Success), so we EXIT.
@REM doskey /macros|findstr /i "resetdoskeys=">nul && exit /b 0||echo no doskeys>nul
@REM SET "HOME=%USERPROFILE%"
@REM :: Create the "Flag" and the "Reset" mechanism in one go = logic: Unset HOME -> Call this script again (re-loading macros)
@REM DOSKEY resetdoskeys=set "HOME=" ^&^& DOSKEY resetdoskeys= ^&^& "%~f0"

SET "ROOT=C:\root"

SET "USERTMPDIR=%USERPROFILE%\Temp"

REM SET MYPROMPT= $_$E[93m$E[41m$E[1m$S$D$S$E[93m$E[102m$E[1m$S$T$E[0m$H$H$H$S$_$E[97m$E[44m$E[4m$P$+$G$E[0m
SET MYPROMPT=$_$E[93m$E[41m$E[1m$S$D$S$E[93m$E[102m$E[1m$S$T$S$E[97m$E[44m$E[4m$S$P$+$S$E[0m$_$G$S

PROMPT !MYPROMPT!!GITPROMPT!

DOSKEY /OVERSTRIKE /MACROFILE="%DOSFILE%" $2>1