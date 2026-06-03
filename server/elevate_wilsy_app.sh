#!/bin/bash
# // ============================================================================
# // Wilsy OS - Billion Dollar Architecture
# // Script: Administrative Elevation & Tenant Binding
# // Path: /Users/wilsonkhanyezi/legal-doc-system/server/elevate_wilsy_app.sh
# // ============================================================================
# // Collaboration Note: Elevating wilsy_app to include 'userAdmin' role.
# // This is a mechanical necessity because dbAdmin does not permit role
# // grants. This ensures future-proof, self-sufficient provisioning.
# // ============================================================================

# We MUST use the root admin to modify user roles
mongosh --port 27017 \
  -u "admin" \
  -p "ENTER_YOUR_ROOT_ADMIN_PASSWORD_HERE" \
  --authenticationDatabase "admin" << 'MONGOEOF'

use wilsy;

print("--- ELEVATING SERVICE ACCOUNT PERMISSIONS ---");

// 1. Give wilsy_app the ability to manage its own roles and tenant roles
db.grantRolesToUser("wilsy_app", [
  { role: "userAdmin", db: "wilsy" },
  { role: "readWrite", db: "tenant_69dd419f39c41a1b067fc048" }
]);

print("--- WILSY OS FORENSIC VALIDATION ---");
const user = db.getUser("wilsy_app");
if (user) {
    print("User: " + user.user);
    print("New Roles: " + JSON.stringify(user.roles));
}

print("✅ Forensic precision achieved: wilsy_app elevated and tenant bound.");
MONGOEOF
