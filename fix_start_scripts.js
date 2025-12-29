const fs = require('fs');
const path = require('path');

console.log('🔧 RESTORING MISSING START SCRIPTS...');

// 1. BILLING CONFIG
const billingPath = path.join(__dirname, 'services/billing/package.json');
const billingPkg = {
  "name": "svc-billing",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": { "start": "node index.js" },  // <--- THIS WAS MISSING
  "dependencies": { "express": "^4.18.2", "cors": "^2.8.5" }
};
fs.writeFileSync(billingPath, JSON.stringify(billingPkg, null, 2));
console.log('✅ FIXED: Billing package.json');

// 2. AI CONFIG
const aiPath = path.join(__dirname, 'services/ai/package.json');
const aiPkg = {
  "name": "svc-ai",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": { "start": "node index.js" },  // <--- THIS WAS MISSING
  "dependencies": { "express": "^4.18.2" }
};
fs.writeFileSync(aiPath, JSON.stringify(aiPkg, null, 2));
console.log('✅ FIXED: AI package.json');

// 3. CRYPTO CONFIG
const cryptoPath = path.join(__dirname, 'services/crypto/package.json');
const cryptoPkg = {
  "name": "svc-crypto",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": { "start": "node index.js" },  // <--- THIS WAS MISSING
  "dependencies": { "express": "^4.18.2" }
};
fs.writeFileSync(cryptoPath, JSON.stringify(cryptoPkg, null, 2));
console.log('✅ FIXED: Crypto package.json');
