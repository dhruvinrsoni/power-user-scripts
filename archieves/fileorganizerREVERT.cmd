@echo off
title "Organize files REVERT"
set syspass=chaos
goto execute
if [%1]==[] (
	goto AskPass
) else (
	if [%1]==[%syspass%] (
		goto AskPath 
	) else (
		goto invalid 
	)
)

:AskPass
set userpass=""
set /p userpass="Enter the password:-"
if [%userpass%]==[%syspass%] (
	goto AskPath 
) else (
	goto invalid 
)

:AskPath
set rootDir=
set /p rootDir="Enter the path to the folder:- "
goto execute

:execute
if [%rootDir%]==[] ( set rootDir=.)
REM echo rootDir is %rootDir% && pause
rem For each "%rootDir%\.extension"  format folder %%a
for /D %%a in ("%rootDir%\.*") do (
rem go inside each "%%a"  named folder
cd %%a
REM echo Entered the folder %%a
rem For each file %%b in the current folder %%a
for %%b in ("*.*") do (
REM echo File:- %%b
rem move the file to the parent folder
move "%%b" "..\"
echo Moved the file:- "%%a" ======^> "%%b">>"..\movedfiles.txt"
)
rem go to the parent folder
cd ..
rem remove the empty ".extension" named folder
rmdir /s /Q "%%a"
echo ======^> Deleted the folder:- "%%a">>"movedfiles.txt"
REM echo Deleted the folder %%a
REM pause
)
echo. && echo.
type movedfiles.txt
del /Q movedfiles.txt
rem echo =DONE=
PAUSE>nul
goto exit

:invalid
echo Invalid
echo Exiting...
goto exit

:exit
exit /B 0




