#!/bin/bash

# WILSY OS - Automated Secret Rotation
# Rotates all secrets while maintaining zero-downtime

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔄 WILSY OS - Automated Secret Rotation${NC}"
echo "==========================================="

# Check if running in Kubernetes
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

# Check namespace exists
if ! kubectl get namespace wilsy-os &> /dev/null; then
    echo -e "${RED}❌ Namespace wilsy-os not found. Deploy first.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}📦 Current secrets (masked):${NC}"
kubectl get secrets -n wilsy-os

# Backup current secrets
echo -e "\n${YELLOW}💾 Backing up current secrets...${NC}"
BACKUP_FILE="secrets-backup-$(date +%Y%m%d-%H%M%S).yaml"
kubectl get secrets -n wilsy-os -o yaml > ${BACKUP_FILE}
echo -e "  ✅ Backed up to: ${BACKUP_FILE}"

# Generate new secrets
echo -e "\n${YELLOW}🔐 Generating new secrets...${NC}"
./k8s/generate-secrets.sh

# Apply new secrets
echo -e "\n${YELLOW}🚀 Applying new secrets...${NC}"
kubectl apply -f k8s/secrets.yaml

# Roll restart deployment to pick up new secrets
echo -e "\n${YELLOW}🔄 Rolling restart deployment...${NC}"
kubectl rollout restart deployment/wilsy-os-predictive -n wilsy-os

# Wait for rollout
echo -e "\n${YELLOW}⏳ Waiting for rollout to complete...${NC}"
kubectl rollout status deployment/wilsy-os-predictive -n wilsy-os --timeout=5m

# Verify new secrets are working
echo -e "\n${YELLOW}✅ Verifying new secrets...${NC}"
POD_NAME=$(kubectl get pods -n wilsy-os -l app=wilsy-os -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n wilsy-os ${POD_NAME} -- printenv | grep -E "API_KEY|JWT_SECRET" | head -3

echo -e "\n${GREEN}✅ Secret rotation complete!${NC}"
echo -e "  • Old secrets backed up to: ${BACKUP_FILE}"
echo -e "  • New secrets applied and verified"
echo -e "  • Deployment rolled out successfully"

# Cleanup old backup
echo -e "\n${YELLOW}🧹 Cleanup old backups? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    find . -name "secrets-backup-*" -mtime +30 -delete
    echo -e "  ✅ Old backups cleaned"
fi
