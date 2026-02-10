#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   INVESTOR VERIFICATION - CORRECTED                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "1. Checking evidence file..."
if [ -f "__tests__/controllers/evidence.json" ]; then
    echo "✅ Evidence file exists"
    
    ROI=$(jq -r '.economicValidation.roi' __tests__/controllers/evidence.json)
    RISK=$(jq -r '.economicValidation.riskElimination' __tests__/controllers/evidence.json)
    SAVINGS=$(jq -r '.economicValidation.annualSavings' __tests__/controllers/evidence.json)
    HASH=$(jq -r '.hash' __tests__/controllers/evidence.json)
    
    echo "   ROI: $ROI:1"
    echo "   Risk elimination: R$RISK"
    echo "   Annual savings: R$SAVINGS"
    echo "   Hash: ${HASH:0:16}..."
    
    # Verify hash
    CALC_HASH=$(jq -c 'del(.hash)' __tests__/controllers/evidence.json | sha256sum | cut -d' ' -f1)
    if [ "$HASH" = "$CALC_HASH" ]; then
        echo "   🔐 Hash verification: ✅"
    else
        echo "   🔐 Hash verification: ❌"
        echo "   Calculated: ${CALC_HASH:0:16}..."
    fi
else
    echo "❌ Evidence file missing"
fi

echo ""
echo "2. Economic Validation..."
if [ ! -z "$ROI" ] && [ ! -z "$RISK" ] && [ ! -z "$SAVINGS" ]; then
    echo "   ROI: $ROI ≥ 8.0 = $(echo "$ROI >= 8" | bc -l 2>/dev/null && echo "✅" || echo "❌")"
    echo "   Risk: R$RISK ≥ R2400000 = $( [ $RISK -ge 2400000 ] && echo "✅" || echo "❌")"
    echo "   Savings: R$SAVINGS ≥ R200000 = $( [ $SAVINGS -ge 200000 ] && echo "✅" || echo "❌")"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   VERIFICATION COMPLETE                                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
