#!/*
 * @jest-environment node
 */

const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');
const OnboardingSession = require('../../models/OnboardingSession.minimal');

describe('MINIMAL MODEL TEST', () => {
  let mongoServer;

  beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    await mongoose.connect(mongoServer.getUri());
    console.log('✅ Connected');
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  test('Model is function', () => {
    expect(typeof OnboardingSession).toBe('function');
  });

  test('Can create instance', () => {
    const session = new OnboardingSession({
      sessionId: 'test-123',
      tenantId: 'tenant-1',
      clientType: 'INDIVIDUAL',
      clientData: { test: true },
      metadata: { createdBy: 'test' },
    });
    expect(session).toBeDefined();
  });
});
