// ~/legal-doc-system/server/routes/dashboard.js

const express = require('express');
const router = express.Router();

// Mock Data - Replace with actual database queries
const dashboardData = {
    metrics: {
        totalDocuments: 100,
        totalUsers: 50,
        monthlyGrowth: 5,
    },
    charts: {
        documentsOverTime: [
            { month: 'Jan', documents: 10 },
            { month: 'Feb', documents: 15 },
            { month: 'Mar', documents: 20 },
            { month: 'Apr', documents: 25 },
            { month: 'May', documents: 30 },
            { month: 'Jun', documents: 35 },
            { month: 'Jul', documents: 40 },
            { month: 'Aug', documents: 45 },
            { month: 'Sep', documents: 50 },
            { month: 'Oct', documents: 55 },
            { month: 'Nov', documents: 60 },
            { month: 'Dec', documents: 65 },
        ],
        userActivity: [
            { user: 'John', actions: 5 },
            { user: 'Jane', actions: 7 },
            { user: 'Bob', actions: 3 },
            { user: 'Alice', actions: 8 },
            { user: 'Mike', actions: 4 },
        ],
    },
};

// GET /api/dashboard
router.get('/', (req, res) => {
    res.json(dashboardData);
});

module.exports = router;
