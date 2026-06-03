#!/bin/bash
# WILSY OS 2050 - Fix all import statements in page files

cd /Users/wilsonkhanyezi/legal-doc-system/client

echo "🔧 Fixing all page imports to use superAdminAPI..."

# Fix Audit.jsx
if [ -f src/pages/superadmin/Audit.jsx ]; then
  sed -i '' 's/import { fetchAuditLogs } from/import { superAdminAPI } from/g' src/pages/superadmin/Audit.jsx
  sed -i '' 's/fetchAuditLogs(/superAdminAPI.getAuditLogs(/g' src/pages/superadmin/Audit.jsx
  echo "✅ Fixed Audit.jsx"
fi

# Fix Dashboard.jsx
if [ -f src/pages/superadmin/Dashboard.jsx ]; then
  sed -i '' 's/import { fetchDashboardStats } from/import { superAdminAPI } from/g' src/pages/superadmin/Dashboard.jsx
  sed -i '' 's/fetchDashboardStats(/superAdminAPI.getDashboardStats(/g' src/pages/superadmin/Dashboard.jsx
  echo "✅ Fixed Dashboard.jsx"
fi

# Fix Users.jsx
if [ -f src/pages/superadmin/Users.jsx ]; then
  sed -i '' 's/import { fetchUsers } from/import { superAdminAPI } from/g' src/pages/superadmin/Users.jsx
  sed -i '' 's/fetchUsers(/superAdminAPI.getUsers(/g' src/pages/superadmin/Users.jsx
  echo "✅ Fixed Users.jsx"
fi

# Fix Tenants.jsx
if [ -f src/pages/superadmin/Tenants.jsx ]; then
  sed -i '' 's/import { fetchTenants } from/import { superAdminAPI } from/g' src/pages/superadmin/Tenants.jsx
  sed -i '' 's/fetchTenants(/superAdminAPI.getTenants(/g' src/pages/superadmin/Tenants.jsx
  echo "✅ Fixed Tenants.jsx"
fi

# Fix Security.jsx
if [ -f src/pages/superadmin/Security.jsx ]; then
  sed -i '' 's/import { fetchSecurityEvents } from/import { superAdminAPI } from/g' src/pages/superadmin/Security.jsx
  sed -i '' 's/fetchSecurityEvents(/superAdminAPI.getSecurityEvents(/g' src/pages/superadmin/Security.jsx
  echo "✅ Fixed Security.jsx"
fi

# Fix System.jsx
if [ -f src/pages/superadmin/System.jsx ]; then
  sed -i '' 's/import { fetchSystemStatus } from/import { superAdminAPI } from/g' src/pages/superadmin/System.jsx
  sed -i '' 's/fetchSystemStatus(/superAdminAPI.getSystemStatus(/g' src/pages/superadmin/System.jsx
  echo "✅ Fixed System.jsx"
fi

# Fix Reports.jsx
if [ -f src/pages/superadmin/Reports.jsx ]; then
  sed -i '' 's/import { generateReport } from/import { superAdminAPI } from/g' src/pages/superadmin/Reports.jsx
  sed -i '' 's/generateReport(/superAdminAPI.generateReport(/g' src/pages/superadmin/Reports.jsx
  echo "✅ Fixed Reports.jsx"
fi

echo ""
echo "🎉 All imports fixed!"
