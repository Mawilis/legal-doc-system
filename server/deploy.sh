#!/bin/bash

# WILSY OS: PRODUCTION DEPLOYMENT SCRIPT
# Deploys API, Sentinel, and WebSocket with zero downtime

set -e

echo "🚀 WILSY OS PRODUCTION DEPLOYMENT"
echo "=================================="

# Load environment
source .env.production

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --only=production

# Run tests
echo "🧪 Running test suite..."
npm test

# Build if needed
echo "🔨 Building..."
npm run build --if-present

# Run database migrations
echo "🗄️ Running database migrations..."
npm run migrate --if-present

# Verify sentinel is healthy
echo "🛡️ Verifying Recovery Sentinel..."
node scripts/healthcheck-sentinel.js

# Reload applications with PM2
echo "🔄 Reloading applications..."
pm2 reload ecosystem.config.js

# Verify deployment
echo "✅ Verifying deployment..."
sleep 5
curl -f http://localhost:3000/api/health || exit 1
curl -f http://localhost:3001/health || exit 1

# Check sentinel status
node scripts/check-sentinel-status.js

echo "✅ Deployment complete!"
echo "📊 Monitor with: pm2 monit"
echo "📝 Logs: pm2 logs"
