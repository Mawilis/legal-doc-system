#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Running WILSY OS Client Tests${NC}"
echo "================================"

# Check if mocha is installed
if ! command -v npx mocha &> /dev/null; then
    echo -e "${RED}❌ mocha not found. Installing...${NC}"
    npm install --save-dev mocha chai @testing-library/react-hooks
fi

# Run the utils index test
echo -e "\n${YELLOW}📋 Testing Utils Index...${NC}"
npx mocha \
  --require @babel/register \
  tests/utils/index.test.js \
  --timeout 10000 \
  --exit

# Check result
if [ $? -eq 0 ]; then
  echo -e "\n${GREEN}✅ Utils Index tests PASSED!${NC}"
else
  echo -e "\n${RED}❌ Utils Index tests FAILED${NC}"
fi
