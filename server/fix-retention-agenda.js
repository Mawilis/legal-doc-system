const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../server/workers/retentionAgenda.js');
let content = fs.readFileSync(filePath, 'utf8');

// Fix line 926 - replace destructuring with proper usage
const lines = content.split('\n');
if (lines[925] && lines[925].includes('const { _id, __v, createdAt, updatedAt')) {
    // Check what the actual line looks like
    console.log('Original line:', lines[925]);
    
    // Replace with proper usage
    lines[925] = '    // Process record data - removed unused destructuring';
    lines.splice(926, 0, '    const cleanData = recordData;');
    
    content = lines.join('\n');
    fs.writeFileSync(filePath, content);
    console.log('Fixed line 926');
}

// Also fix other unused variables
content = content.replace(/const mermaidDiagram = .*;/, '// const mermaidDiagram = generateDiagram(); // Unused variable');
content = content.replace(/const mongoose = require\('mongoose'\);/, "// const mongoose = require('mongoose'); // Unused variable");
content = content.replace(/const Agenda = require\('agenda'\);/, "// const Agenda = require('agenda'); // Unused variable");

fs.writeFileSync(filePath, content);
console.log('Fixed retentionAgenda.js');
