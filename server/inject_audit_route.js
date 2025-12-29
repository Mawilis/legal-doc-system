const fs = require('fs');
const path = require('path');

const appJsPath = path.join(__dirname, '../client/src/App.js');
let code = fs.readFileSync(appJsPath, 'utf8');

// Add Import if missing
if (!code.includes('AuditPage')) {
    const importStmt = "import AuditPage from './features/documents/pages/AuditPage';\n";
    code = importStmt + code;
}

// Add Route if missing
const route = '<Route path="sheriff/audit" element={<AuditPage />} />';
const anchor = '<Route path="sheriff/analytics" element={<SheriffAnalytics />} />';

if (!code.includes('sheriff/audit') && code.includes(anchor)) {
    code = code.replace(anchor, anchor + '\n              ' + route);
    fs.writeFileSync(appJsPath, code);
    console.log("✅ ROUTE INJECTED: /sheriff/audit");
} else if (code.includes('sheriff/audit')) {
    console.log("ℹ️ Route already exists.");
} else {
    console.log("⚠️ Could not find insertion point (SheriffAnalytics). Checking backup...");
    // Backup anchor
    const backupAnchor = '<Route path="sheriff/tracking" element={<SheriffTracking />} />';
    if (code.includes(backupAnchor)) {
         code = code.replace(backupAnchor, backupAnchor + '\n              ' + route);
         fs.writeFileSync(appJsPath, code);
         console.log("✅ ROUTE INJECTED (Backup): /sheriff/audit");
    } else {
         console.log("❌ Could not inject route automatically.");
    }
}
