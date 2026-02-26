/* eslint-disable */
/* eslint-env node */
/*╔════════════════════════════════════════════════════════════════╗
  ║ TEST HELPER - FORENSIC TEST SETUP (v2.0 ESM)                  ║
  ╚════════════════════════════════════════════════════════════════╝*/
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto'; // SURGICAL FIX: Proper ESM import

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Global test variables
global.__TEST_MONGO_SERVER = null;
global.__TEST_EVIDENCE_PATH = path.join(__dirname, '../../__tests__/workers/evidence.json');

// Setup before all tests
before(async function() {
  this.timeout(30000);
    
  // Start in-memory MongoDB for Zero-Persistence Testing
  global.__TEST_MONGO_SERVER = await MongoMemoryServer.create();
  const mongoUri = global.__TEST_MONGO_SERVER.getUri();
    
  // Connect mongoose to virtual instance
  await mongoose.connect(mongoUri);
    
  console.log('🛡️  Wilsy OS: Test MongoDB Started (In-Memory)');
});

// Cleanup after each test: Ensures no cross-test data leakage
afterEach(async function() {
  const collections = mongoose.connection.collections;
  for (const key in collections) {
    await collections[key].deleteMany({});
  }
    
  if (fs.existsSync(global.__TEST_EVIDENCE_PATH)) {
    fs.unlinkSync(global.__TEST_EVIDENCE_PATH);
  }
});

// Final Teardown
after(async function() {
  await mongoose.disconnect();
  if (global.__TEST_MONGO_SERVER) {
    await global.__TEST_MONGO_SERVER.stop();
  }
  console.log('🧹 Wilsy OS: Test MongoDB Stopped');
});

// Forensic Helper: Generate Test Tenant ID
global.getTestTenantId = () => `tenant_test_${Date.now()}_${Math.random().toString(36).substring(7)}`;

// Forensic Helper: Generate Cryptographic Evidence (ESM Version)
global.generateTestEvidence = (auditEntries) => {
  const canonicalEntries = auditEntries.map(entry => {
    return Object.keys(entry).sort().reduce((obj, key) => {
      obj[key] = entry[key];
      return obj;
    }, {});
  });

  const entriesHash = crypto.createHash('sha256')
    .update(JSON.stringify(canonicalEntries))
    .digest('hex');

  return {
    auditEntries: canonicalEntries,
    hash: entriesHash,
    timestamp: new Date().toISOString()
  };
};
