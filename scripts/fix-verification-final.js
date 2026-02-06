const fs = require('fs');
const path = require('path');

const verifyPath = path.join(__dirname, 'verify-migration-state.js');

console.log('🔧 Final fix for migration verification...');

try {
    let content = fs.readFileSync(verifyPath, 'utf8');
    
    // Find the migration verification section (around line 290-310)
    // We need to change how it reads migration data
    
    const startMarker = 'const Migration = mongoose.model(\'Migration\', MigrationSchema);';
    const endMarker = 'const hasRollbacks = migrations.some(m => m.rolledBackAt);';
    
    if (content.includes(startMarker)) {
        // Replace the Mongoose-based migration check with direct MongoDB query
        const oldSection = content.substring(
            content.indexOf(startMarker),
            content.indexOf(endMarker) + endMarker.length
        );
        
        const newSection = `
            // Direct MongoDB query for migration registry
            const migrationCollection = this.db.collection('migration_registry');
            const migrations = await migrationCollection.find({}).sort({ appliedAt: -1 }).toArray();
            
            if (migrations.length === 0) {
                this.verificationResults.migrations = {
                    status: 'EMPTY',
                    details: [],
                    actionRequired: 'Apply initial migrations',
                    severity: 'HIGH'
                };
                console.log(\`⚠️  MIGRATION REGISTRY: COLLECTION EXISTS BUT EMPTY\`);
                return;
            }
            
            // Analyze migration health
            const latestMigration = migrations[0];
            const hasRollbacks = migrations.some(m => m.rolledBackAt || m.status === 'rolled_back');
        `;
        
        content = content.replace(oldSection, newSection);
        
        // Also update the success message
        const successMessage = 'console.log(\`✅ MIGRATION REGISTRY: ${migrations.length} MIGRATION(S) FOUND\`);';
        content = content.replace(
            'console.log(\`✅ MIGRATION REGISTRY: ${migrations.length} MIGRATION(S) FOUND\`);',
            'console.log(\`✅ MIGRATION REGISTRY: ${migrations.length} MIGRATION(S) FOUND - SYSTEM MIGRATED\`);'
        );
        
        fs.writeFileSync(verifyPath, content);
        console.log('✅ Verification script fully fixed');
        console.log('\n📝 Changes:');
        console.log('1. Changed from Mongoose to direct MongoDB query');
        console.log('2. Updated success message to show actual count');
        
    } else {
        console.log('⚠️  Could not find the migration verification section');
        console.log('The script structure may have changed');
    }
    
} catch (error) {
    console.error('❌ Error:', error.message);
}
