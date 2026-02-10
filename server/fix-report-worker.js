const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../server/workers/reportWorker.js');
if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace the function to actually use the parameter
    content = content.replace(
        /async function generateReport\(reportData\)\s*\{[\s\S]*?\}/,
        `async function generateReport(reportData) {
    if (!reportData || !reportData.id) {
        throw new Error('Invalid report data');
    }
    
    console.log(\`Generating report for: \${reportData.id}\`);
    // Process report data here
    return { 
        id: reportData.id, 
        status: 'generated',
        timestamp: new Date().toISOString()
    };
}`
    );
    
    fs.writeFileSync(filePath, content);
    console.log('Fixed reportWorker.js to use parameter');
}
