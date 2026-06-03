/* eslint-disable */
/**
 * 🧪 DisputeResolution Forensic Audit
 * @description Verifying the generation of sealed legal verdicts.
 */
import { expect } from 'chai';
import DisputeResolutionService from '../../services/legal/DisputeResolution.service.js';

describe('⚖️ DisputeResolution Sovereign Audit', () => {
  it('generates a court-admissible verdict with a perfect integrity score', async () => {
    const docId = 'DOC-ROYAL-001';
    const content = 'Sovereign Transaction Data - R2.3T';

    const result = await DisputeResolutionService.evaluateIntegrity(docId, content);

    expect(result.integrityScore).to.equal(1.0);
    expect(result.match).to.be.true;
    expect(result.verdictSignature).to.have.lengthOf(128); // SHA-512 check
    expect(result.admissibleEvidence).to.be.true;
  });
});
