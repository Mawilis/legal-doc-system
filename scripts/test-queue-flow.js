import { addEmbeddingJob, getQueueStatus } from '../server/queues/embeddingQueue.js';

async function testFlow() {
  console.log('--- Starting Queue Test (ESM Mode) ---');
  
  const testData = {
    text: 'Legal test document for embedding.',
    precedentId: '507f1f77bcf86cd799439011',
    tenantId: 'test-tenant'
  };

  try {
    const job = await addEmbeddingJob(testData);
    console.log('✅ Job added successfully. ID:', job.id);
    
    const status = await getQueueStatus();
    console.log('📊 Current Queue Status:', JSON.stringify(status, null, 2));
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }
}

testFlow();
