@ECHO Off
REM powershell -noprofile -window Maximized -command "" 2>nul
SET COMMAND=%1

IF NOT [%COMMAND%]==[] GOTO select

SET COLUMNS=2
SET CHOICES=
SET DEBUG=0
SET WIDTH=45
FOR /F "tokens=1 delims=: skip=2" %%L IN ('FINDSTR /R "^:[a-zA-Z]" "%~f0"') DO (
    SET CHOICES=!CHOICES! %%L
)
SET "CHOICES=!CHOICES:~1!"
IF !DEBUG! EQU 1 ECHO [DEBUG] Choices: !CHOICES!
SET COUNT=0
FOR %%C IN (!CHOICES!) DO (
    SET /A COUNT+=1
    SET /A MODULO=COUNT %% COLUMNS
    IF !DEBUG! EQU 1 ECHO [DEBUG] count=!COUNT! and modulo=!MODULO! and Choice is %%C
    IF !MODULO! EQU 1 (
        SET LINE=!COUNT! =^> %%C
		IF !DEBUG! EQU 1 ECHO [DEBUG] modulo=!MODULO! and LINE=!LINE!
        CALL :PadLine "!LINE!"
    ) ELSE (
        CALL :PadLine "!LINE!"
		ECHO.
        ECHO !LINE! !COUNT! =^> %%C
		IF !DEBUG! EQU 1 ECHO [DEBUG] modulo=!MODULO! and LINE=!LINE!
    )
)
IF DEFINED LINE (
    CALL :PadLine "!LINE!"
    ECHO.
    ECHO !LINE!
)
ECHO.
SET /P "MYCHOICE=Enter number or directly the command: "
IF !DEBUG! EQU 1 ECHO [DEBUG] User choice: %MYCHOICE%
ECHO %MYCHOICE%|FINDSTR "^[-][1-9][0-9]*$ ^[1-9][0-9]*$ ^0$"
IF NOT ERRORLEVEL 1 (
    SET /A MYCHOICE-=1
    SET /A INDEX=0
    FOR %%C IN (!CHOICES!) DO (
        IF !INDEX! EQU !MYCHOICE! (
            SET "COMMAND=%%C"
        )
        SET /A INDEX+=1
    )
) ELSE (
    SET "COMMAND=%MYCHOICE%"
)


REM SET CHOICES=
REM SET COUNTER=1
REM SET /A COLUMN=2
REM @ECHO OFF
REM FOR /f "usebackq delims=: tokens=1 skip=1" %%f in (`findstr /B ":" "%~dpnx0"`) do ( 
	REM IF "!COLUMN!"=="" (
		REM ECHO !COUNTER! =^> %%f
		REM SET COLUMN=1
	REM ) else (
		REM ECHO.
		REM ECHO|SET /p="!COUNTER! =^> %%f								"
		REM SET COLUMN=)
	REM SET /A COUNTER=COUNTER+1 
	REM SET CHOICES=!CHOICES!%%f,
REM )
REM FOR /f "usebackq tokens=*" %%i in (`findstr /B ":" "%~dpnx0" ^| find /C ":"`) do (SET "COUNT=%%i")
REM SET MYCHOICE=
REM ECHO. && SET /P "MYCHOICE=Enter number or directly the command:- "
REM if NOT "%MYCHOICE%"=="" (
	REM ECHO %MYCHOICE%|findstr "^[-][1-9][0-9]*$ ^[1-9][0-9]*$ ^0$">nul&&( ECHO Selecting command from choice: %MYCHOICE% )||( SET "COMMAND=%MYCHOICE%" && GOTO select )
	REM FOR /f "usebackq tokens=1 skip=%MYCHOICE% delims=:" %%f in (`findstr /B ":" "%~dpnx0"`) do (SET "COMMAND=%%f" && GOTO select)
REM )
REM ECHO. & SET /p COMMAND=Enter command:- 
REM GOTO select


