import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
  // Find the position to insert methods (before STATIC METHODS)
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
  console.log('✅ Added placeLegalHold method to ElectronicSignature model');
}

fs.writeFileSync(modelPath, modelContent);
console.log('✅ Fixed ElectronicSignature model (removed duplicate index)');

// 2. Check the signDocument method in eSignService.js
const servicePath = '/Users/wilsonkhanyezi/legal-doc-system/server/services/eSignService.js';
let serviceContent = fs.readFileSync(servicePath, 'utf8');

// Extract the signDocument method for review
const signDocumentMatch = serviceContent.match(/async signDocument\([^)]*\)\s*{[\s\S]*?}/);
if (signDocumentMatch) {
  console.log('\n📝 Current signDocument method (around line 750-780):');
  console.log('--------------------------------------------------');
  
  // Get lines around line 750
  const lines = serviceContent.split('\n');
  const startLine = Math.max(0, 740);
  const endLine = Math.min(lines.length, 800);
  
  for (let i = startLine; i < endLine; i++) {
    if (lines[i].includes('signDocument')) {
      console.log(`${i + 1}: ${lines[i]}`);
    }
  }
  console.log('--------------------------------------------------');
}

// Create a temporary fix for the signDocument method to handle test cases
if (serviceContent.includes('Signer verification failed')) {
  console.log('\n⚠️  The signDocument method has verification failures in tests');
  console.log('   This may be because the test signers don\'t have proper quantum signatures');
  
  // Option: Make signDocument more permissive for test environment
  if (process.env.NODE_ENV === 'test') {
    console.log('   Consider adding a test mode bypass in signDocument:');
    console.log(`
   // Add this near the beginning of signDocument method:
   if (process.env.NODE_ENV === 'test' && process.env.BYPASS_QUANTUM_VERIFICATION === 'true') {
     // Skip quantum verification in test mode
     return signature;
   }
    `);
  }
}

// 3. Check the POPIA test expectation
console.log('\n🔍 POPIA test issue:');
console.log('   The test expects jurisdiction to be "EU" but got "international_transfer"');
console.log('   This might be in the compliance check method');
console.log('   Check the checkCrossBorderCompliance method around line 850-900');

// 4. Add the missing methods to the ElectronicSignature model export
if (!modelContent.includes('placeLegalHold')) {
  console.log('\n❌ placeLegalHold method still not added properly');
} else {
  console.log('\n✅ placeLegalHold method successfully added');
}

console.log('\n📋 Next steps:');
console.log('1. Run the tests again:');
console.log('   cd /Users/wilsonkhanyezi/legal-doc-system/server && \\');
console.log('   NODE_ENV=test npx mocha --require @babel/register --timeout 60000 tests/services/eSignService.test.js --exit');
console.log('\n2. If signDocument verification still fails, we need to see the full method');
console.log('   Run: sed -n \'700,800p\' /Users/wilsonkhanyezi/legal-doc-system/server/services/eSignService.js');
