#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - FINAL TEST CLEANUP                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Create final backup
BACKUP_DIR="backups/final-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tests "$BACKUP_DIR/"
echo "✅ Final backup created in $BACKUP_DIR"
echo ""

# Fix 1: TenantConfig.test.js double extension
echo "🔧 Fix 1: Fixing TenantConfig.test.js..."
sed -i '' 's/TenantConfig\.js\.js/TenantConfig\.js/g' tests/models/TenantConfig.test.js
grep -n "TenantConfig" tests/models/TenantConfig.test.js | head -3
echo "✅ Done"
echo ""

# Fix 2: Run a quick scan for any remaining issues
echo "🔍 Scanning for remaining issues..."

# Check for any remaining .js.js
REMAINING=$(find tests -name "*.test.js" -type f -exec grep -l "\.js\.js" {} \;)
if [ -n "$REMAINING" ]; then
    echo "⚠️ Found remaining double extensions in:"
    echo "$REMAINING"
    
    # Fix them automatically
    find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;
    echo "✅ Fixed automatically"
else
    echo "✅ No double extensions found"
fi
echo ""

# Fix 3: Check for imports without .js
echo "🔧 Fix 3: Adding missing .js extensions..."
find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]\(\.[^'\"]*\)['\"];/from '\1.js';/g" {} \;
find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]\(\.[^'\"]*\)['\"]/from '\1.js'/g" {} \;
echo "✅ Done"
echo ""

# Fix 4: Remove trailing commas in imports
echo "🔧 Fix 4: Removing trailing commas..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/from \(.*\)",/from \1"/g' {} \;
echo "✅ Done"
echo ""

# Run verification test
echo "🧪 Running verification test..."
NODE_OPTIONS='--experimental-vm-modules' npx mocha --require @babel/register tests/verify-imports.js

if [ $? -eq 0 ]; then
    echo -e "\n✅ VERIFICATION PASSED!"
    
    # Run Case test
    echo -e "\n🧪 Running Case.test.js..."
    NODE_OPTIONS='--experimental-vm-modules' npx mocha --require @babel/register tests/models/Case.test.js
else
    echo -e "\n❌ VERIFICATION FAILED"
    echo "Restoring from backup..."
    cp -r "$BACKUP_DIR/tests/"* tests/
    exit 1
fi

echo ""
echo "📝 If you need to restore from backup:"
echo "cp -r $BACKUP_DIR/tests/* tests/"
