#!/bin/bash
# ============================================================================
# WILSY OS 2050 - PRODUCTION ENVIRONMENT VALIDATION
# VERSION: v2.0.0-R10E74-PRODUCTION-RECOVERY-CONFIG-GATE
# AUTHORITY: Wilsy OS Core Governance
# PURPOSE: Fail closed before production deployment when mandatory platform,
#          password-recovery origin, or encrypted mail configuration is absent.
# SECURITY: Secret values are never printed.
# ============================================================================

set -u

echo "🏛️ WILSY OS 2050 - Environment Validation"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENV_FILE="server/.env.production"

declare -a REQUIRED_VARS=(
  "JWT_SECRET"
  "JWT_REFRESH_SECRET"
  "MONGODB_URI"
  "FORENSIC_HMAC_KEY"
  "ADMIN_EMAIL"
  "ADMIN_PASSWORD"
  "USER_ENCRYPTION_KEY"
  "AUDIT_ENCRYPTION_KEY"
)

declare -a RECOVERY_ORIGIN_VARS=(
  "WILSY_PUBLIC_APP_ORIGIN"
  "WILSY_PUBLIC_APP_URL"
  "CLIENT_URL"
  "FRONTEND_URL"
  "APP_URL"
)

declare -a RECOVERY_DEDICATED_MAIL_VARS=(
  "WILSY_RECOVERY_SMTP_HOST"
  "WILSY_RECOVERY_SMTP_PORT"
  "WILSY_RECOVERY_SMTP_USERNAME"
  "WILSY_RECOVERY_SMTP_PASSWORD"
  "WILSY_RECOVERY_EMAIL_FROM"
  "WILSY_RECOVERY_SMTP_SSL"
)

declare -a EMAIL_MAIL_VARS=(
  "EMAIL_HOST"
  "EMAIL_PORT"
  "EMAIL_USER"
  "EMAIL_PASS"
  "EMAIL_FROM"
  "EMAIL_SECURE"
)

declare -a SMTP_MAIL_BASE_VARS=(
  "SMTP_HOST"
  "SMTP_PORT"
  "SMTP_USER"
  "SMTP_FROM"
  "SMTP_SECURE"
)

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ $ENV_FILE not found${NC}"
    exit 1
fi

env_line_exists() {
    grep -q "^${1}=" "$ENV_FILE"
}

env_value() {
    grep "^${1}=" "$ENV_FILE" | head -n 1 | cut -d'=' -f2-
}

env_has_value() {
    local value
    value="$(env_value "$1")"
    [ -n "$value" ] && [ "$value" != '""' ] && [ "$value" != "''" ]
}

profile_complete() {
    local variable
    for variable in "$@"; do
        if ! env_has_value "$variable"; then
            return 1
        fi
    done
    return 0
}

profile_any_present() {
    local variable
    for variable in "$@"; do
        if env_line_exists "$variable"; then
            return 0
        fi
    done
    return 1
}

