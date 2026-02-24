#!/bin/bash

# ============================================================================
# WILSY OS: NGINX HEALTH CHECK SCRIPT
# ============================================================================
# This script performs comprehensive health checks on all upstream nodes
# and updates the Nginx configuration if nodes are unhealthy.
#
# Designed for 99.999% uptime with automatic failover
# ============================================================================

set -euo pipefail

# Configuration
NGINX_CONF="/etc/nginx/conf.d/fortress-lb.conf"
BACKUP_CONF="/etc/nginx/conf.d/fortress-lb.conf.bak"
HEALTH_ENDPOINT="/api/v1/sys/health"
HEALTH_SECRET="${INTERNAL_HEALTH_SECRET:-quantum_fortress_secure_probe_2026}"
CHECK_INTERVAL=30
FAILURE_THRESHOLD=3
RECOVERY_THRESHOLD=2
ALERT_WEBHOOK="http://localhost:3000/api/v1/alerts"
INTERNAL_API_KEY="${INTERNAL_API_KEY:-}"

# Node definitions by region
AFRICA_NODES=(
    "10.0.1.10"
    "10.0.1.11"
    "10.0.1.12"
    "10.0.1.20"
    "10.0.1.21"
)

EUROPE_NODES=(
    "10.0.2.10"
    "10.0.2.11"
    "10.0.2.12"
    "10.0.2.20"
    "10.0.2.21"
)

US_EAST_NODES=(
    "10.0.3.10"
    "10.0.3.11"
    "10.0.3.12"
    "10.0.3.20"
    "10.0.3.21"
)

ASIA_NODES=(
    "10.0.4.10"
    "10.0.4.11"
    "10.0.4.12"
    "10.0.4.20"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

log_metric() {
    echo -e "${PURPLE}[METRIC]${NC} $1: ${CYAN}$2${NC}"
}

# ============================================================================
# HEALTH CHECK FUNCTIONS
# ============================================================================

check_node() {
    local node=$1
    local port=${2:-3000}
    local region=$3
    
    log_debug "Checking node $node:$port in $region"
    
    # Try health endpoint
    local response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "x-health-secret: $HEALTH_SECRET" \
        -H "x-region: $region" \
        --connect-timeout 5 \
        --max-time 10 \
        "http://$node:$port$HEALTH_ENDPOINT" 2>/dev/null || echo "000")
    
    if [[ "$response" == "200" ]]; then
        return 0
    else
        return 1
    fi
}

check_node_detailed() {
    local node=$1
    local port=${2:-3000}
    local region=$3
    
    # Get detailed health info
    local health_json=$(curl -s \
        -H "x-health-secret: $HEALTH_SECRET" \
        -H "x-region: $region" \
        --connect-timeout 5 \
        --max-time 10 \
        "http://$node:$port$HEALTH_ENDPOINT?depth=standard" 2>/dev/null || echo "{}")
    
    echo "$health_json"
}

get_node_metrics() {
    local node=$1
    local port=${2:-3000}
    
    # Get Prometheus metrics
    local metrics=$(curl -s \
        --connect-timeout 3 \
        --max-time 5 \
        "http://$node:$port/metrics" 2>/dev/null || echo "")
    
    echo "$metrics"
}

# ============================================================================
# NODE FAILURE HANDLING
# ============================================================================

