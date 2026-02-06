const fs = require('fs');

console.log('🔍 Checking server configuration...');

try {
    const serverContent = fs.readFileSync('server.js', 'utf8');
    
    // Look for port configuration
    const portMatch = serverContent.match(/port.*?(\d+)/i);
    const PORTMatch = serverContent.match(/PORT.*?(\d+)/i);
    const listenMatch = serverContent.match(/listen\(.*?(\d+)/);
    
    console.log('📊 Found port references:');
    if (portMatch) console.log(`   - port: ${portMatch[1]}`);
    if (PORTMatch) console.log(`   - PORT: ${PORTMatch[1]}`);
    if (listenMatch) console.log(`   - listen(): ${listenMatch[1]}`);
    
    // Check environment variable usage
    if (serverContent.includes('process.env.PORT')) {
        console.log('   - Using process.env.PORT');
    }
    
    // Check .env file
    if (fs.existsSync('.env')) {
        const envContent = fs.readFileSync('.env', 'utf8');
        const envPort = envContent.match(/PORT=(\d+)/);
        if (envPort) {
            console.log(`   - .env PORT: ${envPort[1]}`);
        }
    }
    
} catch (error) {
    console.error('Error:', error.message);
}
