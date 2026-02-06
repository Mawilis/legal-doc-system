const fs = require('fs');
const path = require('path');

const verifyPath = path.join(__dirname, 'verify-migration-state.js');

console.log('🔧 Fixing verification script migration status display...');

try {
    let content = fs.readFileSync(verifyPath, 'utf8');
    
    // Find and fix the "EMPTY" message
    const emptyLine = '                console.log(\'⚠️  MIGRATION REGISTRY: COLLECTION EXISTS BUT EMPTY\');';
    const fixedLine = '                console.log(\`✅ MIGRATION REGISTRY: \${migrations.length} MIGRATION(S) FOUND\`);';
    
    content = content.replace(emptyLine, fixedLine);
    
    // Also fix the status assignment
    const statusLine = '                    status: \'EMPTY\',';
    const fixedStatus = '                    status: migrations.length > 0 ? \'POPULATED\' : \'EMPTY\',';
    
    content = content.replace(statusLine, fixedStatus);
    
    fs.writeFileSync(verifyPath, content);
    console.log('✅ Verification script fixed');
    
    // Show the changes
    console.log('\n📝 Changes made:');
    console.log('1. Changed "EMPTY" warning to show actual migration count');
    console.log('2. Updated status to show "POPULATED" when migrations exist');
    
} catch (error) {
    console.error('❌ Error fixing verification script:', error.message);
}
