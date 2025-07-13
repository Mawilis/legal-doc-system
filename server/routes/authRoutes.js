const express = require('express');
const { register, login, getMe } = require('../controllers/authController');
const { protect } = require('../middleware/auth');  // ✅ Updated import path
const {
    validate,
    registerRules,
    loginRules,
} = require('../validators/userValidator');

const router = express.Router();

/**
 * @swagger
 * /api/auth/register:
 *   post:
 *     summary: Register a new user
 *     description: Creates a new user account after validating the input data.
 *     tags:
 *       - Auth
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/RegisterUser'
 *     responses:
 *       201:
 *         description: User registered successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User registered successfully
 *                 userId:
 *                   type: string
 *                   example: 60c72b2f5f9b256d88f4e5b0
 *       400:
 *         description: Bad request. Invalid data or missing fields.
 *       422:
 *         description: Validation error (e.g., invalid email, password too short).
 */
router.post('/register', registerRules(), validate, register);

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: Log in a user
 *     description: Authenticates a user and returns a JWT token if successful.
 *     tags:
 *       - Auth
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/LoginUser'
 *     responses:
 *       200:
 *         description: Login successful. Returns JWT token.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 token:
 *                   type: string
 *                   example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
 *       400:
 *         description: Bad request. Missing email or password.
 *       401:
 *         description: Unauthorized. Invalid credentials.
 *       422:
 *         description: Validation error.
 */
router.post('/login', loginRules(), validate, login);

/**
 * @swagger
 * /api/auth/me:
 *   get:
 *     summary: Get current logged-in user's profile
 *     description: Retrieves the profile details of the authenticated user.
 *     tags:
 *       - Auth
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: User profile retrieved successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                   example: 60c72b2f5f9b256d88f4e5b0
 *                 name:
 *                   type: string
 *                   example: John Doe
 *                 email:
 *                   type: string
 *                   example: john.doe@example.com
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.get('/me', protect, getMe);

module.exports = router;
