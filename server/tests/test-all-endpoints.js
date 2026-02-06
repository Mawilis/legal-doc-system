const http = require('http');

console.log('🧪 Testing WILSY OS Investor Endpoints');
console.log('======================================\n');

const endpoints = [
    { name: 'Health Check', path: '/healthz', method: 'GET' },
    { name: 'Migration Status', path: '/api/migrations/status', method: 'GET' },
    { name: 'System Status', path: '/api/status', method: 'GET' },
    { name: 'Investor Dashboard API', path: '/api/investor/dashboard', method: 'GET' }
];

endpoints.forEach(({ name, path, method }) => {
    const options = {
        hostname: 'localhost',
        port: 3001,
        path: path,
        method: method,
        timeout: 5000
    };

    console.log(`Testing: ${name} (${method} ${path})`);
    
    const req = http.request(options, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
            data += chunk;
        });
        
        res.on('end', () => {
            try {
                const json = JSON.parse(data);
                console.log(`✅ Status: ${res.statusCode}`);
                
                // Show specific data for each endpoint
                if (path === '/healthz') {
                    console.log(`   • Investor Ready: ${json.investorReady}`);
                    console.log(`   • Score: ${json.score}`);
                } else if (path === '/api/migrations/status') {
                    console.log(`   • Migration Count: ${json.migrationCount}`);
                    console.log(`   • Investor Score: ${json.investorScore}`);
                } else if (path === '/api/investor/dashboard') {
                    console.log(`   • System Status: ${json.systemStatus}`);
                    console.log(`   • Components: ${json.components.length}`);
                }
                
            } catch (e) {
                console.log(`⚠️  Response is not JSON or invalid`);
            }
            console.log('');
        });
    });

    req.on('error', (err) => {
        console.log(`❌ Error: ${err.message}\n`);
    });

    req.on('timeout', () => {
        console.log(`⚠️  Timeout: Request took too long\n`);
        req.destroy();
    });

    req.end();
});

console.log('🎯 Dashboard available at: http://localhost:3001/dashboard');
