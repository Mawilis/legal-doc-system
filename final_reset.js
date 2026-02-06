const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

/**
 * 💡 MANUAL OVERRIDE
 * Since your local scan showed 'legal-tech' as the active 1.06MB database,
 * we are targeting that specifically.
 */
const URI = 'mongodb://127.0.0.1:27017/legal-tech';

async function godMode() {
    console.log('---------------------------------------------------');
    console.log('🚀 [Wilsy OS] IDENTITY OVERRIDE INITIATED');
    console.log(`🔌 TARGET: ${URI}`);
    console.log('---------------------------------------------------');

    try {
        await mongoose.connect(URI);
        console.log('✅ Connection Established.');

        const email = 'wilsonkhanyezi@gmail.com';

        // 1. Clear any existing Wilson record to fix hash mismatches
        const del = await mongoose.connection.db.collection('users').deleteMany({
            email: new RegExp(`^${email}$`, 'i')
        });
        console.log(`🗑️  Cleared ${del.deletedCount} old records.`);

        // 2. Encrypt password correctly for Bcrypt comparison
        // Password: YourSecurePassword123
        const hashedPassword = await bcrypt.hash('YourSecurePassword123', 10);

        // 3. Inject the Super Admin
        const result = await mongoose.connection.db.collection('users').insertOne({
            name: 'Wilson Khanyezi',
            email: email,
            password: hashedPassword,
            role: 'super_admin',
            tenantId: '650c1f1e1f1e1f1e1f1e1f1e',
            status: 'active',
            permissions: ['*'],
            createdAt: new Date(),
            updatedAt: new Date()
        });

        if (result.insertedId) {
            console.log('---------------------------------------------------');
            console.log('⚡ GOD MODE ACTIVATED');
            console.log(`📧 Email: ${email}`);
            console.log('🔑 Pass:  YourSecurePassword123');
            console.log('🛡️  Role:  SUPER_ADMIN');
            console.log('---------------------------------------------------');
            console.log('👉 ACTION: Restart your gateway now: pm2 restart 0');
        }

    } catch (err) {
        console.error('💥 FATAL ERROR:', err.message);
    } finally {
        await mongoose.disconnect();
        process.exit();
    }
}

godMode();