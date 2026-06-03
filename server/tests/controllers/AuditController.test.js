/* eslint-disable */
/**
 * 🧪 AuditController Forensic Audit
 * @description Verifying the retrieval and integrity of the Forensic HUD stream.
 */
import { expect } from 'chai';
import { getForensicStream } from '../../controllers/forensic/AuditController.js';

describe('🔍 AuditController Forensic Audit', () => {
  let mockReq;
  let mockRes;

  beforeEach(() => {
    mockReq = { params: { tenantId: 'TENANT-001' } };
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; },
      statusCode: null,
      body: null
    };
  });

  it('retrieves an authenticated forensic stream for a specific tenant', async () => {
    await getForensicStream(mockReq, mockRes);

    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.integrity).to.equal('AUTHENTICATED');
    expect(mockRes.body.stream).to.have.lengthOf(2);
    expect(mockRes.body.tenantId).to.equal('TENANT-001');
  });
});
