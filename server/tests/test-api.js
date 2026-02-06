const http = require('http');

console.log('🌐 Testing WILSY OS API Endpoints');
console.log('=================================\n');

const endpoints = [
    { path: '/healthz', method: 'GET', expected: 200 },
    { path: '/api/status', method: 'GET', expected: 200 },
    { path: '/api/migrations/status', method: 'GET', expected: 200 }
];

endpoints.forEach(({ path, method, expected }) => {
    const options = {
        hostname: 'localhost',
        port: 3000,
        path: path,
        method: method,
        timeout: 3000
    };

    const req = http.request(options, (res) => {
        console.log(`✅ ${method} ${path}: Status ${res.statusCode}`);
    });

    req.on('error', (err) => {
        console.log(`❌ ${method} ${path}: ${err.message}`);
    });

    req.on('timeout', () => {
        console.log(`⚠️  ${method} ${path}: Timeout`);
        req.destroy();
    });

    req.end();
});
