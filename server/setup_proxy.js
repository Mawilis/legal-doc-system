const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'server.js');
let serverCode = fs.readFileSync(serverPath, 'utf8');

// Check if we already added the proxy
if (!serverCode.includes('http-proxy-middleware')) {
    
    // 1. Add the Import at the top
    const importStatement = "const { createProxyMiddleware } = require('http-proxy-middleware');\n";
    serverCode = importStatement + serverCode;
    
    // 2. Add the Route (We insert it before the Routes section)
    const proxyRoute = `
// --- MICROSERVICES PROXY ---
console.log('🔗 [Gateway] Wiring Microservices...');
app.use('/api/ledger', createProxyMiddleware({ 
    target: 'http://localhost:6000', // Points to Ledger Service
    changeOrigin: true,
    pathRewrite: { '^/api/ledger': '' } // Remove /api/ledger prefix when forwarding
}));
`;
    // We insert it before the Tracking Routes to ensure it loads early
    const insertPoint = "app.use('/api', loadRoute('./routes/trackingRoutes'));";
    
    if (serverCode.includes(insertPoint)) {
        serverCode = serverCode.replace(insertPoint, insertPoint + proxyRoute);
        fs.writeFileSync(serverPath, serverCode);
        console.log("✅ PROXY WIRED: Main Server is now connected to the Ledger.");
    } else {
        // Fallback: Just append if we can't find the exact line (safety net)
        console.log("⚠️ Standard insertion point not found. Trying backup...");
        const backupPoint = "app.use('/api/documents', loadRoute('./routes/documentRoutes'));";
        if(serverCode.includes(backupPoint)) {
             serverCode = serverCode.replace(backupPoint, backupPoint + proxyRoute);
             fs.writeFileSync(serverPath, serverCode);
             console.log("✅ PROXY WIRED (Backup Method): Connected to Ledger.");
        } else {
             console.log("❌ Could not inject proxy. Please show me your server.js content.");
        }
    }
} else {
    console.log("ℹ️ Proxy configuration is already present.");
}
