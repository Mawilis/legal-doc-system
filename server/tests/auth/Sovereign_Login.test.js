/* eslint-disable */
import { expect } from 'chai';
import { sovereignLogin } from '../../controllers/auth/Sovereign_Login.controller.js';

describe('🏛️ Sovereign Login Forensic Audit', () => {
  let mockRes;

  beforeEach(() => {
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; }
    };
  });

  it('grants access to the Founder with a valid SIT and Secret Key', async () => {
    const mockReq = {
      body: {
        sit_id: 'SIT-WILSON-MASTER-2050',
        secretKey: 'BIBLICAL_WORTH_2050',
        fingerprint: 'MAC-PRO-M3-FOUNDER'
      }
    };

    await sovereignLogin(mockReq, mockRes);

    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.session.role).to.equal('FOUNDER');
    expect(mockRes.body.session.authSeal).to.have.lengthOf(128);
  });

  it('denies access if the Secret Key is incorrect', async () => {
    const mockReq = { body: { sit_id: 'SIT-WILSON-MASTER-2050', secretKey: 'WRONG_KEY' } };
    await sovereignLogin(mockReq, mockRes);
    expect(mockRes.statusCode).to.equal(403);
  });
});
