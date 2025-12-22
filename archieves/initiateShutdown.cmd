@echo off
set syspass=tathastu
set cmdTitle="Shutdown"
echo ^> [%time%]:
echo You are about to Initiate Shutdown. 

if [%2]==[] (
	goto AskPass
) else (
	if [%2]==[%syspass%] (
		goto initiateShutdown
	) else  (
		goto AskPass
	)
)

:AskPass
set userpass=""
set /p userpass="Enter the password:-"
if [%userpass%]==[%syspass%] (
	goto initiateShutdown ) else (
		echo.Wrong Password!... Try Again.
		echo.
		goto exit )

:initiateShutdown
if [%1]==[] (
		set ENABLE_SCRIPT=0
	) else  (
		set ENABLE_SCRIPT=%1
	)
set SHUTDOWN_ENABLED=%ENABLE_SCRIPT%
set EXIT_ON_SCRIPT_END=%ENABLE_SCRIPT%

if [%ENABLE_SCRIPT%]==[1] ( cls )
title ^%cmdTitle%
call :LoadCmdLineSeq
call :InitializingCmdLineSeq
goto Shutdown

:LoadCmdLineSeq
SETLOCAL
echo | set /p= "> Loading Command Sequence"
call :GetRandom RANDOM_NUMBER 12 24
call :PrintFastDots %RANDOM_NUMBER%
echo 100%%
echo.
echo ^> Command Line Loaded ! :)
ping 127.0.0.1 -n 2 -w 6 > nul
ENDLOCAL
exit /B 0

:InitializingCmdLineSeq
SETLOCAL 
echo.
echo | set /p= "> Initializing Command Sequence"
call :GetRandom RANDOM_NUMBER 3 6
call :PrintSlowDots %RANDOM_NUMBER%
ENDLOCAL
exit /B 0

:Shutdown
echo.
echo.
timeout /t 01 > nul
if [%SHUTDOWN_ENABLED%]==[1] ( shutdown /s /f /t 006 && taskkill /f /im explorer.exe && echo. ) else ( start /min cmd /c "msg "%username%" /TIME:003 /V /W Shutdown Command executed successfully. T-06 seconds } : ^)" )
echo |set /p= "> Shutting Down"
call :PrintSlowDots 3
echo.
start "Message" /min cmd /c "msg "%USERNAME%" /TIME:006 /V /W Good bye! Have a nice day ahead... && timeout /t 06 && powershell (Add-Type '[DllImport(\"user32.dll\")]^public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas)::SendMessage(-1,0x0112,0xF170,2)"
goto exit

:GetRandom
set /a number= ( (%random%*(%3 - %2)/32768) ) + (%2)  
REM 0 to 1 => 0 to (%3-%2) => %2 to (%3)  
set %~1=%number% 
exit /B 0

:PrintSlowDots
SETLOCAL
FOR /L %%A IN ( 1,1,%~1 ) DO (
  ECHO | set /p=.
	REM timeout /t 00 > nul
	ping 127.0.0.1 -n 2 -w 6 > nul
) 
ENDLOCAL
exit /B 0

:PrintFastDots
SETLOCAL
FOR /L %%A IN ( 1,1,%~1 ) DO (
  ECHO | set /p=.
	timeout /t 00 > nul
	ping 127.0.0.1 -n 1 -w 6 > nul
) 
ENDLOCAL
exit /B 0

:exit
if [%EXIT_ON_SCRIPT_END%]==[1] ( exit ) else (  echo. && echo ^<^<^<^<^<^<^============ Shut Down :^) ============^>^>^>^>^>^> && timeout /t -1 /nobreak )
