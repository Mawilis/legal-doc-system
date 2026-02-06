const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });
const User = require('./server/models/User'); // Ensure path is correct

const uri = process.env.MONGO_URI;

async function reset() {
    console.log('🚀 REBUILDING IDENTITY...');
    try {
        await mongoose.connect(uri);

        // 1. DELETE any existing Wilson user to clear corruption
        await User.deleteMany({ email: /wilson/i });

        // 2. CREATE a fresh, encrypted Super Admin
        const admin = new User({
            name: 'Wilson Khanyezi',
            email: 'wilsonkhanyezi@gmail.com', // MUST MATCH YOUR LOGIN ATTEMPT
            password: 'YourSecurePassword123', // SET THIS MANUALLY NOW
            role: 'super_admin',
            tenantId: '650c1f1e1f1e1f1e1f1e1f1e', // Standard Tenant
            status: 'active'
        });

        await admin.save(); // ✅ This triggers the Bcrypt Hashing

        console.log('---------------------------------------------------');
        console.log('✅ SUCCESS: Super Admin Recreated with Encrypted Password.');
        console.log(`📧 Email: ${admin.email}`);
        console.log(`🛡️  Role: ${admin.role}`);
        console.log('---------------------------------------------------');

    } catch (err) {
        console.error('💥 ERROR:', err.message);
    } finally {
        await mongoose.disconnect();
        process.exit();
    }
}

reset();
