#!/bin/bash
# Deployment script for investor-ready document controller

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   DEPLOYMENT: SOVEREIGN DOCUMENT CONTROLLER                   ║
║   INVESTOR VALIDATED | PRODUCTION READY                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"

cd /Users/wilsonkhanyezi/legal-doc-system/server

echo ""
echo "1. VERIFYING PRE-DEPLOYMENT CHECKLIST..."
echo "────────────────────────────────────────"

# Check evidence exists
if [ ! -f "__tests__/controllers/evidence.json" ]; then
    echo "❌ Missing evidence.json - running validation..."
    node final-economic-validation.js
fi

# Verify evidence integrity
EXPECTED_HASH=$(jq -r '.hash' __tests__/controllers/evidence.json)
CALCULATED_HASH=$(jq -c '.auditEntries | sort_by(.action)' __tests__/controllers/evidence.json | sha256sum | cut -d' ' -f1)

if [ "$EXPECTED_HASH" != "$CALCULATED_HASH" ]; then
    echo "❌ Evidence integrity check failed"
    exit 1
fi
echo "✓ Evidence integrity verified"

# Check economic targets
ANNUAL_SAVINGS=$(jq '.economicValidation.annualSavings' __tests__/controllers/evidence.json)
if [ $ANNUAL_SAVINGS -lt 200000 ]; then
    echo "❌ Annual savings below target: R$ANNUAL_SAVINGS"
    exit 1
fi
echo "✓ Annual savings: R$ANNUAL_SAVINGS (Target: ≥ R200,000)"

RISK_ELIMINATION=$(jq '.economicValidation.riskElimination' __tests__/controllers/evidence.json)
if [ $RISK_ELIMINATION -lt 2400000 ]; then
    echo "❌ Risk elimination below target: R$RISK_ELIMINATION"
    exit 1
fi
echo "✓ Risk elimination: R$RISK_ELIMINATION (Target: ≥ R2,400,000)"

echo ""
echo "2. RUNNING FINAL VALIDATION..."
echo "──────────────────────────────"

./verify-investor-ready.sh

if [ $? -ne 0 ]; then
    echo "❌ Validation failed - cannot deploy"
    exit 1
fi

echo ""
echo "3. DEPLOYMENT COMMANDS..."
echo "─────────────────────────"

echo "Option A: Git deployment"
echo "───────────────────────"
echo "git push origin main"
echo "git tag -a v1.0.0-investor-validated -m 'Sovereign Document Controller - Investor Validated'"
echo "git push origin v1.0.0-investor-validated"

echo ""
echo "Option B: Direct deployment (if server running)"
echo "──────────────────────────────────────────────"
echo "# The controller is already in controllers/documentController.js"
echo "# Ensure routes are set up in routes/documents.js:"
echo ""
echo "Example route setup:"
echo "const express = require('express');"
echo "const router = express.Router();"
echo "const documentController = require('../controllers/documentController');"
echo ""
echo "router.post('/documents', documentController.uploadDocument);"
echo "router.get('/documents/:id', documentController.getDocument);"
echo "router.get('/documents/:id/download', documentController.downloadDocument);"
echo "router.put('/documents/:id', documentController.updateDocument);"
echo "router.delete('/documents/:id', documentController.deleteDocument);"
echo "router.get('/documents/search', documentController.searchDocuments);"
echo "router.get('/documents/:id/access-history', documentController.getDocumentAccessHistory);"

echo ""
echo "4. POST-DEPLOYMENT VERIFICATION..."
echo "──────────────────────────────────"

echo "Health check endpoints (after deployment):"
echo "-----------------------------------------"
echo "1. Economic validation:"
echo "   curl http://localhost:3000/api/documents/economic-impact"
echo ""
echo "2. Compliance status:"
echo "   curl http://localhost:3000/api/documents/compliance"
echo ""
echo "3. System health:"
echo "   curl http://localhost:3000/api/documents/health"

echo ""
echo "5. INVESTOR COMMUNICATION..."
echo "────────────────────────────"

echo "Documents to share with investors:"
echo "1. INVESTOR_EXECUTIVE_SUMMARY.md - Executive summary"
echo "2. __tests__/controllers/evidence.json - Forensic evidence"
echo "3. Verification command:"
echo "   jq -c '.auditEntries | sort_by(.action)' evidence.json | sha256sum"
echo "4. ROI calculation:"
ROI=$(jq -r '.economicValidation.roi' __tests__/controllers/evidence.json)
echo "   ROI: ${ROI}:1 (Every R1 eliminates R${ROI} risk)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   DEPLOYMENT READY                                            ║
║   All validation passed ✅                                        ║
║   Economic targets met ✅                                         ║
║   Compliance verified ✅                                          ║
║   Investor ready ✅                                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "🚀 To deploy:"
echo "   1. Ensure server is running: npm start"
echo "   2. Verify routes are configured"
echo "   3. Share investor documents"
echo "   4. Schedule investor demo"
echo ""
echo "💰 Status: PRODUCTION READY - INVESTOR VALIDATED"
