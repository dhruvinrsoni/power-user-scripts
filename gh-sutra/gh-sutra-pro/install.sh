#!/bin/bash
echo ""
echo "================================"
echo "Installing GH-Sutra..."
echo "================================"
echo ""

echo "[CORE] Applying core aliases..."
gh alias set pr-create "pr create --fill --web"
gh alias set repo-view "repo view --web"
echo "[CORE] Core Sutras applied."
echo ""

echo "[PRO] Applying pro aliases..."
pr_switch_logic=$(cat templates/pr-switch.ghalias)
gh alias set pr-switch "$pr_switch_logic"
echo "[PRO] -> Installed GH alias: pr-switch"


echo ""
echo "========================================="
echo "✅ GH-Sutra Installation Complete."
echo "========================================="
echo ""
