const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

async function test() {
    try {
        console.log('1. Starting MongoDB Memory Server...');
        const mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        
        console.log('2. Connecting to MongoDB...');
        await mongoose.connect(uri);
        
        console.log('3. Loading model...');
        const OnboardingSession = require('./models/OnboardingSession');
        
        console.log('4. Model type:', typeof OnboardingSession);
        console.log('5. Model is function:', typeof OnboardingSession === 'function');
        
        if (typeof OnboardingSession === 'function') {
            console.log('6. Creating instance...');
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' }
            });
            
            console.log('7. Saving to database...');
            const saved = await session.save();
            console.log('8. Saved with ID:', saved._id);
            
            console.log('✅ SUCCESS! Model works perfectly.');
        } else {
            console.log('❌ Model is not a function');
        }
        
        await mongoose.disconnect();
        await mongoServer.stop();
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

test();
