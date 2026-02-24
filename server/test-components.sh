#!/bin/bash

# ============================================================================
# WILSY OS: COMPONENT TEST SUITE
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                    WILSY OS COMPONENT TEST SUITE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: Can Node.js run?
echo -n "Test 1: Node.js execution: "
if node -e "console.log('ok')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 2: Can we import required modules?
echo -n "Test 2: Module imports: "
if node -e "try { require('express'); console.log('ok'); } catch(e) { console.log('fail'); process.exit(1); }" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (run 'npm install')${NC}"
fi

# Test 3: Quick worker test (5 seconds)
echo -n "Test 3: Worker startup: "
cd "$(dirname "$0")"
timeout 5 node workers/precedentVectorizer.js > /dev/null 2>&1 &
pid=$!
sleep 2
if kill -0 $pid 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    kill $pid 2>/dev/null || true
else
    echo -e "${RED}✗${NC}"
fi

# Test 4: Quick API test (5 seconds)
echo -n "Test 4: API startup: "
timeout 5 node server.js > /dev/null 2>&1 &
pid=$!
sleep 2
if kill -0 $pid 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    kill $pid 2>/dev/null || true
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
