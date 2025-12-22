@echo off
title "Organize files"
set syspass=cosmos
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
rem For each "%%a" file in your "%rootDir%" folder
for %%a in ("%rootDir%\*") do (
rem check if the file has an extension "%%~xa" and if it "%%~dpxa" is not our script "%~dpx0"
REM echo file:- %%a || extension:- %%~xa || "~dpxa":- %%~dpxa || "~dpx0":- %%~dpx0
if "%%~xa" NEQ "" if "%%~dpxa" NEQ "%~dpx0" (
rem check if extension folder "%%~xa" exists, if not it is created mkdir "%%~xa"
if not exist "%%~xa" mkdir "%%~xa"
echo Moved the file:- "%%a" ======^> "%%~dpa%%~xa\">>movedfiles.txt
move "%%a" "%%~dpa%%~xa\"
)
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