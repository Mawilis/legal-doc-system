#!/bin/bash

echo "========================================="
echo "PRETTIER QUICK VERIFICATION"
echo "========================================="

# Check 1: Configuration exists
[ -f .prettierrc ] && echo "✅ .prettierrc exists" || echo "❌ .prettierrc missing"

# Check 2: Ignore file exists
[ -f .prettierignore ] && echo "✅ .prettierignore exists" || echo "❌ .prettierignore missing"

# Check 3: Prettier installed
npx prettier --version &> /dev/null && echo "✅ Prettier installed" || echo "❌ Prettier not installed"

# Check 4: No formatting errors
ERRORS=$(npx prettier --check "**/*.{js,json,md,yml,yaml,cjs,mjs}" 2>&1 | grep -c "error" || true)
[ "$ERRORS" -eq 0 ] && echo "✅ No formatting errors" || echo "❌ Found $ERRORS formatting errors"

# Check 5: Test file exists
[ -f tests/prettier.test.cjs ] && echo "✅ Test file exists" || echo "❌ Test file missing"

echo "========================================="
