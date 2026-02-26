#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     WILSY OS - FIX ALL BUILT-IN MODULE IMPORTS                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/wilsonkhanyezi/legal-doc-system/server

# Create backup if not already done
if [ ! -d "backups/$(date +%Y%m%d)" ]; then
    mkdir -p backups/$(date +%Y%m%d)
    cp -r models backups/$(date +%Y%m%d)/
    cp -r tests backups/$(date +%Y%m%d)/
    echo "✅ Backup created in backups/$(date +%Y%m%d)"
fi

# List of built-in Node.js modules that might have .js extensions
BUILTIN_MODULES=(
    "crypto"
    "fs"
    "path"
    "http"
    "https"
    "url"
    "util"
    "events"
    "stream"
    "buffer"
    "assert"
    "os"
    "child_process"
    "cluster"
    "dns"
    "domain"
    "http2"
    "net"
    "tls"
    "zlib"
    "timers"
    "console"
    "process"
)

echo "🔧 Fixing imports for built-in modules..."

for module in "${BUILTIN_MODULES[@]}"; do
    # Fix quoted imports
    find models -name "*.js" -type f -exec sed -i '' "s/from ['\"]${module}\.js['\"]/from '${module}'/g" {} \; 2>/dev/null
    find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]${module}\.js['\"]/from '${module}'/g" {} \; 2>/dev/null
    
    # Fix imports with semicolons
    find models -name "*.js" -type f -exec sed -i '' "s/from ['\"]${module}\.js['\"];/from '${module}';/g" {} \; 2>/dev/null
    find tests -name "*.test.js" -type f -exec sed -i '' "s/from ['\"]${module}\.js['\"];/from '${module}';/g" {} \; 2>/dev/null
    
    echo "  ✅ Fixed $module"
done

# Fix any remaining .js.js patterns
find models -name "*.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \; 2>/dev/null
find tests -name "*.test.js" -type f -exec sed -i '' 's/\.js\.js/\.js/g' {} \; 2>/dev/null

echo -e "\n✅ All built-in module imports fixed"

# Verify Case.js specifically
echo -e "\n🔍 Verifying Case.js imports:"
grep -E "from (['\"])[a-zA-Z]+\.js(['\"])" models/Case.js || echo "✅ No .js extensions found in imports"

echo -e "\n📊 Total files processed:"
find models -name "*.js" | wc -l | xargs echo "  Models:"
find tests -name "*.test.js" | wc -l | xargs echo "  Tests:"

echo -e "\n📝 If anything went wrong, restore with:"
echo "cp -r backups/$(date +%Y%m%d)/models/* models/"
echo "cp -r backups/$(date +%Y%m%d)/tests/* tests/"
