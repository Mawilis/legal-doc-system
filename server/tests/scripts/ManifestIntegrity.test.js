/* eslint-disable */
/**
 * 🧪 ManifestIntegrity Forensic Audit
 * @description Verifying the "Proof of Worth" for Wilsy OS investors.
 */
import { expect } from 'chai';
import fs from 'fs';

describe('📜 ManifestIntegrity Forensic Audit', () => {
  const manifestPath = '/Users/wilsonkhanyezi/legal-doc-system/server/dist/Sovereign_Manifest.json';

  it('contains the correct R120B+ valuation anchor and SHA-512 master signature', () => {
    const content = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

    expect(content.projectName).to.equal('Wilsy OS');
    expect(content.valuationAnchor).to.equal('R120B+');
    expect(content.masterSignature).to.have.lengthOf(128);
    expect(content.coreComponents).to.have.lengthOf(5);
  });
});
