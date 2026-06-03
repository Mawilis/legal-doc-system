#!/bin/bash
echo "====================================================================="
echo "🏛️ WILSY OS - FORENSIC HUD DISCOVERY SCAN [SINGULARITY MATRIX]"
echo "====================================================================="
echo "Scanning /client/src/components and /client/src/pages for HUDs..."
echo ""

# Find all files with HUD or Dashboard in the name, or containing the word HUD inside the file
find /Users/wilsonkhanyezi/legal-doc-system/client/src -type f \( -name "*HUD*.jsx" -o -name "*Dashboard*.jsx" \) | while read file; do
    echo "📍 [FOUND] $file"
done

echo ""
echo "====================================================================="
echo "✅ FORENSIC SCAN COMPLETE. Anchor identified components to FounderDashboard."
