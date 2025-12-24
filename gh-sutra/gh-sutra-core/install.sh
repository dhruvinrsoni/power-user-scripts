#!/bin/bash
echo ""
echo "=========================================="
echo "Applying GH-Sutra Core..."
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
echo "✅ GH-Sutra Core installation complete."
echo "=========================================="
echo ""
