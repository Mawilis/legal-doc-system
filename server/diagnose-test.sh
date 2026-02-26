#!/bin/bash

echo "🔍 WILSY OS - TEST DIAGNOSTIC TOOL"
echo "==================================="
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Check Node version
echo "📦 Node version: $(node --version)"
echo ""

# Check if files exist
echo "📄 Checking test files:"
if [ -f "tests/models/Case.test.js" ]; then
    echo "  ✅ Case.test.js exists"
    echo "  Lines: $(wc -l < tests/models/Case.test.js)"
else
    echo "  ❌ Case.test.js MISSING"
fi

if [ -f "models/Case.js" ]; then
    echo "  ✅ Case.js exists"
else
    echo "  ❌ Case.js MISSING"
fi
echo ""

# Check Babel config
echo "⚙️ Checking Babel config:"
if [ -f "babel.config.cjs" ]; then
    echo "  ✅ babel.config.cjs exists"
    echo "  Content:"
    cat babel.config.cjs
else
    echo "  ❌ babel.config.cjs MISSING"
fi
echo ""

# Check Mocha config
echo "⚙️ Checking Mocha config:"
if [ -f ".mocharc.cjs" ]; then
    echo "  ✅ .mocharc.cjs exists"
    echo "  Content:"
    cat .mocharc.cjs
else
    echo "  ❌ .mocharc.cjs MISSING"
fi
echo ""

# Check for multiple Babel configs
echo "🔍 Checking for conflicting configs:"
CONFLICTS=$(find . -maxdepth 1 -name "babel.config.*" -o -name ".babelrc*" | wc -l)
if [ $CONFLICTS -gt 1 ]; then
    echo "  ⚠️ Found $CONFLICTS Babel config files - THIS IS THE ISSUE"
    find . -maxdepth 1 -name "babel.config.*" -o -name ".babelrc*"
    echo ""
    echo "Run: rm -f babel.config.js .babelrc .babelrc.json"
else
    echo "  ✅ No config conflicts"
fi
echo ""

# Test with node directly
echo "🧪 Testing direct node import:"
echo "console.log('Testing import...');" > test-import.js
echo "import { expect } from 'chai'; console.log('✅ Chai imported');" >> test-import.js
node --input-type=module test-import.js 2>&1 || echo "❌ Import failed"
rm test-import.js

echo ""
echo "Run ./reset-and-run-tests.sh to fix"
