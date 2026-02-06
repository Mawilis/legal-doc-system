const fs = require('fs');
const path = require('path');

const rollbackPath = path.join(__dirname, 'rollback-migration.js');

console.log('🔧 Fixing rollback script DNS timeout handling...');

try {
    let content = fs.readFileSync(rollbackPath, 'utf8');
    
    // Add better MongoDB connection options with retry and timeout handling
    const searchText = 'new MongoClient(this.config.MONGO_URI';
    const replacement = 'new MongoClient(this.config.MONGO_URI, {\n' +
        '            serverSelectionTimeoutMS: 10000,\n' +
        '            connectTimeoutMS: 15000,\n' +
        '            socketTimeoutMS: 45000,\n' +
        '            retryWrites: true,\n' +
        '            retryReads: true\n' +
        '        }';
    
    content = content.replace(searchText, replacement);
    
    // Add DNS timeout handling
    const connectMethod = content.indexOf('async connect()');
    if (connectMethod !== -1) {
        const beforeConnect = content.substring(0, connectMethod);
        const afterConnect = content.substring(connectMethod);
        
        // Add DNS retry logic
        const dnsRetryCode = `
    async connect() {
        let lastError;
        const maxRetries = 3;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(\`🔗 Connection attempt \${attempt}/\${maxRetries}...\`);
                this.dbConnection = new MongoClient(this.config.MONGO_URI, {
                    serverSelectionTimeoutMS: 10000,
                    connectTimeoutMS: 15000,
                    socketTimeoutMS: 45000,
                    retryWrites: true,
                    retryReads: true
                });
                
                await this.dbConnection.connect();
                this.db = this.dbConnection.db();
                console.log(\`✅ Connected to database: \${this.db.databaseName}\`);
                return;
                
            } catch (error) {
                lastError = error;
                console.log(\`⚠️  Connection attempt \${attempt} failed: \${error.message}\`);
                
                if (attempt < maxRetries) {
                    const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
                    console.log(\`⏳ Retrying in \${delay}ms...\`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        throw new Error(\`Failed to connect after \${maxRetries} attempts: \${lastError.message}\`);
    }
`;
        
        // Replace the entire connect method
        const methodEnd = afterConnect.indexOf('}', afterConnect.indexOf('{')) + 1;
        const newContent = beforeConnect + dnsRetryCode + afterConnect.substring(methodEnd);
        content = newContent;
    }
    
    fs.writeFileSync(rollbackPath, content);
    console.log('✅ Rollback script updated with DNS retry logic');
    
} catch (error) {
    console.error('❌ Error fixing rollback script:', error.message);
}
