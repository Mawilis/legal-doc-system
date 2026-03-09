#!/bin/bash
# ============================================================================
# WILSY OS 2050 - ONE-CLICK SETUP SCRIPT
# ============================================================================

echo "🏛️ WILSY OS 2050 - One-Click Setup"
echo "===================================="

# Create directory structure
echo "📁 Creating directories..."
mkdir -p {ssl,config,data/{audit-logs,forensic-evidence,reports,models}}
mkdir -p server/{logs,data,test-results,tmp}

# Set permissions
echo "🔒 Setting permissions..."
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

# Create SSL directory with placeholder
touch ssl/.gitkeep

# Install dependencies
echo "📦 Installing dependencies..."
cd server
npm install
cd ..

# Run validation
echo "✅ Running validation..."
./validate-env.sh

# Run production readiness check
echo "📊 Running production readiness check..."
./production-ready.sh

echo ""
echo "===================================="
echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Copy server/.env.template to server/.env.production"
echo "2. Fill in your production values"
echo "3. Run ./deploy-prod.sh to deploy"
echo "===================================="
