#!/bin/bash

echo "📦 Installing missing dependencies for WILSY OS"

# Worker dependencies
npm install --save bullmq agenda node-cron
npm install --save natural stopword compromise
npm install --save luxon

# Development dependencies
npm install --save-dev eslint-plugin-import

echo "✅ Dependencies installed"
