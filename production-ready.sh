#!/bin/bash
# ============================================================================
# WILSY OS 2050 - MASTER PRODUCTION READINESS CHECK
# ============================================================================

echo "🏛️ WILSY OS 2050 - PRODUCTION READINESS CHECK"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCORE=0
MAX_SCORE=20

# Check 1: Environment files
echo "📁 1. Environment Files"
if [ -f "server/.env.production" ]; then
    PERMS=$(stat -f "%OLp" server/.env.production 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo -e "   ${GREEN}✅ .env.production exists with secure permissions${NC}"
        SCORE=$((SCORE + 2))
    else
        echo -e "   ${RED}❌ .env.production permissions incorrect (should be 600)${NC}"
    fi
else
    echo -e "   ${RED}❌ .env.production missing${NC}"
fi

# Check 2: Docker Compose
echo -e "\n🐳 2. Docker Configuration"
if [ -f "docker-compose.prod.yml" ]; then
    if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ docker-compose.prod.yml is valid${NC}"
        SCORE=$((SCORE + 2))
    else
        echo -e "   ${RED}❌ docker-compose.prod.yml has syntax errors${NC}"
    fi
else
    echo -e "   ${RED}❌ docker-compose.prod.yml missing${NC}"
fi

# Check 3: Test Suite
echo -e "\n🧪 3. Test Suite"
if [ -d "server/tests/enterprise" ]; then
    TEST_COUNT=$(find server/tests/enterprise -name "*.test.js" | wc -l | tr -d ' ')
    echo -e "   ${GREEN}✅ Found $TEST_COUNT test files${NC}"
    SCORE=$((SCORE + 2))
else
    echo -e "   ${RED}❌ Test directory missing${NC}"
fi

# Check 4: Git Configuration
echo -e "\n📦 4. Git Configuration"
if [ -f ".gitignore" ]; then
    if grep -q "\.env\.production" .gitignore; then
        echo -e "   ${GREEN}✅ .env.production is gitignored${NC}"
        SCORE=$((SCORE + 2))
    else
        echo -e "   ${RED}❌ .env.production not in .gitignore${NC}"
    fi
else
    echo -e "   ${RED}❌ .gitignore missing${NC}"
fi

# Check 5: Deployment Scripts
echo -e "\n🚀 5. Deployment Scripts"
if [ -f "deploy-prod.sh" ] && [ -f "validate-env.sh" ]; then
    echo -e "   ${GREEN}✅ Deployment scripts exist${NC}"
    SCORE=$((SCORE + 2))
else
    echo -e "   ${RED}❌ Deployment scripts missing${NC}"
fi

# Check 6: SSL Directory
echo -e "\n🔐 6. SSL Configuration"
if [ -d "ssl" ]; then
    echo -e "   ${GREEN}✅ SSL directory exists${NC}"
    SCORE=$((SCORE + 2))
else
    echo -e "   ${YELLOW}⚠️  SSL directory missing (will be created)${NC}"
    mkdir -p ssl
    touch ssl/.gitkeep
fi

# Check 7: Node Modules Permissions
echo -e "\n📦 7. Node Modules"
if [ -f "server/node_modules/.bin/mocha" ]; then
    if [ -x "server/node_modules/.bin/mocha" ]; then
        echo -e "   ${GREEN}✅ Node modules permissions correct${NC}"
        SCORE=$((SCORE + 2))
    else
        echo -e "   ${YELLOW}⚠️  Fixing node modules permissions...${NC}"
        find server/node_modules/.bin -type f -exec chmod 755 {} \; 2>/dev/null
        echo -e "   ${GREEN}✅ Fixed permissions${NC}"
        SCORE=$((SCORE + 2))
    fi
else
    echo -e "   ${YELLOW}⚠️  Node modules not installed${NC}"
fi

# Check 8: Redis Configuration
echo -e "\n📀 8. Redis Configuration"
if grep -q "REDIS_PASSWORD" server/.env.production 2>/dev/null; then
    echo -e "   ${GREEN}✅ Redis password configured${NC}"
    SCORE=$((SCORE + 2))
fi

# Check 9: MongoDB Connection
echo -e "\n🗄️ 9. MongoDB Configuration"
if grep -q "MONGODB_URI" server/.env.production 2>/dev/null; then
    echo -e "   ${GREEN}✅ MongoDB URI configured${NC}"
    SCORE=$((SCORE + 2))
fi

# Check 10: JWT Secrets
echo -e "\n🔑 10. JWT Configuration"
if grep -q "JWT_SECRET" server/.env.production 2>/dev/null; then
    if grep -q "JWT_REFRESH_SECRET" server/.env.production 2>/dev/null; then
        echo -e "   ${GREEN}✅ JWT secrets configured${NC}"
        SCORE=$((SCORE + 2))
    fi
fi

# Final Score
echo ""
echo "=========================================="
echo -e "📊 PRODUCTION READINESS SCORE: ${SCORE}/${MAX_SCORE}"
echo "=========================================="

if [ $SCORE -ge 18 ]; then
    echo -e "${GREEN}✅ EXCEPTIONAL - Production Ready!${NC}"
elif [ $SCORE -ge 14 ]; then
    echo -e "${YELLOW}⚠️  GOOD - Minor improvements needed${NC}"
else
    echo -e "${RED}❌ CRITICAL - Not production ready${NC}"
fi

echo ""
