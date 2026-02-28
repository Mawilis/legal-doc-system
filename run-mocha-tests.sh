#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MOCHA TEST RUNNER - DOCUMENT GENERATION SYSTEM             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

cd /Users/wilsonkhanyezi/legal-doc-system/server

export NODE_ENV=test
export NODE_OPTIONS="--experimental-vm-modules"

run_test() {
  local test_file=$1
  local timeout=${2:-10000}
  
  echo -e "\n${YELLOW}Running: ${test_file}${NC}"
  npx mocha \
    --config .mocharc.cjs \
    --file tests/setup.cjs \
    "$test_file" \
    --timeout $timeout \
    --exit
  
  return $?
}

case "$1" in
  template)
    run_test "tests/unit/DocumentTemplate.test.js" 10000
    ;;
  engine)
    echo -e "${YELLOW}DocumentGenerationEngine tests need conversion to Mocha/Chai${NC}"
    echo "Run template tests first: ./run-mocha-tests.sh template"
    ;;
  integration)
    echo -e "${YELLOW}Integration tests need conversion to Mocha/Chai${NC}"
    echo "Run template tests first: ./run-mocha-tests.sh template"
    ;;
  *)
    echo "Usage: ./run-mocha-tests.sh [template|engine|integration]"
    echo "  template  - Run DocumentTemplate model tests"
    echo "  engine    - Run DocumentGenerationEngine tests (needs conversion)"
    echo "  integration - Run integration tests (needs conversion)"
    ;;
esac
