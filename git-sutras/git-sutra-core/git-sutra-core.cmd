@echo off
echo.
echo ===========================================
echo Applying Git-Sutra Core...
echo (The Universal Foundation for Sane Defaults)
echo ===========================================
echo.

:: -- Prune on fetch: Automatically remove local tracking branches 
:: -- for remote branches that have been deleted.
:: -- Sutra: "Do not carry ghosts of the past."
echo [Applying] fetch.prune = true
git config --global fetch.prune true

:: -- Rebase on pull: Avoids creating useless "merge bubbles" when you
:: -- pull changes. Keeps history linear and clean.
:: -- Sutra: "Maintain a single, clear stream of thought."
echo [Applying] pull.rebase = true
git config --global pull.rebase true

:: -- Default Branch Name: Set the standard to 'main' for all new
:: -- repositories, moving away from the outdated 'master'.
:: -- Sutra: "Begin all journeys on the main path."
echo [Applying] init.defaultBranch = main
git config --global init.defaultBranch main

:: -- Autocorrect: If you type 'git staus', Git will wait 1 second
:: -- and then automatically run 'git status' instead of erroring out.
:: -- Sutra: "Understand the intent, not just the word."
echo [Applying] help.autocorrect = 1
git config --global help.autocorrect 1

echo.
echo [ALIASES] Applying core shorthand...
git config --global alias.s "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.c "commit"
echo.

echo ==========================================
echo ✅ Git-Sutra Core installation complete.
echo ==========================================
echo.
