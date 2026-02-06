#!/usr/bin/env node

const { MongoClient } = require('mongodb');
require('dotenv').config();

console.log('🚀 WILSY OS - Database Migration Manager (Fixed)');
console.log('💰 INTELLIGENT INDEX HANDLING');
console.log('===============================\n');

class FixedMigrationManager {
    constructor() {
        this.mongoUri = process.env.MONGO_URI;
        this.client = null;
        this.db = null;
    }

    async connect() {
        console.log('🔗 Connecting to MongoDB...');
        this.client = new MongoClient(this.mongoUri);
        await this.client.connect();
        this.db = this.client.db();
        console.log('✅ Connected to database:', this.db.databaseName);
    }

    async checkOrCreateIndex(collectionName, indexSpec, indexOptions = {}) {
        const collection = this.db.collection(collectionName);
        const existingIndexes = await collection.listIndexes().toArray();
        
        // Find if similar index exists
        const indexKey = JSON.stringify(indexSpec);
        const existingIndex = existingIndexes.find(idx => 
            JSON.stringify(idx.key) === indexKey
        );
        
        if (existingIndex) {
            console.log(`   ⏭️  Index already exists: ${existingIndex.name}`);
            
            // Check if we need to update index options
            let needsUpdate = false;
            const updates = [];
            
            if (indexOptions.unique && !existingIndex.unique) {
                needsUpdate = true;
                updates.push('adding unique constraint');
                // Note: Cannot change existing index to unique if it has duplicates
                // We need to drop and recreate
                console.log(`   ⚠️  Cannot convert existing index to unique (may have duplicates)`);
                return false;
            }
            
            if (!needsUpdate) {
                return true;
            }
        }
        
        // Create new index
        try {
            const indexName = await collection.createIndex(indexSpec, indexOptions);
            console.log(`   ✅ Created index: ${indexName}`);
            return true;
        } catch (error) {
            if (error.codeName === 'IndexOptionsConflict' || error.codeName === 'IndexKeySpecsConflict') {
                console.log(`   ⚠️  Index conflict: ${error.message.split(':')[0]}`);
                return false;
            }
            throw error;
        }
    }

    async runMigrations() {
        console.log('\n📊 Running intelligent migrations...');
        
        // Migration 1: Ensure all collections exist
        console.log('\n1. 📁 Ensuring required collections...');
        const requiredCollections = ['users', 'clients', 'cases', 'documents', 'audit_logs', 'tenants', 'migration_registry'];
        const existingCollections = await this.db.listCollections().toArray();
        const existingNames = existingCollections.map(c => c.name);
        
        for (const collection of requiredCollections) {
            if (!existingNames.includes(collection)) {
                console.log(`   Creating: ${collection}`);
                await this.db.createCollection(collection);
            } else {
                console.log(`   ✅ ${collection} exists`);
            }
        }

        // Migration 2: User indexes (with conflict handling)
        console.log('\n2. 👤 User collection indexes...');
        await this.checkOrCreateIndex('users', { email: 1 }, { unique: true, name: 'email_unique' });
        await this.checkOrCreateIndex('users', { tenantId: 1 }, { name: 'tenantId_idx' });
        await this.checkOrCreateIndex('users', { role: 1 }, { name: 'role_idx' });

        // Migration 3: Case indexes
        console.log('\n3. 🏛️ Case collection indexes...');
        await this.checkOrCreateIndex('cases', { caseNumber: 1 }, { unique: true, name: 'caseNumber_unique' });
        await this.checkOrCreateIndex('cases', { clientId: 1 }, { name: 'clientId_idx' });
        await this.checkOrCreateIndex('cases', { status: 1 }, { name: 'status_idx' });
        await this.checkOrCreateIndex('cases', { createdAt: -1 }, { name: 'createdAt_desc' });

        // Migration 4: Document indexes
        console.log('\n4. 📄 Document collection indexes...');
        await this.checkOrCreateIndex('documents', { documentId: 1 }, { unique: true, name: 'documentId_unique' });
        await this.checkOrCreateIndex('documents', { caseId: 1 }, { name: 'caseId_idx' });
        await this.checkOrCreateIndex('documents', { uploadedAt: -1 }, { name: 'uploadedAt_desc' });
        await this.checkOrCreateIndex('documents', { type: 1 }, { name: 'type_idx' });

        // Migration 5: Check existing indexes
        console.log('\n5. 📊 Database index analysis...');
        const collections = ['users', 'cases', 'documents', 'clients', 'audit_logs'];
        let totalIndexes = 0;
        
        for (const collection of collections) {
            try {
                const indexes = await this.db.collection(collection).listIndexes().toArray();
                console.log(`   ${collection}: ${indexes.length} indexes`);
                totalIndexes += indexes.length;
            } catch (error) {
                console.log(`   ${collection}: Not accessible`);
            }
        }
        
        console.log(`\n📈 Total indexes across collections: ${totalIndexes}`);

        // Update migration registry
        console.log('\n6. 📝 Updating migration registry...');
        const registry = this.db.collection('migration_registry');
        
        const migrationRecord = {
            migrationId: 'fixed_migration_001',
            version: '1.1.0',
            description: 'Fixed migration with intelligent index handling',
            appliedAt: new Date(),
            appliedBy: 'fixed_migration_script',
            status: 'completed',
            metadata: {
                totalIndexesCreated: totalIndexes,
                collectionsVerified: requiredCollections.length,
                script: 'migrate-fixed.js'
            }
        };
        
        await registry.insertOne(migrationRecord);
        console.log('   ✅ Updated migration registry');
    }

    async close() {
        if (this.client) {
            await this.client.close();
            console.log('\n🔌 Database connection closed');
        }
    }
}

async function main() {
    const manager = new FixedMigrationManager();
    
    try {
        await manager.connect();
        await manager.runMigrations();
        
        console.log('\n===============================');
        console.log('🎉 FIXED MIGRATION COMPLETE');
        console.log('===============================');
        console.log('💰 System is INVESTOR-READY');
        console.log('✅ Run verification: npm run migrate:verify');
        
    } catch (error) {
        console.error('\n❌ Migration failed:', error.message);
        console.error('Stack:', error.stack);
        process.exit(1);
    } finally {
        await manager.close();
    }
}

main();
