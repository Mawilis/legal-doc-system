#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 DIAGNOSING CSS 500 ERROR${NC}"
echo "============================="

# Check Node version
echo -e "\n📦 Node version:"
node --version

# Check if tailwind is installed
echo -e "\n📦 Tailwind CSS version:"
npm list tailwindcss || echo "${RED}❌ Tailwind not installed${NC}"

# Check postcss config
echo -e "\n📄 postcss.config.js:"
if [ -f postcss.config.js ]; then
  echo "${GREEN}✅ Found${NC}"
  cat postcss.config.js
else
  echo "${RED}❌ Missing${NC}"
fi

# Check tailwind config
echo -e "\n📄 tailwind.config.js:"
if [ -f tailwind.config.js ]; then
  echo "${GREEN}✅ Found${NC}"
  cat tailwind.config.js | head -10
else
  echo "${RED}❌ Missing${NC}"
fi

# Check index.css
echo -e "\n📄 src/index.css:"
if [ -f src/index.css ]; then
  echo "${GREEN}✅ Found${NC}"
  head -5 src/index.css
else
  echo "${RED}❌ Missing${NC}"
fi

# Check package.json for scripts
echo -e "\n📋 Package.json scripts:"
grep -A 5 '"scripts"' package.json

echo -e "\n${YELLOW}▶ Try running: npm run dev${NC}"
