#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 DEBUGGING LOGIN TEST${NC}"
echo "=========================="

# Run with verbose output
echo -e "\n${YELLOW}Running Login test with verbose output:${NC}"
npx vitest run tests/client/Login.test.jsx --reporter=verbose

# Check if the mock is being called correctly
echo -e "\n${YELLOW}Checking mock implementation:${NC}"
node -e "
const assert = require('assert')
try {
  const { mockLoginSuccess, mockLoginFailure } = require('./tests/client/Login.test.jsx')
  console.log('✅ Mocks loaded')
} catch (err) {
  console.log('❌ Error loading mocks:', err.message)
}
"

echo -e "\n${YELLOW}Checking file structure:${NC}"
ls -la src/pages/Login.jsx 2>/dev/null && echo "✅ Login.jsx exists" || echo "❌ Login.jsx missing"
ls -la src/contexts/authContext.jsx 2>/dev/null && echo "✅ authContext.jsx exists" || echo "❌ authContext.jsx missing"
