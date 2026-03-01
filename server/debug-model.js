#!import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { DocumentTemplate } from './models/DocumentTemplate.js';

async function debug() {
  try {
    console.log('🚀 Starting MongoDB memory server...');
    const mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();

    await mongoose.connect(mongoUri);
    console.log('✅ Test MongoDB connected');

    // Create a test template
    const testData = {
      tenantId: 'test-tenant-123',
      name: 'Test Contract Template',
      templateType: 'contract',
      practiceArea: 'commercial',
      content: {
        raw: 'Test content {{variable}}',
        format: 'handlebars',
      },
      variables: [
        {
          name: 'variable',
          type: 'string',
          required: true,
        },
      ],
      audit: {
        createdBy: 'test-user',
      },
    };

    console.log('\n📝 Creating template with data:', JSON.stringify(testData, null, 2));

    const template = new DocumentTemplate(testData);

    console.log('\n🔍 Before save:');
    console.log('  - templateId:', template.templateId);
    console.log('  - forensicHash:', template.forensicHash);
    console.log('  - retentionEnd:', template.retentionEnd);
    console.log('  - version:', template.version);

    const saved = await template.save();

    console.log('\n✅ After save:');
    console.log('  - templateId:', saved.templateId);
    console.log('  - forensicHash:', saved.forensicHash);
    console.log('  - retentionEnd:', saved.retentionEnd);
    console.log('  - version:', saved.version);
    console.log('  - status:', saved.status);

    // Verify the hash
    console.log('\n🔐 Hash verification:', saved.verifyIntegrity());

    await mongoose.disconnect();
    await mongoServer.stop();
    console.log('\n✅ Debug complete');
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

debug();
