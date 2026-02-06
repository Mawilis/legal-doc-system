#!/bin/bash
# Wilsy OS Production Monitoring Setup

echo "🛡️  Setting up Wilsy OS Production Monitoring..."

# Create monitoring directory
mkdir -p monitoring/{prometheus,grafana,alerts}

# Prometheus configuration
cat > monitoring/prometheus/prometheus.yml << 'PROMETHEUSEOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'wilsy-api'
    static_configs:
      - targets: ['wilsy-api:3000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
PROMETHEUSEOF

# Grafana datasources
cat > monitoring/grafana/datasources.yml << 'GRAFANAEOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true

  - name: MongoDB
    type: prometheus
    access: proxy
    url: http://prometheus:9090

  - name: Redis
    type: prometheus
    access: proxy
    url: http://prometheus:9090
GRAFANAEOF

# Alert rules
cat > monitoring/alerts/api-alerts.yml << 'ALERTSEOF'
groups:
  - name: wilsy-api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on Wilsy API"
          description: "Error rate is {{ $value }}% for the last 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="wilsy-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Wilsy API is down"
          description: "Service has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 1024
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }} MB"
ALERTSEOF

echo "✅ Monitoring setup complete"
echo "📊 Run with: docker-compose -f docker-compose.monitoring.yml up -d"
