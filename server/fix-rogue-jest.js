#!import fs from 'fs';

const validatorPath =
  '/Users/wilsonkhanyezi/legal-doc-system/server/validators/complianceValidator.js';

try {
  let content = fs.readFileSync(validatorPath, 'utf8');

  // Find and comment out any line trying to import Jest globals
  if (content.includes('@jest/globals')) {
    content = content.replace(
      /.*['"]@jest\/globals['"].*/g,
      '// FORENSIC FIX: Purged rogue IDE auto-import for @jest/globals'
    );
    fs.writeFileSync(validatorPath, content);
    console.log('✅ Purged rogue @jest/globals from complianceValidator.js');
  } else {
    console.log('✅ No rogue Jest imports found.');
  }
} catch (error) {
  console.error('⚠️ Patch failed:', error.message);
}
