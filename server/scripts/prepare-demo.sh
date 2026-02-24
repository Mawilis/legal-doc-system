#!/bin/bash

# ============================================================================
# WILSY OS: DEMO PREPARATION SCRIPT - LOAD TEST DATA
# ============================================================================
#
# This script prepares the demo environment with realistic test data
# to ensure a smooth investor presentation.
#
# ============================================================================

set -e

API_GATEWAY="http://localhost:9095"
TOKEN_DEMO="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRJZCI6ImRlbW8tZmlybSIsInJvbGUiOiJhdHRvcm5leSJ9.example"

echo ""
echo "🚀 WILSY OS - DEMO ENVIRONMENT PREPARATION"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Create test tenant
echo "📋 Creating demo tenant..."
curl -s -X POST "$API_GATEWAY/api/v1/admin/tenants" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN_DEMO" \
     -d '{
       "tenantId": "demo-firm",
       "name": "Silicon Valley Demo Law Firm",
       "plan": "enterprise",
       "features": {
         "semanticSearch": true,
         "citationNetwork": true,
         "deepAnalysis": true,
         "internationalMapping": true
       }
     }' > /dev/null

echo "✅ Demo tenant created"

# Load test precedents
echo "📚 Loading test precedents (this may take a moment)..."

PRECEDENTS=(
  '{
    "citation": "[2023] ZACC 15",
    "court": "Constitutional Court",
    "jurisdiction": "ZA",
    "date": "2023-05-15",
    "ratio": "The principle of legality requires that all law must be rationally connected to a legitimate governmental purpose. This fundamental principle ensures that exercises of public power are not arbitrary.",
    "holdings": [
      {"text": "Section 172(1)(a) of the Constitution empowers courts to declare invalid any law inconsistent with the Constitution", "weight": 100},
      {"text": "The doctrine of separation of powers does not preclude judicial oversight of executive action", "weight": 85}
    ]
  }'
  '{
    "citation": "[2022] ZASCA 42",
    "court": "Supreme Court of Appeal",
    "jurisdiction": "ZA",
    "date": "2022-08-20",
    "ratio": "In determining whether a contractual term is enforceable, courts must consider public policy. The Constitutional values of dignity, equality and freedom inform the public policy inquiry.",
    "holdings": [
      {"text": "Freedom of contract remains an important value, but it is not absolute", "weight": 90}
    ]
  }'
  '{
    "citation": "[2023] UKSC 12",
    "court": "UK Supreme Court",
    "jurisdiction": "UK",
    "date": "2023-03-10",
    "ratio": "The duty of care in negligence extends to third parties where there is sufficient proximity and it is fair, just and reasonable to impose such a duty.",
    "holdings": [
      {"text": "Proximity alone is insufficient; policy considerations must also be considered", "weight": 95}
    ]
  }'
  '{
    "citation": "[2024] USSC 8",
    "court": "US Supreme Court",
    "jurisdiction": "US",
    "date": "2024-01-15",
    "ratio": "In cases involving digital privacy, the reasonable expectation of privacy test must account for technological changes and societal expectations.",
    "holdings": [
      {"text": "Third-party doctrine does not apply to sensitive health data stored digitally", "weight": 100}
    ]
  }'
)

for precedent in "${PRECEDENTS[@]}"; do
    curl -s -X POST "$API_GATEWAY/api/v1/admin/precedents" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN_DEMO" \
         -d "$precedent" > /dev/null
    echo -n "."
done

echo ""
echo "✅ Test precedents loaded"

# Generate usage to hit upsell threshold (80%)
echo "📊 Generating usage to demonstrate upsell triggers..."

for i in {1..80}; do
    curl -s -X POST "$API_GATEWAY/api/v1/precedents/search" \
         -H "Content-Type: application/json" \
         -H "x-tenant-id: demo-firm" \
         -H "Authorization: Bearer $TOKEN_DEMO" \
         -d '{"query": "test query", "limit": 1}' > /dev/null
    echo -n "."
done

echo ""
echo "✅ Usage generated (80% threshold reached)"

echo ""
echo "🎉 Demo environment ready for investor presentation!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next step: Run ./scripts/silicon-valley-demo.sh"
echo ""

exit 0
