#!/bin/bash

echo "🔍 Scanning for common syntax errors in test files..."
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Check for unterminated import statements
echo "Checking for imports without closing quotes:"
find tests -name "*.test.js" -type f -exec grep -l "from.*TenantConfig;" {} \; || echo "  ✅ None found"

# Check for missing .js extensions in imports
echo -e "\nChecking for imports without .js extensions:"
find tests -name "*.test.js" -type f -exec grep -Hn "from.*['\"][^'\"]*[^\.js]['\"];" {} \; | grep -v "node_modules" || echo "  ✅ All imports have .js extensions"

# Check for common syntax errors
echo -e "\nChecking for common syntax errors:"
find tests -name "*.test.js" -type f -exec node --check {} \; 2>&1 | head -20

echo -e "\n✅ Scan complete"
