const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../server/validators/superAdminValidator.js');
if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    let lines = content.split('\n');
    
    // Fix line 1114
    if (lines[1113] && lines[1113].includes('(_email)')) {
        lines[1113] = lines[1113].replace('(_email)', '(email)');
        // Add a usage comment or actual usage
        if (lines[1114] && lines[1114].trim() === '{') {
            lines.splice(1115, 0, '    // Validate email format');
            lines.splice(1116, 0, '    if (!email || typeof email !== \'string\') {');
            lines.splice(1117, 0, '        throw new Error(\'Invalid email parameter\');');
            lines.splice(1118, 0, '    }');
        }
    }
    
    // Fix line 1125
    if (lines[1124] && lines[1124].includes('(_idNumber)')) {
        lines[1124] = lines[1124].replace('(_idNumber)', '(idNumber)');
        // Add usage
        if (lines[1125] && lines[1125].trim() === '{') {
            lines.splice(1126, 0, '    // Validate ID number');
            lines.splice(1127, 0, '    if (!idNumber || typeof idNumber !== \'string\') {');
            lines.splice(1128, 0, '        throw new Error(\'Invalid ID number\');');
            lines.splice(1129, 0, '    }');
        }
    }
    
    fs.writeFileSync(filePath, lines.join('\n'));
    console.log('Fixed superAdminValidator.js parameter usage');
}
