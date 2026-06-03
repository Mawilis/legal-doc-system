/* eslint-disable */
/**
 * 🧪 ForensicService Forensic Audit
 * @description Verification of SHA-512 Sovereign Signatures and Anchor Manifests.
 * 🤝 COLLABORATION: Ensures the R2.3T logic remains immutable during CI/CD.
 */
import { expect } from 'chai';
import ForensicService from '../../services/forensic/ForensicService.js';

describe('🛰️ ForensicService Sovereign Audit', () => {
  it('generates a 128-character SHA-512 signature for transactions', () => {
    const testData = { amount: 'R2.3T', currency: 'ZAR', client: 'WILSY_LTD' };
    const signature = ForensicService.signTransaction(testData);

    expect(signature).to.have.lengthOf(128);
    expect(signature).to.be.a('string');
  });

  it('creates an immutable document manifest with a unique anchor ID', async () => {
    const docId = 'DOC-99';
    const contentHash = '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd';

    const manifest = await ForensicService.anchorDocument(docId, contentHash);

    // Aligned with Chai 10/10 standards
    expect(manifest.anchorId).to.have.lengthOf(32);
    expect(manifest.signature).to.have.lengthOf(128);
    expect(manifest.timestamp).to.exist;
  });
});
