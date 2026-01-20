:: Name:		logger.cmd
:: Description:	This is a console application which will add the typed "Work Log" to a file in format [date time day]: <log>
:: Purpose:		User can run this console application to log some of his events/works etc. 
:: Author:		dhruvin.soni
:: Revision:	[0.1.0] 31 October 2019 - initial version. 
::				[0.2.0] 04 November 2019 - added logfile and empty IF conditions. 
::				[0.3.0] 12 November 2019 - added the day of week also into the log. 
::				[0.4.0] 18 December 2019 - added the %* to enter first log from "logger.cmd" command execution. 
::				[0.5.0] 06 January 2020 - splitted the code to labels and added 1hr reminder to log after startup or each log. 
::				[0.6.0] 17 February 2020 - changed the log files as read only. When logged they will be not read only. 
::				[0.7.0] 14 September 2020 - Removed logfile as read-only. 
::				[0.8.0] 10 November 2020 - COPY_TO_CLIP, TIMEOUT, REMINDER, as config, added #log as to log and quit; re-factoring; show this with info command; 
::				[0.9.0] 08 January 2021 - Optimized the requirements and the functionality
::				[1.0.0-alpha] 14 July 2022 - Add the escape character before system reserved charaters like: ^& ^\ ^< ^> ^^ ^|
::				[1.0.1] 15 November 2022 - Added :preCleanUp & :cleanUp
:: Copyright (C) 2019 Dhruvin Soni. All rights reserved.
@ECHO Off
SET SEPARATE_WINDOW=1
SET TIMEOUT_TIME_IN_SECONDS=1800
SETLOCAL EnableDelayedExpansion
CALL get max 
PUSHD %SCRIPTS%
IF NOT DEFINED LOGFILE (SET LOGFILE="%OneDrive%\WorkLogs\MyWorkLog_%date%.LOG")
IF NOT [%1]==[] (
	SET LOG_MSG=%*
	GOTO checkLog
)
IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && ECHO.>nul || start "Work Logger" /D "%~dp0" /max cmd /k "%~f0 %*" && exit /B 0 )
CALL doskeys delete

SET WINDOW_TITLE="Work Logger || quit - exit this app || restart - quit this and start new logger || [Enter] - Skip Logging || logs - open log file || -info - get information about this"
TITLE %WINDOW_TITLE%
ECHO Employee Work Logger [Version 1.0.0-alpha]
ECHO Copyright (C) 2019 Dhruvin Soni. All rights reserved. :)
ECHO.
ECHO %WINDOW_TITLE%
ECHO.
ECHO ^> %date% %time% :
ECHO ^> Log File ^( Read-Write ^):- "%LOGFILE%"
ECHO ^> Running at:- "%CD%"
ECHO.

:resetLog
ECHO.[%DATE% %TIME%]
SET LOG_MSG=
SET /p LOG_MSG=Enter the Log:- 
REM @ECHO On
REM ECHO. PreCleanUp: %LOG_MSG%
IF NOT DEFINED LOG_MSG ( GOTO wait )
SET "LOG_MSG=%LOG_MSG:"='%"
SET "LOG_MSG=%LOG_MSG:&=^&%"
SET "LOG_MSG=%LOG_MSG:|=^|%"
SET "LOG_MSG=%LOG_MSG:<=^<%"
SET "LOG_MSG=%LOG_MSG:>=^>%"
SET "LOG_MSG=%LOG_MSG:^^=^^^^%"
SET "LOG_MSG=%LOG_MSG:^^!=^^!%"
REM ECHO. PostCleanUp: "%LOG_MSG%"
REM PAUSE

:postCleanUp
IF "%LOG_MSG%"=="quit" ( GOTO exitMsg )
IF "%LOG_MSG%"=="restart" ( GOTO restart )

:checkLog
IF "%LOG_MSG%"=="logs" ( 
	START "" "%ROOT%\ProgramFiles\Notepad++\notepad++.exe" -nosession -notabbar -multiInst  "%LOGFILE%" && CALL get min
	IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && GOTO wait || GOTO exit ) ELSE ( IF "%2"=="logs" ( GOTO exit ) else ( GOTO wait ) )
	GOTO exit
)
IF "%LOG_MSG%"=="info" ( ECHO. && findstr /B ":: " "%~f0" 
	IF [%SEPARATE_WINDOW%]==[1] ( GOTO resetLog ) ELSE ( GOTO exitMsg )
)

SET LOG=[%date% %time%]: %LOG_MSG%

ECHO. >> "%LOGFILE%"
ECHO !LOG! >> "%LOGFILE%" && ( GOTO logSuccess ) || ( ECHO CMD needs ^ character before some system reserved charaters like: ^& ^\ ^< ^> ^^ ^| ^" )
ECHO.
GOTO resetLog )

:logSuccess
ECHO !LOG!
msg %USERNAME% /TIME:1 "%LOG_MSG%" 2>nul || msg %USERNAME% /TIME:3 "Some Error has happened while showing the logged message here. May be the length of the message is too long." 
IF [%SEPARATE_WINDOW%]==[1] ( ECHO %CMDCMDLINE%|find "%~f0">nul && GOTO wait || (CALL get min & GOTO exit) )

:wait
CALL get min
REM start "Timeout to the reminder to Log Your Work" /min cmd /c "call get min && timeout /t 1800 && msg %USERNAME% /W "Log Your Work""
timeout /t %TIMEOUT_TIME_IN_SECONDS%
powershell -noprofile -window Maximized -command "" 2>nul
msg %USERNAME% /TIME:6 "Log Your Work "
ECHO.
GOTO resetLog

:reSTART
START logger.cmd
GOTO exitMsg

:exitMsg
ECHO. && ECHO.^> Thank You for Using %~nx0. Exiting... Bye :)
timeout /t 03>nul

:exit
CALL doskeys
exit /B 0

:EOF