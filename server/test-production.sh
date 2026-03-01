#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Testing WILSY OS Production Endpoints"
echo "========================================"

# Test 1: Health endpoint (public)
echo -n "Test 1: Health endpoint (public) ... "
HEALTH_RESPONSE=$(curl -s http://localhost:3000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "$HEALTH_RESPONSE"
fi

# Test 2: Predictive health (protected)
echo -n "Test 2: Predictive health (protected) ... "
PREDICT_HEALTH=$(curl -s http://localhost:3000/api/predict/health)
if echo "$PREDICT_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "$PREDICT_HEALTH"
fi

# Test 3: Analyze endpoint
echo -n "Test 3: Analyze endpoint ... "
ANALYZE_RESPONSE=$(curl -s -X POST http://localhost:3000/api/predict/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "template": {
      "templateId": "test-001",
      "practiceArea": "corporate",
      "jurisdiction": "ZA"
    }
  }')
if echo "$ANALYZE_RESPONSE" | grep -q "accepted"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "$ANALYZE_RESPONSE"
fi

# Test 4: Metrics endpoint
echo -n "Test 4: Metrics endpoint ... "
METRICS_RESPONSE=$(curl -s http://localhost:3000/api/predict/metrics)
if echo "$METRICS_RESPONSE" | grep -q "accuracy"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "$METRICS_RESPONSE"
fi

echo "========================================"
