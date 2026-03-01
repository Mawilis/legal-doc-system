#!/* eslint-env mocha, node */
const assert = require('assert');
const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');

describe('✅ Stage Advancement - FIXED', () => {
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

  it('OPTION 1: Use createSession (recommended)', async () => {
    const session = await OnboardingSession.createSession('tenant-1', {
      clientType: 'INDIVIDUAL',
      identityType: 'SA_ID',
      idNumber: '8001015009081',
      clientData: {
        firstName: 'John',
        lastName: 'Doe',
        dateOfBirth: '1980-01-01',
        nationality: 'South African',
      },
      metadata: { createdBy: 'test' },
    });

    console.log('Initial stages with createSession:', session.stages.length);
    assert.strictEqual(session.stages.length, 1);

    await session.advanceStage('CLIENT_INFO', { test: 'data' }, 'tester');
    console.log('After advanceStage:', session.stages.length);
    assert.strictEqual(session.stages.length, 2);
  });

  it('OPTION 2: Add INITIATED stage manually', async () => {
    const sessionId = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');

    const session = new OnboardingSession({
      sessionId,
      tenantId: 'tenant-1',
      clientType: 'INDIVIDUAL',
      identityType: 'SA_ID',
      idNumber: '8001015009081',
      clientData: {
        firstName: 'Jane',
        lastName: 'Doe',
        dateOfBirth: '1980-01-01',
        nationality: 'South African',
      },
      stages: [
        {
          stage: 'INITIATED',
          status: 'COMPLETED',
          timestamp: new Date(),
          performedBy: 'system',
        },
      ],
      metadata: { createdBy: 'test' },
    });

    await session.save();
    console.log('Initial stages with manual INITIATED:', session.stages.length);
    assert.strictEqual(session.stages.length, 1);

    await session.advanceStage('CLIENT_INFO', { test: 'data' }, 'tester');
    console.log('After advanceStage:', session.stages.length);
    assert.strictEqual(session.stages.length, 2);
  });
});
