/**
 * Audit Ledger Shim - Placeholder for forensic audit logging
 * This is a temporary shim until full audit ledger is implemented
 */
async function appendAuditEntry(entry) {
  console.log(`[AUDIT] ${JSON.stringify(entry)}`);
  return { success: true, entryId: `audit-${Date.now()}` };
}

async function readAuditTrail(params) {
  return { entries: [], total: 0 };
}

module.exports = {
  appendAuditEntry,
  readAuditTrail
};
