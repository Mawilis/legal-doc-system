const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../server/validators/popiaValidator.js');
let content = fs.readFileSync(filePath, 'utf8');

// Remove all mongoose declarations and keep only one at the top
const lines = content.split('\n');
let mongooseFound = false;
let newLines = [];

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('const mongoose = require')) {
        if (!mongooseFound) {
            // Keep the first one
            newLines.push(lines[i]);
            mongooseFound = true;
        } else {
            // Comment out duplicates
            newLines.push('// ' + lines[i] + ' // Duplicate removed');
        }
    } else {
        newLines.push(lines[i]);
    }
}

content = newLines.join('\n');
fs.writeFileSync(filePath, content);
console.log('Fixed duplicate mongoose declaration');
