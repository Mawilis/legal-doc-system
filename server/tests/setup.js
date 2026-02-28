/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ TEST SETUP - DOCUMENT GENERATION SYSTEM                                   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { jest } from '@jest/globals';
import { config } from 'dotenv';

config();

// Mock Redis
jest.unstable_mockModule('../config/redis.js', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    set: jest.fn(),
    setex: jest.fn(),
    del: jest.fn(),
    flushall: jest.fn(),
    quit: jest.fn()
  }
}));

// Mock logger
jest.unstable_mockModule('../utils/logger.js', () => ({
  __esModule: true,
  default: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

jest.unstable_mockModule('../utils/auditLogger.js', () => ({
  __esModule: true,
  default: {
    log: jest.fn()
  }
}));

// Global test setup
let mongoServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();
  await mongoose.connect(mongoUri);
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

beforeEach(async () => {
  // Clear all collections before each test
  const collections = mongoose.connection.collections;
  for (const key in collections) {
    await collections[key].deleteMany();
  }
  
  // Clear all mocks
  jest.clearAllMocks();
});

// Global test utilities
global.generateTestObjectId = () => new mongoose.Types.ObjectId();
global.createTestTenantId = () => `tenant-${Date.now()}-${Math.random().toString(36).substring(7)}`;
global.waitFor = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default mongoose;
