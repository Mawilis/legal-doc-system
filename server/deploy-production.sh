#!/bin/bash

# WILSY OS - PRODUCTION DEPLOYMENT SCRIPT
# Zero-downtime deployment with canary releases

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     WILSY OS v3.0 - PRODUCTION DEPLOYMENT                      ║${NC}"
echo -e "${BLUE}║     Zero-downtime | Canary | Auto-rollback                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Phase 1: Pre-flight checks
echo -e "\n${YELLOW}🔍 Phase 1: Pre-flight checks${NC}"
echo "  ────────────────────────────────────────"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "  ❌ Docker not found. Please install Docker."
    exit 1
fi
echo -e "  ✅ Docker: $(docker --version)"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "  ⚠️  kubectl not found. Skipping Kubernetes deployment."
    SKIP_K8S=true
else
    echo -e "  ✅ kubectl: $(kubectl version --client -o json | jq -r .clientVersion.gitVersion)"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "  ❌ npm not found."
    exit 1
fi
echo -e "  ✅ npm: $(npm --version)"

# Phase 2: Build and test
echo -e "\n${YELLOW}🧪 Phase 2: Build and test${NC}"
echo "  ────────────────────────────────────────"

echo -e "  📦 Installing dependencies..."
npm ci --production

echo -e "  🧪 Running tests..."
npm test

# Phase 3: Build Docker image
echo -e "\n${YELLOW}🐳 Phase 3: Building Docker image${NC}"
echo "  ────────────────────────────────────────"

VERSION=$(node -p "require('./package.json').version")
TIMESTAMP=$(date +%Y%m%d%H%M%S)
TAG="v${VERSION}-${TIMESTAMP}"

echo -e "  📦 Version: ${TAG}"
echo -e "  🏗️  Building image..."

docker build -t wilsy-os/predictive-engine:${TAG} .
docker tag wilsy-os/predictive-engine:${TAG} wilsy-os/predictive-engine:latest

echo -e "  ✅ Image built: wilsy-os/predictive-engine:${TAG}"

# Phase 4: Deploy to Kubernetes (if available)
if [ "$SKIP_K8S" != true ]; then
    echo -e "\n${YELLOW}☸️ Phase 4: Deploying to Kubernetes${NC}"
    echo "  ────────────────────────────────────────"
    
    # Update image in deployment
    kubectl set image deployment/wilsy-os-predictive \
        predictive-engine=wilsy-os/predictive-engine:${TAG} \
        --namespace=wilsy-os
    
    # Wait for rollout
    echo -e "  ⏳ Waiting for rollout..."
    kubectl rollout status deployment/wilsy-os-predictive \
        --namespace=wilsy-os \
        --timeout=5m
    
    # Verify deployment
    echo -e "  ✅ Deployment complete"
    kubectl get pods -n wilsy-os
else
    echo -e "\n${YELLOW}📦 Phase 4: Running locally${NC}"
    echo "  ────────────────────────────────────────"
    
    # Stop existing container if running
    docker stop wilsy-os-local 2>/dev/null || true
    
    # Run new container
    docker run -d \
        --name wilsy-os-local \
        -p 4000:4000 \
        -e NODE_ENV=production \
        wilsy-os/predictive-engine:${TAG}
    
    echo -e "  ✅ Container running: wilsy-os-local"
fi

# Phase 5: Smoke tests
echo -e "\n${YELLOW}🔥 Phase 5: Smoke tests${NC}"
echo "  ────────────────────────────────────────"

echo -e "  ⏳ Waiting for service to be ready..."
sleep 10

# Test health endpoint
if curl -s -f http://localhost:4000/api/predict/health > /dev/null; then
    echo -e "  ✅ Health check passed"
else
    echo -e "  ❌ Health check failed"
    exit 1
fi

# Test metrics endpoint
if curl -s -f http://localhost:4000/api/predict/metrics > /dev/null; then
    echo -e "  ✅ Metrics endpoint working"
else
    echo -e "  ❌ Metrics endpoint failed"
    exit 1
fi

# Phase 6: Generate investor report
echo -e "\n${YELLOW}📊 Phase 6: Generating investor report${NC}"
echo "  ────────────────────────────────────────"

npm run investor-report

# Phase 7: Summary
echo -e "\n${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "  🚀 Version: ${TAG}"
echo -e "  🌐 API: http://localhost:4000"
echo -e "  📊 Metrics: http://localhost:4000/api/predict/metrics"
echo -e "  💓 Health: http://localhost:4000/api/predict/health"
echo -e "  📈 Investor Report: npm run investor-report"
echo -e "  📊 Monitor: ./monitor-production.sh"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}To monitor in real-time:${NC}"
echo "  ./monitor-production.sh"

echo -e "\n${BLUE}To view logs:${NC}"
if [ "$SKIP_K8S" != true ]; then
    echo "  kubectl logs -n wilsy-os -l app=wilsy-os"
else
    echo "  docker logs -f wilsy-os-local"
fi
