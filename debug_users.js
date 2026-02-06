const mongoose = require('mongoose');
require('dotenv').config();

const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';

async function listUsers() {
    try {
        await mongoose.connect(MONGO_URI);
        console.log(`🔌 Connected to DB: ${MONGO_URI}`);
        console.log('---------------------------------------------------');
        console.log('🔍 SCANNING USER REGISTRY...');

        // Fetch all users directly from the 'users' collection
        const users = await mongoose.connection.db.collection('users').find({}).toArray();

        if (users.length === 0) {
            console.log('⚠️  DATABASE IS EMPTY! No users found.');
        } else {
            console.log(`✅ FOUND ${users.length} USERS:`);
            users.forEach(u => {
                console.log(`   --------------------------------`);
                console.log(`   🆔 ID:    ${u._id}`);
                console.log(`   📧 EMAIL: ${u.email}`);
                console.log(`   👤 NAME:  ${u.name || u.firstName}`);
                console.log(`   🛡️ ROLE:  ${u.role}`);
                console.log(`   🏢 TENANT:${u.tenantId}`);
            });
            console.log('---------------------------------------------------');
        }

    } catch (err) {
        console.error('💥 ERROR:', err.message);
    } finally {
        await mongoose.disconnect();
        console.log('👋 Done.');
        process.exit();
    }
}

listUsers();