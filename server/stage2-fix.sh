#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║   WILSY OS - STAGE 2: SYSTEMATIC LINTING FIXES                           ║"
echo "║   [Fixing 8,725 errors strategically]                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

cd /Users/wilsonkhanyezi/legal-doc-system/server

# PHASE 1: Fix no-undef (missing imports/variables)
echo ""
echo "📌 PHASE 1: Fixing no-undef errors..."
npx eslint . --quiet --rule 'no-undef: error' --fix

# PHASE 2: Fix no-console (replace with logger)
echo ""
echo "📌 PHASE 2: Fixing no-console errors..."
npx eslint . --quiet --rule 'no-console: error' --fix

# PHASE 3: Fix radix parameter
echo ""
echo "📌 PHASE 3: Fixing radix parameter..."
npx eslint . --quiet --rule 'radix: error' --fix

# PHASE 4: Fix require-await
echo ""
echo "📌 PHASE 4: Fixing require-await..."
npx eslint . --quiet --rule 'require-await: error' --fix

# PHASE 5: Fix no-use-before-define
echo ""
echo "📌 PHASE 5: Fixing no-use-before-define..."
npx eslint . --quiet --rule 'no-use-before-define: error' --fix

# PHASE 6: Fix no-unused-vars
echo ""
echo "📌 PHASE 6: Fixing no-unused-vars..."
npx eslint . --quiet --rule 'no-unused-vars: error' --fix

echo ""
echo "✅ STAGE 2 COMPLETE - Verify with: npm run lint"
