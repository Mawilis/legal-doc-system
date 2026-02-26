#!/bin/bash

echo "🔧 Running ESLint auto-fix on all files..."

# Fix all auto-fixable issues
npx eslint . --ext .js --fix --quiet

# Fix comma-dangle specifically
npx eslint . --ext .js --rule 'comma-dangle: ["error", "always-multiline"]' --fix

# Fix import/order
npx eslint . --ext .js --rule 'import/order: ["error", { "alphabetize": { "order": "asc" } }]' --fix

# Fix no-unused-vars (add underscore prefix)
npx eslint . --ext .js --rule 'no-unused-vars: ["error", { "argsIgnorePattern": "^_" }]' --fix

echo "✅ ESLint auto-fix complete"
