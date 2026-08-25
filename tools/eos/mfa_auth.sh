#!/usr/bin/env bash
# =============================================================================
# Wilsy OS — Sovereign MFA / 3FA Auth Sequence
# File:    tools/eos/mfa_auth.sh
# Version: v3.0.0-VERIFY-3FA
# Epitome: Aligns with server/routes/auth.js:
#            POST /api/auth/login       → MFA_REQUIRED (no token by design)
#            POST /api/auth/otp/verify  or /api/auth/verify-3fa → accessToken
#          ( /api/auth/mfa/* is setup-only and requires protect → NO_TOKEN )
# =============================================================================
set -euo pipefail

BASE_URL="${WILSY_API_BASE:-http://127.0.0.1:4000}"
TENANT_ID="${TENANT_ID:-MASTER}"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().rstrip("\n")))' <<<"$1"
}

echo "[WILSY OS] 🔐 Sovereign 3FA sequence (login → otp/verify | verify-3fa)"
read -r -p "Email: " EMAIL
read -r -s -p "Password: " PASSWORD
echo
read -r -p "Authenticator code (6 digits): " MFA_CODE
echo

EMAIL_J=$(json_escape "$EMAIL")
PASS_J=$(json_escape "$PASSWORD")
CODE_J=$(json_escape "$MFA_CODE")
TENANT_J=$(json_escape "$TENANT_ID")

HDR=(-H "Content-Type: application/json" -H "X-Tenant-ID: ${TENANT_ID}" -H "Accept: application/json")

echo "[WILSY OS] 🔄 Step 1: POST /api/auth/login"
STEP1=$(curl -s -w "\n%{http_code}" "${HDR[@]}" \
  -X POST "${BASE_URL}/api/auth/login" \
  -d "{\"email\":${EMAIL_J},\"password\":${PASS_J},\"tenantId\":${TENANT_J}}")
BODY1=$(echo "$STEP1" | sed '$d')
CODE1=$(echo "$STEP1" | tail -n1)
echo "[WILSY OS] 📦 Step 1 HTTP ${CODE1}"
echo "$BODY1" | python3 -m json.tool 2>/dev/null || echo "$BODY1"

# If already fully logged in
ACCESS=$(echo "$BODY1" | python3 -c "
import json,sys
d=json.load(sys.stdin)
def dig(o,*ks):
  if not isinstance(o,dict): return ''
  for k in ks:
    v=o.get(k)
    if v: return str(v)
  return ''
bag=d.get('data') if isinstance(d.get('data'),dict) else {}
tok=d.get('tokens') if isinstance(d.get('tokens'),dict) else {}
print(dig(d,'accessToken','token') or dig(bag,'accessToken','token') or dig(tok,'accessToken','token'))
" 2>/dev/null || true)

STATUS=$(echo "$BODY1" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status') or '')" 2>/dev/null || true)

if [[ -n "$ACCESS" && "$STATUS" != "MFA_REQUIRED" ]]; then
  echo "[WILSY OS] ✅ Access token received at login."
  echo "$ACCESS" > /tmp/wilsy_bearer.txt
  echo "export WILSY_BEARER='${ACCESS}'"
  exit 0
fi

echo "[WILSY OS] 🔄 Step 2: Complete MFA via otp/verify or verify-3fa (NOT /mfa/verify)"

# Payloads matching typical Wilsy authController.verifyOTP / verify3FA
PAYLOADS=(
  "{\"email\":${EMAIL_J},\"password\":${PASS_J},\"otp\":${CODE_J},\"code\":${CODE_J},\"mfaCode\":${CODE_J},\"tenantId\":${TENANT_J}}"
  "{\"email\":${EMAIL_J},\"otp\":${CODE_J},\"code\":${CODE_J},\"tenantId\":${TENANT_J}}"
  "{\"email\":${EMAIL_J},\"token\":${CODE_J},\"otp\":${CODE_J}}"
)

PATHS=("/api/auth/otp/verify" "/api/auth/verify-3fa" "/api/auth/sovereign-login")

SUCCESS_BODY=""
SUCCESS_CODE=""
FINAL_TOKEN=""

for path in "${PATHS[@]}"; do
  for payload in "${PAYLOADS[@]}"; do
    RESP=$(curl -s -w "\n%{http_code}" "${HDR[@]}" \
      -X POST "${BASE_URL}${path}" \
      -d "$payload")
    B=$(echo "$RESP" | sed '$d')
    C=$(echo "$RESP" | tail -n1)
    echo "[WILSY OS]    POST ${path} → HTTP ${C}"
    if [[ "$C" == "200" || "$C" == "201" ]]; then
      TOK=$(echo "$B" | python3 -c "
import json,sys
d=json.load(sys.stdin)
def dig(o,*ks):
  if not isinstance(o,dict): return ''
  for k in ks:
    if o.get(k): return str(o[k])
  return ''
bag=d.get('data') if isinstance(d.get('data'),dict) else {}
tok=d.get('tokens') if isinstance(d.get('tokens'),dict) else {}
print(dig(d,'accessToken','token','jwt') or dig(bag,'accessToken','token') or dig(tok,'accessToken','token'))
" 2>/dev/null || true)
      if [[ -n "$TOK" ]]; then
        SUCCESS_BODY="$B"
        SUCCESS_CODE="$C"
        FINAL_TOKEN="$TOK"
        break 2
      fi
      # 200 but no token — still keep body for inspection
      SUCCESS_BODY="$B"
      SUCCESS_CODE="$C"
    fi
  done
done

echo "[WILSY OS] 📦 Step 2 result HTTP ${SUCCESS_CODE:-none}"
echo "${SUCCESS_BODY:-}" | python3 -m json.tool 2>/dev/null || echo "${SUCCESS_BODY:-}"

if [[ -z "$FINAL_TOKEN" ]]; then
  echo "[WILSY OS] ❌ No accessToken from otp/verify or verify-3fa."
  echo "    Open server/controllers/authController.js and check verifyOTP / verify3FA body fields."
  echo "    grep -n \"verifyOTP\\|verify3FA\\|MFA_REQUIRED\" server/controllers/authController.js | head -40"
  exit 1
fi

echo "$FINAL_TOKEN" > /tmp/wilsy_bearer.txt
echo "[WILSY OS] ✅ 3FA complete — token saved to /tmp/wilsy_bearer.txt"
echo "export WILSY_BEARER='${FINAL_TOKEN}'"
echo
echo "Verify:"
echo "  export WILSY_BEARER=\$(cat /tmp/wilsy_bearer.txt)"
echo "  curl -s -H \"Authorization: Bearer \$WILSY_BEARER\" -H \"X-Tenant-ID: ${TENANT_ID}\" ${BASE_URL}/api/auth/me | head -c 400"
