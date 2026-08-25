#!/usr/bin/env bash
# ==============================================================================
# WILSY OS - ARCHITECTURAL FILE MAPPING TOOL
# Purpose: Auto-generates high-density, clean system file tree & architectural index.
# ==============================================================================

OUTPUT_FILE="PROJECT_FILE_MAP.md"

echo "# WILSY OS - PRODUCTION REPOSITORY FILE MAP" > "$OUTPUT_FILE"
echo "Generated on: $(date -u)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## Directory Structure" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"

if command -v tree &> /dev/null; then
    tree -a -I 'node_modules|.git|.next|dist|coverage|build|.DS_Store' >> "$OUTPUT_FILE"
else
    find . -maxdepth 4 -not -path '*/.*' -not -path './node_modules*' -not -path './dist*' | sort | sed -e 's;[^/]*/;|----;g;s;----|; |;g' >> "$OUTPUT_FILE"
fi

echo '```' >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## Core Service Registry & Critical Paths" >> "$OUTPUT_FILE"
echo '| Path | Service / Component | Status |' >> "$OUTPUT_FILE"
echo '|---|---|---|' >> "$OUTPUT_FILE"

# Walk through JS/TS source files and log them to table
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.json" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/dist/*" \
    -not -path "*/coverage/*" | sort | while read -r file; do
        echo "| \`$file\` | $(basename "$file") | Production Ready |" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*File map successfully compiled for system ingestion.*" >> "$OUTPUT_FILE"

echo "File map created at: $OUTPUT_FILE"
