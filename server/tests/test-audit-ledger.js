const mongoose = require('mongoose');
const { createAuditLedger } = require('./lib/auditLedger');

async function test() {
    console.log('Connecting to MongoDB...');
    await mongoose.connect(process.env.MONGO_URI_TEST || 'mongodb://localhost:27017/test');
    
    console.log('Creating audit ledger instance...');
    const ledger = createAuditLedger({ REQUIRE_TENANT_CONTEXT: false });
    
    console.log('Appending test audit entry...');
    const result = await ledger.append(
        { action: 'SYSTEM_STARTUP', component: 'auditLedger' },
        'test-tenant-001',
        { eventType: 'SYSTEM', userId: 'system' }
    );
    
    console.log('Result:', result);
    
    console.log('Verifying integrity...');
    const verification = await ledger.verifyIntegrity('test-tenant-001');
    console.log('Verification:', verification.valid ? '✅ VALID' : '❌ INVALID');
    
    await mongoose.disconnect();
    console.log('✅ Test completed successfully');
}

test().catch(console.error);
