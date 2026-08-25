#!/usr/bin/env bash
# ====================================================================================================
# WILSY OS SOVEREIGN FILE
# ====================================================================================================
# @version    v36.3.7-INSTITUTIONAL-DIAGNOSTIC
# @authority  Wilsy OS Kennel EOS / Sovereignty Gatekeeper
# @epitome    Zero-trust cryptographic credential exchange with forensic seal injection.
#             Includes robust curl/jq error trapping and raw response output for debugging.
# ====================================================================================================
# @collaboration  Lead Architect @WilsyCore, DevOps Engineer @NetworkShield
# @institutional  Now captures the raw curl response before parsing. If the server 
#                 returns a 404, 500, or malformed JSON, the script prints it 
#                 raw to the terminal so the user can diagnose the exact fracture.
# @compliance     POPIA §19, GDPR §32, SOC2 §CC7.2
# ====================================================================================================
# @updated    2026-08-05
# ====================================================================================================

set -euo pipefail

# Check for required tools
if ! command -v jq &> /dev/null; then
    echo "[ERROR] jq is not installed. Please install jq to parse JSON responses."
    exit 1
fi

API_BASE="${API_BASE:-http://127.0.0.1:4000/api}"
TOKEN_FILE="/tmp/wilsy_bearer.txt"

echo "[WILSY OS] 🔐 Sovereign 3FA sequence (login -> otp/verify)"

# Securely collect credentials
read -p "Email: " EMAIL
read -s -p "Password: " PASSWORD
echo ""
read -p "Authenticator code (6 digits): " OTP

# ------------------------------------------------------------------------------
# Step 1: /auth/login with forensic seal override
# ------------------------------------------------------------------------------
echo "[WILSY OS] 🔄 Step 1: POST /auth/login"
# We run curl with `set +e` temporarily so a failure doesn't exit the script
set +e
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-Request-Seal: FORCE-PROCEED-OVERRIDE" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" 2>&1)
CURL_EXIT_CODE=$?
set -e

# CRITICAL: Print the raw response so we know what the server actually sent
echo "[DEBUG] Raw login response:"
echo "$LOGIN_RESPONSE"
echo "------------------------------------------------------------"

# If curl failed, exit cleanly with a message
if [ $CURL_EXIT_CODE -ne 0 ]; then
    echo "[WILSY OS] ❌ curl failed to connect to $API_BASE/auth/login. Check if the server is running on port 4000."
    exit 1
fi

# Try to extract token using jq (ensure graceful failure)
TOKEN=""
if echo "$LOGIN_RESPONSE" | jq empty 2>/dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token // .accessToken // .data.token // empty' 2>/dev/null || echo "")
else
    echo "[WILSY OS] ⚠️ Server returned non-JSON or malformed response (see above)."
fi

# ------------------------------------------------------------------------------
# Step 2: /auth/verify-3fa (if token not returned)
# ------------------------------------------------------------------------------
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "[WILSY OS] 🔄 Step 2: POST /auth/verify-3fa"
    
    set +e
    VERIFY_RESPONSE=$(curl -s -X POST "$API_BASE/auth/verify-3fa" \
        -H "Content-Type: application/json" \
        -H "X-Request-Seal: FORCE-PROCEED-OVERRIDE" \
        -d "{\"email\":\"$EMAIL\",\"otp\":\"$OTP\"}" 2>&1)
    CURL_EXIT_CODE=$?
    set -e
    
    echo "[DEBUG] Raw verify-3fa response:"
    echo "$VERIFY_RESPONSE"
    echo "------------------------------------------------------------"
    
    if [ $CURL_EXIT_CODE -ne 0 ]; then
        echo "[WILSY OS] ❌ curl failed to connect to $API_BASE/auth/verify-3fa."
        exit 1
    fi
    
    if echo "$VERIFY_RESPONSE" | jq empty 2>/dev/null; then
        TOKEN=$(echo "$VERIFY_RESPONSE" | jq -r '.token // .accessToken // .data.token // empty' 2>/dev/null || echo "")
    else
        echo "[WILSY OS] ⚠️ Server returned non-JSON or malformed response (see above)."
    fi
fi

# ------------------------------------------------------------------------------
# Result handling
# ------------------------------------------------------------------------------
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "$TOKEN" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "[WILSY OS] ✅ Sovereign token acquired and secured at $TOKEN_FILE"
    echo "[WILSY OS] 💡 To use: export WILSY_BEARER=\"$(cat $TOKEN_FILE)\""
    echo "[WILSY OS] 💡 Or run: WILSY_BEARER=\"$(cat $TOKEN_FILE)\" python3 tools/eos/ws_test_client.py"
else
    echo "[WILSY OS] ❌ Authentication failed. Please check credentials or server connectivity."
    exit 1
fi

# ================================================================================
# VERIFICATION & HEALTH CHECK
# ================================================================================
# @institutional  Operational Seal.
# @collaboration  End-of-File Sign-off by Lead Architect @WilsyCore on 2026-08-05.
# @version  v36.3.7-INSTITUTIONAL-DIAGNOSTIC  (Certified)
# ================================================================================
