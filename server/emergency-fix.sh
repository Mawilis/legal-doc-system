#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - EMERGENCY TEST FIX                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Create emergency backup
BACKUP_DIR="backups/emergency-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tests "$BACKUP_DIR/"
echo "✅ Emergency backup created in $BACKUP_DIR"
echo ""

# Fix 1: Fix Case.test.js db import (reduce multiple .js to single)
echo "🔧 Fixing Case.test.js db import..."
sed -i '' 's/\.js\.js\.js/\.js/g' tests/models/Case.test.js
sed -i '' 's/\.js\.js/\.js/g' tests/models/Case.test.js
grep -n "db" tests/models/Case.test.js
echo "✅ Done"
echo ""

# Fix 2: Fix any other multi-js extensions
echo "🔧 Fixing all multi-js extensions..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js\.js/\.js/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;
echo "✅ Done"
echo ""

# Fix 3: Specifically check TenantConfig
echo "🔧 Verifying TenantConfig.test.js..."
grep -n "TenantConfig" tests/models/TenantConfig.test.js | head -3
echo "✅ Done"
echo ""

# Fix 4: Run verification
echo "🧪 Running verification test..."
NODE_OPTIONS='--experimental-vm-modules' npx mocha --require @babel/register tests/verify-imports.js

if [ $? -eq 0 ]; then
    echo -e "\n✅ VERIFICATION PASSED!"
    
    # Run Case test
    echo -e "\n🧪 Running Case.test.js..."
    NODE_OPTIONS='--experimental-vm-modules' npx mocha --require @babel/register tests/models/Case.test.js
else
    echo -e "\n❌ VERIFICATION FAILED"
    echo "Manual intervention required."
    echo "Check tests/models/Case.test.js line 12"
    exit 1
fi