handle_node_failure() {
    local node=$1
    local region=$2
    local port=${3:-3000}
    local failure_count_file="/tmp/nginx_fail_${node}.count"
    local current_failures=0
    
    if [[ -f "$failure_count_file" ]]; then
        current_failures=$(cat "$failure_count_file")
    fi
    
    current_failures=$((current_failures + 1))
    echo "$current_failures" > "$failure_count_file"
    
    if [[ $current_failures -ge $FAILURE_THRESHOLD ]]; then
        log_error "Node $node:$port in $region has failed $current_failures times - marking as DOWN"
        
        # Create backup of config
        cp "$NGINX_CONF" "$BACKUP_CONF"
        
        # Comment out the failed node in config
        sed -i.bak "s/^[[:space:]]*server $node:$port/# server $node:$port # FAILED - $(date)/" "$NGINX_CONF"
        
        # Test and reload nginx
        if nginx -t; then
            systemctl reload nginx
            log_success "Nginx reloaded successfully - node $node removed"
            
            # Log the failure
            log_metric "Node Failure" "$node in $region"
        else
            log_error "Nginx configuration test failed - restoring backup"
            cp "$BACKUP_CONF" "$NGINX_CONF"
            nginx -t && systemctl reload nginx
        fi
        
        # Send alert
        if [[ -n "$INTERNAL_API_KEY" ]]; then
            curl -X POST -H "Content-Type: application/json" \
                -H "Authorization: Bearer $INTERNAL_API_KEY" \
                -d "{
                    \"title\":\"Node Failure - $region\",
                    \"message\":\"Node $node:$port in $region marked as DOWN after $current_failures failures\",
                    \"severity\":\"critical\",
                    \"source\":\"health-check\",
                    \"details\":{
                        \"node\":\"$node\",
                        \"port\":$port,
                        \"region\":\"$region\",
                        \"failureCount\":$current_failures,
                        \"threshold\":$FAILURE_THRESHOLD,
                        \"timestamp\":\"$(date -Iseconds)\"
                    }
                }" \
                "$ALERT_WEBHOOK" 2>/dev/null || log_warn "Failed to send alert"
        fi
    else
        log_warn "Node $node:$port in $region failed (attempt $current_failures/$FAILURE_THRESHOLD)"
        
        # Send warning alert
        if [[ -n "$INTERNAL_API_KEY" ]] && [[ $current_failures -eq 2 ]]; then
            curl -X POST -H "Content-Type: application/json" \
                -H "Authorization: Bearer $INTERNAL_API_KEY" \
                -d "{
                    \"title\":\"Node Unstable - $region\",
                    \"message\":\"Node $node:$port in $region has failed $current_failures times\",
                    \"severity\":\"warning\",
                    \"source\":\"health-check\",
                    \"details\":{
                        \"node\":\"$node\",
                        \"port\":$port,
                        \"region\":\"$region\",
                        \"failureCount\":$current_failures,
                        \"threshold\":$FAILURE_THRESHOLD
                    }
                }" \
                "$ALERT_WEBHOOK" 2>/dev/null || true
        fi
    fi
}

# ============================================================================
# NODE RECOVERY HANDLING
# ============================================================================

handle_node_recovery() {
    local node=$1
    local region=$2
    local port=${3:-3000}
    local recovery_count_file="/tmp/nginx_recovery_${node}.count"
    local failure_count_file="/tmp/nginx_fail_${node}.count"
    local current_recoveries=0
    
    # Check if node was previously failed
    if [[ -f "$failure_count_file" ]]; then
        rm -f "$failure_count_file"
    fi
    
    if [[ -f "$recovery_count_file" ]]; then
        current_recoveries=$(cat "$recovery_count_file")
    fi
    
    current_recoveries=$((current_recoveries + 1))
    echo "$current_recoveries" > "$recovery_count_file"
    
    if [[ $current_recoveries -ge $RECOVERY_THRESHOLD ]]; then
        log_success "Node $node:$port in $region has recovered - adding back to load balancer"
        
        # Check if node is commented out in config
        if grep -q "^#.*server $node:$port" "$NGINX_CONF"; then
            # Create backup
            cp "$NGINX_CONF" "$BACKUP_CONF"
            
            # Uncomment the node
            sed -i.bak "s/^#.*server $node:$port/server $node:$port/" "$NGINX_CONF"
            
            # Test and reload nginx
            if nginx -t; then
                systemctl reload nginx
                log_success "Nginx reloaded successfully - node $node restored"
                
                # Clean up counters
                rm -f "$recovery_count_file"
                rm -f "$failure_count_file" 2>/dev/null || true
                
                # Log recovery
                log_metric "Node Recovery" "$node in $region"
                
                # Send recovery alert
                if [[ -n "$INTERNAL_API_KEY" ]]; then
                    curl -X POST -H "Content-Type: application/json" \
                        -H "Authorization: Bearer $INTERNAL_API_KEY" \
                        -d "{
                            \"title\":\"Node Recovered - $region\",
                            \"message\":\"Node $node:$port in $region has recovered and been restored\",
                            \"severity\":\"info\",
                            \"source\":\"health-check\",
                            \"details\":{
                                \"node\":\"$node\",
                                \"port\":$port,
                                \"region\":\"$region\",
                                \"timestamp\":\"$(date -Iseconds)\"
                            }
                        }" \
                        "$ALERT_WEBHOOK" 2>/dev/null || log_warn "Failed to send recovery alert"
                fi
            else
                log_error "Nginx configuration test failed after recovery - manual intervention required"
            fi
        fi
    else
        log_info "Node $node:$port in $region recovered (attempt $current_recoveries/$RECOVERY_THRESHOLD)"
    fi
}

