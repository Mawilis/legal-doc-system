const fs = require('fs');
const path = require('path');

console.log('🔧 WILSY OS 2050 - Fixing remaining test issues...\n');

// 1. Fix duplicate index in ElectronicSignature.js
const modelPath = '/Users/wilsonkhanyezi/legal-doc-system/server/models/ElectronicSignature.js';
let modelContent = fs.readFileSync(modelPath, 'utf8');

// Remove duplicate index from forensicHash
modelContent = modelContent.replace(
  /(forensicHash:\s*\{[^}]*)index:\s*true,?\s*/g,
  '$1'
);

// Add placeLegalHold method if not present
if (!modelContent.includes('placeLegalHold')) {
  const methodsEndIndex = modelContent.indexOf('// ============================================================================\n// STATIC METHODS');
  
  const legalHoldMethods = `

electronicSignatureSchema.methods.placeLegalHold = function(reason, imposedBy, courtOrderNumber = null) {
  if (!this.legalHolds) this.legalHolds = [];
  
  const holdId = \`HLD-\${crypto.randomBytes(8).toString('hex').toUpperCase()}\`;
  
  this.legalHolds.push({
    holdId,
    imposedAt: new Date(),
    imposedBy,
    reason,
    courtOrderNumber: courtOrderNumber,
    status: 'active'
  });
  
  this.retentionPolicy = 'FORENSIC_INDEFINITE';
  this.retentionEnd = null;
  
  if (!this.audit.events) this.audit.events = [];
  this.audit.events.push({
    event: 'LEGAL_HOLD_PLACED',
    timestamp: new Date(),
    userId: imposedBy,
    metadata: { holdId, reason, courtOrderNumber }
  });
  
  return holdId;
};

electronicSignatureSchema.methods.releaseLegalHold = function(holdId, releasedBy) {
  if (!this.legalHolds) return false;
  
  const hold = this.legalHolds.find(h => h.holdId === holdId);
  if (!hold) return false;
  
  hold.status = 'released';
  hold.releasedAt = new Date();
  hold.releasedBy = releasedBy;
  
  if (!this.audit.events) this.audit.events = [];
  this.audit.events.push({
    event: 'LEGAL_HOLD_RELEASED',
    timestamp: new Date(),
    userId: releasedBy,
    metadata: { holdId }
  });
  
  return true;
};
`;

  modelContent = modelContent.slice(0, methodsEndIndex) + legalHoldMethods + modelContent.slice(methodsEndIndex);
}

fs.writeFileSync(modelPath, modelContent);
console.log('✅ Fixed ElectronicSignature model (removed duplicate index, added legal hold methods)');

// 2. Quick fix for eSignService.js signDocument method to handle test cases
const servicePath = '/Users/wilsonkhanyezi/legal-doc-system/server/services/eSignService.js';
let serviceContent = fs.readFileSync(servicePath, 'utf8');

// Make signDocument more permissive for tests
if (serviceContent.includes('Signer verification failed')) {
  // This is a complex fix - would need to see the actual method
  console.log('⚠️  Manual review needed for eSignService.js signDocument method');
}

console.log('\n✅ Fixes applied!');
console.log('\n📋 Next steps:');
console.log('1. Review eSignService.js signDocument method around line 765');
console.log('2. Run tests again:');
console.log('   cd /Users/wilsonkhanyezi/legal-doc-system/server && \\');
console.log('   NODE_ENV=test npx mocha --require @babel/register --timeout 60000 tests/services/eSignService.test.js --exit');
