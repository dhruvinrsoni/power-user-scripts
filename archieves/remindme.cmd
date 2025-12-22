:: Name:         remindme.cmd
:: Description:  This is a console application which remind the user on time interval of countdowntime with the remindermessage
:: Purpose:      User can run this console application to focus on working and get reminder on every interval
:: Author:       mailto:dhruvinrsoni
:: Revision:[0.1.0]   25 November 2019 - initial version 
::  		[0.2.0]   13 January 2020 - Relaunched it with same code. Added Timestamps. 
::               
:: Copyright (C) 2019 Dhruvin Soni. All rights reserved.

title "Remind Me"
@echo off
cls
echo Reminder [Version 0.2.0]
echo Copyright (C) 2019 Dhruvin Soni. All rights reserved. :)

:start
echo.
echo.Start with a New Reminder
goto clearAll

:clearAll
set countdowntime=
set remindermessage=
goto setValues

:setValues
if [%1]==[] (
	set /p countdowntime="Enter the countdown time(in seconds):"
) else (
	set countdowntime=%1 
)
if "%countdowntime%"=="" goto exit
if [%2]==[] (
	set /p remindermessage="Enter Your message:"
) else (
	set remindermessage=%*
)
if "%remindermessage%"=="" goto exit
goto startReminder

:startReminder
echo| set /p="> [%time%] Reminder Started..."
timeout /t 01>nul
call minimizeme
timeout /t %countdowntime% 
echo ^> [%time%] timeout!...
msg %username% /TIME:300 "%remindermessage%" 
echo.
rem goto startReminder
powershell -window maximized -command "exit"
set quitornor=
set /p quitornor="Press 'q' to quit this application and 'Enter" to restart the timer: "
if "%quitornor%"=="q" ( goto exit 
) else ( goto startReminder )

:exit
title C:\Windows\System32\cmd.exe
echo.
echo.^> Thank You for Using remindme.bat. Exiting... Bye :)
timeout /t 03>nul
exit /B 0