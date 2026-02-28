import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
/*
 * @jest-environment node
 */

jest.unmock('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');

describe('Model Validation', () => {
  let mongoServer;

  beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri);
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  test('OnboardingSession model loads', () => {
    const OnboardingSession = require('../../models/OnboardingSession');
    expect(OnboardingSession).toBeDefined();
    expect(typeof OnboardingSession).toBe('function');
    console.log('✅ Model loaded successfully');
  });
});
