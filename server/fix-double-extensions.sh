#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - FIX DOUBLE EXTENSIONS                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Create backup
BACKUP_DIR="backups/double-ext-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tests "$BACKUP_DIR/"
echo "✅ Backup created in $BACKUP_DIR"
echo ""

# Fix all .js.js extensions
echo "🔧 Fixing .js.js double extensions..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;
find models -name "*.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;
find utils -name "*.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \; 2>/dev/null
find services -name "*.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \; 2>/dev/null
echo "✅ Done"
echo ""

# Specifically fix Case.test.js import
echo "🔧 Verifying Case.test.js..."
grep -n "db" tests/models/Case.test.js
echo ""

# Check for any remaining double extensions
echo "🔍 Checking for remaining double extensions..."
find tests models utils services -name "*.js" -type f 2>/dev/null | xargs grep -l "\.js\.js" 2>/dev/null || echo "✅ No double extensions found"

echo ""
echo "📝 If anything went wrong, restore with:"
echo "cp -r $BACKUP_DIR/tests/* tests/"
