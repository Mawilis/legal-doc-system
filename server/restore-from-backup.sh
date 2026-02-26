#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - RESTORE FROM BACKUP                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# List available backups
echo "Available backups:"
ls -la backups/ 2>/dev/null || echo "No backups found"

if [ -d "backups" ]; then
    LATEST=$(ls -t backups/ | head -1)
    echo -e "\nLatest backup: $LATEST"
    
    read -p "Restore from this backup? (y/n): " answer
    if [ "$answer" = "y" ]; then
        cp -r "backups/$LATEST/models/"* models/
        cp -r "backups/$LATEST/tests/"* tests/
        echo "✅ Restored from $LATEST"
    fi
fi
