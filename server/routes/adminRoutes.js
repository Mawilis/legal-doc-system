const express = require('express');
const { check, validationResult } = require('express-validator');
const adminController = require('../controllers/adminController');  // Import adminController
const { protect, restrictToAdmin } = require('../middleware/authMiddleware');  // Import middleware for authentication and role-based access control
const rateLimit = require('express-rate-limit');  // Rate limiting for routes
const router = express.Router();

// Debug log to confirm all functions are imported
console.log('Admin Controller Functions:', Object.keys(adminController));  // Log imported functions

// Rate limiter for admin actions (e.g., user management)
const adminLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 50, // Limit each IP to 50 requests per window
    message: 'Too many requests from this IP, please try again after 15 minutes.',
});

// Password complexity validation
const passwordComplexityCheck = check('password')
    .isLength({ min: 8 }).withMessage('Password must be at least 8 characters long')
    .matches(/\d/).withMessage('Password must contain at least one number')
    .matches(/[!@#$%^&*]/).withMessage('Password must contain at least one special character (!@#$%^&*)');

// Helper function to handle validation errors
const handleValidationErrors = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        console.error('Validation errors:', errors.array());
        return res.status(400).json({ errors: errors.array() });
    }
    next();
};

// Admin routes (protected with role-based access)
router.post(
    '/users',
    protect,  // Apply `protect` middleware to secure the route
    restrictToAdmin,  // Apply admin-only restriction
    adminLimiter,  // Apply rate limiting
    [
        check('name').not().isEmpty().withMessage('Name is required'),
        check('email').isEmail().withMessage('Email is invalid'),
        passwordComplexityCheck,
    ],
    handleValidationErrors,  // Validate request data
    adminController.createUser  // Create a new user
);

router.get('/users', protect, restrictToAdmin, adminLimiter, adminController.getAllUsers);  // Get all users
router.get('/users/:userId', protect, restrictToAdmin, adminLimiter, adminController.getUserById);  // Get a user by ID
router.put(
    '/users/:userId',
    protect,
    restrictToAdmin,
    adminLimiter,
    [
        check('name').optional().not().isEmpty().withMessage('Name must not be empty'),
        check('email').optional().isEmail().withMessage('Email is invalid'),
        passwordComplexityCheck.optional(),
    ],
    handleValidationErrors,
    adminController.updateUser  // Update a user
);

router.delete('/users/:userId', protect, restrictToAdmin, adminLimiter, adminController.deleteUser);  // Delete a user

// Export the router
module.exports = router;