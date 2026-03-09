#!/bin/bash
# ============================================================================
# WILSY OS 2050 - ENVIRONMENT VALIDATION SCRIPT
# Checks all required environment variables are set
# ============================================================================

echo "🏛️ WILSY OS 2050 - Environment Validation"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Required variables
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

# Check environment file
ENV_FILE="server/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ $ENV_FILE not found${NC}"
    exit 1
fi

echo -e "\n📁 Checking $ENV_FILE"
echo "----------------------------------------"

# Load and check each variable
MISSING=0
for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^${var}=" "$ENV_FILE"; then
        value=$(grep "^${var}=" "$ENV_FILE" | cut -d'=' -f2-)
        if [ -z "$value" ] || [ "$value" = "\"\"" ]; then
            echo -e "${RED}❌ $var is empty${NC}"
            MISSING=$((MISSING + 1))
        else
            echo -e "${GREEN}✅ $var is set${NC}"
        fi
    else
        echo -e "${RED}❌ $var is missing${NC}"
        MISSING=$((MISSING + 1))
    fi
done

# Check file permissions
PERMS=$(stat -f "%OLp" "$ENV_FILE" 2>/dev/null)
if [ "$PERMS" = "600" ]; then
    echo -e "${GREEN}✅ File permissions: 600 (secure)${NC}"
else
    echo -e "${RED}❌ File permissions: $PERMS (should be 600)${NC}"
    chmod 600 "$ENV_FILE"
    echo -e "${GREEN}   → Fixed permissions${NC}"
fi

echo "----------------------------------------"
if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✅ All environment variables validated${NC}"
    exit 0
else
    echo -e "${RED}❌ $MISSING variables missing or empty${NC}"
    exit 1
fi