# ============================================================================
# REGION HEALTH CHECK
# ============================================================================

check_region() {
    local region=$1
    local port=${2:-3000}
    local -n nodes_ref="$region"
    local healthy_count=0
    local total_count=${#nodes_ref[@]}
    
    log_info "Checking region $region ($total_count nodes)"
    
    for node in "${nodes_ref[@]}"; do
        echo -n "  Checking $node... "
        if check_node "$node" "$port" "$region"; then
            echo -e "${GREEN}HEALTHY${NC}"
            handle_node_recovery "$node" "$region" "$port"
            healthy_count=$((healthy_count + 1))
        else
            echo -e "${RED}UNHEALTHY${NC}"
            handle_node_failure "$node" "$region" "$port"
            
            # Get detailed health info for debugging (first failure only)
            if [[ $healthy_count -eq 0 ]]; then
                local health_info=$(check_node_detailed "$node" "$port" "$region")
                if [[ "$health_info" != "{}" ]]; then
                    log_debug "    Health details: $health_info"
                fi
            fi
        fi
    done
    
    local health_percent=$((healthy_count * 100 / total_count))
    log_info "Region $region health: $healthy_count/$total_count nodes healthy ($health_percent%)"
    log_metric "Region $region Health" "$health_percent%"
    
    # Alert if region health is below threshold
    if [[ $health_percent -lt 50 ]]; then
        log_error "Region $region critically degraded - only $health_percent% healthy"
        
        if [[ -n "$INTERNAL_API_KEY" ]]; then
            curl -X POST -H "Content-Type: application/json" \
                -H "Authorization: Bearer $INTERNAL_API_KEY" \
                -d "{
                    \"title\":\"Region Degraded - $region\",
                    \"message\":\"Region $region has only $healthy_count/$total_count healthy nodes\",
                    \"severity\":\"error\",
                    \"source\":\"health-check\",
                    \"details\":{
                        \"region\":\"$region\",
                        \"healthy\":$healthy_count,
                        \"total\":$total_count,
                        \"healthPercent\":$health_percent,
                        \"timestamp\":\"$(date -Iseconds)\"
                    }
                }" \
                "$ALERT_WEBHOOK" 2>/dev/null || true
        fi
    elif [[ $health_percent -lt 80 ]]; then
        log_warn "Region $region degraded - $health_percent% healthy"
    fi
    
    return $healthy_count
}

# ============================================================================
# GLOBAL HEALTH CHECK
# ============================================================================

