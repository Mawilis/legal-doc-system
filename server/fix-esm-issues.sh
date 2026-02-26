#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - ESM/CJS COMPATIBILITY FIXER                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Step 1: Downgrade Chai to version 4
echo "📦 Downgrading Chai to v4 (CommonJS compatible)..."
npm uninstall chai
npm install --save-dev chai@4.3.10

# Step 2: Update test files to use proper syntax
echo "📝 Updating test file syntax..."

# Replace expect.fail with assert.fail
find tests -name "*.test.js" -type f -exec sed -i '' 's/expect\.fail/assert.fail/g' {} \;

# Add assert import where missing
find tests -name "*.test.js" -type f | while read file; do
    if ! grep -q "import.*assert" "$file"; then
        sed -i '' '/import { expect/ s/}/, assert }/' "$file"
    fi
done

# Step 3: Create a simple test to verify
echo "🧪 Creating verification test..."
cat > tests/verify-setup.js <<'EOF'
import { expect, assert } from 'chai';

describe('Setup Verification', function() {
  it('should have chai 4.x working', function() {
    expect(true).to.be.true;
    assert.isTrue(true);
    console.log('✅ Chai version:', typeof expect);
  });
});
