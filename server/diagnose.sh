#!/bin/bash

# ============================================================================
# WILSY OS: DIAGNOSTIC ENGINE
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                    WILSY OS DIAGNOSTIC ENGINE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check Node.js
echo -n "Node.js: "
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ $(node -v)${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
fi

# Check npm
echo -n "npm: "
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✓ $(npm -v)${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
fi

# Check Redis
echo -n "Redis: "
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi
else
    echo -e "${RED}✗ CLI not found${NC}"
fi

# Check required files
echo ""
echo -e "${YELLOW}Required Files:${NC}"

check_file() {
    echo -n "  $1: "
    if [[ -f "$1" ]]; then
        echo -e "${GREEN}✓ Found${NC}"
    else
        echo -e "${RED}✗ Missing${NC}"
    fi
}

check_file "workers/precedentVectorizer.js"
check_file "services/monitoring/MonitoringDashboard.js"
check_file "server.js"
check_file "package.json"

# Check dependencies
echo ""
echo -e "${YELLOW}Installed Dependencies:${NC}"
if [[ -f "node_modules" ]]; then
    echo "  node_modules directory exists"
else
    echo -e "${RED}  node_modules not found - run 'npm install'${NC}"
fi

# Check logs
echo ""
echo -e "${YELLOW}Recent Errors:${NC}"
if [[ -d "logs" ]]; then
    for log in logs/*.error.log; do
        if [[ -f "$log" ]]; then
            echo "  $log:"
            tail -5 "$log" 2>/dev/null | sed 's/^/    /'
        fi
    done
else
    echo "  No logs directory found"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
