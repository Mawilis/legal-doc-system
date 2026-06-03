/* eslint-disable */
/**
 * 🧪 ComplianceArchiver Forensic Audit
 * @description Verifying the 100-year retention logic and immutable sealing.
 */
import { expect } from 'chai';
import ComplianceArchiverService from '../../services/compliance/ComplianceArchiver.service.js';

describe('🗄️ ComplianceArchiver Sovereign Audit', () => {
  it('sets a retention expiry date exactly 100 years into the future', async () => {
    const mockManifest = { docId: 'DOC-CENTENNIAL', contentHash: 'abc123hash' };
    const result = await ComplianceArchiverService.archiveManifest(mockManifest);

    const currentYear = new Date().getFullYear();
    const expiryYear = new Date(result.retentionExpiry).getFullYear();

    expect(expiryYear).to.equal(currentYear + 100);
    expect(result.preservationStatus).to.equal('IMMUTABLE');
    expect(result.archiveSignature).to.have.lengthOf(128); // SHA-512 Verification
  });
});
