const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    res.json({
        status: 'active',
        message: 'Billion-dollar revenue API',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

module.exports = router;
