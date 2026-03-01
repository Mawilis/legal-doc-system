#!/* eslint-env mocha, node */
const assert = require('assert');
const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');

describe('Simple Test', () => {
  let mongoServer;
  let OnboardingSession;

  before(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri);
    OnboardingSession = require('../models/OnboardingSession');
  });

  after(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  it('should load model as function', () => {
    assert.strictEqual(typeof OnboardingSession, 'function');
  });

  it('should create instance', () => {
    const session = new OnboardingSession({
      sessionId: 'ONB_IND_TEST_001',
      tenantId: 'tenant-1',
      clientType: 'INDIVIDUAL',
      identityType: 'SA_ID',
      idNumber: '8001015009081',
      clientData: {
        firstName: 'Test',
        lastName: 'User',
        dateOfBirth: '1980-01-01',
        nationality: 'South African',
      },
      metadata: { createdBy: 'test' },
    });
    assert.ok(session);
  });
});
