import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import AuditLog from './models/auditLogModel.js';

async function debug() {
  console.log('🔍 DEBUGGING MODEL LOADING');
  console.log('==========================');
  
  // Check what's actually in the file at line 838
  console.log('\n📄 Checking actual file line 838:');
  const fs = await import('fs');
  const fileContent = fs.readFileSync('./models/auditLogModel.js', 'utf8');
  const lines = fileContent.split('\n');
  console.log(`Line 838: ${lines[837]}`); // Arrays are 0-indexed
  
  // Check the loaded model's middleware
  console.log('\n🔧 Loaded Model Middleware:');
  const preSaveHooks = AuditLog.schema.callQueue.filter(q => q[0] === 'pre' && q[1] === 'save');
  console.log('Pre-save hooks count:', preSaveHooks.length);
  
  // Test creating a document
  console.log('\n🧪 Test document creation:');
  const mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();
  await mongoose.connect(mongoUri);
  
  try {
    const testDoc = new AuditLog({
      tenantId: 'test-tenant',
      firmId: new mongoose.Types.ObjectId(),
      userId: new mongoose.Types.ObjectId(),
      userRole: 'test',
      action: 'DOCUMENT_VIEWED',
      category: 'DOCUMENT'
    });
    
    await testDoc.save();
    console.log('✅ Test document saved successfully');
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('Stack:', error.stack);
  }
  
  await mongoose.disconnect();
  await mongoServer.stop();
}

debug().catch(console.error);
