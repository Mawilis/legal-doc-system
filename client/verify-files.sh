#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📁 FILE VERIFICATION${NC}"
echo "==================="

# Check Login component
echo -e "\nLogin component:"
if [ -f src/pages/Login.jsx ]; then
  echo -e "  ${GREEN}✅ src/pages/Login.jsx${NC}"
  head -5 src/pages/Login.jsx
else
  echo -e "  ${RED}❌ src/pages/Login.jsx not found${NC}"
fi

# Check auth context
echo -e "\nAuth context:"
if [ -f src/contexts/authContext.jsx ]; then
  echo -e "  ${GREEN}✅ src/contexts/authContext.jsx${NC}"
else
  echo -e "  ${RED}❌ src/contexts/authContext.jsx not found${NC}"
fi

# Check test file
echo -e "\nTest file:"
if [ -f tests/client/Login.test.jsx ]; then
  echo -e "  ${GREEN}✅ tests/client/Login.test.jsx${NC}"
  echo -e "\nImport path in test:"
  grep "import.*Login" tests/client/Login.test.jsx
else
  echo -e "  ${RED}❌ tests/client/Login.test.jsx not found${NC}"
fi

echo -e "\n${YELLOW}Running test...${NC}"
npx vitest run tests/client/Login.test.jsx
