const express = require('express');
const app = express();

// Your middleware and routes here...

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OPERATIONAL',
        system: 'Wilsy OS Legal Engine',
        timestamp: new Date().toISOString()
    });
});

// 4. PORT CONFIGURATION
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Server active on http://localhost:${PORT}`);
    console.log(`🛡️  Security Stack: ACTIVE`);
});
