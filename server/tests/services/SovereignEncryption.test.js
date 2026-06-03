/* eslint-disable */
/**
 * 🧪 SovereignEncryption Forensic Audit
 * @description Verifying the AES-256-GCM lifecycle for sensitive database fields.
 */
import { expect } from 'chai';
import SovereignEncryptionService from '../../services/security/SovereignEncryption.service.js';

describe('🔒 SovereignEncryption Sovereign Audit', () => {
  it('encrypts sensitive text and produces an authTag for integrity verification', () => {
    const secretData = 'R2.3T_ASSET_ALLOCATION';
    const encrypted = SovereignEncryptionService.encrypt(secretData);

    expect(encrypted.content).to.not.equal(secretData);
    expect(encrypted.authTag).to.have.lengthOf(32);
    expect(encrypted.integrity).to.equal('QUANTUM_SEALED');
  });

  it('correctly decrypts the ciphertext back to its original biblical form', () => {
    const secretData = 'SOVEREIGN_FOUNDER_DNA_CODE';
    const encrypted = SovereignEncryptionService.encrypt(secretData);
    const decrypted = SovereignEncryptionService.decrypt(encrypted);

    expect(decrypted).to.equal(secretData);
  });
});
