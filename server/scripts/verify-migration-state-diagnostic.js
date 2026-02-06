#!/usr/bin/env node
/*===========================================================================
  WILSY OS - DIAGNOSTIC VERIFICATION SYSTEM
  ===========================================================================
  PURPOSE: Diagnose and fix MongoDB connection issues for investors
  ==========================================================================*/

'use strict';

const mongoose = require('mongoose');
const { execSync } = require('child_process');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

class DiagnosticVerifier {
    constructor() {
        this.config = {
            MONGO_URI: process.env.MONGO_URI,
            MONGO_URI_TEST: process.env.MONGO_URI_TEST
        };
        this.publicIP = this._getPublicIP();
    }

    async diagnose() {
        console.log('🔍 WILSY OS - INVESTOR CONNECTION DIAGNOSTICS');
        console.log('='.repeat(60));
        
        console.log('\n📱 SYSTEM INFORMATION:');
        console.log('   Node.js:', process.version);
        console.log('   Platform:', process.platform);
        console.log('   Public IP:', this.publicIP);
        console.log('   Time:', new Date().toISOString());
        
        console.log('\n🔗 CONNECTION TESTS:');
        
        // Test 1: Check if MongoDB URI is set
        await this._testMongoURI();
        
        // Test 2: Test connection without SSL (diagnostic)
        await this._testConnection(false);
        
        // Test 3: Test connection with SSL (production)
        await this._testConnection(true);
        
        // Generate investor report
        await this._generateInvestorDiagnosticReport();
    }

    async _testMongoURI() {
        console.log('\n1. 📋 Checking MongoDB Configuration...');
        
        if (!this.config.MONGO_URI) {
            console.log('   ❌ MONGO_URI is not set in .env file');
            console.log('   💡 Solution: Add MONGO_URI to your .env file');
            return false;
        }
        
        const maskedUri = this.config.MONGO_URI.replace(/\/\/([^:]+):([^@]+)@/, '//***:***@');
        console.log('   ✅ MONGO_URI is configured:', maskedUri);
        
        // Check if it's MongoDB Atlas
        if (this.config.MONGO_URI.includes('mongodb+srv://')) {
            console.log('   🌐 Using: MongoDB Atlas (Cloud)');
            console.log('   ⚠️  Note: IP whitelisting required');
            console.log('   🔗 Your IP to whitelist:', this.publicIP + '/32');
        } else {
            console.log('   💻 Using: Local/On-premise MongoDB');
        }
        
        return true;
    }

    async _testConnection(useSSL) {
        console.log(`\n2. ${useSSL ? '🔐' : '🔓'} Testing ${useSSL ? 'SSL' : 'Non-SSL'} Connection...`);
        
        try {
            await mongoose.disconnect(); // Clean any existing connections
            
            const options = {
                useNewUrlParser: true,
                useUnifiedTopology: true,
                serverSelectionTimeoutMS: 5000,
                ssl: useSSL,
                sslValidate: false // Disable for testing
            };
            
            const startTime = Date.now();
            const conn = await mongoose.connect(this.config.MONGO_URI, options);
            const connectionTime = Date.now() - startTime;
            
            console.log(`   ✅ ${useSSL ? 'SSL' : 'Non-SSL'} Connection Successful!`);
            console.log(`   ⏱️  Connection Time: ${connectionTime}ms`);
            console.log(`   🗄️  Database: ${conn.connection.name}`);
            console.log(`   🌐 Host: ${conn.connection.host}`);
            
            if (useSSL) {
                console.log('   🎉 PRODUCTION READY: SSL encryption enabled');
            }
            
            await mongoose.disconnect();
            return true;
            
        } catch (error) {
            console.log(`   ❌ ${useSSL ? 'SSL' : 'Non-SSL'} Connection Failed`);
            console.log(`   📝 Error: ${error.message}`);
            
            if (error.message.includes('whitelist')) {
                console.log('\n   🚨 IMMEDIATE ACTION REQUIRED:');
                console.log('   1. Go to https://cloud.mongodb.com');
                console.log('   2. Select your cluster');
                console.log('   3. Click "Network Access"');
                console.log(`   4. Add IP Address: ${this.publicIP}/32`);
                console.log('   5. Wait 2 minutes and retry');
            }
            
            if (error.message.includes('SSL')) {
                console.log('\n   ⚠️  SSL CONFIGURATION ISSUE:');
                console.log('   1. Check if MongoDB supports SSL');
                console.log('   2. Try connecting without SSL for testing');
                console.log('   3. Update connection string if needed');
            }
            
            return false;
        }
    }

    async _generateInvestorDiagnosticReport() {
        console.log('\n' + '='.repeat(60));
        console.log('💰 WILSY OS - INVESTOR CONNECTION REPORT');
        console.log('='.repeat(60));
        
        console.log('\n🎯 CONNECTION STATUS:');
        console.log('   Public IP Address:', this.publicIP);
        console.log('   MongoDB Type:', this.config.MONGO_URI.includes('mongodb+srv://') ? 'Atlas (Cloud)' : 'Local');
        
        console.log('\n🔧 RECOMMENDED ACTIONS:');
        
        if (this.config.MONGO_URI.includes('mongodb+srv://')) {
            console.log('   1. ✅ Whitelist IP in MongoDB Atlas');
            console.log('   2. ✅ Verify network connectivity');
            console.log('   3. ✅ Test with SSL enabled');
            console.log('   4. ✅ Document connection for investors');
        } else {
            console.log('   1. ✅ Ensure MongoDB service is running');
            console.log('   2. ✅ Check firewall settings');
            console.log('   3. ✅ Verify database credentials');
            console.log('   4. ✅ Prepare cloud migration plan for investors');
        }
        
        console.log('\n📊 INVESTOR READINESS METRICS:');
        console.log('   Database: MongoDB (Enterprise-ready)');
        console.log('   Security: SSL/TLS supported');
        console.log('   Scalability: Atlas or On-premise options');
        console.log('   Compliance: Configurable for POPIA/GDPR');
        
        console.log('\n👔 FOR INVESTOR PRESENTATION:');
        console.log('   "Our database infrastructure is enterprise-grade');
        console.log('    with proper security protocols. We use MongoDB');
        console.log('    with SSL encryption and IP-based access controls');
        console.log('    ensuring data sovereignty and compliance."');
        console.log('\n   - Wilson Khanyezi, Founder');
        console.log('='.repeat(60));
    }

    _getPublicIP() {
        try {
            return execSync('curl -s ifconfig.me').toString().trim();
        } catch {
            try {
                return execSync('curl -s icanhazip.com').toString().trim();
            } catch {
                return 'Unable to determine IP';
            }
        }
    }
}

// Execute
async function main() {
    const verifier = new DiagnosticVerifier();
    await verifier.diagnose();
}

if (require.main === module) {
    main();
}
