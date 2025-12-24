#!/bin/bash
echo ""
echo "================================="
echo "Installing Git-Sutra..."
echo "================================="
echo ""

echo "[CORE] Applying core configuration..."
git config --global fetch.prune true
git config --global pull.rebase true
git config --global init.defaultBranch main
git config --global help.autocorrect 1
git config --global alias.s "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
echo "[CORE] Core Sutras applied."
echo ""

echo "[PRO] Applying pro aliases from templates..."

for file in templates/*.gitalias; do
    if [ -f "$file" ]; then
        alias_name=$(basename "$file" .gitalias)
        alias_logic=$(cat "$file")
        git config --global "alias.$alias_name" "$alias_logic"
        echo "[PRO] -> Installed Git alias: $alias_name"
    fi
done

echo ""
echo "=========================================="
echo "✅ Git-Sutra Installation Complete."
echo "Restart your terminal to use the new aliases."
echo "=========================================="
echo ""
