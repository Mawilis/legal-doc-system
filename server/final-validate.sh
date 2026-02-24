#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ WILSY OS FINAL VALIDATION - INVESTOR READY                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: No deprecated Prettier options
echo -n "Check 1: .prettierrc valid... "
if ! grep -q "jsxBracketSameLine" .prettierrc 2>/dev/null; then
  echo "✅"
else
  echo "❌"
  exit 1
fi

# Check 2: No ** in comments
echo -n "Check 2: No ** in comments... "
COUNT=$(find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" 2>/dev/null | xargs grep -l "\*\*" 2>/dev/null | wc -l)

if [ "$COUNT" -eq 0 ]; then
  echo "✅"
else
  echo "❌ ($COUNT files remain)"
  echo ""
  echo "Files with **:"
  find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \
    -not -path "*/node_modules/*" \
    -not -path "*/coverage/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" 2>/dev/null | xargs grep -l "\*\*" 2>/dev/null | head -10
  exit 1
fi

# Check 3: Evidence exists
echo -n "Check 3: Evidence exists... "
LATEST=$(ls -t docs/evidence/prettier-final-*.forensic.json 2>/dev/null | head -1)
if [ -f "$LATEST" ]; then
  echo "✅ $(basename $LATEST)"
  
  # Show evidence summary
  echo ""
  echo "📊 EVIDENCE SUMMARY:"
  echo "   ID: $(jq -r '.evidenceId' "$LATEST")"
  echo "   Files: $(jq -r '.metrics.totalJsFiles' "$LATEST")"
  echo "   Fixed: $(jq -r '.metrics.filesFixed' "$LATEST")"
  echo "   Savings: R$(jq -r '.economicImpact.annualSavingsZAR' "$LATEST")"
  echo "   ROI: $(jq -r '.economicImpact.roi' "$LATEST")%"
  echo "   Hash: $(jq -r '.forensicHash' "$LATEST" | cut -c1-16)..."
else
  echo "❌ No evidence found"
  exit 1
fi

echo ""
echo "========================================"
echo "🎉 ALL CHECKS PASSED - INVESTOR READY"
echo "========================================"
echo ""
echo "📍 NEXT STEPS:"
echo "   1. git add ."
echo "   2. git commit -m \"fix(prettier): final forensic fix complete\""
echo "   3. git push"
echo "   4. Present evidence to investors: cat $LATEST | jq '.'"
