const express = require('express');
const { protect, authorize } = require('../middleware/authMiddleware');  // Import the correct middleware function
const router = express.Router();

// Protect all dashboard routes if required for authentication
router.use(protect);

// Dashboard route - replace with real logic or fetching from database
router.get('/', authorize('admin'), (req, res) => {  // Use 'authorize' instead of 'restrictToAdmin'
    const dashboardData = {
        title: "Dashboard Info",
        stats: {
            users: 120,  // Replace with real data
            documents: 50,  // Replace with real data
            notifications: 10,  // Replace with real data
        }
    };
    res.status(200).json(dashboardData);
});

module.exports = router;
