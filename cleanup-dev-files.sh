#!/bin/bash
# ============================================================================
# WILSY OS 2050 - DEVELOPMENT FILE CLEANUP
# Run this to reset all development files before committing
# ============================================================================

echo "🧹 Cleaning up development files..."

# Reset all debug and fix scripts
git checkout -- \
  server/debug-*.js \
  server/diagnose-*.js \
  server/inspect-*.js \
  server/fix-*.js \
  server/fix-*.sh \
  server/test-*.js \
  2>/dev/null

# Reset model files
git checkout -- server/models/ 2>/dev/null

# Reset quantum metadata
git checkout -- wilsy-os-2050/ 2>/dev/null

# Reset investment suite
git checkout -- WILSY-OS-INVESTMENT-READY/ 2>/dev/null
git checkout -- WILSY-OS-INVESTMENT-SUITE/ 2>/dev/null

echo "✅ Development files cleaned up"
git status
