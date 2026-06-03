#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ WILSY OS - FORENSIC INTEGRITY & GAP ANALYSER [v1.0.0-SINGULARITY]                                                                      ║
# ║ EPITOME: BIBLICAL WORTH BILLIONS | ELON MUSK GRADE | NO CHILD'S PLACE                                                                  ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 INITIATING FORENSIC AUDIT OF WILSY OS CITADEL...${NC}\n"

# 1. 🚯 THE EXTINCTION LIST (Redundant/Legacy Fragments)
echo -e "${YELLOW}🔍 SEARCHING FOR FRAGMENTED/REDUNDANT DEBRIS...${NC}"
LEGACY_FILES=(
  "models/BillingRecord.js"
  "models/BillingInvoice.js"
  "services/pdf/InvoicePdfService.js" # Verify if this moved to a Sovereign variant
  "models/userModel.js" # Check if should be renamed to User.js for standard
)

for file in "${LEGACY_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${RED}[FRAGMENT DETECTED]${NC} $file -> Schedule for Purge."
  fi
done

# 2. 🏛️ THE SOVEREIGN PILLARS (Required for Singularity)
echo -e "\n${YELLOW}🛡️ VERIFYING SOVEREIGN PILLAR INTEGRITY...${NC}"
PILLARS=(
  "config/database.js"
  "middleware/tenantContext.js"
  "middleware/tenantGuard.js"
  "middleware/authMiddleware.js"
  "models/Billing.js"
  "models/Asset.js"
  "services/RevenueSingularity.js"
  "utils/auditLogger.js"
)

for pillar in "${PILLARS[@]}"; do
  if [ -f "$pillar" ]; then
    # Check for BIBLICAL credits
    if grep -q "Wilson Khanyezi" "$pillar"; then
      echo -e "${GREEN}[PILLAR SECURED]${NC} $pillar (Sovereign Credits Found)"
    else
      echo -e "${YELLOW}[PILLAR WEAK]${NC} $pillar (Missing Collaboration Credits)"
    fi
  else
    echo -e "${RED}[CRITICAL GAP]${NC} $pillar IS MISSING. SYSTEM INCOMPLETE."
  fi
done

# 3. 🔬 CROSS-LINK VALIDATION (Module Sync)
echo -e "\n${YELLOW}🔬 CHECKING FOR SINGULARITY BREACHES (Broken Imports)...${NC}"
grep -r "BillingInvoice" . --exclude-dir=node_modules | grep "import" && echo -e "${RED}⚠️ LEGACY IMPORTS FOUND!${NC}" || echo -e "${GREEN}✅ Module Imports Aligned.${NC}"

echo -e "\n${CYAN}🏁 FORENSIC AUDIT COMPLETE.${NC}"
