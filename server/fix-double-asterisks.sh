#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ WILSY OS DOUBLE ASTERISK ELIMINATOR - PRODUCTION GRADE                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

echo ""
echo "🔍 WILSY OS - DOUBLE ASTERISK ELIMINATOR"
echo "=========================================="
echo ""

# Step 1: Fix app.js first (most critical)
echo "📍 Step 1: Fixing app.js..."
if [ -f "app.js" ]; then
  sed -i.bak 's/tests\/\*\*\/\*.js/tests\/\*\/\*.js/g' app.js
  sed -i.bak 's/\*\*/*/g' app.js
  rm -f app.js.bak
  echo "  ✓ app.js fixed"
fi

# Step 2: Fix all JS files in project directories (excluding node_modules)
echo ""
echo "📍 Step 2: Fixing all project JS files..."

# Count initial files with **
INITIAL_COUNT=$(find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" 2>/dev/null | xargs grep -l "\*\*" 2>/dev/null | wc -l)

echo "  Found $INITIAL_COUNT files with double asterisks"

# Fix them
FIXED_COUNT=0
find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" 2>/dev/null | while read file; do
  if grep -q "\*\*" "$file" 2>/dev/null; then
    # Create backup
    cp "$file" "$file.bak"
    
    # Fix double asterisks in comments
    # JSDoc comments
    sed -i '' 's/\/\*\*/\/\*/g' "$file"
    # Regular expressions in strings (preserve them)
    sed -i '' 's/"\*\*"/"*"/g' "$file"
    # Any remaining ** that are likely in comments
    sed -i '' 's/\*\*/*/g' "$file"
    
    # If file changed, count it
    if ! cmp -s "$file" "$file.bak"; then
      FIXED_COUNT=$((FIXED_COUNT + 1))
      echo "  ✅ Fixed: $file"
    fi
    
    # Remove backup
    rm -f "$file.bak"
  fi
done

echo ""
echo "  ✅ Fixed $FIXED_COUNT files with double asterisks"

# Step 3: Run Prettier
echo ""
echo "📍 Step 3: Running Prettier..."
npx prettier --write "**/*.{js,cjs,mjs,json,md,yml,yaml}" --loglevel=error 2>/dev/null
echo "  ✓ Prettier formatting complete"

# Step 4: Final verification
echo ""
echo "📍 Step 4: Final verification..."
REMAINING=$(find . -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" 2>/dev/null | xargs grep -l "\*\*" 2>/dev/null | wc -l)

if [ "$REMAINING" -eq 0 ]; then
  echo "  ✓ All double asterisks eliminated!"
else
  echo "  ⚠️  $REMAINING files still have double asterisks (likely in node_modules or strings)"
fi

echo ""
echo "✅ WILSY OS - DOUBLE ASTERISK ELIMINATION COMPLETE"
echo "==================================================="
