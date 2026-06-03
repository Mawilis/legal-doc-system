/* eslint-disable */
/**
 * 🧪 SovereignAuth Forensic Audit
 * @description Verifying the cryptographic seal of Sovereign Identity Tokens.
 */
import { expect } from 'chai';
import SovereignAuthService from '../../services/auth/SovereignAuth.service.js';

describe('🔐 SovereignAuth Sovereign Audit', () => {
  it('generates a 128-character SHA-512 signature for the identity marker', () => {
    const userId = 'WILSON_KHANYEZI_FOUNDER';
    const biometricHash = 'FINGERPRINT_DNA_OR_RETINA_HASH_2050';

    const result = SovereignAuthService.generateSovereignToken(userId, biometricHash);

    expect(result.sit_id).to.match(/^SIT-/);
    expect(result.tokenSignature).to.have.lengthOf(128);
    expect(result.payload.userId).to.equal(userId);
  });
});
