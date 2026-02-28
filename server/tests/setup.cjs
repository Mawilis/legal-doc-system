// tests/setup.cjs - CommonJS setup file for Mocha tests
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const { randomBytes } = require('crypto');

// Import Mocha hooks - these are global in Mocha
// No need to require them, they're available globally

let mongoServer;

// Use Mocha's global hooks
before(async function() {
  this.timeout(30000); // Increase timeout for setup
  
  console.log('🚀 Starting MongoDB memory server...');
  mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();
  
  await mongoose.connect(mongoUri, {
    maxPoolSize: 10,
    minPoolSize: 2,
    socketTimeoutMS: 30000,
    connectTimeoutMS: 30000
  });
  
  console.log('✅ Test MongoDB connected');
});

after(async function() {
  this.timeout(10000);
  
  console.log('🧹 Cleaning up test environment...');
  await mongoose.disconnect();
  await mongoServer.stop();
  console.log('✅ Test environment cleaned up');
});

beforeEach(async function() {
  // Clear all collections
  const collections = mongoose.connection.collections;
  for (const key in collections) {
    await collections[key].deleteMany();
  }
});

// Global utilities
global.generateTestObjectId = () => new mongoose.Types.ObjectId();
global.createTestTenantId = () => `tenant-${Date.now()}-${randomBytes(4).toString('hex')}`;
global.waitFor = (ms) => new Promise(resolve => setTimeout(resolve, ms));
global.generateCorrelationId = () => `test-${Date.now()}-${randomBytes(8).toString('hex')}`;

module.exports = mongoose;
