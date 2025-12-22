@ECHO off
SETLOCAL EnableDelayedExpansion
call get max

SET SEPARATE_WINDOW=0
IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && ECHO.>nul || START "Check API" /D "%~dp0" /max cmd /k "%~f0 %*" && exit /B 0 )

:: User-defined settings
SET API_URL=%1
SET TIMEOUT_TIME=%2
SET SEARCH_KEYWORD=%3
SET ONLY_STATUS_CHANGE=%4
SET LOOP=%5
echo.
echo 1 API_URL=%API_URL%, 2 TIMEOUT_TIME=%TIMEOUT_TIME%, 3 SEARCH_KEYWORD=%SEARCH_KEYWORD%, 4 ONLY_STATUS_CHANGE=%ONLY_STATUS_CHANGE%, 5 LOOP=%LOOP%

:: Prompt for input if not provided
IF [%API_URL%]==[] (SET /P API_URL="Enter the URL of the API(https://example.com/api):- ")
IF [%API_URL%]==[] (SET API_URL=https://example.com/api)

IF [%TIMEOUT_TIME%]==[] (SET /P TIMEOUT_TIME="Enter Timeout in seconds(30):- ")
IF "%TIMEOUT_TIME%"=="" (SET TIMEOUT_TIME=30)

IF [%SEARCH_KEYWORD%]==[] (SET /P SEARCH_KEYWORD="Enter the keyword to search for in the API response(version):- ")
IF "%SEARCH_KEYWORD%"=="" (SET SEARCH_KEYWORD=version)

IF [%ONLY_STATUS_CHANGE%]==[] (SET /P ONLY_STATUS_CHANGE="Only Status Changes[yes=1,no=0] (1):- ")
IF "%ONLY_STATUS_CHANGE%"=="" (SET ONLY_STATUS_CHANGE=1)

IF [%LOOP%]==[] (SET /P LOOP="Loop the script[yes=1,no=0] (0):- ")
IF "%LOOP%"=="" (SET LOOP=0)
echo.
echo API_URL=%API_URL%, TIMEOUT_TIME=%TIMEOUT_TIME%, SEARCH_KEYWORD=%SEARCH_KEYWORD%, ONLY_STATUS_CHANGE=%ONLY_STATUS_CHANGE%, LOOP=%LOOP%

powershell -noprofile write-host -fore yellow Checking the API: !API_URL! every %TIMEOUT_TIME% seconds interval...

SET TITLE=%~nx0: Initialized 

IF NOT "!LOOP!"=="0" (TITLE !TITLE! ^|^| CHECKING API @!API_URL!...) else (TITLE %~nx0: CHECKING API @!API_URL!...)

REM call get min


:check

curl -s !API_URL! | findstr /C:"%SEARCH_KEYWORD%" > nul
IF ERRORLEVEL 1 (
    GOTO fail
) ELSE (
	echo.
    GOTO success
)

:fail
SET TITLE=%~nx0: !API_URL!: KEYWORD NOT FOUND
TITLE !TITLE!
IF [%ONLY_STATUS_CHANGE%]==[1] (
    IF NOT "!PREVIOUS_STATUS!"=="0" (
        powershell -noprofile write-host -fore red %DATE% %TIME% ************ !API_URL!: KEYWORD NOT FOUND ************
        SET PREVIOUS_STATUS=0
        :: Log the full response only if status changes
        curl -s !API_URL!
    )
) ELSE (
    powershell -noprofile write-host -fore red %DATE% %TIME% ************ !API_URL!: KEYWORD NOT FOUND ************
    curl -s !API_URL!
)
GOTO wait

:success
SET TITLE=%~nx0: !API_URL!: KEYWORD FOUND
TITLE !TITLE!
IF [%ONLY_STATUS_CHANGE%]==[1] (
    IF NOT "!PREVIOUS_STATUS!"=="1" (
        powershell -noprofile write-host -fore green %DATE% %TIME% ************ !API_URL!: KEYWORD FOUND ************
        SET PREVIOUS_STATUS=1
        :: Log the full response only if status changes
        curl -s !API_URL!
    )
) ELSE (
    powershell -noprofile write-host -fore green %DATE% %TIME% ************ !API_URL!: KEYWORD FOUND ************
    curl -s !API_URL!
)
CALL :msg
IF NOT "%LOOP%"=="0" (GOTO wait) ELSE (GOTO exit)

:wait
call get min
IF NOT "%LOOP%"=="0" (
    TITLE %~nx0: !TITLE! ^|^| WAITING FOR %TIMEOUT_TIME% seconds
) ELSE (
    TITLE %~nx0: WAITING FOR %TIMEOUT_TIME% seconds
)
timeout /t %TIMEOUT_TIME% > nul
GOTO check

:msg
REM owershell -noprofile -window Maximized -command ""
call get max
msg "%USERNAME%" /W "@ %date% %time% : Keyword [%SEARCH_KEYWORD%] found in API response at URL [!API_URL!]"
start msedge "!API_URL!"

:exit
ECHO Exiting...
EXIT 0
