/**
 * 🛡️ QuantumGuard Backend Forensic Audit (ESM)
 */
import { quantumGuard } from '../../middleware/forensic/quantumGuard.js';

describe('🛡️ QuantumGuard Backend Forensic Audit', () => {
  let mockReq;
  let mockRes;
  let nextFunction;

  beforeEach(() => {
    mockReq = {
      headers: {},
      method: 'GET',
      url: '/api/v1/vault'
    };
    mockRes = {
      status: function(code) {
        this.statusCode = code;
        return this;
      },
      json: function(data) {
        this.body = data;
        return this;
      },
      statusCode: null,
      body: null
    };
    nextFunction = () => {};
  });

  it('allows the request through in development mode', () => {
    let called = false;
    const next = () => { called = true; };
    quantumGuard(mockReq, mockRes, next);
    if (!called && process.env.NODE_ENV !== 'production') {
        throw new Error("Next function was not called");
    }
  });

  it('blocks the request if the forensic signature is missing in production', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    quantumGuard(mockReq, mockRes, () => {});

    const status = mockRes.statusCode;
    process.env.NODE_ENV = originalEnv;

    if (status !== 403) {
        throw new Error(`Expected 403, got ${status}`);
    }
  });
});