strip_outer_quotes() {
    local value="$1"
    if [[ "$value" == \"*\" ]] && [ "${#value}" -ge 2 ]; then
        value="${value#\"}"
        value="${value%\"}"
    elif [[ "$value" == \'*\' ]] && [ "${#value}" -ge 2 ]; then
        value="${value#\'}"
        value="${value%\'}"
    fi
    printf '%s' "$value"
}

echo -e "\n📁 Checking $ENV_FILE"
echo "----------------------------------------"

MISSING=0

for var in "${REQUIRED_VARS[@]}"; do
    if env_has_value "$var"; then
        echo -e "${GREEN}✅ $var is set${NC}"
    else
        echo -e "${RED}❌ $var is missing or empty${NC}"
        MISSING=$((MISSING + 1))
    fi
done

echo -e "\n🔐 Password-recovery public origin"
echo "----------------------------------------"

RECOVERY_ORIGIN_VAR=""
RECOVERY_ORIGIN_VALUE=""
for var in "${RECOVERY_ORIGIN_VARS[@]}"; do
    if env_line_exists "$var"; then
        RECOVERY_ORIGIN_VAR="$var"
        RECOVERY_ORIGIN_VALUE="$(env_value "$var")"
        break
    fi
done

if [ -z "$RECOVERY_ORIGIN_VAR" ]; then
    echo -e "${RED}❌ No server-owned recovery public origin is configured${NC}"
    MISSING=$((MISSING + 1))
elif ! env_has_value "$RECOVERY_ORIGIN_VAR"; then
    echo -e "${RED}❌ $RECOVERY_ORIGIN_VAR is explicitly empty${NC}"
    MISSING=$((MISSING + 1))
else
    RECOVERY_ORIGIN_VALUE="$(strip_outer_quotes "$RECOVERY_ORIGIN_VALUE")"
    case "$RECOVERY_ORIGIN_VALUE" in
        https://*)
            echo -e "${GREEN}✅ $RECOVERY_ORIGIN_VAR is set to an HTTPS origin${NC}"
            ;;
        *)
            echo -e "${RED}❌ $RECOVERY_ORIGIN_VAR must use HTTPS${NC}"
            MISSING=$((MISSING + 1))
            ;;
    esac
fi

echo -e "\n📧 Password-recovery encrypted mail transport"
echo "----------------------------------------"

MAIL_PROFILE=""

if profile_any_present "${RECOVERY_DEDICATED_MAIL_VARS[@]}"; then
    if profile_complete "${RECOVERY_DEDICATED_MAIL_VARS[@]}"; then
        MAIL_PROFILE="WILSY_RECOVERY"
    else
        echo -e "${RED}❌ Dedicated WILSY_RECOVERY_* mail profile is partial${NC}"
        MISSING=$((MISSING + 1))
    fi
elif profile_complete "${EMAIL_MAIL_VARS[@]}"; then
    MAIL_PROFILE="EMAIL"
else
    SMTP_PASSWORD_NAME=""
    if env_has_value "SMTP_PASSWORD"; then
        SMTP_PASSWORD_NAME="SMTP_PASSWORD"
    fi
    if env_has_value "SMTP_PASS"; then
        if [ -n "$SMTP_PASSWORD_NAME" ]; then
            SMTP_PASSWORD_VALUE="$(env_value "SMTP_PASSWORD")"
            SMTP_PASS_VALUE="$(env_value "SMTP_PASS")"
            if [ "$SMTP_PASSWORD_VALUE" != "$SMTP_PASS_VALUE" ]; then
                echo -e "${RED}❌ SMTP_PASSWORD and SMTP_PASS conflict${NC}"
                MISSING=$((MISSING + 1))
                SMTP_PASSWORD_NAME="CONFLICT"
            fi
        else
            SMTP_PASSWORD_NAME="SMTP_PASS"
        fi
    fi

    if [ "$SMTP_PASSWORD_NAME" != "CONFLICT" ] && \
       profile_complete "${SMTP_MAIL_BASE_VARS[@]}" && \
       [ -n "$SMTP_PASSWORD_NAME" ]; then
        MAIL_PROFILE="SMTP"
    fi
fi

if [ -n "$MAIL_PROFILE" ]; then
    echo -e "${GREEN}✅ Recovery mail profile is complete: $MAIL_PROFILE${NC}"
elif ! profile_any_present "${RECOVERY_DEDICATED_MAIL_VARS[@]}"; then
    echo -e "${RED}❌ No complete recovery-capable EMAIL_* or SMTP_* profile is configured${NC}"
    MISSING=$((MISSING + 1))
fi

PERMS=$(stat -f "%OLp" "$ENV_FILE" 2>/dev/null || true)
if [ "$PERMS" = "600" ]; then
    echo -e "${GREEN}✅ File permissions: 600 (secure)${NC}"
else
    echo -e "${YELLOW}⚠️ File permissions: ${PERMS:-unknown}; enforcing 600${NC}"
    chmod 600 "$ENV_FILE"
    echo -e "${GREEN}✅ File permissions corrected to 600${NC}"
fi

echo "----------------------------------------"
if [ "$MISSING" -eq 0 ]; then
    echo -e "${GREEN}✅ Production environment and recovery delivery configuration validated${NC}"
    exit 0
fi

echo -e "${RED}❌ Production environment validation failed with $MISSING issue(s)${NC}"
exit 1

# ============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: validate-env.sh
# VERSION: v2.0.0-R10E74-PRODUCTION-RECOVERY-CONFIG-GATE
# AUTHORITY BOUNDARY: deployment configuration validation only
# TENANT POSTURE: no tenant authority is created or inferred
# FAIL-CLOSED POSTURE: missing/partial/unsafe recovery configuration blocks deploy
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
# ============================================================================
