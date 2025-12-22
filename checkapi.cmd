@ECHO off
SETLOCAL EnableDelayedExpansion
call get max

SET SEPARATE_WINDOW=0
IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && ECHO.>nul || START "Check API" /D "%~dp0" /max cmd /k "%~f0 %*" && exit /B 0 )

SET API_URL=%1
SET TIMEOUT_TIME=%2
SET ONLY_STATUS_CHANGE=%3
SET LOOP=%4

echo 1 API_URL=%1, 2 TIMEOUT_TIME=%2, 3 ONLY_STATUS_CHANGE=%3, 4 LOOP=%4

IF [%API_URL%]==[] (call get max && SET /P API_URL="Enter the URL of the API:- ")
IF [%API_URL%]==[] (SET API_URL=https://example.com/api)

IF "%TIMEOUT_TIME%"=="" (call get max && SET /P TIMEOUT_TIME="Enter Timeout in seconds(30):- ")
IF "%TIMEOUT_TIME%"=="" (SET TIMEOUT_TIME=30)

IF "%ONLY_STATUS_CHANGE%"=="" (call get max && SET /P ONLY_STATUS_CHANGE="Only Status Changes[yes=1,no=0] (1):- ")
IF "%ONLY_STATUS_CHANGE%"=="" (SET ONLY_STATUS_CHANGE=1)

IF "%LOOP%"=="" (call get max && SET /P LOOP="Loop the script[yes=1,no=0] (0):- ")
IF "%LOOP%"=="" (SET LOOP=0)

echo API_URL=%API_URL%, TIMEOUT_TIME=%TIMEOUT_TIME%, ONLY_STATUS_CHANGE=%ONLY_STATUS_CHANGE%, LOOP=%LOOP%

powershell -noprofile write-host -fore yellow Checking the API: !API_URL! every %TIMEOUT_TIME% seconds interval till available... 

SET TITLE=%~nx0: Initialized 

IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| CHECKING API @!API_URL!...) else (TITLE %~nx0: CHECKING API @!API_URL!...)

REM call get min

:check
IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| CHECKING API @!API_URL!...) else (TITLE %~nx0: CHECKING API @!API_URL!...)

curl -s -o nul -w "%%{http_code}" !API_URL! | find "200" >nul && (GOTO reachable) || (GOTO notreachable)

:notreachable
SET TITLE=%~nx0: !API_URL!: NOT AVAILABLE
TITLE !TITLE!
IF [%ONLY_STATUS_CHANGE%]==[1] (
	IF [%PREVIOUS_STATUS%]==[1] (
		powershell -noprofile write-host -fore red %DATE% %TIME% ************ !API_URL!: NOT AVAILABLE ************  2>nul
		SET PREVIOUS_STATUS=0
		call get max 2>nul
	)
) ELSE (
	powershell -noprofile write-host -fore red %DATE% %TIME% ************ !API_URL!: NOT AVAILABLE ************  2>nul
)
GOTO wait

:reachable
SET TITLE=%~nx0: !API_URL!: AVAILABLE
TITLE !TITLE!
IF [%ONLY_STATUS_CHANGE%]==[1] (
	IF [%PREVIOUS_STATUS%]==[0] (
		powershell -noprofile write-host -fore green %DATE% %TIME% ************ !API_URL!: AVAILABLE ************  2>nul
		SET PREVIOUS_STATUS=1
		call get max 2>nul
	)
) ELSE (
	powershell -noprofile write-host -fore green %DATE% %TIME% ************ !API_URL!: AVAILABLE ************  2>nul
	IF NOT "!LOOP!"=="0" (call get max 2>nul)
)
CALL :msg
IF NOT "!LOOP!"=="0" (GOTO wait) ELSE (GOTO exit)

:wait
call get min
IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| WAITING FOR %TIMEOUT_TIME% seconds) else (TITLE %~nx0: WAITING FOR %TIMEOUT_TIME% seconds)
timeout /t %TIMEOUT_TIME% > nul
GOTO check

:msg
call get max 2>nul
msg "%USERNAME%" /W "@ %date% %time% : API [!API_URL!] is now available"
start msedge "!API_URL!"

:exit
ECHO Exiting Soon... && timeout /t 1 >nul
call get min
ECHO %CMDCMDLINE%|find "%~f0">nul && timeout /t 300
EXIT 0