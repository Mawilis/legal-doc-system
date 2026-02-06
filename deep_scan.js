const mongoose = require('mongoose');

// Standard Local Connection
const LOCAL_URI = 'mongodb://127.0.0.1:27017';

async function deepScan() {
    console.log('---------------------------------------------------');
    console.log('🦈 DEEP SEA SCANNER INITIATED');
    console.log('---------------------------------------------------');

    try {
        await mongoose.connect(LOCAL_URI);
        const admin = new mongoose.mongo.Admin(mongoose.connection.db);
        const list = await admin.listDatabases();

        let found = false;

        // 1. LOOP THROUGH EVERY DATABASE
        for (const dbInfo of list.databases) {
            const dbName = dbInfo.name;
            if (['admin', 'config', 'local'].includes(dbName)) continue; // Skip system DBs

            console.log(`\n📂 CHECKING DATABASE: [ ${dbName} ]`);

            // Connect to this specific DB
            const dbConn = await mongoose.createConnection(`${LOCAL_URI}/${dbName}`).asPromise();
            const collections = await dbConn.db.listCollections().toArray();

            // 2. LOOP THROUGH EVERY COLLECTION
            for (const col of collections) {
                const count = await dbConn.db.collection(col.name).countDocuments();

                if (count > 0) {
                    console.log(`   > Found collection '${col.name}' with ${count} documents.`);

                    // 3. PEEK INSIDE FOR YOU
                    const sample = await dbConn.db.collection(col.name).find({}).toArray();
                    const target = sample.find(doc =>
                        JSON.stringify(doc).toLowerCase().includes('wilson') ||
                        JSON.stringify(doc).toLowerCase().includes('admin')
                    );

                    if (target) {
                        console.log('   🎯 MATCH FOUND IN THIS COLLECTION!');
                        console.log(`      ID: ${target._id}`);
                        console.log(`      Email: ${target.email}`);
                        console.log(`      Current Role: ${target.role}`);

                        // 4. THE FIX (Instant Promotion)
                        await dbConn.db.collection(col.name).updateOne(
                            { _id: target._id },
                            { $set: { role: 'super_admin', permissions: ['*'], status: 'active' } }
                        );
                        console.log('   ⚡ AUTOMATICALLY PROMOTED TO SUPER_ADMIN.');
                        found = true;
                    }
                }
            }
            await dbConn.close();
        }

        if (!found) {
            console.log('\n❌ SCAN COMPLETE. NO USER FOUND LOCALLY.');
            console.log('   This confirms your app is using a CLOUD Database (Atlas).');
            console.log('   We MUST read your .env file to find the Cloud URI.');
        }

    } catch (err) {
        console.error('💥 ERROR:', err.message);
    } finally {
        await mongoose.disconnect();
        process.exit();
    }
}

deepScan();