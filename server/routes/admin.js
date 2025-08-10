// ~/server/routes/admin.js

const express = require('express');
const router = express.Router();

// --- Import Middleware ---
const { protect, authorize } = require('../middleware/authMiddleware');
const asyncHandler = require('../middleware/asyncHandler');
const validateObjectId = require('../middleware/validateObjectId');

// --- Import Controllers ---
const { getSystemStats } = require('../controllers/adminController');
const {
    getAllUsers,
    createUser,
    updateUser,
    deleteUser,
    updatePermissions,
    assignUserToTeam
} = require('../controllers/userController');

// --- Security for All Admin Routes ---
// This ensures every route in this file requires authentication and the 'admin' role.
router.use(protect);
router.use(authorize('admin'));

// --- Admin Dashboard & Stats ---
router.get('/stats', asyncHandler(getSystemStats));

// --- User Management Routes ---
router.get('/users', asyncHandler(getAllUsers));
router.post('/users', asyncHandler(createUser));

router.route('/users/:id')
    .put(validateObjectId, asyncHandler(updateUser))
    .delete(validateObjectId, asyncHandler(deleteUser));

// --- Permissions & Teams ---
router.put('/users/:id/permissions', validateObjectId, asyncHandler(updatePermissions));
router.put('/users/:id/team', validateObjectId, asyncHandler(assignUserToTeam));

module.exports = router;