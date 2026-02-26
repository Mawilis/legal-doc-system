#!/bin/bash

echo "🔧 Fixing missing .js extensions..."

find . -type f -name "*.js" -not -path "*/node_modules/*" -exec sed -i '' "s/from '\([^']*\)';/from '\1.js';/g" {} \;
find . -type f -name "*.js" -not -path "*/node_modules/*" -exec sed -i '' 's/from "\([^"]*\)";/from "\1.js";/g' {} \;

echo "✅ Extensions fixed"
