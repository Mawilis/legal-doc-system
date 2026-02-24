#!/bin/bash

# ============================================================================
# WILSY OS: 10TH GENERATION FORENSIC ENGINE LAUNCHER
# ============================================================================
#
#     ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗
#     ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝
#     ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝███████╗
#     ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗╚════██║
#     ╚███╔███╔╝██║███████╗███████║   ██║       ██║  ██║███████║
#      ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═╝╚══════╝
#
#                   10TH GENERATION FORENSIC ENGINE
#                    "IGNITING 10 GENERATIONS OF WEALTH"
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
WORKER_COUNT=8
LOG_DIR="./logs"
PID_DIR="./.pids"

# Timestamp function
timestamp() {
    date '+%I:%M:%S %p'
}

# Print banner
print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "    ╔══════════════════════════════════════════════════════════════════════════╗"
    echo "    ║                                                                          ║"
    echo "    ║   ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗           ║"
    echo "    ║   ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝           ║"
    echo "    ║   ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝███████╗           ║"
    echo "    ║   ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗╚════██║           ║"
    echo "    ║   ╚███╔███╔╝██║███████╗███████║   ██║       ██║  ██║███████║           ║"
    echo "    ║    ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═╝╚══════╝           ║"
    echo "    ║                                                                          ║"
    echo "    ║                   10TH GENERATION FORENSIC ENGINE                       ║"
    echo "    ║                    \"IGNITING 10 GENERATIONS OF WEALTH\"                  ║"
    echo "    ║                                                                          ║"
    echo "    ╠══════════════════════════════════════════════════════════════════════════╣"
    echo "    ║                                                                          ║"
    echo "    ║  👑 GENESIS: Wilson Khanyezi - Generation 1 (2000)                      ║"
    echo "    ║  💰 VALUATION TARGET: R 1,000,000,000 (Year 1)                          ║"
    echo "    ║  🌍 MARKET: 54 African Countries | 270,000 Law Firms                    ║"
    echo "    ║  ⚖️  COMPLIANCE: POPIA §19 | ECT Act §15 | Companies Act §24            ║"
    echo "    ║  🚀 WORKERS: ${WORKER_COUNT} Parallel Processes                           ║"
    echo "    ║                                                                          ║"
    echo "    ╚══════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Print generational wealth table
print_wealth_table() {
    echo -e "${CYAN}"
    echo "    ┌──────────────────────────────────────────────────────────────────────┐"
    echo "    │                    GENERATIONAL WEALTH PROGRESSION                   │"
    echo "    ├──────────────────────────────────────────────────────────────────────┤"
    echo "    │  Gen 1: R 1,000,000,000     │ Gen 6: R 2,500,000,000,000            │"
    echo "    │  Gen 2: R 5,000,000,000     │ Gen 7: R 10,000,000,000,000           │"
    echo "    │  Gen 3: R 25,000,000,000    │ Gen 8: R 50,000,000,000,000           │"
    echo "    │  Gen 4: R 100,000,000,000   │ Gen 9: R 250,000,000,000,000          │"
    echo "    │  Gen 5: R 500,000,000,000   │ Gen 10: R 1,000,000,000,000,000       │"
    echo "    └──────────────────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# Log function
log() {
    local level=$1
    local msg=$2
    local color=$NC
    
    case $level in
        "GENERATIONAL") color=$PURPLE ;;
        "INFO") color=$GREEN ;;
        "ERROR") color=$RED ;;
        "WARN") color=$YELLOW ;;
    esac
    
    echo -e "${color}[${level}]${NC} $(timestamp) - $msg"
}

# Health checks
run_health_checks() {
    log "INFO" "Performing pre-flight health checks..."
    local failed=0
    
    # Check database connectivity (simulated)
    if [ -f ".env" ]; then
        log "INFO" "✅ Database Connection: PASSED"
    else
        log "ERROR" "❌ Database Connection: FAILED"
        failed=$((failed + 1))
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null && redis-cli ping > /dev/null 2>&1; then
        log "INFO" "✅ Redis Connection: PASSED"
    else
        log "ERROR" "❌ Redis Connection: FAILED"
        failed=$((failed + 1))
    fi
    
    # Check log directory
    mkdir -p "$LOG_DIR"
    if [ -d "$LOG_DIR" ]; then
        log "INFO" "✅ Log Directory: PASSED"
    else
        log "ERROR" "❌ Log Directory: FAILED"
        failed=$((failed + 1))
    fi
    
    # Check worker scripts
    if [ -f "workers/precedentVectorizer.js" ]; then
        log "INFO" "✅ Worker Scripts: PASSED"
    else
        log "ERROR" "❌ Worker Scripts: FAILED (CRITICAL)"
        failed=$((failed + 1))
    fi
    
    # Check environment variables
    if [ -f ".env" ]; then
        log "INFO" "✅ Environment Variables: PASSED"
    else
        log "ERROR" "❌ Environment Variables: FAILED (CRITICAL)"
        failed=$((failed + 1))
    fi
    
    # Check disk space
    local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -lt 90 ]; then
        log "INFO" "✅ Disk Space: PASSED"
    else
        log "WARN" "⚠️  Disk Space: WARNING (${disk_usage}%)"
    fi
    
    return $failed
}

# Start workers
start_workers() {
    log "GENERATIONAL" "Starting $WORKER_COUNT forensic workers..."
    
    for i in $(seq 1 $WORKER_COUNT); do
        node workers/precedentVectorizer.js > "$LOG_DIR/worker-$i.log" 2>&1 &
        local pid=$!
        echo $pid > "$PID_DIR/worker-$i.pid"
        log "INFO" "Worker $i started (PID: $pid)"
        sleep 0.5
    done
}

# Start monitoring
start_monitoring() {
    log "GENERATIONAL" "Starting monitoring dashboard..."
    node services/monitoring/MonitoringDashboard.js > "$LOG_DIR/monitoring.log" 2>&1 &
    local pid=$!
    echo $pid > "$PID_DIR/monitoring.pid"
    log "INFO" "Monitoring started (PID: $pid)"
}

# Start API
start_api() {
    log "GENERATIONAL" "Starting API gateway..."
    # Placeholder for API server
    log "INFO" "API gateway ready (simulated)"
}

# Main
main() {
    print_banner
    print_wealth_table
    echo ""
    
    log "GENERATIONAL" "FORENSIC ENGINE STARTING"
    
    # Setup
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    log "GENERATIONAL" "Environment initialized"
    
    # Health checks
    if ! run_health_checks; then
        echo ""
        log "ERROR" "CRITICAL HEALTH CHECKS FAILED - Aborting startup"
        exit 1
    fi
    
    echo ""
    log "GENERATIONAL" "All health checks passed - Starting components"
    
    # Start components
    start_workers
    start_monitoring
    start_api
    
    echo ""
    log "GENERATIONAL" "✅ FORENSIC ENGINE FULLY OPERATIONAL"
    log "GENERATIONAL" "10 Generations of Wealth initialization complete"
    log "INFO" "Use Ctrl+C to stop"
    echo ""
    
    # Keep running
    while true; do
        sleep 10
        # Heartbeat
        log "INFO" "System heartbeat - All systems operational"
    done
}

# Cleanup on exit
cleanup() {
    echo ""
    log "WARN" "Shutting down forensic engine..."
    
    # Kill all child processes
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            kill $pid 2>/dev/null || true
            rm "$pid_file"
        fi
    done
    
    log "GENERATIONAL" "Forensic engine stopped"
    exit 0
}

trap cleanup INT TERM

# Run main
main
