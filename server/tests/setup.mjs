import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';

let mongod;

before(async function() {
  this.timeout(30000);
  mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  await mongoose.connect(uri);
  console.log('🚀 Starting MongoDB memory server via Native ESM...');
  console.log('✅ Test MongoDB connected');
});
beforeEach(async () => {
  const collections = mongoose.connection.collections;
  for (const key in collections) { await collections[key].deleteMany({}); }
});


after(async function() {
  await mongoose.disconnect();
  await mongod.stop();
  console.log('🧹 Cleaning up test environment...');
  console.log('✅ Test environment cleaned up');
});
