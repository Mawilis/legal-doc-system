const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'server.js');
let serverCode = fs.readFileSync(serverPath, 'utf8');

const standardsRoute = `
// --- PROXY: STANDARDS ENGINE ---
app.use('/api/standards', createProxyMiddleware({ 
    target: 'http://localhost:6100', 
    changeOrigin: true,
    pathRewrite: { '^/api/standards': '' } 
}));
`;

// We look for the Ledger Proxy we added earlier, and place this right after it.
const anchor = "pathRewrite: { '^/api/ledger': '' } // Remove /api/ledger prefix when forwarding\n}));";

if (serverCode.includes('http://localhost:6100')) {
    console.log("ℹ️ Standards Proxy already exists.");
} else if (serverCode.includes(anchor)) {
    serverCode = serverCode.replace(anchor, anchor + standardsRoute);
    fs.writeFileSync(serverPath, serverCode);
    console.log("✅ PROXY WIRED: Main Server connected to Standards Engine.");
} else {
    console.log("❌ Could not find insertion point. Check server.js structure.");
}
