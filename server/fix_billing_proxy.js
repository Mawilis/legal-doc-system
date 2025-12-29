const fs = require('fs');
const path = require('path');

console.log('🔗 UPDATING GATEWAY PROXY SETTINGS...');

const serverPath = path.join(__dirname, 'server.js');
let code = fs.readFileSync(serverPath, 'utf8');

// Replace potentially ambiguous 'localhost' with robust '127.0.0.1' for Billing
const oldProxy = "target: 'http://localhost:6400'";
const newProxy = "target: 'http://127.0.0.1:6400'";

if (code.includes(oldProxy)) {
    code = code.replace(oldProxy, newProxy);
    fs.writeFileSync(serverPath, code);
    console.log("✅ FIXED: Gateway now points to Billing at 127.0.0.1:6400");
} else if (code.includes(newProxy)) {
    console.log("ℹ️ Gateway already using IPv4.");
} else {
    console.log("⚠️ Could not find Billing Proxy config. Ensure it was wired correctly.");
}
