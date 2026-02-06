/*
 * File: server/routes/api.js
 * STATUS: PRODUCTION-READY | ARCHITECTURAL CORE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Master API Manifest. Maps all versioned endpoints to their respective 
 * controllers and enforces global security perimeters via middleware.
 * -----------------------------------------------------------------------------
 */

'use strict';

const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/authMiddleware');

// --- 1. CORE & IDENTITY ---
const auth = require('../controllers/authController');
const user = require('../controllers/userController');
const tenant = require('../controllers/tenantController');

// --- 2. LEGAL MATTERS ---
const cases = require('../controllers/caseController');
const clients = require('../controllers/clientController');
const docs = require('../controllers/documentController');
const court = require('../controllers/courtController');

// --- 3. FINANCE & BILLING ---
const billing = require('../controllers/billingController');
const fees = require('../controllers/feeController');
const invoices = require('../controllers/invoiceController');
const payments = require('../controllers/paymentController');
const subs = require('../controllers/subscriptionController');

// --- 4. LOGISTICS & FIELD OPS ---
const dispatch = require('../controllers/dispatchController');
const sheriff = require('../controllers/sheriffController');
const attempts = require('../controllers/attemptController');
const returns = require('../controllers/returnController');

// --- 5. INTELLIGENCE & COMPLIANCE ---
const ai = require('../controllers/aiController');
const audit = require('../controllers/auditController');
const compliance = require('../controllers/complianceController');
const analytics = require('../controllers/analyticsController');
const retention = require('../controllers/retentionController');

// --- 6. UTILITIES & COMMUNICATION ---
const dash = require('../controllers/dashboardController');
const task = require('../controllers/taskController');
const msg = require('../controllers/messageController');
const search = require('../controllers/searchController');

// -----------------------------------------------------------------------------
// PUBLIC ROUTES (No Auth Required)
// -----------------------------------------------------------------------------
router.get('/health', (req, res) => res.status(200).json({ status: 'UP', timestamp: new Date() }));
router.post('/auth/register', auth.register);
router.post('/auth/login', auth.login);

// -----------------------------------------------------------------------------
// PROTECTED ROUTES (Requires Bearer Token & Iron Wall Isolation)
// -----------------------------------------------------------------------------
router.use(protect); // Apply global gatekeeper to all routes below

// --- User & Firm Profile ---
router.get('/auth/me', auth.getMe);
router.get('/tenants/me', tenant.getCurrentTenant);
router.route('/users').get(user.getUsers).post(authorize('admin'), user.createUser);

// --- Legal Case Management ---
router.route('/cases').get(cases.getCases).post(cases.createCase);
router.route('/clients').get(clients.getClients).post(clients.createClient);
router.route('/documents').get(docs.getDocuments).post(docs.createDocument);
router.get('/courts', court.getAll);

// --- Financial Engine ---
router.post('/billing/calculate', billing.calculateFees);
router.get('/fees', fees.getAllFees);
router.route('/invoices').get(invoices.getAllInvoices).post(invoices.createInvoice);
router.route('/payments').get(payments.getAllPayments).post(payments.createPayment);
router.get('/subscriptions/current', subs.getSubscription);

// --- Logistics & Field Ops ---
router.route('/dispatch').get(dispatch.getAllDispatches).post(dispatch.createDispatch);
router.get('/sheriffs/nearest', sheriff.findNearest);
router.patch('/sheriffs/location', sheriff.updateLocation);
router.post('/attempts/:id', attempts.createAttempt);
router.post('/returns/:id', returns.generateReturns);

// --- AI & Analytics ---
router.post('/ai/analyze', ai.analyzeDocument);
router.get('/analytics/monetization', authorize('admin', 'super_admin'), analytics.getMonetization);
router.get('/audit', authorize('admin'), audit.getAll);
router.get('/compliance/dashboard', compliance.getDashboard);

// --- Operations & Discovery ---
router.get('/dashboard/kpis', dash.getKpis);
router.get('/search', search.globalSearch);
router.route('/tasks').get(task.getMyTasks).post(task.createTask);
router.route('/messages').get(msg.getMyMessages).post(msg.sendMessage);

// --- Retention & Destruction (SuperAdmin Only) ---
router.post('/retention/destroy', authorize('super_admin'), retention.destroyExpiredRecords);

module.exports = router;