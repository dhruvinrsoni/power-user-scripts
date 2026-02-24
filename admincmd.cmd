:: Name:        admincmd.cmd
:: Description: This is a console application which will execute the passed parameters as administrator command prompt.
::              It logs the typed commands to "Admin Command Text Logs" in the format: [date time day]: <parameters>
::
:: Usage Help:
::   - `admincmd.cmd exit <commands>` : Runs the commands as admin and closes the admin window after execution.
::   - `admincmd.cmd this`            : Opens an interactive input mode. Type your script, then press [Ctrl+Z] and [Enter] to save and run it as admin.
::   - `admincmd.cmd checkadmin`      : Checks if the current shell is running with administrator privileges.
::   - `admincmd.cmd <commands>`      : Runs the commands as admin and keeps the admin window open.
::   - `admincmd.cmd` (no args)       : Just opens a command prompt as admin.
::
:: Requirements:
::   - A scheduled task named "cmd-as-admin" must exist and be configured to run `cmd.exe` with admin privileges.
::
:: Purpose:     Allows users to run commands as administrator from a standard console or script.
:: Author:      Dhruvin Soni
:: Revision:    [0.1.0] 16 November 2022 - Initial version.
:: Copyright (C) 2022 Dhruvin Soni. All rights reserved.

@ECHO OFF
@echo Admin CMD [Version 0.1.0]
@echo Copyright (C) 2022 Dhruvin Soni. All rights reserved. :)
@if defined FPS_BROWSER_USER_PROFILE_STRING (
    echo This script was invoked from PowerShell.
) else (
    echo This script was not invoked from PowerShell.
)
@echo %CMDCMDLINE%|find "%~f0" && (@ECHO ON) || (@ECHO OFF)
:: give first parameter as "exit" to exit the admin script after the execution of the parameteres %2 onwards
:: give first parameter as "this" to start typing the script and then [Ctrl-Z]+[Enter] to insert that as script to run as admin
:: give all parameters as a command to run and keep the admin prompt open
:: or don't give any command and open cmd as admin

SET "ADMIN_CMD_LOGS_FILE=%~dp0admin.cmd.txt"
SET "ADMIN_CMD_FILE=%~dp0admin.cmd"
REM ECHO %*
IF "%1"=="exit" (
	SET ARGS=%*
	ECHO !ARGS!
	SET ARGS=!ARGS:~5!
	ECHO !ARGS!
		
	ECHO !ARGS! > "%ADMIN_CMD_FILE%"
	REM ECHO. >> "%ADMIN_CMD_FILE%"
	ECHO exit >> "%ADMIN_CMD_FILE%"
	ECHO [%date% %time%]: %* >> "%ADMIN_CMD_LOGS_FILE%"
	ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
	
	goto schedule
)

IF "%1"=="this" (
	ECHO Opens an interactive input mode. Type your script, then press [Ctrl+Z] and [Enter] to save and run it as admin.
	REM ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
	:: add commans to the file
	COPY CON "%ADMIN_CMD_FILE%"
	:: log all details
	ECHO [%date% %time%]: >> "%ADMIN_CMD_LOGS_FILE%"
	TYPE "%ADMIN_CMD_FILE%" >> "%ADMIN_CMD_LOGS_FILE%"
	ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
	
	goto schedule
)

IF "%1"=="checkadmin" (
    net session >nul 2>&1 && ( ECHO [INFO] You are running as Administrator. ) || ( ECHO [INFO] You are NOT running as Administrator. )
    REM IF %ERRORLEVEL% EQU 0 (
        REM ECHO [INFO] You are running as Administrator.
    REM ) ELSE (
        REM ECHO [INFO] You are NOT running as Administrator.
    REM )
    EXIT /B
)

IF NOT "%*"=="" (
	:: run parameteres as command 
	REM ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
	REM ECHO ECHO %* > %~dp0args.cmd && PAUSE
	ECHO %* > "%ADMIN_CMD_FILE%"
	ECHO [%date% %time%]: %* >> "%ADMIN_CMD_LOGS_FILE%"
	ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
) else (
	:: just opening CMD AS ADMIN
	ECHO Parameters passed are empty ^^^%^^^*: "%*"
	ECHO @echo off ^&^& powershell -noprofile -window Maximized -command "" ^&^& @echo on > "%ADMIN_CMD_FILE%"
	ECHO. >> "%ADMIN_CMD_LOGS_FILE%"
	ECHO [%date% %time%]: @echo off ^&^& powershell -noprofile -window Maximized -command "" ^&^& @echo on >> "%ADMIN_CMD_LOGS_FILE%"
	REM ECHO @echo off ^&^& powershell -noprofile -window Maximized -command "" ^&^& @echo on >> "%ADMIN_CMD_LOGS_FILE%"
)

REM "%~dp0cmdasadmin.lnk" "%*"
REM START "" "%~dp0cmdasadmin.lnk" "%*"
REM PAUSE

:schedule
schtasks /Run /I /TN "cmd-as-admin"

REM type nul > "%ADMIN_CMD_FILE%"
