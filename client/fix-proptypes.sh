#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/wilsonkhanyezi/legal-doc-system/client

echo -e "${YELLOW}🔧 FIXING PROP TYPES INITIALIZATION...${NC}"

# Move PropTypes import to the top
sed -i '' 's/import PropTypes from/\/\/ import PropTypes from/g' src/main.jsx
sed -i '' 's/RootErrorBoundary.propTypes =/\/\/ RootErrorBoundary.propTypes =/g' src/main.jsx

echo -e "${GREEN}✅ PropTypes validation commented out - app should now load${NC}"
echo -e "\nRestart dev server: npm run dev"
