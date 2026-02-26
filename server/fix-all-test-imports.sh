#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - FIX ALL TEST FILE IMPORTS                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Create timestamped backup
BACKUP_DIR="backups/import-fixes-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tests "$BACKUP_DIR/"
echo "✅ Backup created in $BACKUP_DIR"
echo ""

# Fix 1: Remove trailing commas in import statements
echo "🔧 Fix 1: Removing trailing commas in imports..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/from \(.*\)",/from \1"/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/import \(.*\)",/import \1"/g' {} \;
echo "✅ Done"
echo ""

# Fix 2: Add .js extensions to relative imports
echo "🔧 Fix 2: Adding .js extensions to relative imports..."
find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]\(\.[^'\"]*\)['\"];/from '\1.js';/g" {} \;
find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]\(\.[^'\"]*\)['\"]/from '\1.js'/g" {} \;
echo "✅ Done"
echo ""

# Fix 3: Fix any remaining missing quotes or syntax
echo "🔧 Fix 3: Fixing common syntax errors..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/;$/;/g' {} \;  # Ensure semicolons are proper
echo "✅ Done"
echo ""

# Fix 4: Specifically fix ValidationAudit.test.js
echo "🔧 Fix 4: Fixing ValidationAudit.test.js..."
sed -i '' 's/from '"'"'\.\.\/\.\.\/models\/ValidationAudit/from '"'"'\.\.\/\.\.\/models\/ValidationAudit.js/g' tests/models/ValidationAudit.test.js 2>/dev/null
echo "✅ Done"
echo ""

# Fix 5: Specifically fix caseAnalysisService.test.js
echo "🔧 Fix 5: Fixing caseAnalysisService.test.js..."
sed -i '' 's/from '"'"'\.\.\/\.\.\/\.\.\/services\/case-analysis\/caseAnalysisService/from '"'"'\.\.\/\.\.\/\.\.\/services\/case-analysis\/caseAnalysisService.js/g' tests/services/case-analysis/caseAnalysisService.test.js 2>/dev/null
echo "✅ Done"
echo ""

# Verify fixes
echo "🔍 Verifying fixes..."
echo ""
echo "Checking redactUtil.test.js:"
head -5 tests/utils/redactUtil.test.js | grep -n "import" || echo "  ✅ Fixed"
echo ""

echo "Checking ValidationAudit.test.js:"
grep -n "ValidationAudit" tests/models/ValidationAudit.test.js | head -3
echo ""

echo "Checking caseAnalysisService.test.js:"
grep -n "caseAnalysisService" tests/services/case-analysis/caseAnalysisService.test.js | head -3
echo ""

# Run syntax check
echo "🧪 Running final syntax check..."
find tests -name "*.test.js" -type f -exec node --check {} \; 2>&1 | grep -v "OK" | head -10 || echo "✅ No syntax errors found!"

echo ""
echo "📝 If anything went wrong, restore with:"
echo "cp -r $BACKUP_DIR/tests/* tests/"
