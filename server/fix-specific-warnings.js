const fs = require('fs');
const path = require('path');

const filesToFix = [
    {
        path: '/Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js',
        fixes: [
            { line: 2037, find: '(entityType)', replace: '(_entityType)' },
            { line: 2046, find: '(_, data)', replace: '(_unused, data)' },
            { line: 2870, find: 'const now = ', replace: '// const now = ' }
        ]
    },
    {
        path: '/Users/wilsonkhanyezi/legal-doc-system/server/validators/superAdminValidator.js',
        fixes: [
            { line: 1114, find: '(_email)', replace: '(email)' }, // Actually use it or keep as _
            { line: 1125, find: '(_idNumber)', replace: '(idNumber)' }
        ]
    },
    {
        path: '/Users/wilsonkhanyezi/legal-doc-system/server/websockets/auditWebSocket.js',
        fixes: [
            { line: 614, find: '(verificationId)', replace: '(_verificationId)' }
        ]
    },
    {
        path: '/Users/wilsonkhanyezi/legal-doc-system/server/workers/reportWorker.js',
        fixes: [
            { line: 20, find: 'async function generateReport(_report)', replace: 'async function generateReport(reportData)' }
        ]
    }
];

filesToFix.forEach(fileInfo => {
    if (fs.existsSync(fileInfo.path)) {
        let content = fs.readFileSync(fileInfo.path, 'utf8');
        let lines = content.split('\n');
        
        fileInfo.fixes.forEach(fix => {
            const lineIndex = fix.line - 1;
            if (lines[lineIndex]) {
                lines[lineIndex] = lines[lineIndex].replace(fix.find, fix.replace);
                console.log(`Fixed ${path.basename(fileInfo.path)}:${fix.line}`);
            }
        });
        
        fs.writeFileSync(fileInfo.path, lines.join('\n'));
    }
});

console.log('=== SPECIFIC WARNINGS FIXED ===');
