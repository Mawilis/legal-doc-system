/* eslint-disable */
/**
 * 🧪 Handover & Onboarding Forensic Audit
 * @version 10.0.0-QUANTUM-2050
 * @description Simulating third-party node registration (e.g., Royal Logistics TZ).
 * * 🤝 COLLABORATION NOTES:
 * - NODE_VALIDATION: Ensures only Apple Silicon/Sovereign hardware IDs are accepted.
 * - SIT_EXCHANGE: Verifies the cryptographic handshake between Genesis and Edge.
 * - WORTH: This is the bridge that scales Wilsy OS to R120B+ global operations.
 */
import { expect } from 'chai';
import crypto from 'crypto';
import SovereignAuthService from '../../services/auth/SovereignAuth.service.js';
import GlobalSyncService from '../../services/sync/GlobalSync.service.js';

describe('🛰️ Sovereign Handover: Node Onboarding Audit', () => {
  it('successfully registers an external Royal Logistics node using a Sovereign Identity Token', async () => {
    const externalNodeId = 'RL-TZ-DAR-NODE-01';
    const hardwareFingerprint = 'M3-MAX-64GB-APPLE-SILICON';

    // 1. Generate SIT for the new node
    const registrationToken = SovereignAuthService.generateSovereignToken(externalNodeId, hardwareFingerprint);

    expect(registrationToken.sit_id).to.match(/^SIT-/);
    expect(registrationToken.tokenSignature).to.have.lengthOf(128);

    // 2. Simulate the first Sync Pulse from the new node
    const initialBatch = {
      batchId: 'GENESIS-SYNC-TZ',
      signature: registrationToken.tokenSignature,
      node: externalNodeId
    };

    const syncResult = await GlobalSyncService.syncEdgeBatch(initialBatch);

    expect(syncResult.status).to.equal('SYNCHRONIZED');
    expect(syncResult.integrityCheck).to.equal('PASSED');
    expect(syncResult.masterSyncSig).to.have.lengthOf(128);
  });

  it('rejects an onboarding attempt from a node with an invalid forensic signature', async () => {
    const maliciousNode = { batchId: 'ROGUE-NODE', signature: 'INVALID_SIG' };

    try {
      await GlobalSyncService.syncEdgeBatch(maliciousNode);
    } catch (error) {
      expect(error.message).to.equal('INVALID_EDGE_SIGNATURE_DETECTED');
    }
  });
});
