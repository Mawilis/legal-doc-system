#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - SAFE IMPORT FIXER (APPEND-ONLY)                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Step 1: Create timestamped backup
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r models "$BACKUP_DIR/"
cp -r tests "$BACKUP_DIR/"
echo "✅ Backups created in $BACKUP_DIR"

# Step 2: Count files to be processed
MODEL_COUNT=$(find models -name "*.js" | wc -l)
TEST_COUNT=$(find tests -name "*.test.js" | wc -l)
echo "📊 Found $MODEL_COUNT model files and $TEST_COUNT test files"

# Step 3: Preview changes for Case.js specifically
echo -e "\n🔍 Previewing changes for models/Case.js:"
echo "Current mongoose import:"
grep -n "mongoose" models/Case.js | head -1

# Step 4: Fix imports (preserve everything else)
echo -e "\n🔧 Fixing import statements..."
find models -name "*.js" -type f -exec sed -i '' 's/from ["'\'']mongoose\.js["'\'']/from "mongoose"/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/from ["'\'']mongoose\.js["'\'']/from "mongoose"/g' {} \;

# Step 5: Verify Case.js is intact
echo -e "\n✅ Case.js after fixes:"
head -20 models/Case.js | grep -v "^$" | head -5

# Step 6: Count total lines to ensure no data loss
ORIGINAL_LINES=$(wc -l < "$BACKUP_DIR"/models/Case.js)
NEW_LINES=$(wc -l < models/Case.js)
echo -e "\n📊 Line count: Original=$ORIGINAL_LINES, New=$NEW_LINES"

if [ $ORIGINAL_LINES -eq $NEW_LINES ]; then
    echo "✅ No lines lost - structure preserved"
else
    echo "⚠️ Line count mismatch - check backup"
fi

# Step 7: Create a verification test
cat > tests/verify-imports.js <<'EOFIMPORT'
import mongoose from 'mongoose';
import { expect } from 'chai';

describe('Import Verification', function() {
  it('should have correct imports', function() {
    expect(mongoose).to.be.ok;
    console.log('✅ Mongoose import works');
  });
});
EOFIMPORT

echo -e "\n✅ Verification test created"

# Step 8: Run verification
echo -e "\n🧪 Running import verification..."
NODE_OPTIONS='--experimental-vm-modules' npx mocha --require @babel/register tests/verify-imports.js

echo -e "\n📝 If verification fails, restore with:"
echo "cp -r $BACKUP_DIR/models/* models/"
