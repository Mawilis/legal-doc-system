#!/bin/bash
# ============================================================================
# WILSY OS 2050 - PRODUCTION DEPLOYMENT SCRIPT
# ============================================================================

set -e

echo "🏛️ WILSY OS 2050 - Production Deployment"
echo "=========================================="
echo "Started: $(date)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# Step 1: Validate environment
echo "📋 Step 1: Validating environment..."
./validate-env.sh
check_status "Environment validation"

# Step 2: Run tests
echo -e "\n🧪 Step 2: Running test suite..."
cd server
npm test
check_status "Test suite"
cd ..

# Step 3: Build Docker images
echo -e "\n🐳 Step 3: Building Docker images..."
export BUILD_VERSION=$(date +%Y%m%d-%H%M%S)
docker build -t wilsy-os-2050:${BUILD_VERSION} -t wilsy-os-2050:latest -f Dockerfile .
docker build -t wilsy-worker-2050:${BUILD_VERSION} -t wilsy-worker-2050:latest -f server/Dockerfile.worker .
check_status "Docker build"

# Step 4: Backup current .env
echo -e "\n💾 Step 4: Backing up configuration..."
mkdir -p backups
cp server/.env.production backups/.env.production.$(date +%Y%m%d-%H%M%S)
check_status "Configuration backup"

# Step 5: Deploy with docker-compose
echo -e "\n🚀 Step 5: Deploying to production..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
check_status "Docker Compose deployment"

# Step 6: Health check
echo -e "\n🏥 Step 6: Running health checks..."
sleep 10
curl -f http://localhost:3000/health > /dev/null 2>&1
check_status "Health check"

# Step 7: Verify metrics
echo -e "\n📊 Step 7: Verifying metrics endpoint..."
curl -f http://localhost:9090/metrics > /dev/null 2>&1
check_status "Metrics endpoint"

# Step 8: Cleanup old images
echo -e "\n🧹 Step 8: Cleaning up old images..."
docker image prune -f
check_status "Cleanup"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ PRODUCTION DEPLOYMENT COMPLETE${NC}"
echo "=========================================="
echo "Build Version: ${BUILD_VERSION}"
echo "Deployed at: $(date)"
echo ""
echo "Services:"
echo "  - API: http://localhost:3000"
echo "  - Metrics: http://localhost:9090"
echo "  - Investor Portal: http://localhost:9096"
echo ""
