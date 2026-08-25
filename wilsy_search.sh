#!/usr/bin/env bash
# ============================================================================
# WILSY OS - KENNEL / EOS / EOF ZERO-DEPENDENCY SEARCH & MAPPER
# STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE
# ============================================================================

OUTPUT_FILE="wilsy_kennel_eos_summary.txt"

echo "============================================================================" > "$OUTPUT_FILE"
echo "WILSY OS ARCHITECTURE - KENNEL / EOS / EOF SEARCH MAP" >> "$OUTPUT_FILE"
echo "ROOT DIRECTORY: $(pwd)" >> "$OUTPUT_FILE"
echo "GENERATED: $(date)" >> "$OUTPUT_FILE"
echo "STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "=== MATCHED KENNEL / EOS / EOF FILES ===" >> "$OUTPUT_FILE"
find . -type d \( -name node_modules -o -name .git -o -name .mongodb -o -name dist -o -name build \) -prune -o \
  -type f \( -iname "*kennel*" -o -iname "*eos*" -o -iname "*eof*" \) -print | tee -a "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "FULL ARCHITECTURE MAP" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

if command -v tree &> /dev/null; then
    tree -I 'node_modules|.git|.mongodb|dist|build' >> "$OUTPUT_FILE"
else
    find . -type d \( -name node_modules -o -name .git -o -name .mongodb -o -name dist -o -name build \) -prune -o -print | sed -e 's;[^/]*/;|  ;g' >> "$OUTPUT_FILE"
fi

echo ""
echo "[WILSY OS] Mapping complete. Output written to $OUTPUT_FILE"
