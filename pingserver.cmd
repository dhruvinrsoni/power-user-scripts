@ECHO off
SETLOCAL EnableDelayedExpansion

IF "%1"=="net" (echo Calling Preset:"%1" as call %~n0 google.com 15 0 0 && call %~n0 google.com 15 0 0)

SET SEPARATE_WINDOW=1
IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && ECHO.>nul || START "Ping Server" /D "%~dp0" /max cmd /k "%~f0 %*" && exit /B 0 )
REM SET ONLY_STATUS_CHANGE=1
REM IF [%ONLY_STATUS_CHANGE%]==[1] (SET PREVIOUS_STATUS=)

SET SERVER_IP=%1
SET TIMEOUT_TIME=%2
SET ONLY_STATUS_CHANGE=%3
SET LOOP=%4

echo 1 SERVER_IP=%1, 2 TIMEOUT_TIME=%2, 3 ONLY_STATUS_CHANGE=%3, 4 LOOP=%4

IF [%SERVER_IP%]==[] (SET /P SERVER_IP="Enter the ip of the Server(google.com):- ")
IF [%SERVER_IP%]==[] (SET SERVER_IP=google.com)

IF "%TIMEOUT_TIME%"=="" (SET /P TIMEOUT_TIME="Enter Timeout in seconds(30):- ")
IF "%TIMEOUT_TIME%"=="" (SET TIMEOUT_TIME=30)

IF "%ONLY_STATUS_CHANGE%"=="" (SET /P ONLY_STATUS_CHANGE="Only Status Changes[yes=1,no=0] (1):- ")
IF "%ONLY_STATUS_CHANGE%"=="" (SET ONLY_STATUS_CHANGE=1)

IF "%LOOP%"=="" (SET /P LOOP="Loop the script[yes=1,no=0] (0):- ")
IF "%LOOP%"=="" (SET LOOP=0)

echo SERVER_IP=%SERVER_IP%, TIMEOUT_TIME=%TIMEOUT_TIME%, ONLY_STATUS_CHANGE=%ONLY_STATUS_CHANGE%, LOOP=%LOOP%

::powershell -noprofile -window Maximized -command ""  2>nul
IF "%LOOP%"=="0" (powershell -noprofile write-host -fore yellow Pinging the SERVER:!SERVER_IP! every %TIMEOUT_TIME% seconds interval till reachable...) ELSE ( IF "%ONLY_STATUS_CHANGE%"=="1" (powershell -noprofile write-host -fore yellow Pinging the SERVER:!SERVER_IP! every %TIMEOUT_TIME% seconds interval displaying only changes...) ELSE (powershell -noprofile write-host -fore yellow Pinging the SERVER:!SERVER_IP! every %TIMEOUT_TIME% seconds interval displaying all...) )
REM ECHO Pinging the SERVER:!SERVER_IP! every %TIMEOUT_TIME% seconds interval till reachable...
REM powershell -noprofile write-host -fore yellow Pinging the SERVER IP:!SERVER_IP! every %TIMEOUT_TIME% seconds interval till reachable...  2>nul
REM timeout /t 3 > nul
REM powershell -noprofile -window Minimized -command ""  2>nul
SET TITLE=Intialized 
REM call get min
IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| CHECKING SERVER @!SERVER_IP!...) else (TITLE CHECKING SERVER @!SERVER_IP!...)
REM TITLE CHECKING SERVER @!SERVER_IP!...
ping !SERVER_IP!|find /C "Reply">nul && (
	SET PREVIOUS_STATUS=0
	GOTO reachable
) || (
	SET PREVIOUS_STATUS=1
	GOTO notreachable
)

:check
IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| CHECKING SERVER @!SERVER_IP!...) else (TITLE CHECKING SERVER @!SERVER_IP!...)
REM TITLE CHECKING SERVER @!SERVER_IP!...
ping !SERVER_IP!|find /C "Reply">nul && (GOTO reachable) || (GOTO notreachable)

:notreachable
SET TITLE=!SERVER_IP!: NOT AVAILABLE
TITLE !TITLE!
REM ECHO %DATE% %TIME% ************ !SERVER_IP!: NOT AVAILABLE ************
REM powershell -noprofile write-host -fore red %DATE% %TIME% ************ !SERVER_IP!: NOT AVAILABLE ************  2>nul
IF [%ONLY_STATUS_CHANGE%]==[1] (
	IF [%PREVIOUS_STATUS%]==[1] (
		powershell -noprofile write-host -fore red %DATE% %TIME% ************ !SERVER_IP!: NOT AVAILABLE ************  2>nul
		SET PREVIOUS_STATUS=0
		powershell -noprofile -window Maximized -command ""  2>nul
	)
) ELSE (
	powershell -noprofile write-host -fore red %DATE% %TIME% ************ !SERVER_IP!: NOT AVAILABLE ************  2>nul
)
GOTO wait

:reachable
SET TITLE=!SERVER_IP!: AVAILABLE
TITLE !TITLE!
REM ECHO %DATE% %TIME% ************ !SERVER_IP!: AVAILABLE ************
REM IF NOT "!LOOP!"=="0" (powershell -noprofile write-host -fore green %DATE% %TIME% ************ !SERVER_IP!: AVAILABLE ************  2>nul)
IF [%ONLY_STATUS_CHANGE%]==[1] (
	REM only status change so need to confirm previous state
	IF [%PREVIOUS_STATUS%]==[0] (
		REM Previous state not available so need to log as available and maximize window to show
		powershell -noprofile write-host -fore green %DATE% %TIME% ************ !SERVER_IP!: AVAILABLE ************  2>nul
		SET PREVIOUS_STATUS=1
		powershell -noprofile -window Maximized -command ""  2>nul
	)
) ELSE (
	REM need all statuses so logging on console
	powershell -noprofile write-host -fore green %DATE% %TIME% ************ !SERVER_IP!: AVAILABLE ************  2>nul
	IF NOT "!LOOP!"=="0" (powershell -noprofile -window Maximized -command ""  2>nul)
)
CALL :msg
IF NOT "!LOOP!"=="0" (GOTO wait) ELSE (GOTO exit)

:wait
call get min
IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| WAITING FOR %TIMEOUT_TIME% seconds) else (TITLE WAITING FOR %TIMEOUT_TIME% seconds)
REM TITLE WAITING FOR %TIMEOUT_TIME% seconds
timeout /t %TIMEOUT_TIME% > nul
GOTO check

:msg
powershell -noprofile -window Maximized -command ""  2>nul
msg "%USERNAME%" /W "@ %date% %time% : Server [!SERVER_IP!] is now available"
start msedge "!SERVER_IP!"

:exit
ECHO Exiting...
REM ECHO %CMDCMDLINE%|find "%~f0">nul && timeout /nobreak /t -1 || call get min
ECHO %CMDCMDLINE%|find "%~f0">nul && timeout /t -1 /nobreak || call get min
EXIT 0