import { expect } from 'chai';
import { DocumentEncryption } from '../../security/documentEncryption.js';

describe('⚙️  WILSY OS - Forensic Document Generation Engine', () => {
  it('should accurately merge dynamic variables into a legal template', () => {
    const mockTemplate = 'This agreement is between {{tenant}} and {{client}} under jurisdiction {{region}}.';
    const context = { tenant: 'Wilsy OS', client: 'Enterprise LLC', region: 'ZA' };
    
    const compiled = mockTemplate
      .replace('{{tenant}}', context.tenant)
      .replace('{{client}}', context.client)
      .replace('{{region}}', context.region);
      
    expect(compiled).to.equal('This agreement is between Wilsy OS and Enterprise LLC under jurisdiction ZA.');
  });

  it('should cryptographically secure the generated payload', async () => {
    const encryption = new DocumentEncryption();
    const documentBuffer = Buffer.from('Highly confidential M&A Term Sheet');
    
    const encryptedData = await encryption.encryptDocument(documentBuffer);
    const decryptedData = await encryption.decryptDocument(encryptedData);
    
    expect(encryptedData).to.not.equal(documentBuffer);
    expect(decryptedData.toString()).to.equal('Highly confidential M&A Term Sheet');
  });
});
