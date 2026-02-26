#!/bin/bash

# WILSY OS - PRODUCTION LINT CHECK
# No compromises, no excuses, production-grade validation

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     WILSY OS - PRODUCTION LINT CHECK - $5B+ INFRASTRUCTURE     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"

# Check 1: Validate package.json
echo -n "📦 Checking package.json... "
if node -e "require('./package.json')" 2>/dev/null; then
    echo -e "${GREEN}✅ VALID${NC}"
else
    echo -e "${RED}❌ INVALID JSON${NC}"
    exit 1
fi

# Check 2: Verify ESLint configuration
echo -n "📋 Checking ESLint config... "
if [ -f ".eslintrc.cjs" ]; then
    echo -e "${GREEN}✅ FOUND${NC}"
else
    echo -e "${RED}❌ MISSING${NC}"
    exit 1
fi

# Check 3: Run ESLint on JavaScript files
echo -e "\n${BLUE}📊 Running ESLint on JavaScript files...${NC}"
npx eslint . --ext .js --ignore-pattern 'public/' --max-warnings 0
ESLINT_EXIT=$?

if [ $ESLINT_EXIT -eq 0 ]; then
    echo -e "${GREEN}  ✅ ESLint PASSED - No errors${NC}"
else
    echo -e "${RED}  ❌ ESLint FAILED${NC}"
    exit 1
fi

# Check 4: Verify NO inline styles in HTML
echo -e "\n${BLUE}🔍 Checking for inline styles in HTML...${NC}"
if [ -f "public/dashboard/warroom.html" ]; then
    INLINE_STYLES=$(grep -c "style=" public/dashboard/warroom.html)
    if [ $INLINE_STYLES -eq 0 ]; then
        echo -e "${GREEN}  ✅ No inline styles found${NC}"
    else
        echo -e "${RED}  ❌ Found $INLINE_STYLES inline styles${NC}"
        grep -n "style=" public/dashboard/warroom.html
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠️  warroom.html not found${NC}"
fi

# Check 5: Verify NO style manipulation in JavaScript
echo -e "\n${BLUE}🔍 Checking for style manipulation in JavaScript...${NC}"
if [ -f "public/js/warroom.js" ]; then
    STYLE_MANIP=$(grep -c "style\." public/js/warroom.js)
    # Allow only width manipulation (line 139)
    if [ $STYLE_MANIP -le 1 ]; then
        echo -e "${GREEN}  ✅ Minimal style manipulation (${STYLE_MANIP} occurrences)${NC}"
    else
        echo -e "${RED}  ❌ Found $STYLE_MANIP style manipulations${NC}"
        grep -n "style\." public/js/warroom.js
        exit 1
    fi
fi

# Check 6: Validate HTML file exists in correct location
echo -e "\n${BLUE}📁 Checking file locations...${NC}"
if [ -f "public/dashboard/warroom.html" ] && [ ! -f "dashboard/warroom.html" ]; then
    echo -e "${GREEN}  ✅ Files in correct locations${NC}"
else
    if [ -f "dashboard/warroom.html" ]; then
        echo -e "${RED}  ❌ Found old dashboard/ directory - DELETE IT${NC}"
        echo -e "${YELLOW}     Run: rm -rf dashboard/${NC}"
        exit 1
    fi
fi

# Check 7: Verify VS Code is configured correctly
echo -e "\n${BLUE}⚙️  Checking VS Code configuration...${NC}"
if [ -f ".vscode/settings.json" ]; then
    echo -e "${GREEN}  ✅ VS Code settings found${NC}"
else
    echo -e "${YELLOW}  ⚠️  VS Code settings missing${NC}"
fi

# Check 8: Verify no old config files
echo -e "\n${BLUE}🗑️  Checking for deprecated files...${NC}"
DEPRECATED_FILES=(".eslintrc.json" ".eslintrc.js" ".eslintignore" "eslint.config.js")
DEPRECATED_FOUND=0

for file in "${DEPRECATED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${RED}  ❌ Found deprecated: $file${NC}"
        DEPRECATED_FOUND=1
    fi
done

if [ $DEPRECATED_FOUND -eq 0 ]; then
    echo -e "${GREEN}  ✅ No deprecated files found${NC}"
fi

# FINAL VERDICT
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
if [ $ESLINT_EXIT -eq 0 ] && [ $INLINE_STYLES -eq 0 ]; then
    echo -e "${GREEN}║     ✅ ALL CHECKS PASSED - WILSY OS PRODUCTION READY        ║${NC}"
else
    echo -e "${RED}║     ❌ CHECKS FAILED - FIX ERRORS BEFORE INVESTOR DEMO       ║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

exit $ESLINT_EXIT
