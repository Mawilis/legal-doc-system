/* eslint-disable */
import { expect } from 'chai';
import { getSystemSettings, updateSystemSettings } from '../../controllers/admin/SovereignSettings.controller.js';

describe('🛰️ Sovereign Settings Forensic Audit', () => {
  let mockRes;

  beforeEach(() => {
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; }
    };
  });

  it('allows the founder to update the Forensic Seal Fee to R10.00', async () => {
    const mockReq = { body: { newSettings: { forensicSealFee: 10.00 } } };
    await updateSystemSettings(mockReq, mockRes);

    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.message).to.equal('SYSTEM_LAWS_UPDATED_AND_ANCHORED');
    expect(mockRes.body.auditSignature).to.have.lengthOf(128);
  });
});
