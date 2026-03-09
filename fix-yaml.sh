#!/bin/bash
# Simple script to fix common YAML issues

echo "🔧 Fixing YAML files..."

# Fix GitHub Actions workflow
if [ -f "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows/ci.yml" ]; then
  # Remove trailing spaces
  sed -i '' 's/[[:space:]]*$//' "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows/ci.yml"
  
  # Add newline at end of file if missing
  if [ -n "$(tail -c1 /Users/wilsonkhanyezi/legal-doc-system/.github/workflows/ci.yml)" ]; then
    echo "" >> "/Users/wilsonkhanyezi/legal-doc-system/.github/workflows/ci.yml"
  fi
  
  echo "✅ Fixed ci.yml"
fi

echo "✅ YAML fixes complete"
