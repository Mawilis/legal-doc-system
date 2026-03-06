import fs from 'fs';

// Fix ElectronicSignature.js - more aggressive pattern matching
const modelPath = '/Users/wilsonkhanyezi/legal-doc-system/server/models/ElectronicSignature.js';
let content = fs.readFileSync(modelPath, 'utf8');

// Remove ANY index: true from ANY field
content = content.replace(/index:\s*true,?\s*/g, '');

// Make sure forensicHash still has unique: true
if (!content.includes('unique: true')) {
  content = content.replace(
    /forensicHash:\s*\{\s*type:\s*String,\s*/,
    'forensicHash: { type: String, unique: true, '
  );
}

fs.writeFileSync(modelPath, content);
console.log('✅ Deep cleaned ElectronicSignature indexes');

// Fix DocumentTemplate.js
const templatePath = '/Users/wilsonkhanyezi/legal-doc-system/server/models/DocumentTemplate.js';
if (fs.existsSync(templatePath)) {
  let templateContent = fs.readFileSync(templatePath, 'utf8');
  templateContent = templateContent.replace(/index:\s*true,?\s*/g, '');
  fs.writeFileSync(templatePath, templateContent);
  console.log('✅ Deep cleaned DocumentTemplate indexes');
}
