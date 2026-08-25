/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ 🏛️ WILSY OS – MONGOSH BACKFILL SCRIPT                                                                                               ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE                                                                                              ║
 * ║ EPITOME: Backfills traceId and signNonce for all Invoices and Statements using mongosh.                                            ║
 * ║ USAGE: mongosh "mongodb+srv://wilsonkhanyezi:Mawilis8596@legaldocsystem.knucgy2.mongodb.net/wilsy?retryWrites=true&w=majority&appName=legalDocSystem&authSource=admin" --file server/scripts/backfill.js
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

// ─── Helper functions (same as pre‑save) ────────────────────────────────
function generateTraceId(tenantId, numberField) {
  const tenantPrefix = String(tenantId || 'MASTER').slice(0, 8).toUpperCase();
  const entropy = crypto.randomBytes(16).toString('hex').toUpperCase();
  const base = numberField ? numberField.slice(-8) : entropy.slice(0, 8);
  return `WILSY-TRACE-${tenantPrefix}-${base}-${entropy.slice(0, 8)}`;
}

function generateSignNonce() {
  return crypto.randomBytes(32).toString('hex');
}

// ─── Backfill Invoices ──────────────────────────────────────────────────
print('📄 Processing Invoices...');
let invoiceCount = 0;
const invoices = db.invoices.find({
  $or: [
    { traceId: { $exists: false } },
    { traceId: null },
    { traceId: '' },
    { signNonce: { $exists: false } },
    { signNonce: null },
  ]
});

invoices.forEach(doc => {
  let update = {};
  let modified = false;
  if (!doc.traceId) {
    update.traceId = generateTraceId(doc.tenantId, doc.invoiceNumber);
    modified = true;
  }
  if (!doc.signNonce) {
    update.signNonce = generateSignNonce();
    modified = true;
  }
  if (modified) {
    db.invoices.updateOne({ _id: doc._id }, { $set: update });
    invoiceCount++;
    if (invoiceCount % 10 === 0) print(`  ... ${invoiceCount} invoices updated`);
  }
});
print(`✅ Invoices updated: ${invoiceCount} documents modified.`);

// ─── Backfill Statements ────────────────────────────────────────────────
print('📄 Processing Statements...');
let statementCount = 0;
const statements = db.statements.find({
  $or: [
    { traceId: { $exists: false } },
    { traceId: null },
    { traceId: '' },
    { signNonce: { $exists: false } },
    { signNonce: null },
  ]
});

statements.forEach(doc => {
  let update = {};
  let modified = false;
  if (!doc.traceId) {
    update.traceId = generateTraceId(doc.tenantId, doc.statementNumber);
    modified = true;
  }
  if (!doc.signNonce) {
    update.signNonce = generateSignNonce();
    modified = true;
  }
  if (modified) {
    db.statements.updateOne({ _id: doc._id }, { $set: update });
    statementCount++;
    if (statementCount % 10 === 0) print(`  ... ${statementCount} statements updated`);
  }
});
print(`✅ Statements updated: ${statementCount} documents modified.`);

print('🎉 Backfill completed successfully.');
