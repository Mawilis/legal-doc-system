const mongoose = require('mongoose');
require('dotenv').config();

async function testAtlasConnection() {
  try {
    console.log('🔐 Testing MongoDB Atlas Connection...');
    console.log('📡 This verifies IP whitelisting is working');

    // Get masked URI for logging
    const uri = process.env.MONGO_URI;
    const maskedUri = uri.replace(/\/\/([^:]+):([^@]+)@/, '//*:*@');
    console.log(`🔗 Attempting to connect to: ${maskedUri}`);

    // Try connection without SSL first to diagnose
    const testUri = uri + '&ssl=false';
    console.log('\n🔄 Testing connection (diagnostic mode)...');

    const conn = await mongoose.connect(testUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 10000,
    });

    console.log('✅ SUCCESS: Connected to MongoDB Atlas!');
    console.log(`🏷️  Database: ${conn.connection.name}`);
    console.log(`🌐 Host: ${conn.connection.host}`);
    console.log(`⚡ Ready State: ${conn.connection.readyState}`);

    // Test SSL connection
    console.log('\n🔐 Testing SSL connection...');
    await mongoose.disconnect();

    const sslConn = await mongoose.connect(uri, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 10000,
      ssl: true,
    });

    console.log('✅ SSL Connection Successful!');
    console.log('🎉 MongoDB Atlas is properly configured!');

    await mongoose.disconnect();
    console.log('\n🚀 WILSY OS - DATABASE CONFIGURATION VERIFIED');
    console.log('💰 READY FOR INVESTOR DEMONSTRATION');
  } catch (error) {
    console.error('\n❌ CONNECTION FAILED');
    console.error(`Error: ${error.message}`);

    if (error.message.includes('whitelist')) {
      console.log('\n🔧 IMMEDIATE ACTION REQUIRED:');
      console.log('1. Go to MongoDB Atlas Dashboard');
      console.log('2. Click "Network Access"');
      console.log('3. Add your current IP address');
      console.log('4. Wait 2 minutes and retry');
      console.log(
        '\n📱 Your IP is likely:',
        require('child_process').execSync('curl -s ifconfig.me').toString().trim()
      );
    }

    process.exit(1);
  }
}

testAtlasConnection();
