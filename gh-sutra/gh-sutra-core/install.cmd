@echo off
echo.
echo ===========================================
echo Applying GH-Sutra Core...
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
echo ✅ GH-Sutra Core installation complete.
echo ==========================================
echo.
