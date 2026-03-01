#!/bin/bash

# Test the Document Generation API
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Testing Document Generation API${NC}"
echo "================================"

# Test 1: Generate a document
echo -e "\n${GREEN}Test 1: Generate Document${NC}"
curl -X POST http://localhost:3000/api/documents/generate \
  -H 'X-Tenant-ID: acme-corp' \
  -H 'Content-Type: application/json' \
  -d '{
    "templateId": "TMP-CONTRACT-001",
    "variables": {
      "clientName": "Acme Corporation",
      "date": "2026-02-28",
      "amount": 1500000,
      "signatory": "John Smith"
    },
    "options": {
      "format": "pdf",
      "correlationId": "test-001"
    }
  }'

# Test 2: Batch generation
echo -e "\n${GREEN}Test 2: Batch Generation${NC}"
curl -X POST http://localhost:3000/api/documents/batch \
  -H 'X-Tenant-ID: acme-corp' \
  -H 'Content-Type: application/json' \
  -d '{
    "batchId": "batch-001",
    "documents": [
      {
        "id": "doc-1",
        "templateId": "TMP-CONTRACT-001",
        "variables": {
          "clientName": "Client 1",
          "amount": 50000
        }
      },
      {
        "id": "doc-2",
        "templateId": "TMP-CONTRACT-001",
        "variables": {
          "clientName": "Client 2",
          "amount": 75000
        }
      }
    ]
  }'

echo -e "\n${BLUE}✅ API tests complete${NC}"
