@echo off
title "KillAll"
set syspass=livelong

if [%1]==[] (
	goto AskPass
) else (
	if [%1]==[%syspass%] (
		goto valid
	) else  (
		goto invalid
	)
)

:AskPass
set userpass=""
set /p userpass="Enter the password:-"
if [%userpass%]==[%syspass%] (
	goto valid ) else (
		goto invalid )

:valid
::PAUSE
REM FOR /F "tokens=2" %%# in ('tasklist /v ^| find "Windows Command Processor"') do set PID=%%#
set list=notepad.exe,taskmgr.exe,robo3t.exe,eclipse.exe,javaw.exe,notepad++.exe,CodeMix,scalc.exe,swriter.exe,soffice.bin,chrome.exe,TortoiseProc.exe,lync.exe
for /f "skip=3 tokens=1" %%i in ('TASKLIST /FI "USERNAME eq %userdomain%\%username%" /FI "STATUS eq running"') do (
REM set processname=%%i
rem if %%i==notepad.exe ( echo taskkill /f /im "%%i" )
rem find "%%i" "%SCRIPTS_DRIVE%\%SCRIPTS%\processes_to_kill.txt">nul && echo taskkill /f /im "%%i" 
for %%a in ("%list:,=" "%") do (
   if "%%i"==%%a taskkill /f /im "%%i"
)
)
if [%2]==[] goto invalid 
if %2==0 goto invalid 

:KillCmdConsoles
:: Now to kill all the cmd consoles other than the current one.
for /f %%i in ('powershell -noprofile -c "[Console]::Title.Replace(' - '+[Environment]::CommandLine,'')"') do set oldTitle=%%i
REM title "exclude"
if [%3]==[] ( set saveConsoleTitle=%oldTitle%
) else (
set saveConsoleTitle=%3
)
echo third param is %saveConsoleTitle%
for /f "usebackq  tokens=*" %%a in (`tasklist /NH /v /fo csv /FI "IMAGENAME eq cmd.exe" /FI "STATUS eq running"`) do (
  (
    echo %%a | FIND /I %saveConsoleTitle% 1>NUL
  ) || ( 
    for /f "usebackq tokens=2 delims=," %%i in (`echo %%a`) do (
      echo TASKKILL /PID %%~i /f
	  TASKKILL /PID %%~i /f
    )
  )
)
title ^%oldTitle%

:invalid
REM exit for /f "usebackq  tokens=*" %a in (`tasklist /NH /v /fo csv /FI "IMAGENAME eq cmd.exe" /FI "STATUS eq running" | find /I hi`) do ( for /f "usebackq tokens=2 delims=," %i in (`echo %a`) do ( TASKKILL /PID %~i /f )