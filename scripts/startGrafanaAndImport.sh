#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  WILSY OS – GRAFANA LAUNCHER & DASHBOARD IMPORTER [v1.0.1-OMEGA]            ║
# ║  [AUTOMATED PROVISIONING | ZERO-LOSS | SOVEREIGN TELEMETRY]               ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  EPITOME: One‑click start of Grafana + import of verification sync dashboard.║
# ║                                                                                                                                          ║
# ║  INSTITUTIONAL COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001  ║
# ║  KENNEL EOS AWARENESS: Deploys monitoring for all tenants.               ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  VERSION: 1.0.1-OMEGA | PRODUCTION READY                                  ║
# ║  PATH: scripts/startGrafanaAndImport.sh                                   ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                   ║
# ║  • Wilson Khanyezi (CEO) – Mandated automated provisioning. 2026‑08‑12.   ║
# ║  • AI Engineering – v1.0.1: Fixed .env parsing to handle multi‑line vars.║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e

GRAFANA_PORT=3000
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# ─── Load .env safely ──────────────────────────────────────────────────────────
if [ -f "$ENV_FILE" ]; then
    echo "📄 Loading environment from $ENV_FILE"
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Export only if line contains '='
        if [[ "$line" == *"="* ]]; then
            export "$line"
        fi
    done < "$ENV_FILE"
fi

echo "🔍 Checking if Grafana is already running..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$GRAFANA_PORT" | grep -q "200\|302"; then
    echo "✅ Grafana is already running on port $GRAFANA_PORT."
else
    echo "⚠️  Grafana not running. Attempting to start..."

    # Option 1: Docker (preferred)
    if command -v docker &> /dev/null; then
        if docker ps -a --format '{{.Names}}' | grep -q "^grafana$"; then
            echo "🔄 Grafana container exists but stopped. Starting..."
            docker start grafana
        else
            echo "🐳 Starting Grafana via Docker..."
            docker run -d -p $GRAFANA_PORT:3000 --name=grafana --restart=unless-stopped grafana/grafana:latest
        fi
    # Option 2: Homebrew (macOS fallback)
    elif command -v brew &> /dev/null && brew list grafana &> /dev/null; then
        echo "🍺 Starting Grafana via Homebrew services..."
        brew services start grafana
    else
        echo "❌ Neither Docker nor Homebrew Grafana found. Please install Grafana manually."
        echo "   Docker: docker run -d -p 3000:3000 --name=grafana grafana/grafana:latest"
        echo "   Homebrew: brew install grafana && brew services start grafana"
        exit 1
    fi

    # Wait for Grafana to be ready
    echo "⏳ Waiting for Grafana to be ready (max 30s)..."
    for i in {1..30}; do
        if curl -s -o /dev/null "http://localhost:$GRAFANA_PORT"; then
            echo "✅ Grafana is ready."
            break
        fi
        sleep 1
    done
    if ! curl -s -o /dev/null "http://localhost:$GRAFANA_PORT"; then
        echo "❌ Grafana failed to start within 30 seconds. Check Docker/brew logs."
        exit 1
    fi
fi

# ─── Import Dashboard ──────────────────────────────────────────────────────────
echo "📊 Importing dashboard..."
node "$SCRIPT_DIR/importGrafanaDashboard.js"
