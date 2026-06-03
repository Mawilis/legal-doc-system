#!/bin/bash
# 🚀 WILSY OS - SOVEREIGN DEPLOYMENT AUTOMATION
# @version 10.0.0-QUANTUM-2050
# MANDATE: BIBLICAL WORTH | PRODUCTION READY | NO CHILD'S PLACE

set -e

echo "🏛️  INITIATING WILSY OS SOVEREIGN DEPLOYMENT..."

# 1. Audit Citadel Backend
cd /Users/wilsonkhanyezi/legal-doc-system/server
npm test tests/integration/SovereignAPI_v2.test.js

# 2. Audit Sovereign HUD
cd /Users/wilsonkhanyezi/legal-doc-system/client
npm test tests/SovereignNodeDashboard.test.js

# 3. Build Production Assets
cd /Users/wilsonkhanyezi/legal-doc-system/client
npm run build

# 4. Sealing Sovereign Manifest
# This step creates the Sovereign_Manifest.json required for the 101/10 audit
cd /Users/wilsonkhanyezi/legal-doc-system/server
node scripts/generateManifest.js

echo "🚀 WILSY OS IS NOW LIVE ON MAC SERVER CLUSTER"
echo "--- DEPLOYMENT 101/10 COMPLETE ---"
