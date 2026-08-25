/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QR FORENSIC ANOMALY DETECTOR [v1.0.0-ROUTE-BOUND]                                                                          ║
 * ║ [DOCUMENT SHAPE VALIDATION | QR PAYLOAD INTEGRITY | NO OPTIONAL ML RUNTIME | TENANT-SAFE SIGNALS]                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Provides deterministic verification signals required by the QR controller without coupling a revenue route to optional ML.    ║
 * ║ BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/anomalyDetector.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/Chief Architect) | AI Engineering (Codex) - restores QR route boot integrity.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function createAnomaly
 * @description Creates a stable, serialisable forensic anomaly record.
 * @param {string} type - Machine-readable anomaly type.
 * @param {'LOW'|'MEDIUM'|'HIGH'|'CRITICAL'} severity - Assessed severity.
 * @param {string} description - Operator-readable condition.
 * @param {string} remediation - Safe corrective action.
 * @returns {{type: string, severity: string, description: string, remediation: string}} Anomaly record.
 * @collaboration Keeps QR response contracts consistent for BillingHUD and audit exports.
 */
function createAnomaly(type, severity, description, remediation) {
  return { type, severity, description, remediation };
}

/**
 * @function hasValidCurrency
 * @description Checks an ISO 4217 alpha currency representation.
 * @param {unknown} currency - Candidate currency value.
 * @returns {boolean} True when the value is a three-letter currency code.
 * @collaboration Rejects malformed QR payloads before any downstream ledger interpretation.
 */
function hasValidCurrency(currency) {
  return typeof currency === 'string' && /^[A-Z]{3}$/.test(currency.toUpperCase());
}

/**
 * @function hasValidSeal
 * @description Checks an optional hexadecimal SHA3-512 seal without requiring a legacy record to have one.
 * @param {unknown} sealHash - Candidate seal hash.
 * @returns {boolean} True when absent or a 128-character hexadecimal digest.
 * @collaboration Separates missing legacy proof material from malformed proof material.
 */
function hasValidSeal(sealHash) {
  return !sealHash || (typeof sealHash === 'string' && /^[a-fA-F0-9]{128}$/.test(sealHash));
}

/**
 * @function checkDocument
 * @description Detects structural anomalies in a persisted invoice or statement selected by the tenant-bound QR controller.
 * @param {object} document - Persisted invoice or statement.
 * @param {'INVOICE'|'STATEMENT'} type - Document type.
 * @param {object} [options={}] - Verification options retained for controller compatibility.
 * @returns {Promise<Array<object>>} Deterministic anomaly records.
 * @collaboration Avoids optional machine-learning dependencies in the QR request path while preserving forensic response evidence.
 */
export async function checkDocument(document = {}, type, options = {}) {
  const anomalies = [];
  const amount = Number(document.totalAmount ?? document.amount);
  const tenantId = document.recipientTenantId || document.tenantId || options.tenantId;

  if (!['INVOICE', 'STATEMENT'].includes(String(type || '').toUpperCase())) {
    anomalies.push(createAnomaly('UNRECOGNISED_DOCUMENT_TYPE', 'HIGH', 'The QR target has an unsupported document type.', 'Issue a QR proof only for an invoice or statement.'));
  }
  if (!tenantId) {
    anomalies.push(createAnomaly('MISSING_TENANT_CONTEXT', 'CRITICAL', 'The document has no tenant ownership marker.', 'Restore tenant ownership before verification.'));
  }
  if (!document.traceId) {
    anomalies.push(createAnomaly('MISSING_TRACE', 'HIGH', 'The document has no persisted forensic trace.', 'Issue a ledger trace before publishing a QR proof.'));
  }
  if (!Number.isFinite(amount) || amount < 0) {
    anomalies.push(createAnomaly('INVALID_AMOUNT', 'CRITICAL', 'The document amount is not a non-negative finite number.', 'Correct the ledger amount before verification.'));
  }
  if (!hasValidCurrency(document.currency || 'ZAR')) {
    anomalies.push(createAnomaly('INVALID_CURRENCY', 'HIGH', 'The document currency is not an ISO 4217 code.', 'Correct the document currency before verification.'));
  }
  if (!hasValidSeal(document.sealHash)) {
    anomalies.push(createAnomaly('MALFORMED_SEAL', 'CRITICAL', 'The document seal is not a SHA3-512 digest.', 'Regenerate the document seal from canonical ledger data.'));
  }

  return anomalies;
}

/**
 * @function checkPayload
 * @description Detects tampering or expiry conditions in a decoded QR payload.
 * @param {object} payload - Decoded signed QR payload.
 * @param {object} [options={}] - Verification options retained for controller compatibility.
 * @returns {Promise<Array<object>>} Deterministic anomaly records.
 * @collaboration Makes generated QR payloads verifiable even when the optional ML service is not installed.
 */
export async function checkPayload(payload = {}, options = {}) {
  const anomalies = [];
  const requiredFields = ['documentId', 'tenantId', 'amount', 'currency', 'traceId'];
  for (const field of requiredFields) {
    if (payload[field] === undefined || payload[field] === null || payload[field] === '') {
      anomalies.push(createAnomaly(`MISSING_${field.toUpperCase()}`, 'HIGH', `The QR payload is missing ${field}.`, 'Regenerate the QR code from the persisted document.'));
    }
  }
  if (options.tenantId && payload.tenantId && String(options.tenantId) !== String(payload.tenantId)) {
    anomalies.push(createAnomaly('TENANT_MISMATCH', 'CRITICAL', 'The QR payload tenant does not match the verification context.', 'Verify the QR code from its owning tenant context.'));
  }
  if (!Number.isFinite(Number(payload.amount)) || Number(payload.amount) < 0) {
    anomalies.push(createAnomaly('INVALID_AMOUNT', 'CRITICAL', 'The QR payload amount is invalid.', 'Regenerate the QR payload from the ledger.'));
  }
  if (!hasValidCurrency(payload.currency)) {
    anomalies.push(createAnomaly('INVALID_CURRENCY', 'HIGH', 'The QR payload currency is invalid.', 'Regenerate the QR payload with an ISO 4217 currency.'));
  }
  if (!hasValidSeal(payload.sealHash)) {
    anomalies.push(createAnomaly('MALFORMED_SEAL', 'CRITICAL', 'The QR payload seal is malformed.', 'Regenerate the QR payload from a sealed document.'));
  }
  if (payload.expiresAt && Number(payload.expiresAt) < Date.now()) {
    anomalies.push(createAnomaly('PAYLOAD_EXPIRED', 'MEDIUM', 'The QR payload has expired.', 'Issue a fresh QR proof for the document.'));
  }
  return anomalies;
}

export default { checkDocument, checkPayload };
