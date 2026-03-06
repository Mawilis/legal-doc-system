#!/bin/bash

# WILSY OS - Signature Flow Test Script
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TENANT="test-tenant"
TEMPLATE_ID="TMP-3E7D2EEE"

echo -e "${YELLOW}🔍 Testing complete signature flow...${NC}"

# 1. Activate template
echo -e "\n${YELLOW}📝 Activating template...${NC}"
curl -s -X PUT http://localhost:3000/api/templates/$TEMPLATE_ID \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: $TENANT" \
  -d '{"status":"active"}' | jq '.status'

# 2. Create signature request
echo -e "\n${YELLOW}📝 Creating signature request...${NC}"
SIGNATURE_RESPONSE=$(curl -s -X POST http://localhost:3000/api/signatures \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: $TENANT" \
  -d "{
    \"documentId\": \"$TEMPLATE_ID\",
    \"signers\": [
      {\"email\": \"beta@wilsyos.com\", \"name\": \"Beta User\"}
    ]
  }")

SIGNATURE_ID=$(echo "$SIGNATURE_RESPONSE" | jq -r '.signatureId')
echo -e "${GREEN}✅ Signature ID: $SIGNATURE_ID${NC}"

# 3. Sign document
echo -e "\n${YELLOW}✍️ Signing document...${NC}"
curl -s -X POST http://localhost:3000/api/signatures/$SIGNATURE_ID/sign \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: $TENANT" \
  -d "{
    \"signerData\": {
      \"email\": \"beta@wilsyos.com\",
      \"legalConsent\": true
    }
  }" | jq '.status'

# 4. Verify signature
echo -e "\n${YELLOW}✅ Verifying signature...${NC}"
curl -s -X POST http://localhost:3000/api/signatures/$SIGNATURE_ID/verify \
  -H "X-Tenant-ID: $TENANT" | jq '.verified'

echo -e "\n${GREEN}✅ Signature flow test complete!${NC}"
