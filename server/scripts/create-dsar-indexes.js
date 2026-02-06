// Run with: node scripts/create-dsar-indexes.js
const mongoose = require('mongoose');
const DSARRequest = require('./models/DSARRequest');

async function createIndexes() {
  await mongoose.connect(process.env.MONGO_URI);
  
  const indexes = [
    { tenantId: 1, status: 1, slaDeadline: 1 },
    { tenantId: 1, 'dataSubject.userId': 1, submittedAt: -1 },
    { tenantId: 1, dsarType: 1, submittedAt: -1 },
    { tenantId: 1, 'dataSubject.email': 1, status: 1 },
    { tenantId: 1, assignedTo: 1, status: 1 },
    { referenceNumber: 1 }
  ];
  
  for (const index of indexes) {
    await DSARRequest.collection.createIndex(index);
  }
  
  console.log('DSAR request indexes created successfully');
  await mongoose.disconnect();
}

createIndexes().catch(console.error);
