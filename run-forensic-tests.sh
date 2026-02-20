#!/bin/bash
cd /Users/wilsonkhanyezi/legal-doc-system

export NODE_ENV=test
TOTAL_PASSED=0
TOTAL_TESTS=0
FAILED_SUITES=()

mkdir -p server/docs/evidence

run_test_suite() {
    local name=$1
    local pattern=$2
    
    echo ""
    echo "📋 Running $name Tests..."
    echo "──────────────────────────────────────────────────────────────────────────────"
    
    if npx jest --runInBand --testMatch="**/$pattern" --verbose; then
        echo "✅ $name tests PASSED"
        TOTAL_PASSED=$((TOTAL_PASSED + 1))
    else
        echo "❌ $name tests FAILED"
        FAILED_SUITES+=("$name")
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

# Run all test suites with both forensic and regular patterns
run_test_suite "SA Legal Validators (Forensic)" "validators/*.forensic.test.js"
run_test_suite "SA Legal Validators (Basic)" "validators/*.test.js"
run_test_suite "Compliance ID Generator (Forensic)" "utils/*.forensic.test.js"
run_test_suite "Compliance ID Generator (Basic)" "utils/*.test.js"
run_test_suite "Encryption Service" "services/encryptionService*.test.js"
run_test_suite "Client Onboarding" "services/clientOnboardingService*.test.js"
run_test_suite "All Services" "forensic/all-services*.test.js"

echo ""
echo "══════════════════════════════════════════════════════════════════════════════"
if [ ${#FAILED_SUITES[@]} -eq 0 ]; then
    echo "✅ ALL TEST SUITES PASSED - $TOTAL_PASSED/$TOTAL_TESTS"
    
    echo ""
    echo "📁 Evidence Files:"
    ls -la server/docs/evidence/*.forensic.json 2>/dev/null | head -5
    
else
    echo "❌ SOME TEST SUITES FAILED: ${FAILED_SUITES[*]}"
    exit 1
fi
echo "══════════════════════════════════════════════════════════════════════════════"
