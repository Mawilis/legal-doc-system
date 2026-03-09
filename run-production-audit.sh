#!/bin/bash
# ============================================================================
# WILSY OS 2050 - MASTER PRODUCTION AUDIT SCRIPT
# Run: chmod +x run-production-audit.sh && ./run-production-audit.sh
# ============================================================================

set -e

echo "🏛️ WILSY OS 2050 - MASTER PRODUCTION AUDIT"
echo "=================================================="
echo "Started: $(date)"
echo ""

# Create audit directory
AUDIT_DIR="/Users/wilsonkhanyezi/legal-doc-system/audit-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$AUDIT_DIR"
echo "📁 Audit logs: $AUDIT_DIR"
echo ""

# ============================================================================
# SECTION 1: FILE AUDIT
# ============================================================================
echo "📁 FILE AUDIT"
echo "--------------------------------------------------"

# GitHub Actions
echo ""
echo "🔍 GITHUB ACTIONS FILES:"
if [ -d "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows" ]; then
  ls -la "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows/"
  
  for file in /Users/wilsonkhanyezi/legal-doc-system/.github/workflows/*.yml; do
    if [ -f "$file" ]; then
      filename=$(basename "$file")
      size=$(wc -c < "$file" | tr -d ' ')
      lines=$(wc -l < "$file" | tr -d ' ')
      modified=$(stat -f "%Sm" "$file")
      
      # Check YAML syntax
      if yamllint -d relaxed "$file" > /dev/null 2>&1; then
        syntax="✅ Valid"
      else
        syntax="❌ Invalid"
        yamllint -d relaxed "$file" >> "$AUDIT_DIR/yaml-errors.log" 2>&1
      fi
      
      echo "  📄 $filename | Size: $size | Lines: $lines | Modified: $modified | $syntax"
    fi
  done
else
  echo "  ❌ No GitHub Actions workflows found"
fi

# Docker Files
echo ""
echo "🐳 DOCKER FILES:"
ls -la /Users/wilsonkhanyezi/legal-doc-system/Dockerfile* 2>/dev/null || echo "  ❌ No Dockerfiles found"

for file in /Users/wilsonkhanyezi/legal-doc-system/docker-compose*.yml; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    size=$(wc -c < "$file" | tr -d ' ')
    services=$(grep -c "^  [a-zA-Z0-9_-]:" "$file" 2>/dev/null || echo "0")
    
    if docker-compose -f "$file" config > /dev/null 2>&1; then
      syntax="✅ Valid"
    else
      syntax="❌ Invalid"
      docker-compose -f "$file" config >> "$AUDIT_DIR/compose-errors.log" 2>&1
    fi
    
    echo "  📄 $filename | Size: $size | Services: $services | $syntax"
  fi
done

# Kubernetes Files
echo ""
echo "☸️  KUBERNETES FILES:"
ls -la /Users/wilsonkhanyezi/legal-doc-system/*.yaml 2>/dev/null | grep -E 'k8s|kubernetes|deployment|service' || echo "  ❌ No Kubernetes files found"

# Test Files
echo ""
echo "🧪 TEST FILES:"
if [ -d "/Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise" ]; then
  ls -la "/Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise/"
  test_count=$(ls -1 /Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise/*.test.js 2>/dev/null | wc -l | tr -d ' ')
  echo "  📊 Total test files: $test_count"
else
  echo "  ❌ No test files found"
fi

# Configuration Files
echo ""
echo "⚙️  CONFIGURATION FILES:"
ls -la /Users/wilsonkhanyezi/legal-doc-system/server/.env* 2>/dev/null || echo "  ❌ No env files found"
ls -la /Users/wilsonkhanyezi/legal-doc-system/server/.mocharc* 2>/dev/null || echo "  ❌ No mocha config files found"
ls -la /Users/wilsonkhanyezi/legal-doc-system/.yamllint 2>/dev/null || echo "  ❌ No yamllint config found"

# ============================================================================
# SECTION 2: SECURE FILES
# ============================================================================
echo ""
echo "🔒 SECURING FILES AND FOLDERS"
echo "--------------------------------------------------"

# Set base permissions
echo "📁 Setting base permissions..."
find /Users/wilsonkhanyezi/legal-doc-system -type d -exec chmod 755 {} \; 2>/dev/null
find /Users/wilsonkhanyezi/legal-doc-system -type f -exec chmod 644 {} \; 2>/dev/null

# Make scripts executable
echo "🔐 Making scripts executable..."
find /Users/wilsonkhanyezi/legal-doc-system -name "*.sh" -exec chmod 755 {} \; 2>/dev/null
find /Users/wilsonkhanyezi/legal-doc-system -name "*.py" -exec chmod 755 {} \; 2>/dev/null

# Secure sensitive files
echo "🔒 Securing sensitive files..."
chmod 600 /Users/wilsonkhanyezi/legal-doc-system/server/.env* 2>/dev/null
chmod 600 /Users/wilsonkhanyezi/legal-doc-system/server/.env 2>/dev/null
chmod 600 /Users/wilsonkhanyezi/legal-doc-system/server/.env.test 2>/dev/null

# Secure CI/CD files
echo "🔐 Securing CI/CD files..."
chmod 644 /Users/wilsonkhanyezi/legal-doc-system/.github/workflows/*.yml 2>/dev/null

# Verify permissions
echo ""
echo "✅ Permission verification:"
dir_insecure=$(find /Users/wilsonkhanyezi/legal-doc-system -type d -not -perm 755 2>/dev/null | wc -l | tr -d ' ')
script_insecure=$(find /Users/wilsonkhanyezi/legal-doc-system -name "*.sh" -not -perm 755 2>/dev/null | wc -l | tr -d ' ')
env_insecure=$(find /Users/wilsonkhanyezi/legal-doc-system -name ".env*" -not -perm 600 2>/dev/null | wc -l | tr -d ' ')

echo "   Project directories: $dir_insecure insecure"
echo "   Script files: $script_insecure insecure"
echo "   Env files: $env_insecure insecure"

# Fix env files if needed
if [ "$env_insecure" -gt 0 ]; then
  echo "   🔧 Fixing env file permissions..."
  chmod 600 /Users/wilsonkhanyezi/legal-doc-system/server/.env* 2>/dev/null
fi

# ============================================================================
# SECTION 3: PRODUCTION READINESS SCORE
# ============================================================================
echo ""
echo "📊 PRODUCTION READINESS SCORE"
echo "--------------------------------------------------"

SCORE=0
MAX_SCORE=20

# Check GitHub Actions
if [ -d "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows" ]; then
  SCORE=$((SCORE + 2))
  echo "   ✅ GitHub Actions: Configured (+2)"
fi

# Check GitLab CI
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/.gitlab-ci.yml" ]; then
  SCORE=$((SCORE + 2))
  echo "   ✅ GitLab CI: Configured (+2)"
fi

# Check Jenkins
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/Jenkinsfile" ]; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Jenkins: Configured (+2)"
fi

# Check Docker Compose
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/docker-compose.yml" ]; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Docker Compose: Configured (+2)"
fi

# Check Kubernetes
if ls /Users/wilsonkhanyezi/legal-doc-system/*k8s*.yaml 1> /dev/null 2>&1; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Kubernetes: Configured (+2)"
fi

# Check test suite
if [ -d "/Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise" ]; then
  TEST_COUNT=$(ls -1 /Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise/*.test.js 2>/dev/null | wc -l | tr -d ' ')
  if [ "$TEST_COUNT" -ge 5 ]; then
    SCORE=$((SCORE + 2))
    echo "   ✅ Test suite: $TEST_COUNT test files (+2)"
  fi
fi

# Check env files security
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/server/.env.test" ]; then
  PERMS=$(stat -f "%OLp" /Users/wilsonkhanyezi/legal-doc-system/server/.env.test 2>/dev/null)
  if [ "$PERMS" = "600" ]; then
    SCORE=$((SCORE + 2))
    echo "   ✅ Env files: Secure permissions (+2)"
  fi
fi

# Check YAML syntax
YAML_VALID=0
for file in /Users/wilsonkhanyezi/legal-doc-system/.github/workflows/*.yml 2>/dev/null; do
  if yamllint -d relaxed "$file" > /dev/null 2>&1; then
    YAML_VALID=$((YAML_VALID + 1))
  fi
done
if [ "$YAML_VALID" -gt 0 ]; then
  SCORE=$((SCORE + 2))
  echo "   ✅ YAML syntax: $YAML_VALID files valid (+2)"
fi

# Check Docker Compose syntax
if docker-compose -f /Users/wilsonkhanyezi/legal-doc-system/docker-compose.yml config > /dev/null 2>&1; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Docker Compose: Valid syntax (+2)"
fi

# Check for production best practices
if grep -q "healthcheck:" /Users/wilsonkhanyezi/legal-doc-system/docker-compose.yml 2>/dev/null; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Healthchecks: Configured (+2)"
fi

if grep -q "restart:.*unless-stopped" /Users/wilsonkhanyezi/legal-doc-system/docker-compose.yml 2>/dev/null; then
  SCORE=$((SCORE + 2))
  echo "   ✅ Restart policy: Configured (+2)"
fi

echo ""
echo "🏆 FINAL SCORE: $SCORE/$MAX_SCORE"
echo ""

if [ $SCORE -ge 18 ]; then
  echo "🎉 EXCEPTIONAL - Production Ready!"
elif [ $SCORE -ge 14 ]; then
  echo "✅ GOOD - Minor improvements needed"
elif [ $SCORE -ge 10 ]; then
  echo "⚠️  FAIR - Several improvements needed"
else
  echo "❌ CRITICAL - Not production ready"
fi

# ============================================================================
# SECTION 4: SUMMARY REPORT
# ============================================================================
echo ""
echo "📋 PRODUCTION READINESS SUMMARY"
echo "--------------------------------------------------"
{
  echo "WILSY OS 2050 - PRODUCTION AUDIT REPORT"
  echo "========================================"
  echo "Date: $(date)"
  echo "Score: $SCORE/$MAX_SCORE"
  echo ""
  echo "FILES CHECKED:"
  echo "- GitHub Actions: $(ls -1 /Users/wilsonkhanyezi/legal-doc-system/.github/workflows/*.yml 2>/dev/null | wc -l | tr -d ' ') files"
  echo "- Docker Compose: $(ls -1 /Users/wilsonkhanyezi/legal-doc-system/docker-compose*.yml 2>/dev/null | wc -l | tr -d ' ') files"
  echo "- Test Files: $(ls -1 /Users/wilsonkhanyezi/legal-doc-system/server/tests/enterprise/*.test.js 2>/dev/null | wc -l | tr -d ' ') files"
  echo ""
  echo "SECURITY STATUS:"
  echo "- Env Files: $([ $env_insecure -eq 0 ] && echo "SECURE" || echo "INSECURE")"
  echo "- Script Permissions: $([ $script_insecure -eq 0 ] && echo "OK" || echo "FIX NEEDED")"
  echo ""
  echo "RECOMMENDATIONS:"
  if [ $SCORE -lt 18 ]; then
    echo "- Review and fix YAML syntax errors"
    echo "- Ensure all env files have 600 permissions"
    echo "- Add healthchecks to all services"
    echo "- Configure resource limits"
  else
    echo "- All checks passed! Ready for production."
  fi
} | tee "$AUDIT_DIR/summary.txt"

echo ""
echo "📁 Audit complete! Reports saved to: $AUDIT_DIR"
echo "=================================================="
