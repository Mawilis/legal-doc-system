#!/bin/bash
# -----------------------------------------------------------------------------
# Copyright (c) 2025 Wilsy Pty Ltd [Reg: 2024/617944/07].
# All Rights Reserved.
# Proprietary and confidential.
# -----------------------------------------------------------------------------

echo "🚀 LAUNCHING WILSY PTY LTD ENTERPRISE OS..."

# 1. CLEANUP: Kill any lingering processes
lsof -ti:3001,6000,6100,6400,6500,6600 | xargs kill -9 2>/dev/null

echo "--- CORE SERVICES ---"

# We use (cd path && cmd) to run in a bubble. The main script stays in the root.

(cd services/ledger && nohup npm start > ../../ledger.log 2>&1 &)
echo "✅ Ledger (Port 6000)"

(cd services/standards && nohup npm start > ../../standards.log 2>&1 &)
echo "✅ Standards (Port 6100)"

(cd services/billing && nohup npm start > ../../billing.log 2>&1 &)
echo "✅ Billing (Port 6400)"

(cd services/ai && nohup npm start > ../../ai.log 2>&1 &)
echo "✅ AI Engine (Port 6500)"

(cd services/crypto && nohup npm start > ../../crypto.log 2>&1 &)
echo "✅ Crypto Vault (Port 6600)"

echo "--- GATEWAY ---"

# Main Server (Foreground)
(cd server && npm start)
