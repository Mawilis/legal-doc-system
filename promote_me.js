const mongoose = require('mongoose');
const path = require('path');
// Load the exact same .env file your server uses
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

const uri = process.env.MONGO_URI;

async function run() {
    console.log('---------------------------------------------------');
    console.log('🚀 INITIALIZING GOD MODE PROMOTION');
    console.log(`🔌 TARGET DB URI: ${uri ? uri.split('@')[1] || 'Localhost' : 'UNDEFINED!'}`);
    console.log('---------------------------------------------------');

    if (!uri) {
        console.error('❌ FATAL: MONGO_URI is missing in .env file');
        process.exit(1);
    }

    try {
        await mongoose.connect(uri);
        console.log('✅ Connected. Scanning for users...');

        // 1. FIND ANY USER (To verify connection)
        const users = await mongoose.connection.db.collection('users').find({}).toArray();

        if (users.length === 0) {
            console.log('⚠️  STILL 0 USERS FOUND.');
            console.log('   This means your App is likely using a different .env file location');
            console.log('   or the data was deleted.');
        } else {
            console.log(`✅ FOUND ${users.length} USER(S).`);

            // 2. FIND YOU (By Name or Email fuzzy match)
            // We search loosely for "Wilson" or "admin" to find the record
            const target = users.find(u =>
                (u.email && u.email.toLowerCase().includes('wilson')) ||
                (u.name && u.name.toLowerCase().includes('wilson'))
            );

            if (target) {
                console.log(`🎯 TARGET ACQUIRED: ${target.email} (${target.role})`);

                // 3. EXECUTE PROMOTION
                await mongoose.connection.db.collection('users').updateOne(
                    { _id: target._id },
                    {
                        $set: {
                            role: 'super_admin',
                            permissions: ['*'],
                            status: 'active'
                        }
                    }
                );
                console.log('⚡ GOD MODE ACTIVATED: Role set to SUPER_ADMIN.');
            } else {
                console.log('❌ Could not find a user matching "Wilson".');
                console.log('   Dumping available users for manual check:');
                users.forEach(u => console.log(`   - ${u.email} (${u.role})`));
            }
        }

    } catch (err) {
        console.error('💥 ERROR:', err.message);
    } finally {
        await mongoose.disconnect();
        process.exit();
    }
}

run();