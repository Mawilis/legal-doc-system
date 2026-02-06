const http = require('http');

console.log('🔍 Quick Server Test');
console.log('===================\n');

// Check if server is running
const options = {
    hostname: 'localhost',
    port: 3001,
    path: '/healthz',
    method: 'GET',
    timeout: 3000
};

const req = http.request(options, (res) => {
    console.log(`✅ Server responded with status: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const json = JSON.parse(data);
            console.log(`📊 Service: ${json.service}`);
            console.log(`💰 Score: ${json.score}`);
            console.log(`🚀 Investor Ready: ${json.investorReady}`);
            console.log(`\n🌐 Dashboard URL: http://localhost:3001/dashboard`);
        } catch (e) {
            console.log('⚠️ Could not parse response as JSON');
        }
    });
});

req.on('error', (err) => {
    console.log(`❌ Server is not running: ${err.message}`);
    console.log('\n💡 Start the server with:');
    console.log('   node demo-server-fixed.js');
    console.log('   OR');
    console.log('   ./start-investor-demo.sh');
});

req.on('timeout', () => {
    console.log('⚠️ Request timeout - server may be starting');
});

req.end();
