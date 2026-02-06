const mongoose = require('mongoose');

// We connect to the admin level to see all DBs
const MONGO_URI = 'mongodb://127.0.0.1:27017';

async function scanServer() {
    try {
        await mongoose.connect(MONGO_URI);
        console.log(`📡 RADAR ACTIVE: Scanning ${MONGO_URI}...`);

        const admin = new mongoose.mongo.Admin(mongoose.connection.db);
        const result = await admin.listDatabases();

        console.log('\n📊 DATABASE REPORT:');
        console.log('-------------------');

        for (const dbInfo of result.databases) {
            const sizeMb = (dbInfo.sizeOnDisk / 1024 / 1024).toFixed(2);
            console.log(`💽 DB Name: [ ${dbInfo.name} ]  (Size: ${sizeMb} MB)`);

            // Peek inside to see if it has a 'users' collection
            if (dbInfo.sizeOnDisk > 0 && !['admin', 'config', 'local'].includes(dbInfo.name)) {
                const tempConn = await mongoose.createConnection(`${MONGO_URI}/${dbInfo.name}`).asPromise();
                const collections = await tempConn.db.listCollections().toArray();
                const colNames = collections.map(c => c.name);

                if (colNames.includes('users')) {
                    const count = await tempConn.db.collection('users').countDocuments();
                    console.log(`   ✅ FOUND MATCH: Contains 'users' collection with ${count} records.`);
                    console.log(`   👉 THIS IS YOUR TARGET DATABASE.`);
                } else {
                    console.log(`   ❌ No users table found here.`);
                }
                await tempConn.close();
            }
        }
        console.log('-------------------');

    } catch (err) {
        console.error('Connection Failed:', err.message);
    } finally {
        await mongoose.disconnect();
        process.exit();
    }
}

scanServer();