#!/bin/bash
cd /Users/wilsonkhanyezi/legal-doc-system
echo "🚀 Running LPC 35.2 tests..."
NODE_ENV=test npx jest --runInBand --testMatch="**/rule35.2.executive-reports.forensic.test.js" --verbose
echo ""
echo "📊 Evidence files:"
ls -la server/docs/evidence/lpc-35.2-*.forensic.json 2>/dev/null || echo "No evidence files yet"
