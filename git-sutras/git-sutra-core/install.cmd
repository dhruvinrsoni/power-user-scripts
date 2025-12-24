@echo off
echo.
echo ===========================================
echo Applying Git-Sutra Core...
echo ===========================================
echo.

for /f "usebackq tokens=*" %%a in ("core.logic") do (
    rem Ignore comments and empty lines
    echo %%a | findstr /b /c:"#" >nul || (
        if not "%%a"=="" (
            echo [Applying] %%a
            %%a
        )
    )
)

echo.
echo ==========================================
echo ✅ Git-Sutra Core installation complete.
echo ==========================================
echo.
