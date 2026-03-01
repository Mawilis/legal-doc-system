#!import fs from 'fs';

// Read the current model file
const modelPath = './models/DocumentTemplate.js';
let content = fs.readFileSync(modelPath, 'utf8');

console.log('🔧 Fixing DocumentTemplate model...');

// Check if forensicHash is required in the schema
const forensicHashRegex = /forensicHash:\s*{\s*type:\s*String,\s*required:\s*true/;
if (forensicHashRegex.test(content)) {
  console.log('  - forensicHash is required, fixing...');
  content = content.replace(
    /forensicHash:\s*{\s*type:\s*String,\s*required:\s*true/,
    'forensicHash: {\n    type: String,\n    required: false'
  );
}

// Check if the pre-save hook is generating forensicHash
const preSaveRegex = /pre\('save', async function\(next\) {/;
if (preSaveRegex.test(content)) {
  console.log('  - Found pre-save hook, checking if it generates forensicHash...');

  // Check if forensicHash is being set in pre-save
  if (!content.includes('this.forensicHash =')) {
    console.log('  - WARNING: pre-save hook does not set forensicHash');
  }
}

// Write the fixed content
fs.writeFileSync(modelPath, content);
console.log('✅ Model file updated');

// Now let's look at the pre-save hook more carefully
console.log('\n📝 Current pre-save hook:');
const preSaveMatch = content.match(/pre\('save', async function\(next\) {[^}]+}/s);
if (preSaveMatch) {
  console.log(preSaveMatch[0]);
}

// Create a fixed version of the pre-save hook
console.log('\n🛠️  Creating fixed pre-save hook...');

const fixedPreSaveHook = `
documentTemplateSchema.pre('save', async function(next) {
  try {
    this.audit.updatedAt = new Date();
    
    if (!this.retentionEnd) {
      this.retentionEnd = new Date();
      this.retentionEnd.setFullYear(this.retentionEnd.getFullYear() + 10);
    }
    
    // Add to version history on content change
    if (this.isModified('content.raw') && !this.isNew) {
      this.versionHistory.push({
        version: this.version,
        content: this.content.raw,
        variables: this.variables,
        createdBy: this.audit.updatedBy || this.audit.createdBy,
        changelog: \`Version \${this.version} updated\`
      });
      this.version += 1;
    }
    
    // Compile template (simplified - would use actual compiler in production)
    if (this.content.raw && this.content.format === 'handlebars') {
      // In production, this would compile with Handlebars
      this.content.compiled = this.content.raw;
    }
    
    // Generate templateId if not set
    if (!this.templateId) {
      this.templateId = \`TMP-\${crypto.randomBytes(4).toString('hex').toUpperCase()}\`;
    }
    
    // Generate forensic hash
    const canonicalData = JSON.stringify({
      templateId: this.templateId,
      tenantId: this.tenantId,
      name: this.name,
      templateType: this.templateType,
      practiceArea: this.practiceArea,
      version: this.version,
      status: this.status,
      previousHash: this.previousHash
    }, Object.keys({
      templateId: null,
      tenantId: null,
      name: null,
      templateType: null,
      practiceArea: null,
      version: null,
      status: null,
      previousHash: null
    }).sort());

    this.forensicHash = crypto
      .createHash('sha256')
      .update(canonicalData)
      .digest('hex');

    next();
  } catch (error) {
    next(error);
  }
});
`;

console.log('\n✅ Fixed pre-save hook ready');
console.log('To apply the fix, replace the pre-save hook in models/DocumentTemplate.js');
