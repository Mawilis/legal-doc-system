const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../server/workers/retentionAgenda.js');
let content = fs.readFileSync(filePath, 'utf8');

// Find and fix the TD syntax error
content = content.replace(/graph TD/g, '// graph TD');
content = content.replace(/A\[.*\] --> B\[.*\];/g, '// A[] --> B[];');

// Also fix any other mermaid syntax that might be causing issues
content = content.replace(/^\s*TD\s*$/gm, '// TD');

console.log('Fixed mermaid diagram syntax in retentionAgenda.js');

// Write back
fs.writeFileSync(filePath, content);
