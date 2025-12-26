@rem = '--'; @echo off
@rem = ';'; /*
:<<"::CMDSKIP"
@echo off
goto :WINDOWS
::CMDSKIP
*/

# =============================================================================
# BASH / SH SECTION
# =============================================================================

# Argument Check
if [ -z "$1" ]; then
  echo "Usage: $0 <argument1> [argument2...]"
  echo "This is the help message for the BASH/SH environment."
  exit 1
fi

# --- ADD YOUR BASH/SHELL LOGIC HERE ---

echo "Executing in BASH/SHELL environment..."
echo "First argument was: $1"

# Your script logic goes here. For example:
# find . -name "$1" -print


# --- END OF BASH/SHELL LOGIC ---

exit 0

# =============================================================================
# WINDOWS CMD SECTION
# =============================================================================
:WINDOWS
SETLOCAL enabledelayedexpansion

# Argument Check
if [%1]==[] (
  echo Usage: %0 ^<argument1^> [argument2...]
  echo This is the help message for the WINDOWS CMD environment.
  exit /b 1
)

:: --- ADD YOUR WINDOWS CMD LOGIC HERE ---

ECHO Executing in WINDOWS CMD environment...
ECHO First argument was: %1

:: Your script logic goes here. For example:
:: DIR /s /b "%1"


:: --- END OF WINDOWS CMD LOGIC ---

ENDLOCAL
exit /b 0
