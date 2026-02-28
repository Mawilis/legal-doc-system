#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Running Document Generation System Tests${NC}"
echo -e "${YELLOW}========================================${NC}"

# Navigate to server directory
cd /Users/wilsonkhanyezi/legal-doc-system/server

# Install test dependencies if needed
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
npm install --save-dev \
  jest \
  supertest \
  mongodb-memory-server \
  redis-mock \
  @types/jest

# Run unit tests
echo -e "\n${YELLOW}Running Unit Tests...${NC}"
npm run test:unit

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Unit tests passed${NC}"
else
  echo -e "${RED}✗ Unit tests failed${NC}"
  exit 1
fi

# Run integration tests
echo -e "\n${YELLOW}Running Integration Tests...${NC}"
npm run test:integration

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Integration tests passed${NC}"
else
  echo -e "${RED}✗ Integration tests failed${NC}"
  exit 1
fi

# Run coverage report
echo -e "\n${YELLOW}Generating Coverage Report...${NC}"
npm run test:coverage

# Display coverage summary
echo -e "\n${GREEN}Coverage Summary:${NC}"
cat coverage/lcov-report/index.html | grep -A 5 "Coverage summary"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

# Optional: Open coverage report in browser
if [ "$1" == "--open" ]; then
  open coverage/lcov-report/index.html
fi
