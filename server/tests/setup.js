// server/tests/setup.js
const mongoose = require('mongoose');
require('dotenv').config({ path: '.env.test' });

beforeAll(async () => {
    const uri = process.env.MONGO_URI_TEST;
    if (!uri) throw new Error('❌ MONGO_URI_TEST not found in .env.test file!');

    await mongoose.connect(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });

    console.log('✅ Connected to test MongoDB');
});

afterAll(async () => {
    console.log('🧹 Cleaning up test database...');

    if (mongoose.connection.readyState === 0) {
        console.warn('⚠️ Mongoose not connected. Skipping cleanup.');
        return;
    }

    try {
        const collectionsToClean = ['users', 'documents', 'clients', 'invoices', 'settings', 'alertlogs', 'notifications', 'instructions', 'deputies', 'chats', 'chatmessages'];

        for (const name of collectionsToClean) {
            const collection = mongoose.connection.collections[name];
            if (collection) {
                await collection.deleteMany({});
                console.log(`🧹 Cleared collection: ${name}`);
            }
        }

        await mongoose.disconnect();
        console.log('✅ Disconnected from test database');
    } catch (err) {
        console.error('❌ Cleanup error:', err.message);
    }
});
