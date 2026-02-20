const path = require('path');

console.log('=== Current Working Directory ===');
console.log(process.cwd());

console.log('\n=== Checking absolute paths ===');
const possiblePaths = [
    path.resolve(process.cwd(), 'utils/logger.js'),
    path.resolve(process.cwd(), 'utils/auditLogger.js'),
    path.resolve(process.cwd(), 'utils/cryptoUtils.js'),
    path.resolve(process.cwd(), 'utils/redactUtils.js'),
    path.resolve(process.cwd(), 'config/security.js'),
    path.resolve(process.cwd(), 'middleware/tenantContext.js')
];

possiblePaths.forEach(filePath => {
    try {
        require.resolve(filePath);
        console.log(`✅ Found: ${filePath}`);
    } catch (err) {
        console.log(`❌ Not found: ${filePath}`);
    }
});

console.log('\n=== Testing require from different locations ===');

// Test requiring from security/middleware/core.js location
const coreJsPath = path.resolve(process.cwd(), 'security/middleware/core.js');
console.log(`Testing require from: ${coreJsPath}`);

try {
    const utilsPath = path.resolve(process.cwd(), 'utils/logger.js');
    const relative = path.relative(path.dirname(coreJsPath), utilsPath);
    console.log(`Relative path from core.js to logger.js: ${relative}`);
    
    // Try to resolve using the relative path
    const resolved = require.resolve(relative);
    console.log(`✅ Resolved: ${resolved}`);
} catch (err) {
    console.log(`❌ Failed: ${err.message}`);
}
