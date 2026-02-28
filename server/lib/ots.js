import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
/*
 * OpenTimestamps Shim - Placeholder for blockchain timestamping
 * This is a temporary shim until full OTS integration is implemented
 */
const crypto = require('crypto');

function generateDocumentHash(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

async function createTimestamp(hash, tenantId) {
  return {
    hash,
    tenantId,
    timestamp: new Date().toISOString(),
    anchorId: `ots-${Date.now()}`,
    verified: true,
  };
}

export default {
  generateDocumentHash,
  createTimestamp,
};
