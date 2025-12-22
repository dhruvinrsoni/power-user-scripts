# This script is designed to interleave shell (sh/bash) commands and Windows CMD commands.
# It allows cross-platform execution by mixing code that can run in either environment.
# The script prints environment-specific greetings and handles conditional logic.
# Usage instructions are provided if necessary arguments are missing.
# The script is structured with sections marked by labels to organize execution flow.
# See https://stackoverflow.com/questions/17510688 for more details on hybrid scripts.

:; echo "Hi, I’m ${SHELL}."
:; #exit $?
:<<"::second"
@ECHO OFF
ECHO I'm %COMSPEC%
goto secondcmd

::second
:; true; ret=$?
:; [ ${ret} = 0 ] || { echo "Program failed with code ${ret}." >&2; exit 1; }
:; #exit
:<<"::third"
:secondcmd
ECHO CMD code.
goto thirdcmd

::third
:; echo "I am ${SHELL}"
:<<"::CMDLITERAL"
:thirdcmd
ECHO I am %COMSPEC%
goto fourthcmd
::CMDLITERAL
:; echo "And ${SHELL} is back!"
:<<"::CMDLITERAL2"
:; #exit
:fourthcmd
ECHO And back to %COMSPEC%
goto fifthcmd

:fifthcmd
@ECHO OFF
GOTO CMDSCRIPT
::CMDLITERAL2

echo "I can write free-form ${SHELL} now!"
if :; then
  echo "This makes conditional constructs so much easier because"
  echo "they can now span multiple lines."
fi
:<<"::CMDLITERAL3"
#exit $?

:CMDSCRIPT
ECHO Welcome to %COMSPEC%
goto sixthcmd

::CMDLITERAL3
: # This is a special script which intermixes both sh
: # and cmd code. It is written this way because it is
: # used in system() shell-outs directly in otherwise
: # portable code. See https://stackoverflow.com/questions/17510688
: # for details.
:; echo "This is ${SHELL}"; 
:<<"::CMDLITERAL4"
:sixthcmd
@ECHO OFF
ECHO This is %COMSPEC%
rem goto seventhcmd

::CMDLITERAL4
echo >/dev/null # >nul & GOTO WINDOWS & rem ^
:; if [ -z 0 ]; then
  @echo off
  goto :WINDOWS
fi

if [ -z "$2" ]; then
  echo "usage: $0 <firstArg> <secondArg>"
  exit 1
fi

# bash stuff
exit

:seventhcmd
:WINDOWS
if [%2]==[] (
  SETLOCAL enabledelayedexpansion
  set usage="usage: %0 <firstArg> <secondArg>"
  @echo !usage:"=!
  exit /b 1
)

:: windows stuff