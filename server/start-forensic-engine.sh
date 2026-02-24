#!/bin/bash
# ============================================================================
# WILSY OS: QUANTUM FORENSIC ENGINE LAUNCHER
# ============================================================================
#
# ██╗ ██╗██╗██╗ ███████╗██╗ ██╗ ██████╗ ███████╗
# ██║ ██║██║██║ ██╔════╝╚██╗ ██╔╝ ██╔══██╗██╔════╝
# ██║ █╗ ██║██║██║ ███████╗ ╚████╔╝ ██████╔╝███████╗
# ██║███╗██║██║██║ ╚════██║ ╚██╔╝ ██╔══██╗╚════██║
# ╚███╔███╔╝██║███████╗███████║ ██║ ██║ ██║███████║
# ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝ ╚═╝ ╚═╝ ╚═╝╚══════╝
#
# ███████╗██╗███╗ ██╗ █████╗ ██╗ ███████╗███╗ ██╗ ██████╗ ██╗███╗ ██╗███████╗
# ██╔════╝██║████╗ ██║██╔══██╗██║ ██╔════╝████╗ ██║██╔════╝ ██║████╗ ██║██╔════╝
# █████╗ ██║██╔██╗ ██║███████║██║ █████╗ ██╔██╗ ██║██║ ███╗██║██╔██╗ ██║█████╗
# ██╔══╝ ██║██║╚██╗██║██╔══██║██║ ██╔══╝ ██║╚██╗██║██║ ██║██║██║╚██╗██║██╔══╝
# ██║ ██║██║ ╚████║██║ ██║███████╗ ███████╗██║ ╚████║╚██████╔╝██║██║ ╚████║███████╗
# ╚═╝ ╚═╝╚═╝ ╚═══╝╚═╝ ╚═╝╚══════╝ ╚══════╝╚═╝ ╚═══╝ ╚═════╝ ╚═╝╚═╝ ╚═══╝╚══════╝
#
# ============================================================================
# QUANTUM-GRADE ORCHESTRATION FOR 100M+ USER SCALE
# ============================================================================
set -euo pipefail
IFS=$'\n\t'
# ----------------------------------------------------------------------------
# QUANTUM CONSTANTS
# ----------------------------------------------------------------------------
readonly SCRIPT_VERSION="42.0.0"
readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
readonly TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
readonly START_TIME=$(date +%s)
# Component configuration
readonly WORKER_COUNT=4
readonly HEALTH_CHECK_TIMEOUT=30
readonly HEALTH_CHECK_INTERVAL=2
# Ports
readonly API_PORT=9095
readonly INVESTOR_PORT=9096
readonly METRICS_PORT=9090
readonly REDIS_PORT=6379
# Paths
readonly LOG_DIR="${SCRIPT_DIR}/logs"
readonly PID_DIR="${SCRIPT_DIR}/.pids"
readonly MODEL_DIR="${SCRIPT_DIR}/models"
# ----------------------------------------------------------------------------
# COLOR CODES
# ----------------------------------------------------------------------------
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'
# ----------------------------------------------------------------------------
# LOGGING FUNCTIONS
# ----------------------------------------------------------------------------
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}
log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}
log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}
log_metric() {
    echo -e "${PURPLE}[METRIC]${NC} $1: ${WHITE}$2${NC}"
}
log_investor() {
    echo -e "${BLUE}[INVESTOR]${NC} $1"
}
print_banner() {
    clear
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════════════════════╗
║ ║
║ ██╗ ██╗██╗██╗ ███████╗██╗ ██╗ ██████╗ ███████╗ ║
║ ██║ ██║██║██║ ██╔════╝╚██╗ ██╔╝ ██╔══██╗██╔════╝ ║
║ ██║ █╗ ██║██║██║ ███████╗ ╚████╔╝ ██████╔╝███████╗ ║
║ ██║███╗██║██║██║ ╚════██║ ╚██╔╝ ██╔══██╗╚════██║ ║
║ ╚███╔███╔╝██║███████╗███████║ ██║ ██║ ██║███████║ ║
║ ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝ ╚═╝ ╚═╝ ╚═╝╚══════╝ ║
║ ║
║ QUANTUM LAUNCH ORCHESTRATOR ║
║ Designed for 100M+ User Scale ║
║ v42.0.0 ║
║ ║
╚══════════════════════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    echo ""
    log_info "Initializing Wilsy OS Quantum Engine"
    log_info "Version: ${SCRIPT_VERSION} | PID: $$"
    echo ""
}
# ----------------------------------------------------------------------------
# VALIDATION FUNCTIONS
# ----------------------------------------------------------------------------
validate_node() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 2
    fi
   
    local node_version=$(node -v | cut -d'v' -f2)
    log_info "Node.js $node_version detected"
}
validate_redis() {
    if ! command -v redis-cli &> /dev/null; then
        log_error "Redis CLI not installed"
        exit 1
    fi
   
    if ! redis-cli ping > /dev/null 2>&1; then
        log_error "Redis is not running"
        exit 1
    fi
   
    local redis_version=$(redis-cli info server | grep redis_version | cut -d':' -f2 | tr -d '\r' | xargs)
    log_info "Redis $redis_version connected"
}
# ----------------------------------------------------------------------------
# PROCESS MANAGEMENT
# ----------------------------------------------------------------------------
setup_environment() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    rm -f "$PID_DIR"/*.pid 2>/dev/null || true
    log_info "Environment initialized"
}
cleanup_processes() {
    log_info "Cleaning up existing processes"
    pkill -f "precedentVectorizer" 2>/dev/null || true
    pkill -f "MonitoringDashboard" 2>/dev/null || true
    pkill -f "server.js" 2>/dev/null || true
    sleep 2
}
start_workers() {
    log_info "Starting $WORKER_COUNT neural workers"
   
    for i in $(seq 1 $WORKER_COUNT); do
        node workers/precedentVectorizer.js \
            > "$LOG_DIR/worker-$i.log" \
            2> "$LOG_DIR/worker-$i.error.log" &
        local pid=$!
        echo $pid > "$PID_DIR/worker-$i.pid"
        log_info "Worker $i started (PID: $pid)"
        sleep 1
    done
}
start_monitoring() {
    log_info "Starting monitoring service"
   
    if [[ ! -f "services/monitoring/MonitoringDashboard.js" ]]; then
        log_warn "Monitoring dashboard not found - skipping"
        return 0
    fi
   
    node services/monitoring/MonitoringDashboard.js \
        > "$LOG_DIR/monitoring.log" \
        2> "$LOG_DIR/monitoring.error.log" &
    local pid=$!
    echo $pid > "$PID_DIR/monitoring.pid"
    log_info "Monitoring started (PID: $pid)"
}
start_api() {
    log_info "Starting API gateway"
   
    if [[ ! -f "server.js" ]]; then
        log_error "server.js not found"
        return 1
    fi
   
    node server.js \
        > "$LOG_DIR/api.log" \
        2> "$LOG_DIR/api.error.log" &
    local pid=$!
    echo $pid > "$PID_DIR/api.pid"
    log_info "API gateway started (PID: $pid)"
}
# ----------------------------------------------------------------------------
# HEALTH CHECKS
# ----------------------------------------------------------------------------
check_workers() {
    local running=0
    for i in $(seq 1 $WORKER_COUNT); do
        if [[ -f "$PID_DIR/worker-$i.pid" ]]; then
            local pid=$(cat "$PID_DIR/worker-$i.pid" 2>/dev/null)
            if kill -0 $pid 2>/dev/null; then
                running=$((running + 1))
            fi
        fi
    done
    echo $running
}
check_api() {
    if [[ -f "$PID_DIR/api.pid" ]]; then
        local pid=$(cat "$PID_DIR/api.pid" 2>/dev/null)
        if kill -0 $pid 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}
wait_for_healthy() {
    local timeout=$HEALTH_CHECK_TIMEOUT
    local interval=$HEALTH_CHECK_INTERVAL
    local elapsed=0
   
    log_info "Waiting for system to become healthy..."
   
    while [[ $elapsed -lt $timeout ]]; do
        local workers=$(check_workers)
        if [[ $workers -eq $WORKER_COUNT ]] && check_api; then
            log_info "System healthy after ${elapsed}s"
            return 0
        fi
        sleep $interval
        elapsed=$((elapsed + interval))
    done
   
    log_error "System failed to become healthy"
    return 5
}
# ----------------------------------------------------------------------------
# DISPLAY FUNCTIONS
# ----------------------------------------------------------------------------
display_status() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE} SYSTEM STATUS${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
   
    printf " %-20s ${CYAN}%s${NC}\n" "API Gateway:" "Port $API_PORT"
    printf " %-20s ${CYAN}%s${NC}\n" "Investor API:" "Port $INVESTOR_PORT"
    printf " %-20s ${CYAN}%s${NC}\n" "Workers:" "$(check_workers)/$WORKER_COUNT running"
    printf " %-20s ${CYAN}%s${NC}\n" "Redis:" "Port $REDIS_PORT"
    echo ""
}
display_commands() {
    echo -e "${BLUE}Commands:${NC}"
    echo " tail -f $LOG_DIR/api.log # Watch API logs"
    echo " tail -f $LOG_DIR/worker-1.log # Watch worker logs"
    echo " curl http://localhost:$API_PORT/api/v1/health # Health check"
    echo " ./shutdown-forensic-engine.sh # Stop services"
    echo ""
}
# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
main() {
    print_banner
   
    log_info "Phase 1: Validating environment"
    validate_node
    validate_redis
    echo ""
   
    log_info "Phase 2: Setting up environment"
    setup_environment
    cleanup_processes
    echo ""
   
    log_info "Phase 3: Starting components"
    start_workers
    echo ""
    start_monitoring
    echo ""
    start_api
    echo ""
   
    log_info "Phase 4: Health checks"
    if ! wait_for_healthy; then
        exit 5
    fi
    echo ""
   
    display_status
    display_commands
   
    log_info "Wilsy OS initialization complete"
    log_metric "Startup Time" "$(($(date +%s) - START_TIME))s"
    echo ""
   
    if [[ "${1:-}" == "--foreground" ]]; then
        log_warn "Running in foreground. Press Ctrl+C to stop."
        wait
    else
        log_info "Wilsy OS running in background"
        log_info "Use './shutdown-forensic-engine.sh' to stop"
        echo ""
    fi
    exit 0
}
trap 'log_warn "Interrupted"; exit 130' INT TERM
main "$@"
