import fs from 'fs';

// Fix ElectronicSignature.js
const modelPath = '/Users/wilsonkhanyezi/legal-doc-system/server/models/ElectronicSignature.js';
let content = fs.readFileSync(modelPath, 'utf8');

// Remove the index: true from forensicHash field completely
content = content.replace(
  /(forensicHash:\s*\{[^}]*?)index:\s*true,?\s*/g,
  '$1'
);

// Also check for any other duplicate index patterns
content = content.replace(
  /(unique:\s*true,\s*)index:\s*true,?\s*/g,
  '$1'
);

fs.writeFileSync(modelPath, content);
console.log('✅ Fixed ElectronicSignature duplicate index warning');

// Fix DocumentTemplate.js if it exists
const templatePath = '/Users/wilsonkhanyezi/legal-doc-system/server/models/DocumentTemplate.js';
if (fs.existsSync(templatePath)) {
  let templateContent = fs.readFileSync(templatePath, 'utf8');
  templateContent = templateContent.replace(
    /(forensicHash:\s*\{[^}]*?)index:\s*true,?\s*/g,
    '$1'
  );
  fs.writeFileSync(templatePath, templateContent);
  console.log('✅ Fixed DocumentTemplate duplicate index warning');
}
