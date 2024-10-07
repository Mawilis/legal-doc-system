// routes/dashboardRoutes.js
const express = require('express');
const router = express.Router();

// Dummy dashboard data - replace with actual logic
router.get('/', (req, res) => {
    const dashboardData = {
        title: "Dashboard Info",
        stats: {
            users: 120,
            documents: 50,
            notifications: 10,
        }
    };
    res.status(200).json(dashboardData);
});

module.exports = router;
