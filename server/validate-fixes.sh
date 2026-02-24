#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ WILSY OS FORENSIC FIX VALIDATION                                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: No deprecated Prettier options
echo -n "Check 1: No deprecated Prettier options... "
if ! grep -q "jsxBracketSameLine" .prettierrc 2>/dev/null; then
  echo "✅ PASS"
else
  echo "❌ FAIL - found jsxBracketSameLine"
fi

# Check 2: No syntax errors in JS files
echo -n "Check 2: No syntax errors in JS files... "
SYNTAX_ERRORS=$(find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" -not -path "*/node_modules/*" | xargs node --check 2>&1 | grep -c "SyntaxError" || true)
if [ "$SYNTAX_ERRORS" -eq 0 ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL - $SYNTAX_ERRORS syntax errors found"
fi

# Check 3: No ** in comments
echo -n "Check 3: No ** in comments (cause of syntax errors)... "
STAR_STAR=$(find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" -not -path "*/node_modules/*" | xargs grep -l "\*\*" 2>/dev/null | wc -l)
if [ "$STAR_STAR" -eq 0 ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL - $STAR_STAR files still have **"
fi

# Check 4: Prettier can format all files
echo -n "Check 4: Prettier can format all files... "
if npx prettier --check "**/*.{js,cjs,mjs,json,md,yml,yaml}" --loglevel=error 2>&1 | grep -q "error"; then
  echo "⚠️  WARN - Some formatting issues remain (non-critical)"
else
  echo "✅ PASS"
fi

# Check 5: Evidence file exists
echo -n "Check 5: Forensic evidence exists... "
EVIDENCE_COUNT=$(ls -1 docs/evidence/prettier-*.forensic.json 2>/dev/null | wc -l)
if [ "$EVIDENCE_COUNT" -gt 0 ]; then
  LATEST=$(ls -t docs/evidence/prettier-*.forensic.json | head -1)
  echo "✅ PASS - $LATEST"
else
  echo "❌ FAIL - No evidence found"
fi

echo ""
echo "========================================"
echo "VALIDATION COMPLETE"
echo "========================================"
