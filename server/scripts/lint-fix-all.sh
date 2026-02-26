#!/bin/bash

echo "🔧 WILSY OS - FIXING ALL LINTING ISSUES"
echo "========================================"

# Fix ESLint configuration issues
npx eslint . --ext .js --fix --quiet

# Fix comma-dangle issues specifically
npx eslint . --ext .js --rule 'comma-dangle: ["error", "always-multiline"]' --fix

# Fix import/order issues
npx eslint . --ext .js --rule 'import/order: ["error", { "alphabetize": { "order": "asc" } }]' --fix

# Fix no-unused-vars
npx eslint . --ext .js --rule 'no-unused-vars: ["error", { "argsIgnorePattern": "^_" }]' --fix

echo "========================================"
echo "✅ All linting issues fixed"
echo "========================================"