REM SET COUNTER=1
REM SET COLUMNS=2
REM SET CHOICES=
REM FOR /F "tokens=1 delims=:" %%L IN ('FINDSTR /R "^:[a-zA-Z]" "%~f0"') DO (
    REM SET "CHOICES=!CHOICES! %%L"
REM )
REM SET COUNT=0
REM FOR %%C IN (!CHOICES!) DO (
    REM SET /A COUNT+=1
    REM SET /A MODULO=COUNT %% COLUMNS
    REM IF !MODULO! EQU 1 (
        REM SET LINE=%%C
    REM ) ELSE (
        REM CALL :PrintColumns !LINE! %%C
    REM )
REM )
REM IF !MODULO! NEQ 0 (
    REM CALL :PrintColumns !LINE! ""
REM )
REM ECHO.
REM SET /P "MYCHOICE=Enter number or directly the command: "
REM ECHO %MYCHOICE% | FINDSTR "^[0-9]*$" >nul
REM IF NOT ERRORLEVEL 1 (
    REM SET /A MYCHOICE-=1
    REM FOR /F "tokens=%MYCHOICE% delims=," %%C IN ("!CHOICES!") DO (
        REM SET "COMMAND=%%C"
    REM )
REM ) ELSE (
    REM SET "COMMAND=%MYCHOICE%"
REM )

REM :PrintColumns
REM REM Print two columns with aligned FORmatting
REM SET "SPACES=                                "
REM SET "LEFT=%1"
REM SET "RIGHT=%2"
REM SET "LEFT=!LEFT!!SPACES!"
REM CALL ECHO !LEFT:~0,30!  !RIGHT!
REM GOTO :eof


REM SET COLUMNS=2  REM Ensure COLUMNS is initialized to a non-zero value
REM SET CHOICES=
REM SET DEBUG=0
REM FOR /F "tokens=1 delims=:" %%L IN ('FINDSTR /R "^:[a-zA-Z]" "%~f0"') DO (
    REM SET CHOICES=!CHOICES! %%L
REM )
REM SET "CHOICES=!CHOICES:~1!"
REM IF !DEBUG! EQU 1 ECHO [DEBUG] Choices: !CHOICES!
REM SET COUNT=0
REM SET LINE=
REM FOR %%C IN (!CHOICES!) DO (
    REM SET /A COUNT+=1
	REM SET /A MODULO=COUNT %% COLUMNS
	REM IF !DEBUG! EQU 1 ECHO [DEBUG] count=!count! and modulo=!MODULO! and Choice is %%C
    REM IF !MODULO! EQU 1 (
        REM SET LINE=!COUNT! =^> %%C
    REM ) ELSE (
        REM ECHO !LINE!				!COUNT! =^> %%C
        REM SET LINE=
    REM )
REM )
REM IF DEFINED LINE (
    REM ECHO !LINE!
REM )
REM ECHO.
REM SET /P "MYCHOICE=Enter number or directly the command: "
REM IF !DEBUG! EQU 1 ECHO [DEBUG] User choice: %MYCHOICE%
REM ECHO %MYCHOICE% | FINDSTR "^[0-9]*$" >nul
REM IF NOT ERRORLEVEL 1 (
    REM SET /A MYCHOICE-=1
    REM SET /A INDEX=0
    REM FOR %%C IN (!CHOICES!) DO (
        REM IF !INDEX! EQU !MYCHOICE! (
            REM SET "COMMAND=%%C"
        REM )
        REM SET /A INDEX+=1
    REM )
REM ) ELSE (
    REM SET "COMMAND=%MYCHOICE%"
REM )



:select
SET ARGS=%*
IF NOT "%2"=="" (
	IF !DEBUG! EQU 1 ECHO [DEBUG] ECHO COMMAND='!COMMAND!' AND ARGS='!ARGS!' IN IF NOT ^%^2==""
    SET "ARGS=!ARGS:%COMMAND% =!"
) ELSE (
	IF !DEBUG! EQU 1 ECHO [DEBUG] ECHO COMMAND='!COMMAND!' AND ARGS='!ARGS!' IN ELSE OF IF NOT ^%^2==""
    FOR /F "tokens=1,* delims= " %%A IN ("%COMMAND%") DO (
        SET "COMMAND=%%A"
        SET "ARGS=%%B"
    )
)
IF !DEBUG! EQU 1 ECHO [DEBUG] ECHO COMMAND='!COMMAND!' AND ARGS='!ARGS!'
GOTO %COMMAND% !ARGS! && ECHO %COMMAND% !ARGS! || (
    msg %USERNAME% /TIME:3 "Invalid: COMMAND ARGS=%COMMAND% !ARGS!"
    IF !DEBUG! EQU 1 ECHO [DEBUG] Invalid command or arguments.
)
GOTO exit0

