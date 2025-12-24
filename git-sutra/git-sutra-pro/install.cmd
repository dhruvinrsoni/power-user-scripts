@echo off
echo.
echo =================================
echo Installing Git-Sutra...
echo =================================
echo.

echo [CORE] Applying core configuration...
git config --global fetch.prune true
git config --global pull.rebase true
git config --global init.defaultBranch main
git config --global help.autocorrect 1
git config --global alias.s "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
echo [CORE] Core Sutras applied.
echo.

echo [PRO] Applying pro aliases from templates...
echo [PRO] This requires a shell environment like Git Bash to run.
echo.

rem Read and set amend-to alias
set /p amend_to_alias=<templates\amend-to.gitalias
git config --global alias.amend-to "^!%amend_to_alias:~1%"

rem Read and set lg alias
set /p lg_alias=<templates\lg.gitalias
git config --global alias.lg "^!%lg_alias:~1%"

echo.
echo ==========================================
echo ✅ Git-Sutra Installation Complete.
echo Restart your terminal to use the new aliases.
echo ==========================================
echo.
