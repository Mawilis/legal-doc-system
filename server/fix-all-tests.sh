#!/bin/bash

echo "🔧 WILSY OS - BATCH TEST FILE FIXER"
echo "====================================="
echo "Fixing all 2000+ test files automatically..."
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# 1. Fix imports (remove .js extensions)
echo "📝 Fixing import statements..."
find tests -name "*.test.js" -type f -exec sed -i '' 's/from \(.*\)\.js\(.*\);/from \1\2;/g' {} \;

# 2. Fix chai imports specifically
find tests -name "*.test.js" -type f -exec sed -i '' 's/from ["'\'']chai\.js["'\'']/from "chai"/g' {} \;

# 3. Fix mongoose imports specifically
find tests -name "*.test.js" -type f -exec sed -i '' 's/from ["'\'']mongoose\.js["'\'']/from "mongoose"/g' {} \;

# 4. Fix double .js.js extensions
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \;

# 5. Add mocha env if missing
find tests -name "*.test.js" -type f -exec grep -L "eslint-env mocha" {} \; | while read file; do
    sed -i '' '1i\
/* eslint-env mocha */\
' "$file"
done

# 6. Convert describe/it to function form (for this.timeout to work)
find tests -name "*.test.js" -type f -exec sed -i '' 's/describe(\(.*\), () => {/describe(\1, function() {/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/it(\(.*\), () => {/it(\1, function() {/g' {} \;
find tests -name "*.test.js" -type f -exec sed -i '' 's/it(\(.*\), async () => {/it(\1, async function() {/g' {} \;

echo -e "\n✅ All test files fixed!"
echo "Run ./run-tests.sh to verify"
