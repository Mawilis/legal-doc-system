#!/bin/bash

# ============================================================================
# WILSY OS: QUANTUM FORENSIC ENGINE SHUTDOWN
# ============================================================================
#
# Gracefully terminates all Wilsy OS components with proper cleanup.
#
# ============================================================================

set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

readonly SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
readonly PID_DIR="${SCRIPT_DIR}/.pids"
readonly LOG_DIR="${SCRIPT_DIR}/logs"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

print_banner() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}                 QUANTUM FORENSIC ENGINE SHUTDOWN${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

stop_process_by_pidfile() {
    local pidfile="$1"
    local name="$2"
    
    if [[ -f "$pidfile" ]]; then
        local pid=$(cat "$pidfile" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            echo -n "Stopping $name (PID: $pid)... "
            kill "$pid" 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
            rm -f "$pidfile"
            return 0
        else
            echo "Process $name not running (stale PID file)"
            rm -f "$pidfile"
            return 0
        fi
    fi
    return 1
}

stop_process_by_name() {
    local pattern="$1"
    local name="$2"
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null || echo "")
    if [[ -n "$pids" ]]; then
        local count=$(echo "$pids" | wc -l | xargs)
        echo -n "Stopping $count $name instance(s)... "
        pkill -f "$pattern" 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
        return 0
    fi
    return 1
}

main() {
    print_banner
    
    local stopped=0
    local failed=0
    
    log_info "Initiating graceful shutdown sequence"
    
    # Stop in reverse order (API first, then workers)
    
    # 1. Stop API Gateway
    if stop_process_by_pidfile "$PID_DIR/api.pid" "API Gateway"; then
        stopped=$((stopped + 1))
    elif stop_process_by_name "server.js" "API Gateway"; then
        stopped=$((stopped + 1))
    fi
    
    sleep 1
    
    # 2. Stop Monitoring
    if stop_process_by_pidfile "$PID_DIR/monitoring.pid" "Monitoring"; then
        stopped=$((stopped + 1))
    elif stop_process_by_name "MonitoringDashboard" "Monitoring"; then
        stopped=$((stopped + 1))
    fi
    
    # 3. Stop Workers
    local worker_count=0
    for i in {1..4}; do
        if stop_process_by_pidfile "$PID_DIR/worker-$i.pid" "Worker $i"; then
            worker_count=$((worker_count + 1))
            stopped=$((stopped + 1))
        fi
    done
    
    if [[ $worker_count -eq 0 ]]; then
        # Try bulk stop
        if stop_process_by_name "precedentVectorizer" "Neural Workers"; then
            stopped=$((stopped + 4))
        fi
    fi
    
    # 4. Final cleanup
    echo -n "Cleaning up PID files... "
    rm -f "$PID_DIR"/*.pid 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠️${NC}"
    
    # 5. Verify all stopped
    local remaining=$(pgrep -f "node.*(server|precedentVectorizer|MonitoringDashboard)" | wc -l | xargs)
    
    echo ""
    if [[ $remaining -eq 0 ]]; then
        log_info "All processes stopped successfully ($stopped processes terminated)"
    else
        log_warn "$remaining processes still running"
        ps aux | grep -E "server|precedentVectorizer|MonitoringDashboard" | grep -v grep || true
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    exit 0
}

# Trap signals for cleanup
trap 'log_warn "Received interrupt signal"; exit 130' INT TERM

# Run main with all arguments
main "$@"
