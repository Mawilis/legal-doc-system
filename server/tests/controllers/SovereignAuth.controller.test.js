/* eslint-disable */
/**
 * 🧪 SovereignAuth Controller Audit
 * @description Verifying the secure dispatch of Sovereign Identity Tokens via the API.
 */
import { expect } from 'chai';
import { loginSovereign } from '../../controllers/auth/SovereignAuth.controller.js';

describe('🔐 SovereignAuth Controller Audit', () => {
  let mockReq;
  let mockRes;

  beforeEach(() => {
    mockReq = {
      body: {
        userId: 'WILSON_K_FOUNDER',
        biometricHash: 'SHA3_RETINA_DATA_2050'
      }
    };
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; },
      statusCode: null,
      body: null
    };
  });

  it('verifies sovereign identity and returns a sealed SIT with SHA-512 signature', async () => {
    await loginSovereign(mockReq, mockRes);

    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.message).to.equal('SOVEREIGN_IDENTITY_VERIFIED');
    expect(mockRes.body.sit_id).to.match(/^SIT-/);
    expect(mockRes.body.tokenSignature).to.have.lengthOf(128);
  });
});
