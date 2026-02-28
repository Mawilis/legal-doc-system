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

# Install test dependencies
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
npm install --save-dev \
  jest \
  supertest \
  mongodb-memory-server \
  @jest/globals \
  express \
  body-parser

# Run unit tests only first
echo -e "\n${YELLOW}Running Unit Tests...${NC}"
NODE_OPTIONS=--experimental-vm-modules npx jest tests/unit --runInBand --detectOpenHandles

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Unit tests passed${NC}"
else
  echo -e "${RED}✗ Unit tests failed${NC}"
  exit 1
fi

# Run integration tests
echo -e "\n${YELLOW}Running Integration Tests...${NC}"
NODE_OPTIONS=--experimental-vm-modules npx jest tests/integration --runInBand --detectOpenHandles

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Integration tests passed${NC}"
else
  echo -e "${RED}✗ Integration tests failed${NC}"
  exit 1
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
