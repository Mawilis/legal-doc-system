const mongoose = require('mongoose');
require('dotenv').config();

const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';

async function forcePromote() {
    try {
        await mongoose.connect(MONGO_URI);
        console.log('🔌 Connected to DB...');

        // REPLACE THIS WITH YOUR EMAIL
        const email = 'wilsonkhanyezi@gmail.com';

        const result = await mongoose.connection.db.collection('users').updateOne(
            { email: email },
            {
                $set: {
                    role: 'super_admin',
                    permissions: ['*'],
                    status: 'active'
                }
            }
        );

        if (result.matchedCount === 0) {
            console.log('❌ User not found! Check the email address.');
        } else {
            console.log('✅ GOD MODE ACTIVATED: User promoted to SUPER_ADMIN.');
        }
    } catch (err) {
        console.error(err);
    } finally {
        await mongoose.disconnect();
        console.log('👋 Done.');
        process.exit();
    }
}

forcePromote();