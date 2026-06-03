/* eslint-disable */
/**
 * 🧪 ClientPortal Forensic Audit
 * @description Verifying the secure retrieval of firm workspace data.
 */
import { expect } from 'chai';
import { getTenantWorkspace } from '../../controllers/tenant/ClientPortal.controller.js';

describe('🏢 ClientPortal Forensic Audit', () => {
  let mockReq;
  let mockRes;

  beforeEach(() => {
    mockReq = { params: { tenantId: 'TENANT-ROYAL-LOGISTICS' } };
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; },
      statusCode: null,
      body: null
    };
  });

  it('retrieves a cryptographically sealed workspace for a firm node', async () => {
    await getTenantWorkspace(mockReq, mockRes);

    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.data.tenantId).to.equal('TENANT-ROYAL-LOGISTICS');
    expect(mockRes.body.data.lastBilledAmount).to.equal(5255500);
    expect(mockRes.body.forensicAnchor).to.have.lengthOf(32);
    expect(mockRes.body.data.nodeIntegrity).to.equal('VERIFIED');
  });
});