:PadLine
SET "LINE=%~1"
SET "SPACES=                               "
SET "PADDED_LINE=!LINE!!SPACES!"
SET "LINE=!PADDED_LINE:~0,%WIDTH%!"
GOTO :EOF

:apps
start shell:AppsFolder
goto exit0

:blankscr
START %SystemRoot%\system32\scrnsave.scr /s
GOTO exit0

:hibernate
TIMEOUT /t 6
rundll32.exe powrprof.dll,SetSuspendState 0,1,0
GOTO exit0

:hosts
START notepad "%SYSTEMROOT%\System32\drivers\etc\hosts"
ECHO "%SYSTEMROOT%\System32\drivers\etc\hosts"|clip
GOTO exit0

:lock
%SystemRoot%\System32\rundll32.exe user32.dll,LockWorkStation
GOTO exit0

:max
powershell -noprofile -window Maximized -command "" 2>nul
GOTO exit0

:message
ECHO !ARGS!
REM ECHO START "message" /max cmd /c "msg %USERNAME% /TIME:15 !ARGS!" && pause
IF "!ARGS!"=="" ( START "message" /max cmd /c "msg %USERNAME% /TIME:15 !ARGS!" ) else ( START "message" /min cmd /c "msg %USERNAME% /TIME:15 !ARGS!" )
GOTO exit0

:min
powershell -noprofile -window Minimized -command "" 2>nul
GOTO exit0

:outlooktemplate
START explorer "%USERPROFILE%\AppData\Roaming\Microsoft\Templates"
GOTO exit0

:perfdevedge
START "" "msedge.exe" !ARGS! --profile-directory="Profile 2"
GOTO exit0

:powertoy
"%USERPROFILE%\AppData\Local\PowerToys\WinUI3Apps\PowerToys.Settings.exe" \\.\pipe\powertoys_runner_7f48655b-7f7d-4814-a208-e4c2cb8955db \\.\pipe\powertoys_SETtings_7f48655b-7f7d-4814-a208-e4c2cb8955db 26384 system false true false true false false false
GOTO exit0

:signature
explorer "%USERPROFILE%\AppData\Roaming\Microsoft\Signatures"
GOTO exit0

:sleep
START "message" /min cmd /c "msg %USERNAME% /TIME:1 Disconnected the VPN"
REM %SYSTEMROOT%\System32\rundll32.exe powrprof.dll,SetSuspendState 0,1,0
rundll32.exe powrprof.dll,SetSuspendState Sleep
REM powershell -noprofile START-process cmd.exe -Args '/c', 'psshutdown -d -t 1'" -verb runas
REM call admincmd EXIT psshutdown -d -t 1
GOTO exit0

:startmenu
START explorer %USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs

:startup
START explorer %USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
START explorer %USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Shell Folders
START explorer %PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup
START explorer %SystemRoot%\System32\Startup
GOTO exit0

:taskbar
explorer "%APPDATA%\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
GOTO exit0

:temp
ECHO %temp%|CLIP.exe
explorer %TEMP%
GOTO exit0

:tempscr
SET "TEMP_SCRIPT=%TEMP%\tempscript_%RANDOM%.cmd"
ECHO Creating script: %TEMP_SCRIPT%
SET "ARGS=%*"
SET "ARGS=%ARGS:tempscr=%"
if "!ARGS!"=="" (
    ECHO Type your script below. Press Ctrl+Z then Enter to save and run it.
    COPY CON "%TEMP_SCRIPT%"
) else (
	ECHO Directly SETting the script with the commands: !ARGS!
    ECHO !ARGS! > "%TEMP_SCRIPT%"
)
ECHO Executing script: %TEMP_SCRIPT% as below
type "%TEMP_SCRIPT%"
call "%TEMP_SCRIPT%"
GOTO exit0

:vars
FOR /f "usebackq tokens=* delims==" %%i in (`findstr /B /I "SET" "%DOSFILE%\..\doskeys.cmd"`) do (ECHO %%i)
timeout /t -1 /nobreak
GOTO exit0

:exit0
REM ECHO %CMDCMDLINE%|find "%~f0">nul && EXIT 0 || EXIT /B 0
EXIT /B 0