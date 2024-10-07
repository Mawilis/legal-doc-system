const express = require('express');
const { check, validationResult } = require('express-validator');
const adminController = require('../controllers/adminController');
const { protect, admin } = require('../middleware/authMiddleware');
const rateLimit = require('express-rate-limit');
const router = express.Router();

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
        return res.status(400).json({ errors: errors.array() });
    }
    next();
};

// Admin routes (protected with role-based access)
router.post(
    '/users',
    protect,
    admin,
    adminLimiter,
    [
        check('name').not().isEmpty().withMessage('Name is required'),
        check('email').isEmail().withMessage('Email is invalid'),
        passwordComplexityCheck,
    ],
    handleValidationErrors,
    adminController.createUser
);

router.get('/users', protect, admin, adminLimiter, adminController.getAllUsers);

router.get('/users/:userId', protect, admin, adminLimiter, adminController.getUserById);

router.put(
    '/users/:userId',
    protect,
    admin,
    adminLimiter,
    [
        check('name').optional().not().isEmpty().withMessage('Name must not be empty'),
        check('email').optional().isEmail().withMessage('Email is invalid'),
        passwordComplexityCheck.optional(),
    ],
    handleValidationErrors,
    adminController.updateUser
);

router.delete('/users/:userId', protect, admin, adminLimiter, adminController.deleteUser);

module.exports = router;
