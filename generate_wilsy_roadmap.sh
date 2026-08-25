#!/usr/bin/env bash
# ==============================================================================
# WILSY OS - UNIVERSAL SYSTEM ROADMAP & KERNEL INDEX
# Purpose: Deep-scans the entire infrastructure (Client, Server, Kernel).
# ==============================================================================

OUTPUT_FILE="WILSY_OS_ROADMAP.md"
TARGET_DIR=$(pwd)

echo "# WILSY OS - MASTER ARCHITECTURAL ROADMAP & KERNEL INDEX" > "$OUTPUT_FILE"
echo "Generated on: $(date -u)" >> "$OUTPUT_FILE"
echo "Absolute Path: $TARGET_DIR" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## 1. System Directory Tree (Client & Server)" >> "$OUTPUT_FILE"
echo '```text' >> "$OUTPUT_FILE"
# Prioritize 'tree' if installed, otherwise use 'find' to map the structure
if command -v tree &> /dev/null; then
    tree -a -I 'node_modules|.git|.next|dist|coverage|build|.DS_Store' >> "$OUTPUT_FILE"
else
    find . -maxdepth 5 -not -path '*/.*' -not -path '*/node_modules*' -not -path '*/dist*' -not -path '*/build*' | sort | sed -e 's;[^/]*/;|----;g;s;----|; |;g' >> "$OUTPUT_FILE"
fi
echo '```' >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## 2. Global File Assessment & Processing Pipeline" >> "$OUTPUT_FILE"
echo "Every file listed below requires verification for production readiness, collaboration comments, and Mars-tier architectural standards." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '| Absolute/Relative Path | Sub-System | File Type | Status |' >> "$OUTPUT_FILE"
echo '|---|---|---|---|' >> "$OUTPUT_FILE"

# Walk through ALL source files across client, server, and kernel
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" -o -name "*.env*" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" | sort | while read -r file; do
        
        # Determine subsystem based on path
        if [[ "$file" == *"client/"* ]]; then
            SUBSYSTEM="Client Interface"
        elif [[ "$file" == *"server/"* ]]; then
            SUBSYSTEM="Server Node"
        elif [[ "$file" == *"kernel"* || "$file" == *"sovereign"* ]]; then
            SUBSYSTEM="OS Kernel / Sovereign"
        else
            SUBSYSTEM="Infrastructure"
        fi
        
        echo "| \`$file\` | $SUBSYSTEM | $(basename "$file") | Pending AI Assessment |" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*Wilsy OS Roadmap initialization complete. Handing over to AI Agent for line-by-line file processing.*" >> "$OUTPUT_FILE"

echo "Roadmap successfully generated at: $TARGET_DIR/$OUTPUT_FILE"
