const mongoose = require('mongoose');
require('dotenv').config();

const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI;

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