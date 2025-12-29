const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'server.js');
let code = fs.readFileSync(serverPath, 'utf8');

const newRoutes = `
// --- PROXY: BILLING ENGINE (Port 6400) ---
app.use('/api/billing', createProxyMiddleware({ 
    target: 'http://localhost:6400', 
    changeOrigin: true, 
    pathRewrite: { '^/api/billing': '' } 
}));

// --- PROXY: AI ENGINE (Port 6500) ---
app.use('/api/ai', createProxyMiddleware({ 
    target: 'http://localhost:6500', 
    changeOrigin: true, 
    pathRewrite: { '^/api/ai': '' } 
}));

// --- PROXY: CRYPTO VAULT (Port 6600) ---
app.use('/api/crypto', createProxyMiddleware({ 
    target: 'http://localhost:6600', 
    changeOrigin: true, 
    pathRewrite: { '^/api/crypto': '' } 
}));
`;

const anchor = "pathRewrite: { '^/api/standards': '' } \n}));";

if (code.includes('http://localhost:6400')) {
    console.log("ℹ️ New services already wired.");
} else if (code.includes(anchor)) {
    code = code.replace(anchor, anchor + newRoutes);
    fs.writeFileSync(serverPath, code);
    console.log("✅ GATEWAY UPDATED: Wired Billing, AI, and Crypto services.");
} else {
    // Fallback if anchor looks different due to formatting
    const backupAnchor = "pathRewrite: { '^/api/standards': '' }";
    if (code.includes(backupAnchor)) {
        // Find the closing brackets of the previous proxy to insert cleanly
        const parts = code.split(backupAnchor);
        // We assume the code looks standard. We append after the closing brackets of middleware
        // This is a bit risky blindly, so we append to end of middleware chain if anchor fails
        console.log("⚠️ Precise anchor not found. Please verify server.js manually or re-check the standards proxy.");
    }
}
