#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - COMPLETE TEST RESET & RUN                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Step 1: Clean everything
echo "🧹 Cleaning up old configurations..."
rm -f babel.config.js babel.config.cjs .babelrc .babelrc.json
rm -rf .mocha-cache node_modules/.cache
echo "✅ Cleanup complete"
echo ""

# Step 2: Create fresh configs
echo "📝 Creating fresh configuration files..."

# Babel config
cat > babel.config.cjs <<'EOFBABEL'
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: { node: 'current' },
      modules: 'commonjs'
    }]
  ]
};
EOFBABEL

# Mocha config
cat > .mocharc.cjs <<'EOFMOCHA'
module.exports = {
  require: ['@babel/register'],
  extension: ['js'],
  spec: ['tests/**/*.test.js'],
  timeout: 30000,
  exit: true,
  recursive: true,
  reporter: 'spec'
};
EOFMOCHA

echo "✅ Configs created"
echo ""

# Step 3: Verify single test file
echo "🧪 Testing single file: tests/models/Case.test.js"
echo "------------------------------------------------"

NODE_OPTIONS='--experimental-vm-modules --no-warnings' \
npx mocha --require @babel/register tests/models/Case.test.js

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "\n✅ SINGLE TEST PASSED!"
    echo ""
    
    # Ask to run all tests
    echo "📊 Run ALL tests? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        echo -e "\n🧪 Running ALL tests...\n"
        echo "------------------------------------------------"
        NODE_OPTIONS='--experimental-vm-modules --no-warnings' \
        npx mocha --require @babel/register 'tests/**/*.test.js'
    fi
else
    echo -e "\n❌ TEST FAILED - Let's debug"
    echo ""
    echo "🔍 Debugging information:"
    echo "Node version: $(node --version)"
    echo "Mocha version: $(npx mocha --version)"
    echo ""
    echo "Checking if file exists:"
    ls -la tests/models/Case.test.js
fi
