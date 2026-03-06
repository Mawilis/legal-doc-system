const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

let mongod;

before(async function() {
  this.timeout(30000);
  mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  await mongoose.connect(uri);
  console.log('🚀 Starting MongoDB memory server...');
  console.log('✅ Test MongoDB connected');
});

after(async function() {
  await mongoose.disconnect();
  await mongod.stop();
  console.log('🧹 Cleaning up test environment...');
  console.log('✅ Test environment cleaned up');
});
