#!/bin/bash

# Legal Doc System - Test Suite Setup Script
# POPIA-compliant test environment configuration

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Legal Doc System - Forensic Test Suite Setup                 ║"
echo "║  POPIA Compliance | SOC2 Auditability | R12M Risk Elimination ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Create directory structure
echo "📁 Creating test directories..."
mkdir -p /Users/wilsonkhanyezi/legal-doc-system/tests/client
mkdir -p /Users/wilsonkhanyezi/legal-doc-system/tests/evidence
mkdir -p /Users/wilsonkhanyezi/legal-doc-system/tests/utils
mkdir -p /Users/wilsonkhanyezi/legal-doc-system/tests/fixtures

# Install dependencies
echo "📦 Installing test dependencies..."
cd /Users/wilsonkhanyezi/legal-doc-system

# Update package.json with all required dependencies
cat > package.json <<'INNEREOF'
{
  "name": "legal-doc-system",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "test": "NODE_OPTIONS='--experimental-specifier-resolution=node' mocha --require jsdom-global/register 'tests/**/*.test.js' --exit --timeout 60000",
    "test:client": "NODE_OPTIONS='--experimental-specifier-resolution=node' mocha --require jsdom-global/register 'tests/client/**/*.test.js' --exit --timeout 60000",
    "test:evidence": "cd tests/evidence && for f in *.json; do echo \"Verifying $f\"; jq -r '.auditHash' $f; done",
    "pretest": "npm install",
    "clean:evidence": "rm -f tests/evidence/*.json"
  },
  "devDependencies": {
    "chai": "^5.1.0",
    "jsdom": "^24.0.0",
    "jsdom-global": "^3.0.2",
    "mocha": "^10.3.0",
    "sinon": "^17.0.1",
    "@testing-library/react": "^15.0.2",
    "@testing-library/react-hooks": "^8.0.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "jq": "^1.7.2"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
INNEREOF

# Install dependencies
echo "🔄 Running npm install..."
npm install --silent

# Create mocha config
cat > .mocharc.json <<'INNEREOF'
{
  "extension": ["js"],
  "spec": ["tests/**/*.test.js"],
  "require": ["jsdom-global/register"],
  "timeout": 60000,
  "exit": true,
  "recursive": true,
  "reporter": "spec"
}
INNEREOF

echo "✅ Setup complete! Run 'npm run test:client' to execute tests."
