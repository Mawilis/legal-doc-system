#!/bin/bash

echo "🔍 WILSY OS - PRODUCTION VERIFICATION"
echo "======================================"

# Check if old dashboard file exists
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/server/dashboard/warroom.html" ]; then
    echo "❌ ERROR: Old dashboard file still exists at /server/dashboard/warroom.html"
    echo "   Run: rm -rf /Users/wilsonkhanyezi/legal-doc-system/server/dashboard/"
    exit 1
else
    echo "✅ Old dashboard directory removed"
fi

# Check if new dashboard file exists
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/server/public/dashboard/warroom.html" ]; then
    echo "✅ New dashboard file exists at correct location"
else
    echo "❌ ERROR: New dashboard file not found"
    exit 1
fi

# Check for inline styles in HTML
INLINE_STYLES=$(grep -c "style=" "/Users/wilsonkhanyezi/legal-doc-system/server/public/dashboard/warroom.html")
if [ $INLINE_STYLES -eq 0 ]; then
    echo "✅ No inline styles in HTML"
else
    echo "❌ ERROR: Found $INLINE_STYLES inline styles in HTML"
    exit 1
fi

# Check for style manipulation in JS
STYLE_MANIP=$(grep -c "style\." "/Users/wilsonkhanyezi/legal-doc-system/server/public/js/warroom.js")
if [ $STYLE_MANIP -le 2 ]; then
    echo "✅ Minimal style manipulation in JS ($STYLE_MANIP lines)"
else
    echo "❌ ERROR: Found $STYLE_MANIP style manipulations in JS"
    exit 1
fi

echo "======================================"
echo "✅ PRODUCTION VERIFICATION PASSED"
echo "======================================"
