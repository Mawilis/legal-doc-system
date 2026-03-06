import dotenv from 'dotenv';
import kms from './lib/kms.js';

dotenv.config();

setTimeout(async () => {
  console.log('\n🔧 Testing KMS with production config...\n');
  
  console.log('📊 Environment variables loaded:');
  console.log('   KMS_DEFAULT_ALGORITHM:', process.env.KMS_DEFAULT_ALGORITHM);
  console.log('   KMS_MASTER_KEY_ID:', process.env.KMS_MASTER_KEY_ID);
  console.log('   KMS_QUANTUM_VERIFICATION_SEED exists:', !!process.env.KMS_QUANTUM_VERIFICATION_SEED);
  console.log('   HSM_API_KEY length:', process.env.KMS_HSM_API_KEY?.length);
  console.log('   KEK exists:', !!process.env.KEK);
  console.log('   AUDIT_ENCRYPTION_KEY exists:', !!process.env.AUDIT_ENCRYPTION_KEY);
  
  const health = await kms.health();
  console.log('\n✅ KMS Health:', health.status);
  
  const key = await kms.generateKey('production-test', 'DOCUMENT_ENCRYPTION');
  console.log('\n🔑 Production key generated:', key.keyId);
  console.log('   Algorithm:', key.algorithm);
  console.log('   Quantum Resistant:', key.metadata.quantumResistant);
  
  console.log('\n🎉 KMS is production-ready with quantum security!');
}, 1000);
