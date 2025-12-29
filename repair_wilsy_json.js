const fs = require('fs');
const path = require('path');

console.log('🚑 REPAIRING JSON CONFIGURATION FILES...');

// 1. BILLING Package
const billingPath = path.join(__dirname, 'services/billing/package.json');
const billingPkg = {
  "name": "svc-billing",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2", "body-parser": "^1.20.2", "cors": "^2.8.5" }
};
fs.writeFileSync(billingPath, JSON.stringify(billingPkg, null, 2));
console.log('✅ FIXED: services/billing/package.json');

// 2. AI Package
const aiPath = path.join(__dirname, 'services/ai/package.json');
const aiPkg = {
  "name": "svc-ai",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2" }
};
fs.writeFileSync(aiPath, JSON.stringify(aiPkg, null, 2));
console.log('✅ FIXED: services/ai/package.json');

// 3. CRYPTO Package
const cryptoPath = path.join(__dirname, 'services/crypto/package.json');
const cryptoPkg = {
  "name": "svc-crypto",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2", "crypto": "^1.0.1" }
};
fs.writeFileSync(cryptoPath, JSON.stringify(cryptoPkg, null, 2));
console.log('✅ FIXED: services/crypto/package.json');

console.log('✨ ALL PACKAGE.JSON FILES ARE NOW VALID.');
