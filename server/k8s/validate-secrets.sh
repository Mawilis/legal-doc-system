#!/bin/bash

# WILSY OS - Secrets Validation Script
# Validates that all required secrets exist and are properly formatted

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 WILSY OS - Secrets Validation${NC}"
echo "==================================="

REQUIRED_SECRETS=(
    "API_KEY"
    "DATABASE_URL"
    "REDIS_URL"
    "JWT_SECRET"
    "ENCRYPTION_KEY"
)

# Check if secrets file exists
if [ ! -f "k8s/secrets.yaml" ]; then
    echo -e "${RED}❌ secrets.yaml not found${NC}"
    echo "  Run ./k8s/generate-secrets.sh first"
    exit 1
fi

echo -e "\n${YELLOW}📋 Validating required secrets...${NC}"

# Check each required secret
MISSING=0
for secret in "${REQUIRED_SECRETS[@]}"; do
    if grep -q "${secret}:" k8s/secrets.yaml; then
        VALUE=$(grep "${secret}:" k8s/secrets.yaml | awk '{print $2}')
        if [ ${#VALUE} -gt 10 ]; then
            echo -e "  ✅ ${secret}: ${GREEN}present${NC} (length: ${#VALUE})"
        else
            echo -e "  ⚠️  ${secret}: ${YELLOW}too short${NC}"
            MISSING=$((MISSING+1))
        fi
    else
        echo -e "  ❌ ${secret}: ${RED}missing${NC}"
        MISSING=$((MISSING+1))
    fi
done

# Validate base64 encoding
echo -e "\n${YELLOW}🔐 Validating base64 encoding...${NC}"
INVALID=0

# Extract all secret values and test base64 decoding
while IFS= read -r line; do
    if [[ $line =~ ^[[:space:]]+([A-Z_]+):[[:space:]]+([A-Za-z0-9+/=]+)$ ]]; then
        SECRET_NAME="${BASH_REMATCH[1]}"
        SECRET_VALUE="${BASH_REMATCH[2]}"
        
        # Try to decode the base64 value
        if echo "$SECRET_VALUE" | base64 -d > /dev/null 2>&1; then
            DECODED=$(echo "$SECRET_VALUE" | base64 -d 2>/dev/null)
            if [ ! -z "$DECODED" ]; then
                echo -e "  ✅ ${SECRET_NAME}: valid encoding"
            fi
        else
            echo -e "  ❌ ${SECRET_NAME}: ${RED}invalid base64${NC}"
            INVALID=$((INVALID+1))
        fi
    fi
done < k8s/secrets.yaml

# Summary
echo -e "\n${YELLOW}📊 Validation Summary${NC}"
echo "  • Total secrets: $(grep -c ":$" k8s/secrets.yaml || echo 0)"
echo "  • Missing: ${MISSING}"
echo "  • Invalid encoding: ${INVALID}"

if [ $MISSING -eq 0 ] && [ $INVALID -eq 0 ]; then
    echo -e "\n${GREEN}✅ All secrets valid! Ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Secrets validation failed${NC}"
    exit 1
fi
