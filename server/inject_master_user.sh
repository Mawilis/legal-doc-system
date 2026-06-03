#!/bin/bash
# // ============================================================================
# // Wilsy OS - Billion Dollar Architecture
# // Script: Master Identity Injection (Sovereign Root)
# // Path: /Users/wilsonkhanyezi/legal-doc-system/server/inject_master_user.sh
# // ============================================================================
# // Collaboration Note: This script bypasses the 401 Auth Failure by manually
# // inserting the master user into the wilsy.users collection.
# // Includes sovereign role and active status for immediate Postman access.
# // ============================================================================

mongosh --port 27017 \
  -u "wilsy_app" \
  -p "WilsyApp2026Secure" \
  --authenticationDatabase "wilsy" << 'MONGOEOF'

use wilsy;

print("--- INJECTING MASTER IDENTITY ---");

db.users.updateOne(
  { email: "wilsonkhanyezi@gmail.com" },
  {
    $set: {
      email: "wilsonkhanyezi@gmail.com",
      username: "wilsonkhanyezi",
      role: "sovereign",
      status: "active",
      tenantId: "wilsy-sovereign-root",
      createdAt: new Date(),
      updatedAt: new Date()
    }
  },
  { upsert: true }
);

print("--- WILSY OS IDENTITY VALIDATION ---");
const master = db.users.findOne({ email: "wilsonkhanyezi@gmail.com" });
if (master) {
    print("✅ IDENTITY SECURED: " + master.email);
    print("✅ STATUS: " + master.status);
    print("✅ ROLE: " + master.role);
}

print("✅ Forensic precision achieved: Auth barrier removed.");
MONGOEOF
