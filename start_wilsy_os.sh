/**
 * Copyright (c) 2026 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 * * This software is the confidential and proprietary information of Wilsy Pty Ltd.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 * Proprietary and confidential.
 */

#!/bin/bash
# Copyright (c) 2026 Wilsy Pty Ltd
echo "🚀 LAUNCHING WILSY PTY LTD ENTERPRISE OS..."

# Kill ports to ensure clean start (3001=Gateway, 6000=Ledger, 6100=Standards, 6400=Billing, 6500=AI, 6600=Crypto)
lsof -ti:3001,6000,6100,6400,6500,6600 | xargs kill -9 2>/dev/null

echo "--- CORE SERVICES ---"
# Ledger
cd services/ledger && nohup npm start > ../../ledger.log 2>&1 &
echo "✅ Ledger (Port 6000)"

# Standards
cd ../standards && nohup npm start > ../../standards.log 2>&1 &
echo "✅ Standards (Port 6100)"

# Billing
cd ../billing && nohup npm start > ../../billing.log 2>&1 &
echo "✅ Billing (Port 6400)"

# AI
cd ../ai && nohup npm start > ../../ai.log 2>&1 &
echo "✅ AI Engine (Port 6500)"

# Crypto
cd ../crypto && nohup npm start > ../../crypto.log 2>&1 &
echo "✅ Crypto Vault (Port 6600)"

echo "--- GATEWAY ---"
# Main Server
cd ../../server && npm start &
PID_SERVER=$!

echo "✨ SYSTEM LIVE. Press CTRL+C to stop."
trap "kill 0" SIGINT
wait
