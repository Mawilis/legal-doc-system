const { MongoClient } = require('mongodb');
require('dotenv').config();

async function testConnection() {
    console.log('🔗 Testing MongoDB Atlas Connection');
    console.log('💰 PRODUCTION CONNECTION TEST');
    console.log('===============================\n');
    
    const options = {
        serverSelectionTimeoutMS: 10000,
        connectTimeoutMS: 15000,
        socketTimeoutMS: 45000,
        retryWrites: true,
        retryReads: true
    };
    
    const client = new MongoClient(process.env.MONGO_URI, options);
    
    try {
        console.log('Attempting connection...');
        const start = Date.now();
        await client.connect();
        const duration = Date.now() - start;
        
        const db = client.db();
        console.log(`✅ Connected in ${duration}ms`);
        console.log(`📊 Database: ${db.databaseName}`);
        
        // Test a simple query
        const collections = await db.listCollections().toArray();
        console.log(`📁 Collections: ${collections.length}`);
        
        // Test migration registry
        const registry = db.collection('migration_registry');
        const migrations = await registry.countDocuments();
        console.log(`📋 Migration records: ${migrations}`);
        
        console.log('\n🎉 Connection test PASSED');
        console.log('💰 System is READY for production');
        
    } catch (error) {
        console.error(`❌ Connection failed: ${error.message}`);
        console.log('\n🔧 Troubleshooting steps:');
        console.log('1. Check MONGO_URI in .env file');
        console.log('2. Check internet connection');
        console.log('3. Verify MongoDB Atlas cluster is running');
        console.log('4. Check firewall settings');
        
    } finally {
        await client.close();
        console.log('\n🔌 Connection closed');
    }
}

testConnection();
