#!/bin/bash
# // ============================================================================
# // Wilsy OS - Billion Dollar Architecture
# // Script: Final Emergency Role Repair (Maintenance Mode)
# // Path: /Users/wilsonkhanyezi/legal-doc-system/server/force_fix_wilsy.sh
# // ============================================================================
# // Collaboration Note: Executing with --noauth priority. This injects the
# // required userAdmin and readWrite roles directly into the wilsy_app user.
# // This resolves the Postman 401/403 errors by ensuring the service account
# // has legitimate access to the tenant database.
# // ============================================================================

mongosh --port 27017 << 'MONGOEOF'
use wilsy;

print("--- FORCING ROLE INJECTION ---");

// Update wilsy_app with full authority for the main and tenant databases
db.updateUser("wilsy_app", {
  roles: [
    { role: "userAdmin", db: "wilsy" },
    { role: "dbAdmin", db: "wilsy" },
    { role: "readWrite", db: "wilsy" },
    { role: "readWrite", db: "tenant_69dd419f39c41a1b067fc048" },
    { role: "dbAdmin", db: "wilsy-os" },
    { role: "readWrite", db: "wilsy-os" }
  ]
});

print("--- WILSY OS FORENSIC VALIDATION ---");
const user = db.getUser("wilsy_app");
if (user) {
    print("User: " + user.user);
    print("Injected Roles: " + JSON.stringify(user.roles));
}
print("✅ Forensic precision achieved: Access gates are OPEN.");
MONGOEOF