check_global_health() {
    log_info "="
    log_info "GLOBAL HEALTH CHECK - $(date)"
    log_info "="
    
    local total_healthy=0
    local total_nodes=0
    
    # Check each region
    check_region "AFRICA_NODES" 3000
    local africa_healthy=$?
    total_healthy=$((total_healthy + africa_healthy))
    total_nodes=$((total_nodes + ${#AFRICA_NODES[@]}))
    
    check_region "EUROPE_NODES" 3000
    local europe_healthy=$?
    total_healthy=$((total_healthy + europe_healthy))
    total_nodes=$((total_nodes + ${#EUROPE_NODES[@]}))
    
    check_region "US_EAST_NODES" 3000
    local useast_healthy=$?
    total_healthy=$((total_healthy + useast_healthy))
    total_nodes=$((total_nodes + ${#US_EAST_NODES[@]}))
    
    check_region "ASIA_NODES" 3000
    local asia_healthy=$?
    total_healthy=$((total_healthy + asia_healthy))
    total_nodes=$((total_nodes + ${#ASIA_NODES[@]}))
    
    # Calculate global health
    local global_health_percent=$((total_healthy * 100 / total_nodes))
    
    log_info "="
    log_info "GLOBAL HEALTH SUMMARY"
    log_info "="
    log_metric "Global Health" "$global_health_percent%"
    log_metric "Healthy Nodes" "$total_healthy/$total_nodes"
    
    # Region breakdown
    log_info ""
    log_info "Region Breakdown:"
    printf "  %-15s %3d/%-3d (%3d%%)\n" "Africa" "$africa_healthy" "${#AFRICA_NODES[@]}" "$((africa_healthy * 100 / ${#AFRICA_NODES[@]}))"
    printf "  %-15s %3d/%-3d (%3d%%)\n" "Europe" "$europe_healthy" "${#EUROPE_NODES[@]}" "$((europe_healthy * 100 / ${#EUROPE_NODES[@]}))"
    printf "  %-15s %3d/%-3d (%3d%%)\n" "US East" "$useast_healthy" "${#US_EAST_NODES[@]}" "$((useast_healthy * 100 / ${#US_EAST_NODES[@]}))"
    printf "  %-15s %3d/%-3d (%3d%%)\n" "Asia" "$asia_healthy" "${#ASIA_NODES[@]}" "$((asia_healthy * 100 / ${#ASIA_NODES[@]}))"
    
    # Send global health alert if critical
    if [[ $global_health_percent -lt 60 ]]; then
        log_error "GLOBAL HEALTH CRITICAL - $global_health_percent%"
        
        if [[ -n "$INTERNAL_API_KEY" ]]; then
            curl -X POST -H "Content-Type: application/json" \
                -H "Authorization: Bearer $INTERNAL_API_KEY" \
                -d "{
                    \"title\":\"Global Health Critical\",
                    \"message\":\"Global health is at $global_health_percent% with only $total_healthy/$total_nodes nodes healthy\",
                    \"severity\":\"critical\",
                    \"source\":\"health-check\",
                    \"details\":{
                        \"globalHealth\":$global_health_percent,
                        \"healthyNodes\":$total_healthy,
                        \"totalNodes\":$total_nodes,
                        \"regions\":{
                            \"africa\":$africa_healthy,
                            \"europe\":$europe_healthy,
                            \"useast\":$useast_healthy,
                            \"asia\":$asia_healthy
                        },
                        \"timestamp\":\"$(date -Iseconds)\"
                    }
                }" \
                "$ALERT_WEBHOOK" 2>/dev/null || true
        fi
    fi
    
    # Write status file for monitoring
    cat > /tmp/nginx_health_status.json << EOF
{
    "timestamp": "$(date -Iseconds)",
    "globalHealth": $global_health_percent,
    "healthyNodes": $total_healthy,
    "totalNodes": $total_nodes,
    "regions": {
        "africa": {
            "healthy": $africa_healthy,
            "total": ${#AFRICA_NODES[@]},
            "percentage": $((africa_healthy * 100 / ${#AFRICA_NODES[@]}))
        },
        "europe": {
            "healthy": $europe_healthy,
            "total": ${#EUROPE_NODES[@]},
            "percentage": $((europe_healthy * 100 / ${#EUROPE_NODES[@]}))
        },
        "useast": {
            "healthy": $useast_healthy,
            "total": ${#US_EAST_NODES[@]},
            "percentage": $((useast_healthy * 100 / ${#US_EAST_NODES[@]}))
        },
        "asia": {
            "healthy": $asia_healthy,
            "total": ${#ASIA_NODES[@]},
            "percentage": $((asia_healthy * 100 / ${#ASIA_NODES[@]}))
        }
    }
}
EOF
    
    log_success "Health status written to /tmp/nginx_health_status.json"
}

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

collect_performance_metrics() {
    log_info "Collecting performance metrics..."
    
    # Get connection stats
    local connections=$(curl -s http://localhost/nginx_status 2>/dev/null | grep "Active connections" | awk '{print $3}' || echo "0")
    local accepts=$(curl -s http://localhost/nginx_status 2>/dev/null | grep "server accepts" | awk '{print $2}' || echo "0")
    local handled=$(curl -s http://localhost/nginx_status 2>/dev/null | grep "server accepts" | awk '{print $3}' || echo "0")
    local requests=$(curl -s http://localhost/nginx_status 2>/dev/null | grep "server accepts" | awk '{print $4}' || echo "0")
    
    log_metric "Active Connections" "$connections"
    log_metric "Total Accepts" "$accepts"
    log_metric "Total Handled" "$handled"
    log_metric "Total Requests" "$requests"
    
    # Write metrics to file
    cat >> /tmp/nginx_metrics.log << EOF
$(date -Iseconds),$connections,$accepts,$handled,$requests
EOF
    
    # Keep only last 1000 lines
    tail -n 1000 /tmp/nginx_metrics.log > /tmp/nginx_metrics.log.tmp
    mv /tmp/nginx_metrics.log.tmp /tmp/nginx_metrics.log
}

# ============================================================================
# CLEANUP OLD COUNTERS
# ============================================================================

cleanup_counters() {
    log_debug "Cleaning up old counter files"
    
    # Remove counters older than 1 hour
    find /tmp -name "nginx_*.count" -type f -mmin +60 -delete 2>/dev/null || true
    find /tmp -name "nginx_*.recovery" -type f -mmin +60 -delete 2>/dev/null || true
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    local interval=${1:-$CHECK_INTERVAL}
    
    log_info "Starting Wilsy OS Nginx Health Checker"
    log_info "Check interval: ${interval}s"
    log_info "Failure threshold: $FAILURE_THRESHOLD"
    log_info "Recovery threshold: $RECOVERY_THRESHOLD"
    log_info "Health endpoint: $HEALTH_ENDPOINT"
    
    # Validate health secret
    if [[ -z "$HEALTH_SECRET" ]]; then
        log_error "HEALTH_SECRET not set"
        exit 1
    fi
    
    # Run once immediately
    check_global_health
    collect_performance_metrics
    
    # Continuous monitoring loop
    while true; do
        sleep "$interval"
        check_global_health
        collect_performance_metrics
        cleanup_counters
    done
}

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

case "${1:-}" in
    start)
        shift
        main "$@"
        ;;
    check)
        # Run single check
        check_global_health
        collect_performance_metrics
        ;;
    status)
        # Show last health status
        if [[ -f /tmp/nginx_health_status.json ]]; then
            cat /tmp/nginx_health_status.json | jq '.'
        else
            log_error "No health status file found"
            exit 1
        fi
        ;;
    metrics)
        # Show performance metrics
        if [[ -f /tmp/nginx_metrics.log ]]; then
            echo "Time,Connections,Accepts,Handled,Requests"
            tail -20 /tmp/nginx_metrics.log
        else
            log_error "No metrics file found"
            exit 1
        fi
        ;;
    reset)
        # Reset all counters
        rm -f /tmp/nginx_*.count /tmp/nginx_*.recovery 2>/dev/null || true
        log_success "All counters reset"
        ;;
    help|*)
        echo "Wilsy OS Nginx Health Checker"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start [interval]  Start continuous monitoring"
        echo "  check             Run single health check"
        echo "  status            Show last health status"
        echo "  metrics           Show performance metrics"
        echo "  reset             Reset all failure counters"
        echo "  help              Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start 60       Check every 60 seconds"
        echo "  $0 check          Run once"
        echo "  $0 status         Show status"
        ;;
esac

exit 0