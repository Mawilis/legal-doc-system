#!/bin/bash

# PRODUCTION TEST RUNNER - Document Generation System
# Using Mocha with ES modules support

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     PRODUCTION TEST RUNNER - DOCUMENT GENERATION SYSTEM        ║${NC}"
echo -e "${BLUE}║     Mocha + ES Modules + Full Coverage                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Ensure dependencies are installed
if [ ! -d "node_modules/mocha" ]; then
  echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
  npm install --save-dev mocha chai sinon nyc mongodb-memory-server @babel/register
fi

# Set test environment
export NODE_ENV=test
export NODE_OPTIONS="--experimental-vm-modules"

run_tests() {
  local test_files=$1
  local timeout=${2:-30000}
  
  npx mocha \
    --config .mocharc.cjs \
    --file tests/setup.cjs \
    $test_files \
    --timeout $timeout \
    --exit
}

case "$1" in
  document)
    echo -e "\n${YELLOW}Running Document Generation Tests...${NC}"
    run_tests "tests/unit/DocumentTemplate.test.js tests/unit/DocumentGenerationEngine.test.js tests/integration/documentGeneration.integration.test.js" 30000
    ;;
  template)
    echo -e "\n${YELLOW}Running DocumentTemplate Model Tests...${NC}"
    run_tests "tests/unit/DocumentTemplate.test.js" 10000
    ;;
  engine)
    echo -e "\n${YELLOW}Running DocumentGenerationEngine Tests...${NC}"
    run_tests "tests/unit/DocumentGenerationEngine.test.js" 10000
    ;;
  integration)
    echo -e "\n${YELLOW}Running Integration Tests...${NC}"
    run_tests "tests/integration/documentGeneration.integration.test.js" 30000
    ;;
  coverage)
    echo -e "\n${YELLOW}Running Document Generation Tests with Coverage...${NC}"
    npx nyc \
      --reporter=html \
      --reporter=text \
      --reporter=lcov \
      mocha \
      --config .mocharc.cjs \
      --file tests/setup.cjs \
      tests/unit/DocumentTemplate.test.js \
      tests/unit/DocumentGenerationEngine.test.js \
      tests/integration/documentGeneration.integration.test.js \
      --timeout 30000 \
      --exit
    echo -e "\n${GREEN}Coverage report: coverage/index.html${NC}"
    ;;
  all)
    echo -e "\n${YELLOW}Running All Tests...${NC}"
    run_tests "tests/" 30000
    ;;
  watch)
    echo -e "\n${YELLOW}Running Tests in Watch Mode...${NC}"
    npx mocha \
      --config .mocharc.cjs \
      --file tests/setup.cjs \
      tests/unit/DocumentTemplate.test.js \
      tests/unit/DocumentGenerationEngine.test.js \
      tests/integration/documentGeneration.integration.test.js \
      --watch \
      --timeout 30000
    ;;
  *)
    echo -e "\n${YELLOW}Usage: ./run-production-tests.sh [command]${NC}"
    echo "  document   - Run all document generation tests"
    echo "  template   - Run only DocumentTemplate model tests"
    echo "  engine     - Run only DocumentGenerationEngine tests"
    echo "  integration - Run only integration tests"
    echo "  coverage   - Run with coverage report"
    echo "  all        - Run all tests"
    echo "  watch      - Run in watch mode"
    exit 1
    ;;
esac

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
  echo -e "\n${GREEN}✅ TESTS PASSED${NC}"
else
  echo -e "\n${RED}❌ TESTS FAILED${NC}"
fi

exit $TEST_RESULT
