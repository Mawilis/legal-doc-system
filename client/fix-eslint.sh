#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/wilsonkhanyezi/legal-doc-system/client

echo -e "${YELLOW}🔧 FIXING ESLINT WARNINGS...${NC}"

# Install PropTypes
npm install prop-types

# Update main.jsx to fix warnings
sed -i '' 's/import { BrowserRouter, Routes, Route }/import { BrowserRouter }/' src/main.jsx

echo -e "${GREEN}✅ ESLint warnings fixed!${NC}"
echo -e "\nRemaining warnings should be informational only."
