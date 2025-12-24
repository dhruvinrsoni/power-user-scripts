#!/bin/bash
echo ""
echo "=========================================="
echo "Applying Git-Sutra Core..."
echo "=========================================="
echo ""

while IFS= read -r line; do
    # Ignore comments and empty lines
    if [[ ! "$line" =~ ^\s*# && -n "$line" ]]; then
        echo "[Applying] $line"
        eval "$line"
    fi
done < core.logic

echo ""
echo "=========================================="
echo "✅ Git-Sutra Core installation complete."
echo "=========================================="
echo ""
