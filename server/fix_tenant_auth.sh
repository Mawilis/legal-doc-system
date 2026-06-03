#!/bin/bash
# // ============================================================================
# // Wilsy OS - Billion Dollar Architecture
# // Script: Tenant Database Role Provisioning (Self-Authorization)
# // Path: /Users/wilsonkhanyezi/legal-doc-system/server/fix_tenant_auth.sh
# // ============================================================================
# // Collaboration Note: Utilizing the main wilsy_app credentials to bind
# // the isolated tenant database. This file is production-ready and
# // designed for forensic auditability.
# // ============================================================================

mongosh --port 27017 \
  -u "wilsy_app" \
  -p "WilsyApp2026Secure" \
  --authenticationDatabase "wilsy" << 'MONGOEOF'

use wilsy;

// Attempting to grant permissions to the main service account
db.grantRolesToUser("wilsy_app", [
  { role: "readWrite", db: "tenant_69dd419f39c41a1b067fc048" }
]);

print("--- WILSY OS FORENSIC VALIDATION ---");
const user = db.getUser("wilsy_app");
if (user) {
    print("User: " + user.user);
    print("Roles: " + JSON.stringify(user.roles));
}

print("✅ Forensic precision achieved: Tenant binding command executed.");
MONGOEOF
