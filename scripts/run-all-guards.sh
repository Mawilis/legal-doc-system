#!/bin/bash
# ==============================================================================
# WILSY OS // 2050 - GLOBAL CORE RUNTIME SECURITY GATEWAY
# ==============================================================================
set -e

echo -e "\033[1;34m⚡ INITIALIZING WILSY OS SECURITY INTEGRITY GATEWAY...\033[0m"

# 1. Fire Secret Guard
echo -e "\033[1;33m🔒 RUNNING WILSY SECRET GUARD...\033[0m"
node ./scripts/wilsy-secret-guard.js

# 2. Fire Documentation Guard
echo -e "\033[1;33m📑 RUNNING WILSY DOCUMENTATION GUARD...\033[0m"
node ./scripts/wilsy-documentation-guard.js

echo -e "\033[1;32m✅ ALL SYSTEM GUARDS PASSED. CORE APPLICATION INTEGRITY SECURED.\033[0m"

echo "🔒 Running Wilsy OS Chrome Mandate Guard..."
node scripts/wilsy-chrome-mandate-guard.js client/src/components/account/WilsyAccountCommandCenter.jsx
